#!/usr/bin/env python3
# app.py
# Flask web-app for ICPC-2 coding with streaming

import os
import json
import time
from flask import Flask, render_template, request, jsonify, Response, stream_template
from flask_cors import CORS
from dotenv import load_dotenv
from rag_infer import infer, call_mistral_stream
from icpc_utils import ICPCEntry
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
EMB_MODEL = os.environ.get("EMB_MODEL", "intfloat/multilingual-e5-base")
INDEX_PATH = os.environ.get("INDEX_PATH", "icpc2.faiss")
META_PATH = os.environ.get("META_PATH", "icpc2_meta.json")
TOPN_RETRIEVE = int(os.environ.get("TOPN_RETRIEVE", "40"))
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.2"))
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "800"))

# Load models and data once at startup
print("🔄 Loading models and data...")
faiss_index = faiss.read_index(INDEX_PATH)
with open(META_PATH, "r", encoding="utf-8") as f:
    meta = [ICPCEntry(**r) for r in json.load(f)]
emb = SentenceTransformer(EMB_MODEL)
print("✅ Models loaded successfully!")

def embed_queries(texts, model):
    return model.encode([f"query: {t}" for t in texts], convert_to_numpy=True, normalize_embeddings=True)

def retrieve(note_text, model, faiss_index, meta, topn):
    qvec = embed_queries([note_text], model)[0].astype(np.float32)
    D, I = faiss_index.search(qvec.reshape(1, -1), topn)
    return [meta[i] for i in I[0]]

def format_grounding(entries):
    lines = []
    for e in entries:
        comp = e.component_guess if e.component_guess is not None else e.component_hint
        lines.append(f"{e.code} | {e.title} | component:{comp} | chapter:{e.chapter}")
    return "\n".join(lines)

SYSTEM_PROMPT = """Du er en medisinsk kodeassistent i allmennpraksis.
Oppgave: Foreslå ICPC-2-koder for et konsultasjonsnotat.

Regler:
1) Returner KUN gyldig JSON som matcher skjemaet nedenfor. Ingen fritekst.
2) Velg koder KUN fra listen i <icpc2_kandidater>.
3) Maks 3 forslag.
4) Symptom vs. diagnose: Hvis diagnosen ikke er tydelig etablert, prioriter symptomkode (komponent 1) fremfor sykdomsdiagnose (komponent 7).
5) Prosesskoder (komponent 2–6) kun ved eksplisitt prosess (screening, henvisning, sykmelding, prøver, behandling, administrativt).
6) For hver kode: kort begrunnelse og 1–3 tekstbevis (spans) ordrett fra notatet (angi gjerne seksjon).
7) Sett confidence 0.0–1.0 konservativt. Bruk needs_review: true ved lav sikkerhet eller mulig feilkode.
8) Ingen kjede-resonnering. Ikke avslør interne steg.

Mapping-hjelp (om du trenger):
- 01–29 -> komponent 1 (symptomer/plager)
- 70–99 -> komponent 7 (diagnoser)
- 30–69 -> prosesskoder (2–6). Om mulig: 30–39 (2 diagnostikk/screening), 40–49 (4 testresultat),
  50–59 (3 behandling/prosedyre/medikasjon), 60–69 (5–6 administrativ/henvisning/annet). Bruk tittelteksten til å avgjøre.

Output-skjema (JSON):
{
  "top_k": [
    {
      "code": "ICPC2_CODE",
      "title": "Norsk/Dansk tittel",
      "component": 1,
      "confidence": 0.0,
      "evidence_spans": [
        {"text": "ordrett sitat fra notatet", "section": "Anamnese|Status|Vurdering|Plan|Ukjent"}
      ],
      "alternatives": ["ALT1", "ALT2"],
      "needs_review": false
    }
  ],
  "notes": "Kort kommentar (valgfritt)."
}
"""

def build_messages(note_text, grounding):
    user_content = f"""Du får et konsultasjonsnotat mellom <note>-tagger og en liste av tillatte ICPC-2-koder i <icpc2_kandidater>.
Returner KUN JSON iht. skjemaet. Ikke skriv noe annet.

<icpc2_kandidater>
{grounding}
</icpc2_kandidater>

<note>
{note_text}
</note>
"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

def parse_json_or_raise(text):
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise ValueError("Model did not return JSON.")
    return json.loads(m.group(0))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    note_text = data.get('note_text', '').strip()
    
    if not note_text:
        return jsonify({'error': 'Ingen tekst funnet'}), 400
    
    try:
        # Retrieve candidates
        entries = retrieve(note_text, emb, faiss_index, meta, TOPN_RETRIEVE)
        
        # Build messages
        grounding = format_grounding(entries)
        messages = build_messages(note_text, grounding)
        
        # Call LLM with streaming
        full_response = ""
        for chunk in call_mistral_stream(messages, temperature=TEMPERATURE, max_tokens=MAX_TOKENS):
            full_response += chunk
        
        # Parse JSON
        obj = parse_json_or_raise(full_response)
        
        # Enforce that codes are within retrieved candidates
        allowed = {e.code for e in entries}
        for item in obj.get("top_k", []):
            if item.get("code") not in allowed:
                item["needs_review"] = True
                item["notes"] = (obj.get("notes") or "") + " | Kode ikke i kandidatliste fra RAG."
        
        return jsonify(obj)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stream-analyze', methods=['POST'])
def stream_analyze():
    data = request.get_json()
    note_text = data.get('note_text', '').strip()
    
    if not note_text:
        return jsonify({'error': 'Ingen tekst funnet'}), 400
    
    def generate():
        try:
            # Retrieve candidates
            entries = retrieve(note_text, emb, faiss_index, meta, TOPN_RETRIEVE)
            
            # Build messages
            grounding = format_grounding(entries)
            messages = build_messages(note_text, grounding)
            
            # Stream LLM response
            full_response = ""
            for chunk in call_mistral_stream(messages, temperature=TEMPERATURE, max_tokens=MAX_TOKENS):
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk, 'type': 'stream'})}\n\n"
            
            # Parse and return final result
            obj = parse_json_or_raise(full_response)
            
            # Enforce that codes are within retrieved candidates
            allowed = {e.code for e in entries}
            for item in obj.get("top_k", []):
                if item.get("code") not in allowed:
                    item["needs_review"] = True
                    item["notes"] = (obj.get("notes") or "") + " | Kode ikke i kandidatliste fra RAG."
            
            yield f"data: {json.dumps({'result': obj, 'type': 'final'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"
    
    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

# rag_infer.py
# Retrieve ICPC-2 candidates and query an LLM (Mistral) with RAG grounding

import os, json, re
from typing import List, Dict, Any, Tuple

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from icpc_utils import ICPCEntry

# ------------ Config -------------
EMB_MODEL = os.environ.get("EMB_MODEL", "intfloat/multilingual-e5-base")
INDEX_PATH = os.environ.get("INDEX_PATH", "icpc2.faiss")
META_PATH = os.environ.get("META_PATH", "icpc2_meta.json")

TOPN_RETRIEVE = int(os.environ.get("TOPN_RETRIEVE", "40"))  # how many codes we pass to the prompt
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.2"))
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "800"))

# LLM API settings (pick one)
# Option A: Mistral API
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_BASE = os.getenv("MISTRAL_BASE", "https://api.mistral.ai/v1")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")

# Option B: OpenRouter (or OpenAI-compatible) with a Mistral model
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE = os.getenv("OPENAI_BASE")  # e.g. https://openrouter.ai/api/v1
OPENAI_MODEL = os.getenv("OPENAI_MODEL")  # e.g. mistralai/mistral-large-latest
# ---------------------------------


def load_meta(path: str) -> List[ICPCEntry]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    rows: List[ICPCEntry] = []
    for r in data:
        rows.append(ICPCEntry(**r))
    return rows


def embed_queries(texts: List[str], model: SentenceTransformer) -> np.ndarray:
    # E5 expects "query: " prefix for query embeddings
    return model.encode([f"query: {t}" for t in texts], convert_to_numpy=True, normalize_embeddings=True)


def retrieve(note_text: str, model: SentenceTransformer, index, meta: List[ICPCEntry], topn: int) -> List[ICPCEntry]:
    qvec = embed_queries([note_text], model)[0].astype(np.float32)
    D, I = index.search(qvec.reshape(1, -1), topn)
    return [meta[i] for i in I[0]]


def format_grounding(entries: List[ICPCEntry]) -> str:
    # Keep compact; one item per line
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


def build_messages(note_text: str, grounding: str) -> List[Dict[str, str]]:
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


def call_mistral(messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> str:
    """Call either Mistral native API or an OpenAI-compatible endpoint based on env vars."""
    # Native Mistral
    if MISTRAL_API_KEY:
        import requests
        url = f"{MISTRAL_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": MISTRAL_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            # some providers support: "response_format": {"type": "json_object"}
        }
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

    # OpenAI-compatible (e.g., OpenRouter)
    if OPENAI_API_KEY and OPENAI_BASE and OPENAI_MODEL:
        import requests
        url = f"{OPENAI_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": OPENAI_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

    raise RuntimeError("No LLM credentials configured. Set MISTRAL_API_KEY or OPENAI_* environment variables.")


def parse_json_or_raise(text: str) -> Dict[str, Any]:
    # Extract JSON block if the model wrapped it in code fences
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise ValueError("Model did not return JSON.")
    return json.loads(m.group(0))


def infer(note_text: str) -> Dict[str, Any]:
    # Load index + meta + embedding model
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = [ICPCEntry(**r) for r in json.load(f)]
    emb = SentenceTransformer(EMB_MODEL)

    # Retrieve
    entries = retrieve(note_text, emb, index, meta, TOPN_RETRIEVE)

    # Build messages with grounding
    grounding = format_grounding(entries)
    messages = build_messages(note_text, grounding)

    # Call LLM
    out_text = call_mistral(messages, temperature=TEMPERATURE, max_tokens=MAX_TOKENS)

    # Parse JSON
    obj = parse_json_or_raise(out_text)

    # Optional: enforce that codes are within retrieved candidates
    allowed = {e.code for e in entries}
    for item in obj.get("top_k", []):
        if item.get("code") not in allowed:
            item["needs_review"] = True
            item["notes"] = (obj.get("notes") or "") + " | Kode ikke i kandidatliste fra RAG."
    return obj


if __name__ == "__main__":
    # Demo
    sample_note = """Anamnese: Hoste 5 dager, feber 38.2, sår hals, tett nese. 
Status: Lett påvirket, temp 38.1, svelg rød uten belegg.
Vurdering/Plan: Trolig viral ØLI. Symptomatisk råd. Sykemelding 2 dager."""
    res = infer(sample_note)
    print(json.dumps(res, ensure_ascii=False, indent=2))

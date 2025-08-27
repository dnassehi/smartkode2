# AI Agents Guide for ICPC-2 RAG System

Denne guiden forklarer hvordan KI-agenter kan integrere og bruke ICPC-2 RAG-systemet for automatisk medisinsk koding.

## 🤖 System Oversikt

ICPC-2 RAG-systemet er et AI-drevet verktøy for automatisk koding av medisinske konsultasjonsnotater. Det kombinerer:
- **RAG (Retrieval-Augmented Generation)** for presis koding
- **Mistral AI** for intelligent analyse
- **ICPC-2 standard** for medisinsk klassifisering

## 🔧 API Integrasjon

### REST API Endepunkter

#### 1. Streaming Analyse (Anbefalt)
```http
POST /stream-analyze
Content-Type: application/json

{
  "note_text": "Anamnese: Hoste 5 dager, feber 38.2, sår hals, tett nese. Status: Lett påvirket, temp 38.1, svelg rød uten belegg. Vurdering/Plan: Trolig viral ØLI. Symptomatisk råd. Sykemelding 2 dager."
}
```

**Response (Server-Sent Events):**
```
data: {"chunk": "{\n  \"top_k\": [\n    {\n      \"code\": \"R05\",", "type": "stream"}

data: {"chunk": "\n      \"title\": \"Hoste\",", "type": "stream"}

data: {"result": {"top_k": [{"code": "R05", "title": "Hoste", "component": 1, "confidence": 0.95, "evidence_spans": [{"text": "Hoste 5 dager", "section": "Anamnese"}], "alternatives": ["R07"], "needs_review": false}], "notes": "Kort kommentar"}, "type": "final"}
```

#### 2. Standard Analyse
```http
POST /analyze
Content-Type: application/json

{
  "note_text": "Anamnese: Hoste 5 dager, feber 38.2..."
}
```

**Response:**
```json
{
  "top_k": [
    {
      "code": "R05",
      "title": "Hoste",
      "component": 1,
      "confidence": 0.95,
      "evidence_spans": [
        {"text": "Hoste 5 dager", "section": "Anamnese"}
      ],
      "alternatives": ["R07"],
      "needs_review": false
    }
  ],
  "notes": "Kort kommentar"
}
```

## 🐍 Python Agent Eksempel

### Grunnleggende Agent
```python
import requests
import json
import sseclient

class ICPC2Agent:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def analyze_note(self, note_text, use_streaming=True):
        """Analyserer et konsultasjonsnotat og returnerer ICPC-2 koder."""
        
        if use_streaming:
            return self._stream_analyze(note_text)
        else:
            return self._standard_analyze(note_text)
    
    def _standard_analyze(self, note_text):
        """Standard analyse uten streaming."""
        response = requests.post(
            f"{self.base_url}/analyze",
            json={"note_text": note_text},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def _stream_analyze(self, note_text):
        """Streaming analyse med real-time feedback."""
        response = requests.post(
            f"{self.base_url}/stream-analyze",
            json={"note_text": note_text},
            headers={"Content-Type": "application/json"},
            stream=True
        )
        response.raise_for_status()
        
        client = sseclient.SSEClient(response)
        full_response = ""
        result = None
        
        for event in client.events():
            data = json.loads(event.data)
            
            if data["type"] == "stream":
                full_response += data["chunk"]
                print(f"Streaming: {data['chunk']}", end="", flush=True)
            
            elif data["type"] == "final":
                result = data["result"]
                break
        
        return result

# Bruk eksempel
agent = ICPC2Agent("http://localhost:5000")
result = agent.analyze_note("Anamnese: Hoste 5 dager...")
print(json.dumps(result, indent=2, ensure_ascii=False))
```

### Avansert Agent med Feilhåndtering
```python
import requests
import json
import time
from typing import Dict, List, Optional

class AdvancedICPC2Agent:
    def __init__(self, base_url="http://localhost:5000", max_retries=3):
        self.base_url = base_url
        self.max_retries = max_retries
        self.session = requests.Session()
    
    def analyze_batch(self, notes: List[str]) -> List[Dict]:
        """Analyserer flere notater i batch."""
        results = []
        
        for i, note in enumerate(notes):
            print(f"Analyserer notat {i+1}/{len(notes)}...")
            
            try:
                result = self.analyze_note_with_retry(note)
                results.append({
                    "note_index": i,
                    "note_preview": note[:100] + "...",
                    "result": result,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "note_index": i,
                    "note_preview": note[:100] + "...",
                    "error": str(e),
                    "status": "error"
                })
            
            # Rate limiting
            time.sleep(0.5)
        
        return results
    
    def analyze_note_with_retry(self, note_text: str) -> Dict:
        """Analyserer et notat med retry-logikk."""
        for attempt in range(self.max_retries):
            try:
                return self._standard_analyze(note_text)
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise e
                print(f"Forsøk {attempt + 1} feilet, prøver igjen...")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def _standard_analyze(self, note_text: str) -> Dict:
        """Standard analyse med feilhåndtering."""
        response = self.session.post(
            f"{self.base_url}/analyze",
            json={"note_text": note_text},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def get_codes_summary(self, results: List[Dict]) -> Dict:
        """Lager en sammendrag av alle koder."""
        all_codes = []
        error_count = 0
        
        for result in results:
            if result["status"] == "success":
                codes = result["result"].get("top_k", [])
                all_codes.extend(codes)
            else:
                error_count += 1
        
        # Grupperer koder etter frekvens
        code_counts = {}
        for code in all_codes:
            code_key = code["code"]
            if code_key not in code_counts:
                code_counts[code_key] = {
                    "count": 0,
                    "title": code["title"],
                    "examples": []
                }
            code_counts[code_key]["count"] += 1
            code_counts[code_key]["examples"].append(code)
        
        return {
            "total_notes": len(results),
            "successful_analyses": len(results) - error_count,
            "failed_analyses": error_count,
            "unique_codes": len(code_counts),
            "code_frequency": code_counts
        }

# Bruk eksempel
agent = AdvancedICPC2Agent("http://localhost:5000")

notes = [
    "Anamnese: Hoste 5 dager, feber 38.2...",
    "Anamnese: Hodepine 2 dager, kvalme...",
    "Anamnese: Ryggsmerter 1 uke..."
]

results = agent.analyze_batch(notes)
summary = agent.get_codes_summary(results)
print(json.dumps(summary, indent=2, ensure_ascii=False))
```

## 🔄 LangChain Agent Integrasjon

### LangChain Tool
```python
from langchain.tools import BaseTool
from typing import Optional
import requests

class ICPC2CodingTool(BaseTool):
    name = "icpc2_coding"
    description = "Analyserer medisinske konsultasjonsnotater og foreslår ICPC-2 koder"
    
    def _run(self, note_text: str) -> str:
        """Kjører ICPC-2 koding på et konsultasjonsnotat."""
        try:
            response = requests.post(
                "http://localhost:5000/analyze",
                json={"note_text": note_text},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # Formaterer resultatet for LangChain
            formatted_result = "ICPC-2 Koder:\n"
            for code in result.get("top_k", []):
                formatted_result += f"- {code['code']}: {code['title']} (confidence: {code['confidence']})\n"
            
            if result.get("notes"):
                formatted_result += f"\nNoter: {result['notes']}"
            
            return formatted_result
            
        except Exception as e:
            return f"Feil ved ICPC-2 koding: {str(e)}"
    
    async def _arun(self, note_text: str) -> str:
        """Asynkron versjon av ICPC-2 koding."""
        return self._run(note_text)

# Bruk med LangChain agent
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI

llm = OpenAI(temperature=0)
tools = [ICPC2CodingTool()]

agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Eksempel på bruk
result = agent.run("Analyser dette konsultasjonsnotatet: Anamnese: Hoste 5 dager, feber 38.2...")
print(result)
```

## 🤖 OpenAI Function Calling

### Function Definition
```python
import openai
import requests

def analyze_medical_note(note_text: str) -> dict:
    """Analyserer et medisinsk konsultasjonsnotat og returnerer ICPC-2 koder."""
    response = requests.post(
        "http://localhost:5000/analyze",
        json={"note_text": note_text},
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()
    return response.json()

# OpenAI function definition
functions = [
    {
        "name": "analyze_medical_note",
        "description": "Analyserer medisinske konsultasjonsnotater og foreslår ICPC-2 koder",
        "parameters": {
            "type": "object",
            "properties": {
                "note_text": {
                    "type": "string",
                    "description": "Konsultasjonsnotatet som skal analyseres"
                }
            },
            "required": ["note_text"]
        }
    }
]

# Eksempel på bruk
client = openai.OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Analyser dette notatet: Anamnese: Hoste 5 dager, feber 38.2..."}
    ],
    functions=functions,
    function_call={"name": "analyze_medical_note"}
)

# Håndterer function call
if response.choices[0].message.function_call:
    function_name = response.choices[0].message.function_call.name
    function_args = json.loads(response.choices[0].message.function_call.arguments)
    
    if function_name == "analyze_medical_note":
        result = analyze_medical_note(function_args["note_text"])
        print(json.dumps(result, indent=2, ensure_ascii=False))
```

## 📊 Data Strukturer

### Input Format
```json
{
  "note_text": "Anamnese: [pasientens symptomer og historikk]\nStatus: [fysisk undersøkelse]\nVurdering/Plan: [diagnose og behandlingsplan]"
}
```

### Output Format
```json
{
  "top_k": [
    {
      "code": "R05",
      "title": "Hoste",
      "component": 1,
      "confidence": 0.95,
      "evidence_spans": [
        {
          "text": "Hoste 5 dager",
          "section": "Anamnese"
        }
      ],
      "alternatives": ["R07"],
      "needs_review": false
    }
  ],
  "notes": "Kort kommentar om analysen"
}
```

## 🔒 Sikkerhet og Best Practices

### API Sikkerhet
- ✅ Bruk HTTPS i produksjon
- ✅ Implementer rate limiting
- ✅ Valider input data
- ✅ Håndter feil gracefully

### Data Privatliv
- ✅ Ikke logg sensitive pasientdata
- ✅ Bruk avidentifiserte data for testing
- ✅ Følg GDPR/EØS-regler
- ✅ Implementer data retention policies

### Agent Best Practices
```python
# Eksempel på sikker agent implementasjon
class SecureICPC2Agent:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def analyze_note(self, note_text: str) -> dict:
        # Validerer input
        if not note_text or len(note_text.strip()) < 10:
            raise ValueError("Notatet må være minst 10 tegn")
        
        # Sanitizerer input (fjerner sensitive data)
        sanitized_note = self._sanitize_note(note_text)
        
        try:
            response = self.session.post(
                f"{self.base_url}/analyze",
                json={"note_text": sanitized_note},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Logger feil uten sensitive data
            self._log_error(str(e))
            raise
    
    def _sanitize_note(self, note_text: str) -> str:
        """Fjerner sensitive personopplysninger fra notatet."""
        # Implementer sanitization logikk her
        return note_text
    
    def _log_error(self, error_message: str):
        """Logger feil uten sensitive data."""
        print(f"ICPC-2 Agent Error: {error_message}")
```

## 🚀 Deployment for Agenter

### Docker Compose for Agent Testing
```yaml
version: '3.8'
services:
  icpc2-app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - MISTRAL_API_KEY=${MISTRAL_API_KEY}
    volumes:
      - ./mnt:/app/mnt
      - ./icpc2.faiss:/app/icpc2.faiss
      - ./icpc2_meta.json:/app/icpc2_meta.json
  
  agent-test:
    build: ./agent-test
    depends_on:
      - icpc2-app
    environment:
      - ICPC2_API_URL=http://icpc2-app:5000
```

### Health Check Endpoint
```python
# Legg til i app.py
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "ICPC-2 RAG System",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })
```

## 📈 Monitoring og Analytics

### Agent Metrics
```python
import time
from dataclasses import dataclass
from typing import List

@dataclass
class AgentMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    codes_generated: List[str] = None
    
    def __post_init__(self):
        if self.codes_generated is None:
            self.codes_generated = []
    
    def record_request(self, success: bool, response_time: float, codes: List[str] = None):
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Oppdaterer gjennomsnittlig responstid
        self.average_response_time = (
            (self.average_response_time * (self.total_requests - 1) + response_time) 
            / self.total_requests
        )
        
        if codes:
            self.codes_generated.extend(codes)
    
    def get_success_rate(self) -> float:
        return self.successful_requests / self.total_requests if self.total_requests > 0 else 0.0
    
    def get_most_common_codes(self, top_n: int = 10) -> List[tuple]:
        from collections import Counter
        counter = Counter(self.codes_generated)
        return counter.most_common(top_n)

# Bruk eksempel
metrics = AgentMetrics()

start_time = time.time()
try:
    result = agent.analyze_note("Anamnese: Hoste...")
    response_time = time.time() - start_time
    codes = [code["code"] for code in result.get("top_k", [])]
    metrics.record_request(True, response_time, codes)
except Exception as e:
    response_time = time.time() - start_time
    metrics.record_request(False, response_time)

print(f"Success Rate: {metrics.get_success_rate():.2%}")
print(f"Average Response Time: {metrics.average_response_time:.2f}s")
print(f"Most Common Codes: {metrics.get_most_common_codes(5)}")
```

## 🔗 Integrasjon med Andre Systemer

### FHIR Integration
```python
def fhir_to_icpc2(fhir_observation: dict) -> dict:
    """Konverterer FHIR Observation til ICPC-2 koder."""
    # Ekstraherer relevant informasjon fra FHIR
    note_text = extract_note_from_fhir(fhir_observation)
    
    # Bruker ICPC-2 agent
    icpc2_result = agent.analyze_note(note_text)
    
    # Konverterer tilbake til FHIR format
    return convert_icpc2_to_fhir(icpc2_result)

def extract_note_from_fhir(fhir_observation: dict) -> str:
    """Ekstraherer notattekst fra FHIR Observation."""
    # Implementer FHIR parsing logikk
    pass

def convert_icpc2_to_fhir(icpc2_result: dict) -> dict:
    """Konverterer ICPC-2 resultat tilbake til FHIR format."""
    # Implementer FHIR konvertering
    pass
```

### HL7 Integration
```python
def hl7_to_icpc2(hl7_message: str) -> dict:
    """Konverterer HL7 melding til ICPC-2 koder."""
    # Parser HL7 melding
    parsed_hl7 = parse_hl7_message(hl7_message)
    
    # Ekstraherer notattekst
    note_text = extract_note_from_hl7(parsed_hl7)
    
    # Bruker ICPC-2 agent
    return agent.analyze_note(note_text)
```

## 📚 Eksempler og Use Cases

### 1. Automatisk Koding av Konsultasjonsnotater
```python
# Batch prosessering av notater
notes = load_notes_from_database()
agent = ICPC2Agent()

for note in notes:
    result = agent.analyze_note(note.text)
    save_codes_to_database(note.id, result)
```

### 2. Real-time Koding i EMR System
```python
# Webhook for real-time koding
@app.route('/webhook/note-created', methods=['POST'])
def handle_note_created():
    note_data = request.json
    result = agent.analyze_note(note_data['text'])
    
    # Sender resultatet tilbake til EMR
    send_codes_to_emr(note_data['id'], result)
    
    return jsonify({"status": "success"})
```

### 3. Kvalitetssikring av Manuell Koding
```python
# Sammenligner manuell og automatisk koding
def compare_coding(manual_codes: List[str], note_text: str) -> dict:
    auto_result = agent.analyze_note(note_text)
    auto_codes = [code['code'] for code in auto_result['top_k']]
    
    matches = set(manual_codes) & set(auto_codes)
    discrepancies = set(manual_codes) ^ set(auto_codes)
    
    return {
        "matches": list(matches),
        "discrepancies": list(discrepancies),
        "agreement_rate": len(matches) / len(set(manual_codes) | set(auto_codes))
    }
```

## 🎯 Konklusjon

ICPC-2 RAG-systemet er designet for enkel integrasjon med KI-agenter og andre systemer. Med sin REST API, streaming-støtte og fleksible output-formater kan det brukes i en rekke scenarier:

- **Automatisk koding** av konsultasjonsnotater
- **Real-time assistanse** for leger
- **Kvalitetssikring** av manuell koding
- **Forskning og analyse** av medisinske data

Systemet følger beste praksis for sikkerhet, privatliv og skalerbarhet, og er klart for produksjonsbruk.

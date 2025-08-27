# ICPC-2 RAG Starter

Et RAG-basert system for automatisk ICPC-2-koding av medisinske konsultasjonsnotater ved hjelp av Mistral AI.

## 🚀 Quickstart

### 1. Installer avhengigheter
```bash
pip install -r requirements.txt
```

### 2. Konfigurer miljøvariabler
Opprett en `.env` fil med din Mistral API-nøkkel:

```bash
# Kopier .env.example til .env (hvis du har .env.example)
cp .env.example .env

# Eller opprett .env manuelt med følgende innhold:
MISTRAL_API_KEY=din_mistral_api_nøkkel_her
MISTRAL_MODEL=mistral-large-latest
EMB_MODEL=intfloat/multilingual-e5-base
TEMPERATURE=0.2
TOPN_RETRIEVE=40
MAX_TOKENS=800
ICPC_CSV_PATH=mnt/data/ICPC-2.csv
INDEX_PATH=icpc2.faiss
META_PATH=icpc2_meta.json
```

### 3. Plasser ICPC-2 CSV-fil
Plasser din ICPC-2 CSV-fil i `mnt/data/ICPC-2.csv` (eller endre `ICPC_CSV_PATH` i `.env`)

### 4. Bygg FAISS-indeks
```bash
python build_index.py
```

### 5. Test systemet
```bash
# Kommandolinje-test
python rag_infer.py

# Start web-appen
python app.py
```

### 6. Deploy til produksjon (valgfritt)
Se [AUTO_DEPLOYMENT.md](AUTO_DEPLOYMENT.md) for automatisk deployment via GitHub.

## 🌐 Web-App

### Start web-appen
```bash
python app.py
```

Web-appen er tilgjengelig på:
- **Lokal:** http://127.0.0.1:5000
- **Nettverk:** http://[din-ip]:5000

### Web-app funksjoner
- 📝 **Tekstboks** for konsultasjonsnotater
- ⚡ **Streaming-feedback** mens systemet jobber
- 🏥 **Relevante diagnoser** som output
- 📋 **Kopier-knapp** for diagnosekodene
- 📱 **Responsivt design** (mobil og desktop)
- 🔵 **Blå, lys blå og hvit fargepalett**
- 🔒 **Ingen datalagring** - alt kjører lokalt

## ⚙️ Konfigurasjon

### Miljøvariabler (`.env` fil)

| Variabel | Beskrivelse | Standardverdi |
|----------|-------------|---------------|
| `MISTRAL_API_KEY` | Din Mistral API-nøkkel | (påkrevd) |
| `MISTRAL_MODEL` | Mistral-modell å bruke | `mistral-large-latest` |
| `EMB_MODEL` | Embedding-modell for RAG | `intfloat/multilingual-e5-base` |
| `TEMPERATURE` | LLM kreativitet (0.0-1.0) | `0.2` |
| `TOPN_RETRIEVE` | Antall kandidater til LLM | `40` |
| `MAX_TOKENS` | Maks tokens i LLM-respons | `800` |
| `ICPC_CSV_PATH` | Sti til ICPC-2 CSV-fil | `mnt/data/ICPC-2.csv` |
| `INDEX_PATH` | Sti til FAISS-indeks | `icpc2.faiss` |
| `META_PATH` | Sti til metadata | `icpc2_meta.json` |

### Eksempel på `.env` fil:
```env
MISTRAL_API_KEY=dRnAfaO2jF7LzoqD1YQ5FYzPulF10NEc
MISTRAL_MODEL=mistral-large-latest
EMB_MODEL=intfloat/multilingual-e5-base
TEMPERATURE=0.2
TOPN_RETRIEVE=40
MAX_TOKENS=800
ICPC_CSV_PATH=mnt/data/ICPC-2.csv
INDEX_PATH=icpc2.faiss
META_PATH=icpc2_meta.json
```

## 📁 Filer

- **`icpc_utils.py`** – CSV-loader, komponent-gjetning, metadata-hjelpere
- **`build_index.py`** – bygger FAISS-indeks fra ICPC-2 CSV med multilinguale E5-embeddings
- **`rag_infer.py`** – henter top-N ICPC-2-kandidater og spør LLM med begrenset prompt
- **`app.py`** – Flask web-app med streaming-funksjonalitet
- **`templates/index.html`** – HTML/CSS/JS for web-grensesnittet
- **`prompt_template.txt`** – dokumentasjon av chat-meldingene
- **`requirements.txt`** – Python-avhengigheter
- **`.env`** – miljøvariabler (ikke i Git)
- **`.env.example`** – eksempel på miljøvariabler (i Git)

### Deployment-filer
- **`app.yaml`** – DigitalOcean App Platform konfigurasjon
- **`Dockerfile`** – Docker container konfigurasjon
- **`docker-compose.yml`** – Docker Compose setup
- **`railway.json`** – Railway deployment konfigurasjon
- **`render.yaml`** – Render deployment konfigurasjon
- **`.github/workflows/deploy.yml`** – GitHub Actions for automatisk deployment
- **`AUTO_DEPLOYMENT.md`** – Komplett guide for automatisk deployment
- **`DEPLOY_DIGITALOCEAN.md`** – DigitalOcean Droplet deployment guide

## 🔧 Bruk

### Bygge indeks
```bash
python build_index.py
```
Dette lager:
- `icpc2.faiss` – FAISS-indeks for rask søk
- `icpc2_meta.json` – metadata for ICPC-2-koder

### Kommandolinje inferens
```bash
# Standard (ikke-streaming)
python rag_infer.py

# Med streaming (raskere opplevelse)
python rag_infer.py --stream

# Med streaming og visuell output
python rag_infer.py --stream --show-stream
```
Systemet kjører en demo med et eksempel-notat og returnerer JSON med foreslåtte ICPC-2-koder.

### Web-app
```bash
# Start web-appen
python app.py
```
Åpne nettleseren og gå til `http://127.0.0.1:5000`

### Produksjon deployment
```bash
# DigitalOcean App Platform (anbefalt)
# 1. Push til GitHub
git push origin main
# 2. Koble repo til DigitalOcean Apps
# 3. Sett environment variables
# 4. Deploy automatisk

# Se AUTO_DEPLOYMENT.md for detaljerte instruksjoner
```

### Programmatisk bruk
```python
from rag_infer import infer

# Standard bruk
result = infer("Anamnese: Hoste 5 dager, feber 38.2...")

# Med streaming (raskere)
result = infer("Anamnese: Hoste 5 dager, feber 38.2...", stream=True)

# Med streaming og visuell output
result = infer("Anamnese: Hoste 5 dager, feber 38.2...", stream=True, show_stream=True)
```

## 🎯 Output-format

Systemet returnerer JSON i følgende format:

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
  "notes": "Kort kommentar (valgfritt)"
}
```

## 🔄 Endre modell

For å endre Mistral-modell, rediger `.env` filen:

```env
# Eksempel: Bruk en annen modell
MISTRAL_MODEL=mistral-medium-latest
# eller
MISTRAL_MODEL=mistral-small-latest
```

## ⚡ Streaming

Systemet støtter streaming for bedre brukeropplevelse:

### Kommandolinje:
```bash
# Standard (ikke-streaming)
python rag_infer.py

# Med streaming (raskere opplevelse)
python rag_infer.py --stream

# Med streaming og visuell output
python rag_infer.py --stream --show-stream
```

### Web-app:
- Automatisk streaming-feedback i nettleseren
- Visuell indikasjon på at systemet jobber
- Real-time oppdateringer av resultatet

### Programmatisk:
```python
from rag_infer import infer

# Standard
result = infer(note_text)

# Med streaming (raskere)
result = infer(note_text, stream=True)

# Med streaming og visuell output
result = infer(note_text, stream=True, show_stream=True)
```

### Fordeler med streaming:
- **Bedre UX**: Visuell feedback at systemet jobber
- **Raskere opplevelse**: Føles raskere selv om totaltid er lik
- **Debugging**: Lettere å se hvor lang tid hver del tar

## 🌐 Web-App Detaljer

### Funksjoner
- **Responsivt design**: Fungerer på mobil, tablet og desktop
- **Streaming-feedback**: Visuell indikasjon på at systemet jobber
- **Kopier-funksjonalitet**: En-klikk kopiering av diagnosekodene
- **Moderne UI**: Blå, lys blå og hvit fargepalett
- **Ingen datalagring**: Alt kjører lokalt, ingen data lagres

### Teknisk stack
- **Backend**: Flask med Server-Sent Events (SSE) for streaming
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **AI**: Mistral API med streaming-støtte
- **RAG**: FAISS + SentenceTransformers

## 📝 Viktige merknader

- **Komponent-mapping**: Prosesskoder (30–69) kan variere nasjonalt. Systemet gjør en fornuftig gjetning og instruerer LLM-en til å bruke tittelteksten for presis komponent.
- **Datasikkerhet**: Sørg for at all behandling skjer innenfor EØS og at notater er avidentifiserte for utvikling/testing.
- **API-kostnader**: Hver forespørsel til Mistral API koster penger. Juster `TOPN_RETRIEVE` og `TEMPERATURE` for å optimalisere kostnader.

## 🔒 Sikkerhet

- **API-nøkkel**: Din Mistral API-nøkkel er lagret i `.env` filen som er ekskludert fra Git
- **Ingen datalagring**: Web-appen lagrer ingen data permanent
- **Lokal kjøring**: Alt kjører lokalt på din maskin
- **HTTPS**: For produksjon, sørg for å kjøre over HTTPS
- **Environment variables**: API-nøkler er sikre i cloud platformer via environment variables

## 🛠️ Feilsøking

### Vanlige problemer:

1. **"No LLM credentials configured"**
   - Sjekk at `MISTRAL_API_KEY` er satt i `.env` filen
   - Sjekk at `.env` filen er i prosjektmappen

2. **"Expected a 'Kode' column"**
   - Sjekk at CSV-filen har kolonnen "Kode" (eller "Kode ")
   - Sjekk at `ICPC_CSV_PATH` peker til riktig fil

3. **"Model did not return JSON"**
   - Øk `MAX_TOKENS` i `.env` hvis responsen er kuttet av
   - Reduser `TEMPERATURE` for mer konsistente svar

4. **Web-app starter ikke**
   - Sjekk at alle avhengigheter er installert: `pip install -r requirements.txt`
   - Sjekk at port 5000 er ledig
   - Sjekk at `.env` filen har riktig encoding (UTF-8)

5. **"'function' object has no attribute 'search'"**
   - Dette er fikset i nyeste versjon
   - Sjekk at du bruker den oppdaterte `app.py`

6. **Deployment feiler**
   - Sjekk at alle environment variables er satt i cloud platform
   - Sjekk at GitHub repo er riktig koblet
   - Se AUTO_DEPLOYMENT.md for detaljerte instruksjoner

## 📄 Lisens

Se `LICENSE` filen for detaljer.

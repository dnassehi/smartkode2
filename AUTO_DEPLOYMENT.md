# Automatisk Deployment via GitHub

## 🚀 Rask Setup

### 1. Forbered GitHub repo
```bash
# Sørg for at koden er på GitHub
git add .
git commit -m "Add automatic deployment configs"
git push origin main
```

### 2. Velg platform og følg guide nedenfor

## 🌐 Railway (Anbefalt - Gratis)

### Steg 1: Opprett Railway konto
1. Gå til [railway.app](https://railway.app)
2. Logg inn med GitHub
3. Klikk "New Project"

### Steg 2: Koble GitHub repo
1. Velg "Deploy from GitHub repo"
2. Velg ditt `smartkode2` repo
3. Klikk "Deploy Now"

### Steg 3: Konfigurer environment variables
1. Gå til "Variables" tab
2. Legg til:
   ```
   MISTRAL_API_KEY=your_mistral_api_key_here
   MISTRAL_MODEL=mistral-large-latest
   EMB_MODEL=intfloat/multilingual-e5-base
   TEMPERATURE=0.2
   TOPN_RETRIEVE=40
   MAX_TOKENS=800
   ```

### Steg 4: Sett custom domain (valgfritt)
1. Gå til "Settings" tab
2. Under "Domains" → "Custom Domain"
3. Legg til din domene

**Appen er nå tilgjengelig på:** `https://din-app.railway.app`

## 🌐 Render (Alternativ - Gratis)

### Steg 1: Opprett Render konto
1. Gå til [render.com](https://render.com)
2. Logg inn med GitHub
3. Klikk "New +" → "Web Service"

### Steg 2: Koble GitHub repo
1. Velg ditt `smartkode2` repo
2. Velg branch (main)
3. Klikk "Connect"

### Steg 3: Konfigurer service
1. **Name**: `icpc2-rag-app`
2. **Environment**: `Python 3`
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `python app.py`

### Steg 4: Sett environment variables
1. Scroll ned til "Environment Variables"
2. Legg til alle variablene fra Railway eksempelet

**Appen er nå tilgjengelig på:** `https://din-app.onrender.com`

## 🌐 DigitalOcean App Platform

### Steg 1: Opprett DigitalOcean App
1. Gå til [DigitalOcean Apps](https://cloud.digitalocean.com/apps)
2. Klikk "Create App"
3. Koble GitHub-repo

### Steg 2: Konfigurer App
1. **Source**: GitHub repo
2. **Branch**: main
3. **Run Command**: `python app.py`
4. **Environment**: Python

### Steg 3: Sett environment variables
1. Under "Environment Variables"
2. Legg til alle variablene

**Appen er nå tilgjengelig på:** `https://din-app.ondigitalocean.app`

## 🔄 Automatisk Deployment

Alle platformene over støtter automatisk deployment:

- **Push til main branch** → Automatisk deploy
- **Pull request** → Preview deployment
- **Rollback** → Enkelt å rulle tilbake

## 🔒 Sikkerhet

### Environment Variables
- ✅ API-nøkler er sikre
- ✅ Ikke synlige i kode
- ✅ Enkelt å oppdatere

### HTTPS
- ✅ Automatisk SSL-sertifikater
- ✅ Sikker kommunikasjon
- ✅ Inkludert i alle platformer

## 📊 Sammenligning

| Platform | Gratis Tier | SSL | Auto Deploy | Custom Domain |
|----------|-------------|-----|-------------|---------------|
| Railway | ✅ | ✅ | ✅ | ✅ |
| Render | ✅ | ✅ | ✅ | ✅ |
| DigitalOcean | ❌ ($12/mnd) | ✅ | ✅ | ✅ |

## 🚨 Troubleshooting

### Build feiler
```bash
# Sjekk requirements.txt
pip install -r requirements.txt

# Sjekk Python versjon
python --version
```

### App starter ikke
```bash
# Sjekk logs i platform dashboard
# Vanlige problemer:
# - Manglende environment variables
# - Port ikke riktig (skal være 5000)
# - Manglende dependencies
```

### Environment variables
```bash
# Sjekk at alle variabler er satt:
# MISTRAL_API_KEY
# MISTRAL_MODEL
# EMB_MODEL
# TEMPERATURE
# TOPN_RETRIEVE
# MAX_TOKENS
```

## 🔧 Vedlikehold

### Oppdatere appen
```bash
# Bare push til GitHub
git add .
git commit -m "Update app"
git push origin main
# Automatisk deployment!
```

### Se logs
- Railway: Dashboard → "Deployments" → "View Logs"
- Render: Dashboard → "Logs" tab
- DigitalOcean: Dashboard → "Runtime Logs"

### Rollback
- Alle platformer støtter enkel rollback
- Velg tidligere deployment
- Klikk "Rollback"

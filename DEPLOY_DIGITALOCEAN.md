# DigitalOcean Deployment Guide

## 🚀 Rask Setup (Docker)

### 1. Opprett Droplet
```bash
# Logg inn på DigitalOcean
# Opprett ny Droplet:
# - Image: Ubuntu 22.04 LTS
# - Size: Basic $6/mnd (1GB RAM)
# - Datacenter: Amsterdam/Frankfurt
```

### 2. Koble til og installer Docker
```bash
ssh root@din-droplet-ip

# Oppdater system
apt update && apt upgrade -y

# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl start docker
systemctl enable docker

# Installer Docker Compose
apt install docker-compose -y
```

### 3. Last opp kode
```bash
# Klon repo
git clone https://github.com/dnassehi/smartkode2.git
cd smartkode2

# Eller last opp via SCP (fra lokal maskin):
# scp -r . root@din-droplet-ip:/root/smartkode2/
```

### 4. Konfigurer environment
```bash
# Opprett .env fil
cat > .env << EOF
MISTRAL_API_KEY=min-mistral-api-kode
MISTRAL_MODEL=mistral-large-latest
EMB_MODEL=intfloat/multilingual-e5-base
TEMPERATURE=0.2
TOPN_RETRIEVE=40
MAX_TOKENS=800
ICPC_CSV_PATH=mnt/data/ICPC-2.csv
INDEX_PATH=icpc2.faiss
META_PATH=icpc2_meta.json
EOF
```

### 5. Deploy
```bash
# Bygg og start
docker-compose build
docker-compose up -d

# Sjekk status
docker-compose ps
docker-compose logs -f
```

### 6. Åpne port
```bash
ufw allow 5000
ufw enable
```

**Appen er nå tilgjengelig på:** `http://din-droplet-ip:5000`

## 🌐 Med egen domene (Anbefalt)

### 1. Sett opp domene
```bash
# Opprett A-record i DNS:
# din-domene.no -> din-droplet-ip
```

### 2. Installer Nginx og SSL
```bash
# Installer Nginx
apt install nginx certbot python3-certbot-nginx -y

# Kopier Nginx config
cp nginx.conf /etc/nginx/sites-available/icpc2
ln -s /etc/nginx/sites-available/icpc2 /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

# Test config
nginx -t

# Få SSL-sertifikat
certbot --nginx -d din-domene.no

# Start Nginx
systemctl start nginx
systemctl enable nginx
```

### 3. Oppdater Nginx config
```bash
# Rediger /etc/nginx/sites-available/icpc2
# Erstatt 'din-domene.no' med din faktiske domene
nano /etc/nginx/sites-available/icpc2
```

## 🔧 Vedlikehold

### Oppdatere appen
```bash
cd /root/smartkode2
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

### Se logger
```bash
docker-compose logs -f
```

### Backup
```bash
# Backup data
docker-compose exec icpc2-app tar -czf /tmp/backup.tar.gz /app/mnt /app/icpc2.faiss /app/icpc2_meta.json
docker cp icpc2-app:/tmp/backup.tar.gz ./backup.tar.gz
```

## 💰 Kostnader

- **Droplet**: $6/mnd (Basic 1GB RAM)
- **Domene**: ~$10-15/år
- **SSL**: Gratis med Let's Encrypt
- **Total**: ~$7-8/mnd

## 🔒 Sikkerhet

### Firewall
```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80
ufw allow 443
ufw enable
```

### Fail2ban
```bash
apt install fail2ban -y
systemctl start fail2ban
systemctl enable fail2ban
```

### Oppdateringer
```bash
# Automatiske oppdateringer
apt install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades
```

## 🚨 Troubleshooting

### Appen starter ikke
```bash
# Sjekk logs
docker-compose logs

# Sjekk diskplass
df -h

# Sjekk minne
free -h
```

### Nginx feil
```bash
# Test config
nginx -t

# Se error logs
tail -f /var/log/nginx/error.log
```

### SSL-problemer
```bash
# Forny sertifikat
certbot renew --dry-run

# Sjekk sertifikat
openssl s_client -connect din-domene.no:443
```

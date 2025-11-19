# Agent Aura - Production Deployment Guide

Complete guide for deploying Agent Aura to production with PostgreSQL, SSL/HTTPS, rate limiting, and enterprise security.

## 📋 Prerequisites

- Ubuntu 20.04+ / Debian 11+ server with root access
- Domain name with DNS configured
- PostgreSQL 14+
- Redis 6+
- Node.js 18+
- Python 3.10+
- Nginx
- SSL certificate (Let's Encrypt or commercial)

## 🚀 Quick Start

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.10 python3-pip python3-venv nodejs npm postgresql redis-server nginx certbot python3-certbot-nginx git

# Verify installations
python3.10 --version
node --version
psql --version
redis-cli --version
nginx -v
```

### 2. Database Setup (PostgreSQL)

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE agent_aura_prod;
CREATE USER agent_aura_user WITH PASSWORD 'YOUR_SECURE_PASSWORD_HERE';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE agent_aura_prod TO agent_aura_user;
ALTER DATABASE agent_aura_prod OWNER TO agent_aura_user;

# Enable UUID extension
\c agent_aura_prod
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

# Exit
\q
```

### 3. Clone Repository

```bash
# Create application directory
sudo mkdir -p /var/www/agent-aura
cd /var/www/agent-aura

# Clone repository
git clone https://github.com/yourusername/agent-aura.git .

# Set permissions
sudo chown -R $USER:$USER /var/www/agent-aura
```

### 4. Backend Setup

```bash
cd /var/www/agent-aura/agent-aura-backend

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install production dependencies
pip install --upgrade pip
pip install -r requirements-production.txt

# Copy environment template
cp ../.env.production.template .env

# Edit environment variables
nano .env
```

**Configure `.env`**:
```env
# Application
ENVIRONMENT=production
DEBUG=false
VERSION=2.0.0

# Database - PostgreSQL
DATABASE_URL=postgresql://agent_aura_user:YOUR_SECURE_PASSWORD_HERE@localhost:5432/agent_aura_prod
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# Security
SECRET_KEY=GENERATE_WITH_openssl_rand_hex_32
JWT_SECRET_KEY=GENERATE_WITH_openssl_rand_hex_32
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
BCRYPT_ROUNDS=12

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
USE_REDIS_RATE_LIMIT=true

# SSL
SSL_ENABLED=true
SSL_CERT_PATH=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/yourdomain.com/privkey.pem

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4
RELOAD=false

# Frontend URL
FRONTEND_URL=https://yourdomain.com

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=YOUR_REDIS_PASSWORD_HERE

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/agent-aura/backend.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# Monitoring
SENTRY_DSN=YOUR_SENTRY_DSN_HERE
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com

# API Keys
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
```

**Generate Secure Keys**:
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET_KEY
openssl rand -hex 32

# Generate Redis password
openssl rand -hex 16
```

### 5. Database Migration

```bash
# Activate virtual environment
source venv/bin/activate

# Run migration from SQLite to PostgreSQL
python scripts/migrate_to_postgresql.py

# Verify migration
python -c "from app.models.database_production import check_db_health; import asyncio; print(asyncio.run(check_db_health()))"
```

### 6. Frontend Setup

```bash
cd /var/www/agent-aura/agent-aura-frontend

# Install dependencies
npm install

# Create production environment file
cat > .env.production << EOF
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com/api/v1
NODE_ENV=production
EOF

# Build frontend
npm run build

# Test build
npm run start
```

### 7. SSL Certificate (Let's Encrypt)

```bash
# Stop nginx temporarily
sudo systemctl stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com

# Verify certificate
sudo ls -la /etc/letsencrypt/live/yourdomain.com/

# Set up auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 8. Nginx Configuration

```bash
# Create backend proxy configuration
sudo nano /etc/nginx/sites-available/agent-aura-backend
```

```nginx
# Agent Aura Backend API
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=60r/m;
    limit_req zone=api_limit burst=10 nodelay;

    # Logging
    access_log /var/log/nginx/agent-aura-backend-access.log;
    error_log /var/log/nginx/agent-aura-backend-error.log;

    # Proxy to backend
    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://backend/health;
        access_log off;
    }
}
```

```bash
# Create frontend configuration
sudo nano /etc/nginx/sites-available/agent-aura-frontend
```

```nginx
# Agent Aura Frontend
upstream frontend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/agent-aura-frontend-access.log;
    error_log /var/log/nginx/agent-aura-frontend-error.log;

    # Proxy to Next.js
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Next.js static files
    location /_next/static/ {
        proxy_pass http://frontend;
        proxy_cache_valid 200 60m;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable sites
sudo ln -s /etc/nginx/sites-available/agent-aura-backend /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/agent-aura-frontend /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### 9. Systemd Services

**Backend Service**:
```bash
sudo nano /etc/systemd/system/agent-aura-backend.service
```

```ini
[Unit]
Description=Agent Aura Backend API
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/agent-aura/agent-aura-backend
Environment="PATH=/var/www/agent-aura/agent-aura-backend/venv/bin"
EnvironmentFile=/var/www/agent-aura/agent-aura-backend/.env
ExecStart=/var/www/agent-aura/agent-aura-backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Frontend Service**:
```bash
sudo nano /etc/systemd/system/agent-aura-frontend.service
```

```ini
[Unit]
Description=Agent Aura Frontend
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/agent-aura/agent-aura-frontend
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/npm run start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and Start Services**:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable agent-aura-backend
sudo systemctl enable agent-aura-frontend

# Start services
sudo systemctl start agent-aura-backend
sudo systemctl start agent-aura-frontend

# Check status
sudo systemctl status agent-aura-backend
sudo systemctl status agent-aura-frontend
```

### 10. Redis Configuration

```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf
```

Add/modify:
```conf
# Bind to localhost only
bind 127.0.0.1

# Set password
requirepass YOUR_REDIS_PASSWORD_HERE

# Increase max memory
maxmemory 256mb
maxmemory-policy allkeys-lru

# Enable persistence
save 900 1
save 300 10
save 60 10000
```

```bash
# Restart Redis
sudo systemctl restart redis-server

# Test connection
redis-cli -a YOUR_REDIS_PASSWORD_HERE ping
```

### 11. Monitoring Setup

**Create Log Directories**:
```bash
sudo mkdir -p /var/log/agent-aura
sudo chown www-data:www-data /var/log/agent-aura
```

**Logrotate Configuration**:
```bash
sudo nano /etc/logrotate.d/agent-aura
```

```conf
/var/log/agent-aura/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload agent-aura-backend agent-aura-frontend > /dev/null 2>&1 || true
    endscript
}
```

### 12. Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

### 13. Backup Setup

```bash
# Create backup script
sudo nano /usr/local/bin/backup-agent-aura.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/agent-aura"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL database
pg_dump -U agent_aura_user agent_aura_prod | gzip > $BACKUP_DIR/database_$DATE.sql.gz

# Backup application files
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /var/www/agent-aura

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /etc/nginx /etc/systemd/system/agent-aura-*

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-agent-aura.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
```

Add line:
```cron
0 2 * * * /usr/local/bin/backup-agent-aura.sh >> /var/log/agent-aura/backup.log 2>&1
```

## ✅ Verification

### Check Services
```bash
# Check backend
curl https://api.yourdomain.com/health

# Check frontend
curl https://yourdomain.com

# Check logs
sudo journalctl -u agent-aura-backend -f
sudo journalctl -u agent-aura-frontend -f
```

### Performance Testing
```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test backend
ab -n 1000 -c 10 https://api.yourdomain.com/health

# Test frontend
ab -n 100 -c 5 https://yourdomain.com/
```

## 🔒 Security Checklist

- ✅ PostgreSQL password set
- ✅ Redis password configured
- ✅ SECRET_KEY and JWT_SECRET_KEY generated
- ✅ SSL/TLS certificates installed
- ✅ Firewall configured (UFW)
- ✅ Security headers enabled (Nginx)
- ✅ Rate limiting active
- ✅ CORS properly configured
- ✅ Logs rotated and secured
- ✅ Backups automated
- ✅ Services running as www-data (non-root)
- ✅ Sentry monitoring configured

## 📊 Monitoring Commands

```bash
# System resources
htop
df -h
free -h

# Service status
sudo systemctl status agent-aura-backend
sudo systemctl status agent-aura-frontend
sudo systemctl status postgresql
sudo systemctl status redis-server
sudo systemctl status nginx

# Database connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname='agent_aura_prod';"

# Redis memory
redis-cli -a YOUR_REDIS_PASSWORD_HERE INFO memory

# Nginx access logs
sudo tail -f /var/log/nginx/agent-aura-*-access.log

# Application logs
sudo tail -f /var/log/agent-aura/*.log
```

## 🚨 Troubleshooting

### Backend won't start
```bash
# Check logs
sudo journalctl -u agent-aura-backend -n 50

# Test configuration
source /var/www/agent-aura/agent-aura-backend/venv/bin/activate
python -c "from app.main import app; print('OK')"

# Check permissions
sudo chown -R www-data:www-data /var/www/agent-aura
```

### Database connection failed
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U agent_aura_user -d agent_aura_prod -h localhost

# Check pg_hba.conf
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

### SSL certificate issues
```bash
# Renew certificate
sudo certbot renew --force-renewal

# Check certificate expiry
sudo certbot certificates

# Test SSL
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Add load balancer (HAProxy/Nginx)
- Run multiple backend instances
- Use Redis for shared sessions
- PostgreSQL read replicas

### Vertical Scaling
- Increase DB_POOL_SIZE
- Add more WORKERS to uvicorn
- Increase server resources
- Optimize database queries

---

**Production deployment complete! 🎉**

Your Agent Aura instance is now running securely in production with PostgreSQL, SSL/HTTPS, rate limiting, and comprehensive monitoring.

# 🔒 Agent Aura - Security & Configuration Guide

## ⚠️ Important Security Notice

**NEVER commit sensitive information to your repository!**

This guide explains how to properly configure Agent Aura while keeping your secrets secure.

---

## 🔐 What NOT to Commit

### ❌ Never Commit These Files:
- `.env` - Contains actual API keys and secrets
- `.env.local` - Local overrides with secrets
- `.env.production` - Production environment variables
- `*.key` - Private keys
- `*.pem` - SSL certificates
- `credentials.json` - Service account credentials
- Any file containing API keys, passwords, or tokens

### ✅ Safe to Commit:
- `.env.example` - Template without actual values
- `.gitignore` - Excludes sensitive files
- Documentation about configuration
- Scripts that reference environment variables

---

## 🚀 Initial Setup

### Step 1: Copy Environment Templates

```powershell
# Root directory
Copy-Item .env.example .env

# Backend directory
Copy-Item agent-aura-backend\.env.example agent-aura-backend\.env
```

### Step 2: Get Your API Keys

#### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your key

#### Anthropic API Key (Optional)
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an account
3. Generate an API key

### Step 3: Update Configuration Files

#### Root `.env` File
```env
# Replace with your actual API keys
GEMINI_API_KEY=your_actual_gemini_key_here
ANTHROPIC_API_KEY=your_actual_anthropic_key_here  # Optional
```

#### Backend `.env` File
```env
# API Keys
GEMINI_API_KEY=your_actual_gemini_key_here

# Security Keys (Generate new ones!)
SECRET_KEY=<generate_with_openssl>
JWT_SECRET_KEY=<generate_with_openssl>
```

### Step 4: Generate Secure Keys

```powershell
# Generate SECRET_KEY (PowerShell)
$bytes = New-Object byte[] 32
[Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
[BitConverter]::ToString($bytes).Replace('-','').ToLower()

# Or use Python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🛡️ Security Best Practices

### 1. Environment Variables

**Development:**
```env
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///./agent_aura_local.db
```

**Production:**
```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### 2. Database Security

**Development (SQLite):**
```env
DATABASE_URL=sqlite:///./agent_aura_local.db
```

**Production (PostgreSQL):**
```env
DATABASE_URL=postgresql://agent_aura_user:SECURE_PASSWORD@localhost:5432/agent_aura_prod
```

**Never use default passwords in production!**

### 3. JWT Secrets

```env
# Development (Still change these!)
SECRET_KEY=dev_secret_key_at_least_32_characters_long
JWT_SECRET_KEY=dev_jwt_secret_at_least_32_characters

# Production (MUST be random!)
SECRET_KEY=a8f5f167f44f4964e6c998dee827110c03f7b92f8d1c7a8b5f3d2e9c1b0a8f6e
JWT_SECRET_KEY=7b3e9f8a5c2d1b6e4f8a9c5d3e2f1b8a6c9d4e7f3a2b5c8d1e6f9a3b7c4e2f1
```

### 4. CORS Configuration

**Development:**
```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Production:**
```env
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 5. Rate Limiting

**Enable for production:**
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
USE_REDIS_RATE_LIMIT=true
REDIS_URL=redis://localhost:6379
```

---

## 📦 Before Committing Changes

### Checklist

- [ ] All `.env` files are in `.gitignore`
- [ ] No API keys in code files
- [ ] `.env.example` files have placeholder values
- [ ] Secrets are stored in environment variables
- [ ] Production secrets are different from development
- [ ] Database passwords are strong
- [ ] JWT secrets are random and long

### Verify No Secrets

```powershell
# Search for potential API keys in your code
git grep -i "api[_-]key" -- "*.py" "*.ts" "*.tsx" "*.js"
git grep -i "secret" -- "*.py" "*.ts" "*.tsx" "*.js"
git grep "AIza" -- "*.py" "*.ts" "*.tsx" "*.js"
```

**All searches should return no results or only references to environment variables!**

### Check Git Status

```powershell
# Verify .env files are not staged
git status

# Should NOT see:
# .env
# agent-aura-backend/.env
# credentials.json
```

---

## 🔄 Configuration Management

### Local Development

1. **Never share your `.env` files**
2. **Each developer gets their own API keys**
3. **Use `.env.example` as reference**

### Team Workflow

```powershell
# New team member setup
git clone repository
Copy-Item .env.example .env
Copy-Item agent-aura-backend\.env.example agent-aura-backend\.env

# Team member fills in their own API keys
notepad .env
notepad agent-aura-backend\.env
```

### Production Deployment

1. **Never copy `.env` files to production server**
2. **Set environment variables directly on server**
3. **Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)**

```bash
# Set environment variables on Ubuntu
export GEMINI_API_KEY="your_key_here"
export SECRET_KEY="your_secret_here"

# Or use systemd environment files
sudo nano /etc/agent-aura/environment
```

---

## 🚨 What to Do If You Committed Secrets

### If You Accidentally Committed API Keys

**1. Revoke the Key Immediately**
- Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
- Delete the compromised API key
- Generate a new one

**2. Remove from Git History**
```powershell
# Remove file from all Git history (DANGEROUS!)
git filter-branch --force --index-filter `
  "git rm --cached --ignore-unmatch .env" `
  --prune-empty --tag-name-filter cat -- --all

# Force push (WARNING: Coordinate with team!)
git push origin --force --all
```

**3. Update Your Configuration**
```powershell
# Update with new API key
notepad .env

# Commit the fix (but NOT the .env file!)
git add .gitignore
git commit -m "Security: Updated .gitignore to prevent secret exposure"
git push origin main
```

**4. Notify Your Team**
- Inform team members that keys were compromised
- Ask them to update their local `.env` files
- Document the incident for future reference

---

## 📝 Environment Variable Reference

### Root `.env`

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ | - | Google Gemini API key |
| `ANTHROPIC_API_KEY` | ❌ | - | Anthropic Claude API key (optional) |
| `ORCHESTRATOR_MODEL` | ❌ | `gemini-1.5-pro` | Orchestrator agent model |
| `WORKER_MODEL` | ❌ | `gemini-1.5-pro` | Worker agent model |
| `CRITICAL_RISK_THRESHOLD` | ❌ | `0.90` | Critical risk threshold (0-1) |
| `HIGH_RISK_THRESHOLD` | ❌ | `0.80` | High risk threshold (0-1) |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |

### Backend `.env`

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ | - | Google Gemini API key |
| `SECRET_KEY` | ✅ | - | Application secret (32+ chars) |
| `JWT_SECRET_KEY` | ✅ | - | JWT signing key (32+ chars) |
| `DATABASE_URL` | ✅ | SQLite | Database connection string |
| `CORS_ORIGINS` | ✅ | localhost | Allowed CORS origins |
| `ENVIRONMENT` | ❌ | `development` | Environment name |
| `DEBUG` | ❌ | `true` | Debug mode |
| `RATE_LIMIT_ENABLED` | ❌ | `true` | Enable rate limiting |

---

## 🔍 Auditing & Monitoring

### Regular Security Checks

```powershell
# Check for secrets in repository
git secrets --scan

# Check file permissions
icacls .env

# Verify .gitignore is working
git check-ignore -v .env
```

### Monitoring

```env
# Enable monitoring in production
ENABLE_MONITORING=true
SENTRY_DSN=your_sentry_dsn
SENTRY_ENVIRONMENT=production
```

---

## 📞 Support

If you have questions about security configuration:

1. Check this guide first
2. Review `.env.example` files
3. Open an issue on GitHub (DO NOT include actual secrets!)
4. Contact: sumedhgurchal358@gmail.com

---

## ✅ Security Checklist

Before deploying to production:

- [ ] All API keys are in environment variables
- [ ] `.env` files are NOT in git repository
- [ ] Generated new random SECRET_KEY and JWT_SECRET_KEY
- [ ] Changed default database password
- [ ] Enabled HTTPS/SSL
- [ ] Configured CORS properly
- [ ] Enabled rate limiting with Redis
- [ ] Set up monitoring (Sentry)
- [ ] Configured automated backups
- [ ] Tested secret rotation process
- [ ] Documented recovery procedures

---

**Remember: Security is not a one-time task. Review your configuration regularly!**

For more information, see:
- [PRODUCTION_DEPLOYMENT.md](docs/deployment/PRODUCTION_DEPLOYMENT.md)
- [FastAPI Security Guide](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

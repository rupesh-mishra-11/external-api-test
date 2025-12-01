# Environment Variables Setup Guide

## 🔐 OAuth2 Credentials from Environment Variables

All OAuth2 credentials and URLs are now loaded from **environment variables** for better security and flexibility. No more hardcoded credentials in the repo!

---

## 🚀 Quick Setup (5 Minutes)

### **Step 1: Copy the Example File**

```bash
# Copy env.example to .env
cp env.example .env
```

### **Step 2: (Optional) Update Credentials**

The `.env` file already contains the credentials from your Postman collections. If you need to update them:

```bash
# Edit .env with your preferred editor
nano .env
# or
vim .env
# or
code .env  # VS Code
```

### **Step 3: Start the Application**

```powershell
# Development mode
wsl docker-compose -f docker-compose.dev.yml up --build

# OR Production mode
wsl docker-compose up --build
```

**That's it!** 🎉 The application will automatically load all OAuth2 credentials from the `.env` file.

---

## 📋 Environment Variable Structure

### **Per-Environment OAuth2 Configuration:**

Each environment has 4 environment variables:

| Variable Pattern | Description | Example |
|-----------------|-------------|---------|
| `{ENV}_TOKEN_URL` | OAuth2 token endpoint URL | `TRUNK_TOKEN_URL=https://...` |
| `{ENV}_CLIENT_ID` | OAuth2 client ID | `TRUNK_CLIENT_ID=5s2fglra...` |
| `{ENV}_CLIENT_SECRET` | OAuth2 client secret | `TRUNK_CLIENT_SECRET=1eomncrl...` |
| `{ENV}_OAUTH_SCOPE` | OAuth2 scope (space-separated) | `TRUNK_OAUTH_SCOPE=entrata.respay...` |

### **Environment Prefixes:**

| Environment | Prefix | Example Variables |
|------------|--------|-------------------|
| Capricorn Trunk | `TRUNK_` | `TRUNK_TOKEN_URL`, `TRUNK_CLIENT_ID` |
| Rapid Production | `RAPID_PROD_` | `RAPID_PROD_TOKEN_URL`, `RAPID_PROD_CLIENT_ID` |
| Standard Production | `STANDARD_PROD_` | `STANDARD_PROD_TOKEN_URL`, `STANDARD_PROD_CLIENT_ID` |
| Rapid Stage | `RAPID_STAGE_` | `RAPID_STAGE_TOKEN_URL`, `RAPID_STAGE_CLIENT_ID` |
| Standard Stage | `STANDARD_STAGE_` | `STANDARD_STAGE_TOKEN_URL`, `STANDARD_STAGE_CLIENT_ID` |
| External Local | `EXTERNAL_LOCAL_` | `EXTERNAL_LOCAL_TOKEN_URL`, `EXTERNAL_LOCAL_CLIENT_ID` |

---

## 📁 .env File Structure

```bash
# ============================================
# Capricorn API Trunk (Development)
# ============================================
TRUNK_TOKEN_URL=https://us-resident-auth.d05d0001.entratadev.com/oauth2/token
TRUNK_CLIENT_ID=5s2fglraslk1j418gtefpqpv28
TRUNK_CLIENT_SECRET=1eomncrl4lam7t98uabmt4lt6gsrq01dg6oti7vail191sttquf
TRUNK_OAUTH_SCOPE=entrata.respay.external.api/read.payment_types ...

# ============================================
# Capricorn Rapid Production
# ============================================
RAPID_PROD_TOKEN_URL=https://us-resident-auth.entrata.com/oauth2/token
RAPID_PROD_CLIENT_ID=26kuq00ebf92phq234pj3f164r
RAPID_PROD_CLIENT_SECRET=tsdiplbtm3hv0l5niiuic8v7cj2rstgh6dfv5hodfrg8000kotb
RAPID_PROD_OAUTH_SCOPE=entrata.respay.external.api/read.balance ...

# ... and so on for all 6 environments
```

**Complete example:** See `env.example` file.

---

## 🔄 How It Works

### **Application Startup:**

```
1. Docker starts container
   ↓
2. Docker loads .env file
   ↓
3. Environment variables set in container
   ↓
4. app.py reads environment variables
   ↓
5. load_auth_config() builds OAuth2 config from env vars
   ↓
6. Each environment gets its own OAuth2 config
   ↓
7. Tokens auto-refresh independently per environment
```

### **Code Flow:**

```python
# In app.py
ENV_VAR_MAPPING = {
    'capricorn-trunk': 'TRUNK',
    'rapid-prod': 'RAPID_PROD',
    ...
}

def load_auth_config():
    for env_id, env_prefix in ENV_VAR_MAPPING.items():
        token_url = os.getenv(f'{env_prefix}_TOKEN_URL')
        client_id = os.getenv(f'{env_prefix}_CLIENT_ID')
        # ... build config from env vars
```

---

## ✅ Benefits

### **1. Security:**
- ✅ No credentials committed to Git
- ✅ Each developer has their own `.env`
- ✅ Production credentials separate from repo
- ✅ Easy credential rotation

### **2. Flexibility:**
- ✅ Different credentials per environment
- ✅ Override per developer/deployment
- ✅ CI/CD friendly
- ✅ Multiple deployment configurations

### **3. Simplicity:**
- ✅ One file to manage (`.env`)
- ✅ Standard 12-factor app pattern
- ✅ Clear variable naming
- ✅ Easy to understand

---

## 🔍 Verifying Configuration

### **Check Logs on Startup:**

```powershell
# Start in dev mode
wsl docker-compose -f docker-compose.dev.yml up

# Look for these messages:
✅ Loaded OAuth2 config for capricorn-trunk from environment variables
✅ Loaded OAuth2 config for rapid-prod from environment variables
✅ Loaded OAuth2 config for standard-prod from environment variables
✅ Loaded OAuth2 config for rapid-stage from environment variables
✅ Loaded OAuth2 config for standard-stage from environment variables
✅ Loaded OAuth2 config for external-local from environment variables
```

### **If Environment Missing:**

```
⚠️  Missing OAuth2 env vars for rapid-prod (RAPID_PROD_*)
```

**Fix:** Add the missing environment variables to `.env` file and restart.

---

## 🛠️ Troubleshooting

### **Issue: "Missing OAuth2 env vars" warning on startup**

**Cause:** Environment variables not set in `.env` file.

**Fix:**

1. Check that `.env` file exists in project root
2. Verify variables are defined correctly:
   ```bash
   cat .env | grep TRUNK_CLIENT_ID
   # Should output: TRUNK_CLIENT_ID=5s2fglra...
   ```
3. Restart container:
   ```powershell
   wsl docker-compose -f docker-compose.dev.yml restart
   ```

---

### **Issue: Token refresh failing for specific environment**

**Cause:** Wrong credentials in `.env` file.

**Fix:**

1. Open Postman collection for that environment
2. Find "AuthToken" request
3. Check the credentials
4. Update in `.env` file:
   ```bash
   # For Rapid Production
   RAPID_PROD_CLIENT_ID=correct_client_id
   RAPID_PROD_CLIENT_SECRET=correct_client_secret
   ```
5. Restart container

---

### **Issue: .env file not being loaded**

**Cause:** Docker not detecting `.env` file changes.

**Fix:**

```powershell
# Stop containers
wsl docker-compose -f docker-compose.dev.yml down

# Rebuild and restart
wsl docker-compose -f docker-compose.dev.yml up --build
```

---

### **Issue: Want to use different credentials for local testing**

**Solution:**

1. Create a `.env.local` file:
   ```bash
   cp .env .env.local
   # Edit .env.local with test credentials
   ```

2. Update docker-compose.dev.yml to use it:
   ```yaml
   env_file:
     - .env.local  # Use local credentials
   ```

3. Restart container

---

## 🎯 Advanced Configuration

### **Multiple Environment Files:**

You can use multiple `.env` files for different deployments:

```bash
.env              # Default (gitignored)
.env.example      # Template (committed)
.env.production   # Production credentials (gitignored)
.env.staging      # Staging credentials (gitignored)
.env.local        # Local dev credentials (gitignored)
```

### **Docker Compose Override:**

```yaml
# docker-compose.override.yml
services:
  api-tester:
    env_file:
      - .env.local  # Use local credentials
```

### **CI/CD Integration:**

```yaml
# .github/workflows/deploy.yml
- name: Set environment variables
  run: |
    echo "TRUNK_TOKEN_URL=${{ secrets.TRUNK_TOKEN_URL }}" >> .env
    echo "TRUNK_CLIENT_ID=${{ secrets.TRUNK_CLIENT_ID }}" >> .env
    echo "TRUNK_CLIENT_SECRET=${{ secrets.TRUNK_CLIENT_SECRET }}" >> .env
```

---

## 📊 Comparison: Before vs After

### **Before (Hardcoded in auth_config.json):**

```json
{
  "environments": {
    "capricorn-trunk": {
      "oauth2": {
        "client_id": "5s2fglraslk1j418gtefpqpv28",  ← Committed to Git!
        "client_secret": "1eomncrl..."  ← Security risk!
      }
    }
  }
}
```

**Problems:**
- ❌ Credentials in Git history
- ❌ Hard to rotate credentials
- ❌ All developers use same credentials
- ❌ Can't have different prod/dev credentials

---

### **After (Environment Variables):**

```bash
# .env (gitignored, not committed)
TRUNK_CLIENT_ID=5s2fglraslk1j418gtefpqpv28
TRUNK_CLIENT_SECRET=1eomncrl...
```

**Benefits:**
- ✅ No credentials in Git
- ✅ Easy credential rotation
- ✅ Each developer has own credentials
- ✅ Different prod/dev credentials
- ✅ Industry standard (12-factor app)

---

## 📚 Related Documentation

- **[env.example](env.example)** - Template with all variables
- **[MULTI_ENV_OAUTH2_SETUP.md](MULTI_ENV_OAUTH2_SETUP.md)** - OAuth2 auto-refresh
- **[START_HERE.md](START_HERE.md)** - Quick start guide

---

## 🎓 Best Practices

### **1. Never Commit .env File:**

```bash
# .gitignore
.env
.env.local
.env.*.local
```

✅ Already configured in this project!

### **2. Always Provide .env.example:**

```bash
# Keep env.example updated with all required variables (without real values)
cp .env env.example
# Remove real credentials from env.example
# Commit env.example to Git
```

✅ Already included: `env.example`

### **3. Document All Variables:**

Add comments in `env.example` explaining each variable:

```bash
# OAuth2 token endpoint for Capricorn Trunk environment
TRUNK_TOKEN_URL=https://...
```

✅ Already documented in `env.example`

### **4. Use Secrets Management in Production:**

For production deployments, consider:
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Docker Secrets
- Kubernetes Secrets

---

## ✅ Setup Checklist

- [ ] Copy `env.example` to `.env`
- [ ] Verify all credentials in `.env`
- [ ] Start container: `wsl docker-compose -f docker-compose.dev.yml up --build`
- [ ] Check logs for "✅ Loaded OAuth2 config" messages
- [ ] Open test runner: `http://localhost:5000/test-runner`
- [ ] Select environment and run test
- [ ] Verify token auto-refresh in logs
- [ ] Confirm all 6 environments working

---

## 🎉 Summary

### **What You Have:**
- ✅ All OAuth2 credentials in environment variables
- ✅ No credentials committed to Git
- ✅ Easy credential rotation
- ✅ Per-environment configuration
- ✅ Auto-refresh per environment
- ✅ Industry-standard 12-factor app pattern

### **Setup Time:**
- 📝 Copy `env.example` to `.env`: **30 seconds**
- 🚀 Start container: **1-2 minutes**
- ✅ Verify working: **1 minute**
- **Total: ~3-4 minutes** 🎯

---

**Your OAuth2 credentials are now secure, flexible, and managed through environment variables!** 🔐

Just copy `env.example` to `.env` and start testing across all 6 environments with automatic token management! 🚀


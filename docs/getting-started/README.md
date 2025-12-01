# 🚨 START HERE - Multi-Environment Test Runner

## 🎉 KEY FEATURES:

### 1. **OAuth2 Auto-Refresh** 🔄
- **Tokens refresh automatically** before expiration!
- No more manual token updates from Postman
- Run tests for hours without interruption
- See [AUTO_REFRESH_OAUTH2_GUIDE.md](AUTO_REFRESH_OAUTH2_GUIDE.md)

### 2. **Environment Selector** 🌐
- Switch between **6 different environments**:
  - Capricorn API Trunk (Dev)
  - Capricorn Rapid Production
  - Capricorn Standard Production
  - Capricorn Rapid Stage
  - Capricorn Standard Stage
  - External API Local
- Dropdown in UI - instant switching
- See [MULTI_ENVIRONMENT_GUIDE.md](MULTI_ENVIRONMENT_GUIDE.md)

### 3. **Dual Authentication** 🔐
- OAuth2 Bearer token (auto-refreshed) + x-api-key
- Works for all environments automatically
- See [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md)

**Quick Start:**
1. **Setup OAuth2 credentials:** Copy `env.example` to `.env` (credentials already filled!)
2. **Start:** `wsl docker-compose -f docker-compose.dev.yml up --build`
3. **Open:** http://localhost:5000/test-runner
4. **Select environment** from dropdown
5. **Run tests!** (Token refreshes automatically ✨)

**See:** [ENV_SETUP_GUIDE.md](ENV_SETUP_GUIDE.md) for detailed environment variable setup

---

## 🔐 FIRST TIME SETUP (2 Minutes):

### **Step 1: Configure OAuth2 Credentials**

All OAuth2 credentials are loaded from environment variables (not committed to Git for security).

```powershell
# Copy the example file (credentials already included from Postman collections)
wsl cp env.example .env

# That's it! The .env file already has all credentials configured.
```

**✅ The `.env` file contains OAuth2 credentials for all 6 environments extracted from your Postman collections.**

**See:** [ENV_SETUP_GUIDE.md](ENV_SETUP_GUIDE.md) for:
- How environment variables work
- Updating credentials
- Troubleshooting
- Security best practices

---

## YOUR PROBLEM (If Hot-Reload Isn't Working):

You're running **PRODUCTION mode** where files are baked into the Docker image.
Changes to your code on your computer DON'T affect the running container!

## THE FIX:

### Step 1: Stop Production Container
```powershell
docker-compose down
```

### Step 2: Start Development Container
```powershell
wsl docker-compose -f docker-compose.dev.yml up --build
```

That's it! Now changes will reflect instantly.

---

## 🎯 Quick Commands

### Development Mode (Changes Auto-Reload)
```powershell
# Stop any running containers first
docker-compose down
docker-compose -f docker-compose.dev.yml down

# Start in dev mode (foreground - see logs)
wsl docker-compose -f docker-compose.dev.yml up --build

# OR start in background
wsl docker-compose -f docker-compose.dev.yml up --build -d

# View logs if running in background
docker-compose -f docker-compose.dev.yml logs -f
```

### Production Mode (Requires Rebuild)
```powershell
docker-compose up --build -d
```

---

## ✅ How to Know You're in Dev Mode

Look for this in the startup logs:
```
⚡ Hot-reload enabled - changes will auto-reload
```

---

## 📝 Making Changes

### In Dev Mode:
1. Edit `app.py`, `static/test-runner.html`, or `test_cases.json`
2. Save file
3. Wait 1-2 seconds (Flask reloads)
4. Refresh browser
5. ✅ Changes appear!

### In Production Mode:
1. Edit file
2. Save file
3. Run: `docker-compose up --build -d`
4. Wait for rebuild (~20-30 seconds)
5. Refresh browser
6. ✅ Changes appear

---

## 🎓 Understanding the Difference

| Mode | Files | Reload | Speed | Use For |
|------|-------|--------|-------|---------|
| **Development** | Volume mounted | Auto | Instant | Coding |
| **Production** | Baked into image | Manual rebuild | 20-30 sec | Testing/Deploy |

---

## 🚀 Your Next Steps

1. Run this now:
   ```powershell
   docker-compose down
   wsl docker-compose -f docker-compose.dev.yml up --build
   ```

2. Open: http://localhost:5000/test-runner

3. Edit `static/test-runner.html` - change something

4. Save file

5. Refresh browser - see your changes!

---

**Pro Tip:** Keep the dev container running in one terminal, edit code in VS Code, refresh browser to see changes. No rebuild needed! 🎉

---

## 🔐 Authentication Setup

**OAuth2 tokens now auto-refresh!** ✨ No manual updates needed.

Your `auth_config.json` should look like this:

```json
{
  "oauth2": {
    "enabled": true,
    "token_url": "https://us-resident-auth.d05d0001.entratadev.com/oauth2/token",
    "client_id": "5s2fglraslk1j418gtefpqpv28",
    "client_secret": "1eomncrl4lam7t98uabmt4lt6gsrq01dg6oti7vail191sttquf"
  },
  "auth": {
    "custom_headers": {
      "x-api-key": "cx6y1QcT7H778NlekZDua1FCIOk1XSB29O7Ox4hJ"
    }
  }
}
```

**That's it!** Tokens refresh automatically before expiration.

**Detailed guide:** [AUTO_REFRESH_OAUTH2_GUIDE.md](AUTO_REFRESH_OAUTH2_GUIDE.md)

---

## 🌐 Network Issues?

If you see **"Failed to resolve hostname"** errors:

**Quick fix:**
```powershell
# I've configured host network mode
# Just restart:
docker-compose -f docker-compose.dev.yml down
wsl docker-compose -f docker-compose.dev.yml up --build
```

**If still failing:**
1. Check if API at port 7080 is running
2. See [NETWORK_TROUBLESHOOTING.md](NETWORK_TROUBLESHOOTING.md) for detailed fixes
3. Try using IP address instead: Create `.env` file with:
   ```
   API_BASE_URL=http://localhost:7080
   ```

---


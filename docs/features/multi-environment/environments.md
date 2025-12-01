# Multi-Environment Guide

## 🌐 Available Environments

Your test runner now supports **6 different environments**!

---

## 📋 Environment Overview

| Environment | Type | Base URL | Purpose |
|------------|------|----------|---------|
| **Capricorn API Trunk** | Development | `d05d0001.entratadev.com` | Dev/Testing |
| **Capricorn Rapid Production** | Production | `entrata.com` | Live Production (Rapid) |
| **Capricorn Standard Production** | Production | `entrata.com` | Live Production (Standard) |
| **Capricorn Rapid Stage** | Staging | `s01a0001.entratastage.com` | Pre-production (Rapid) |
| **Capricorn Standard Stage** | Staging | `s01a0001.entratastage.com` | Pre-production (Standard) |
| **External API Local** | Local | `localhost:7080` | Local development |

---

## 🎯 Detailed Environment Info

### 1. **Capricorn API Trunk** (Development)
- **URL:** `https://us-residentpay-external.d05d0001.entratadev.com`
- **API Key:** `cx6y1QcT7H778NlekZDua1FCIOk1XSB29O7Ox4hJ`
- **Use Case:** Development and testing
- **Test Cases:** 22 endpoints
- **OAuth2:** Required (auto-refresh enabled)

---

### 2. **Capricorn Rapid Production** 🚀
- **URL:** `https://us-residentpay-external.entrata.com`
- **API Key:** `XiDfpNWVug1OhBk3iLuFLabr1kG4iWop8JLwEHWu`
- **Use Case:** Live production environment (Rapid deployment)
- **Test Cases:** 5 core endpoints
- **OAuth2:** Required (auto-refresh enabled)
- **⚠️ Caution:** This is PRODUCTION! Changes affect real users.

---

### 3. **Capricorn Standard Production** 🏢
- **URL:** `https://us-residentpay-external.entrata.com`
- **API Key:** `XiDfpNWVug1OhBk3iLuFLabr1kG4iWop8JLwEHWu`
- **Use Case:** Live production environment (Standard deployment)
- **Test Cases:** 5 core endpoints
- **OAuth2:** Required (auto-refresh enabled)
- **⚠️ Caution:** This is PRODUCTION! Changes affect real users.

---

### 4. **Capricorn Rapid Stage** 🧪
- **URL:** `https://us-residentpay-external.s01a0001.entratastage.com`
- **API Key:** `lgvHXC5m8Q5Ab9J6vMcnAa4LDonxZCgU6ZRziOKD`
- **Use Case:** Pre-production testing (Rapid)
- **Test Cases:** 5 core endpoints
- **OAuth2:** Required (auto-refresh enabled)
- **✅ Safe:** Test here before production!

---

### 5. **Capricorn Standard Stage** 🧪
- **URL:** `https://us-residentpay-external.s01a0001.entratastage.com`
- **API Key:** `lgvHXC5m8Q5Ab9J6vMcnAa4LDonxZCgU6ZRziOKD`
- **Use Case:** Pre-production testing (Standard)
- **Test Cases:** 5 core endpoints
- **OAuth2:** Required (auto-refresh enabled)
- **✅ Safe:** Test here before production!

---

### 6. **External API Local** 💻
- **URL:** `http://rsync.residentportal2.residentportal.localhost:7080`
- **Use Case:** Local development server
- **Test Cases:** Multiple local endpoints
- **OAuth2:** Required (auto-refresh enabled)
- **Note:** Requires local server running

---

## 🔄 Switching Environments

### In the UI:

1. Open: `http://localhost:5000/test-runner`
2. Look at the **Environment dropdown** (top-left)
3. Click to expand
4. Select your target environment
5. Tests automatically reload for that environment!

**Example:**
```
Environment: [Capricorn Rapid Production ▼]
             ├─ Capricorn API Trunk
             ├─ Capricorn Rapid Production ✓
             ├─ Capricorn Standard Production
             ├─ Capricorn Rapid Stage
             ├─ Capricorn Standard Stage
             └─ External API Local
```

---

## 🔐 Authentication Per Environment

All environments use **OAuth2 auto-refresh** + **x-api-key**:

### Production Environments:
```http
Authorization: Bearer {auto-refreshed-token}
x-api-key: XiDfpNWVug1OhBk3iLuFLabr1kG4iWop8JLwEHWu
x-client-type: mobile
```

### Stage Environments:
```http
Authorization: Bearer {auto-refreshed-token}
x-api-key: lgvHXC5m8Q5Ab9J6vMcnAa4LDonxZCgU6ZRziOKD
x-client-type: mobile
```

### Trunk (Dev):
```http
Authorization: Bearer {auto-refreshed-token}
x-api-key: cx6y1QcT7H778NlekZDua1FCIOk1XSB29O7Ox4hJ
x-client-type: mobile
```

**Note:** API keys are embedded in test cases, OAuth2 tokens auto-refresh!

---

## 🎯 Typical Workflow

### Development Flow:
```
1. Develop → Test on Local (External API Local)
2. Integration → Test on Trunk (Capricorn API Trunk)
3. Pre-prod → Test on Stage (Rapid/Standard Stage)
4. Production → Test on Prod (Rapid/Standard Production)
```

### Quick Testing Flow:
```
1. Select environment
2. Run tests
3. Check results
4. Switch environment
5. Repeat!
```

---

## ⚠️ Production Safety

### **IMPORTANT: Production Environments**

**Rapid Production** and **Standard Production** are LIVE environments:
- ✅ Safe: Read operations (GET requests)
- ⚠️ Caution: Write operations (POST/PUT/DELETE)
- ❌ Avoid: Test data creation in production

**Best Practice:**
1. Always test on **Stage** first
2. Verify results thoroughly
3. Only then test on **Production**
4. Use real user credentials carefully

---

## 📊 Environment Comparison

| Feature | Trunk | Rapid Prod | Standard Prod | Rapid Stage | Standard Stage | Local |
|---------|-------|------------|---------------|-------------|----------------|-------|
| **Live Data** | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Safe Testing** | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **OAuth2 Auto-Refresh** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Full Test Suite** | ✅ (22) | ❌ (5) | ❌ (5) | ❌ (5) | ❌ (5) | ✅ |
| **Deployment Type** | Dev | Rapid | Standard | Rapid | Standard | Local |

---

## 🔍 Troubleshooting

### Issue: Environment won't load

**Cause:** Test case file missing

**Fix:**
```powershell
# Check if all test case files exist
ls test_cases*.json

# Should show:
# - test_cases.json
# - test_cases_capricorn.json
# - test_cases_rapid_prod.json
# - test_cases_standard_prod.json
# - test_cases_rapid_stage.json
# - test_cases_standard_stage.json
```

---

### Issue: "Unauthorized" on new environment

**Cause:** OAuth2 token needs refresh

**Fix:**
Container automatically refreshes tokens, but if issues persist:
1. Check container logs: `docker-compose logs --tail=50`
2. Look for "✅ Token refreshed successfully"
3. Restart container if needed

---

### Issue: Tests fail on Production but work on Stage

**Possible causes:**
1. Different data in Production
2. Different permissions
3. Rate limiting
4. Production-specific validation

**Solution:**
- Verify test data exists in Production
- Check API key permissions
- Review error messages carefully

---

## 📝 Adding New Environments

To add a new environment:

### 1. Create test case file:
```json
{
  "base_url": "https://your-api.com",
  "test_cases": [...]
}
```

### 2. Update `environments.json`:
```json
{
  "id": "your-env",
  "name": "Your Environment Name",
  "base_url": "https://your-api.com",
  "test_cases_file": "test_cases_your_env.json",
  "description": "Your environment description"
}
```

### 3. Update `Dockerfile`:
```dockerfile
COPY test_cases_your_env.json .
```

### 4. Update `docker-compose.dev.yml`:
```yaml
- ./test_cases_your_env.json:/app/test_cases_your_env.json
```

### 5. Restart:
```powershell
wsl docker-compose -f docker-compose.dev.yml restart
```

---

## ✅ Summary

**What You Have:**
- ✅ 6 different environments
- ✅ Easy switching via dropdown
- ✅ OAuth2 auto-refresh for all
- ✅ Environment-specific test cases
- ✅ Production + Stage + Dev + Local

**What You Can Do:**
- 🔄 Switch environments instantly
- 🧪 Test safely on Stage first
- 🚀 Validate on Production
- 💻 Develop locally
- 📊 Run same tests across all environments

---

## 🎓 Quick Reference

```
Trunk       → Development/Testing
Rapid Prod  → Live (Rapid deployment)
Standard Prod → Live (Standard deployment)
Rapid Stage → Pre-production (Rapid)
Standard Stage → Pre-production (Standard)
Local       → Local development
```

**All environments support OAuth2 auto-refresh!** 🎉

Just select your environment and run tests. The test runner handles everything else automatically!


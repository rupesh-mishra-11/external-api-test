# Multi-Environment Test Runner Guide

## 🎉 NEW FEATURE: Environment Selector

You now have a **dropdown** in the UI to switch between different API environments!

---

## 📋 Available Environments

### 1. **Capricorn API Trunk** (Default)
- **URL**: `https://us-residentpay-external.d05d0001.entratadev.com`
- **Description**: Production Trunk API endpoints
- **Endpoints**: Direct paths like `/addPaymentAccount`, `/makePayment`
- **Test Count**: 22 test cases

### 2. **External API Local**
- **URL**: `http://rsync.residentportal2.residentportal.localhost:7080`
- **Description**: Local development environment  
- **Endpoints**: Query params like `/exapi/?controller=add_payment_account`
- **Test Count**: 23 test cases

---

## 🚀 How to Use

### Switch Environments

1. Open: http://localhost:5000/test-runner
2. Look at the top of the page - you'll see:
   ```
   Environment: [Dropdown ▼]
   ```
3. Click the dropdown
4. Select environment:
   - **Capricorn API Trunk - Production Trunk API endpoints**
   - **External API Local - Local development environment**
5. Tests automatically reload for the selected environment!

### Run Tests

**Single Test:**
- Select your environment
- Click "▶ Run Test" on any test card
- View results

**All Tests:**
- Select your environment
- Click "▶ Run All Tests" at the top
- Watch all tests execute sequentially

**Switch and Test:**
1. Select "Capricorn API Trunk"
2. Run tests
3. Switch to "External API Local"
4. Run same type of tests on different API!

---

## 📁 File Structure

```
external-api-tester/
├── environments.json              # Environment configuration
├── test_cases_capricorn.json      # Capricorn API test cases
├── test_cases.json                # External API Local test cases
└── auth_config.json               # Shared authentication
```

---

## ⚙️ Configuration Files

### environments.json

```json
{
  "environments": [
    {
      "id": "capricorn-trunk",
      "name": "Capricorn API Trunk",
      "base_url": "https://us-residentpay-external.d05d0001.entratadev.com",
      "test_cases_file": "test_cases_capricorn.json",
      "description": "Production Trunk API endpoints"
    },
    {
      "id": "external-local",
      "name": "External API Local",
      "base_url": "http://rsync.residentportal2.residentportal.localhost:7080",
      "test_cases_file": "test_cases.json",
      "description": "Local development environment"
    }
  ],
  "default_environment": "capricorn-trunk"
}
```

---

## 🔧 Adding a New Environment

### Step 1: Create Test Cases File

Create `test_cases_newenv.json`:

```json
{
  "base_url": "https://your-api-url.com",
  "test_cases": [
    {
      "id": "new_1",
      "name": "Test Name",
      "endpoint": "/endpoint",
      "method": "POST",
      "headers": {
        "x-api-key": "your_key"
      },
      "body": {
        "param": "value"
      },
      "category": "Category Name"
    }
  ]
}
```

### Step 2: Update environments.json

Add your environment:

```json
{
  "environments": [
    // ... existing environments ...
    {
      "id": "new-env",
      "name": "New Environment",
      "base_url": "https://your-api-url.com",
      "test_cases_file": "test_cases_newenv.json",
      "description": "Your environment description"
    }
  ]
}
```

### Step 3: Update Docker Files

**Dockerfile:**
```dockerfile
COPY test_cases_newenv.json .
```

**docker-compose.dev.yml:**
```yaml
volumes:
  - ./test_cases_newenv.json:/app/test_cases_newenv.json
```

### Step 4: Restart

```powershell
docker-compose -f docker-compose.dev.yml restart
```

The new environment appears in the dropdown automatically!

---

## 🎨 UI Features

### Environment Indicator

The dropdown shows:
- **Environment name** (bold)
- **Description** (helps you choose)

Example:
```
Capricorn API Trunk - Production Trunk API endpoints
```

### Auto-Clear Results

When you switch environments:
- ✅ Previous results are cleared
- ✅ Test count updates
- ✅ Categories reset
- ✅ Fresh start for new environment

### Persistent Selection

While the page is open:
- Selected environment stays selected
- Navigate between tabs? Selection persists
- Only resets on page refresh

---

## 🔐 Authentication

### Shared Authentication

`auth_config.json` is **shared across all environments**:

```json
{
  "auth": {
    "bearer_token": "YOUR_TOKEN",
    "custom_headers": {
      "x-api-key": "YOUR_KEY",
      "x-client-type": "mobile-android"
    }
  }
}
```

All environments use the same auth by default.

### Environment-Specific Auth

If you need different auth per environment, you can:

**Option 1: Override in test_cases file**
```json
{
  "test_cases": [
    {
      "id": "1",
      "headers": {
        "Authorization": "Bearer SPECIFIC_TOKEN_FOR_THIS_ENV"
      }
    }
  ]
}
```

**Option 2: Create separate auth files**
```
auth_config_capricorn.json
auth_config_local.json
```

Then load conditionally in `app.py`.

---

## 📊 Differences Between Environments

### Capricorn API Trunk

| Feature | Value |
|---------|-------|
| URL Structure | Direct paths: `/addPaymentAccount` |
| Protocol | HTTPS |
| Method | PUT for most operations |
| Auth | x-api-key header |
| Test Count | 22 tests |

**Example Test:**
```json
{
  "endpoint": "/makePayment",
  "method": "PUT",
  "headers": {
    "x-api-key": "..."
  }
}
```

### External API Local

| Feature | Value |
|---------|-------|
| URL Structure | Query params: `/exapi/?controller=xxx` |
| Protocol | HTTP (local) |
| Method | Mostly POST |
| Auth | Bearer token + custom headers |
| Test Count | 23 tests |

**Example Test:**
```json
{
  "endpoint": "/exapi/?controller=add_payment_account",
  "method": "POST",
  "headers": {
    "x-client-type": "mobile_app"
  }
}
```

---

## 🐛 Troubleshooting

### Dropdown Not Appearing

**Check:**
1. Is `environments.json` in the project root?
2. Did you restart the container?
3. Check browser console for errors (F12)

**Fix:**
```powershell
# Restart dev container
docker-compose -f docker-compose.dev.yml restart
```

### Environment Shows But Tests Don't Load

**Check:**
1. Does the test_cases file exist?
2. Is the filename in `environments.json` correct?
3. Is the JSON valid?

**Fix:**
```powershell
# Validate JSON
python -m json.tool test_cases_capricorn.json

# Check container logs
docker-compose -f docker-compose.dev.yml logs -f
```

### Tests Fail After Switching

**Possible causes:**
1. **Auth mismatch** - Different environments may need different tokens
2. **Network issues** - Local vs remote endpoints
3. **Data mismatch** - Test data may not exist in new environment

**Fix:**
1. Check auth_config.json has correct credentials
2. Verify network connectivity to the API
3. Update test data to match environment

### Dropdown Shows "Loading..."

**Cause:** Frontend can't reach `/api/environments`

**Fix:**
```powershell
# Check if backend is running
curl http://localhost:5000/health

# Check environments endpoint
curl http://localhost:5000/api/environments

# Restart if needed
docker-compose -f docker-compose.dev.yml restart
```

---

## 💡 Pro Tips

### Tip 1: Use Descriptive Names

Make environment names clear:
✅ "Production Trunk API"  
✅ "Staging - v2.1"  
✅ "Local Development"  

❌ "Env1"  
❌ "Test"  
❌ "API"  

### Tip 2: Organize Test Cases

Keep test case files organized:
```
test_cases_production.json
test_cases_staging.json  
test_cases_local.json
test_cases_qa.json
```

### Tip 3: Document Differences

Add comments in your test case files:
```json
{
  "comment": "Capricorn uses direct paths, not query params",
  "test_cases": [...]
}
```

### Tip 4: Environment-Specific Data

Use different test data per environment:
- **Production**: Real but safe test accounts
- **Staging**: Any test data
- **Local**: Mock data

### Tip 5: Quick Comparison

Run same test in both environments:
1. Select "Capricorn"
2. Run "Get Payment Accounts"
3. Note the response
4. Select "External Local"
5. Run "Get Payment Accounts"
6. Compare responses!

---

## 📝 Summary

**What I Built:**
- ✅ Environment selector dropdown in UI
- ✅ Support for multiple API environments
- ✅ Automatic test case loading per environment
- ✅ Capricorn API Trunk configuration (22 tests)
- ✅ External API Local configuration (23 tests)
- ✅ Shared authentication across environments
- ✅ Hot-reload support for environment changes

**What You Can Do:**
- Switch between environments with one click
- Run tests on different APIs without code changes
- Compare API responses across environments
- Add new environments easily
- Use the same auth for all environments (or override per environment)

**Quick Start:**
1. Go to http://localhost:5000/test-runner
2. Select environment from dropdown
3. Run tests!

Enjoy your multi-environment test runner! 🎉


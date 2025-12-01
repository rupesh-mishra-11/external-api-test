# Authentication Setup Guide

## 🔐 How Authentication Works

Both APIs require **OAuth2 Bearer Token + API Key** (dual authentication)!

---

## 🌐 Authentication for All Environments

### Capricorn API Trunk & External API Local
**Authentication Method:** OAuth2 Bearer Token + API Key

**Headers Sent:**
```http
Authorization: Bearer eyJraWQiOiJOcmlFXC8wbHRDTEpNS...
x-api-key: cx6y1QcT7H778NlekZDua1FCIOk1XSB29O7Ox4hJ
x-client-type: mobile-android
```

**✅ ALL requests need BOTH headers** - This is dual authentication!

---

## ⚙️ Configuration File: `auth_config.json`

```json
{
  "auth": {
    "bearer_token": "eyJraWQiOiJOcmlFXC8wbHRDTEpNSDFSZ1ZzQlQ3TlRldE83UDA3N0ozWlM3dklGXC9sWlU9IiwiYWxnIjoiUlMyNTYifQ...",
    "api_key": "cx6y1QcT7H778NlekZDua1FCIOk1XSB29O7Ox4hJ",
    "custom_headers": {
      "x-api-key": "cx6y1QcT7H778NlekZDua1FCIOk1XSB29O7Ox4hJ",
      "x-client-type": "mobile-android"
    }
  }
}
```

### Fields Explained:

| Field | Used By | Purpose |
|-------|---------|---------|
| `bearer_token` | External API Local | OAuth2 access token (expires every 5 minutes) |
| `api_key` | Both | API Gateway key (reference, not directly used) |
| `custom_headers.x-api-key` | Both | API key header sent with ALL requests |
| `custom_headers.x-client-type` | Both | Client identifier sent with ALL requests |

---

## 🔄 How It Works (Automatic!)

1. **You select environment** in dropdown
2. **Test runner adds** authentication headers:
   - `Authorization: Bearer {token}` from `bearer_token`
   - `x-api-key: {key}` from `custom_headers`
   - `x-client-type: {type}` from `custom_headers`
3. **Request sent** with all headers
4. **API accepts** request ✅

**Both environments require the same authentication!**

---

## 🚀 Quick Setup

### Step 1: Get Your Bearer Token

If you need to test **External API Local**, get a fresh Bearer token:

```bash
# Using curl (PowerShell)
curl -X POST https://us-resident-auth.d05d0001.entratadev.com/oauth2/token `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -H "Accept: application/json" `
  -H "Authorization: Basic NXMyZmdscmFzbGsxajQxOGd0ZWZwcXB2Mjg6MWVvbW5jcmw0bGFtN3Q5OHVhYm10NGx0NmdzcnEwMWRnNm90aTd2YWlsMTkxc3R0cXVm" `
  -d "grant_type=client_credentials&scope=entrata.respay.external.api/read.payment_types..."
```

Copy the `access_token` from the response.

### Step 2: Update `auth_config.json`

```json
{
  "auth": {
    "bearer_token": "PASTE_YOUR_TOKEN_HERE",
    "api_key": "cx6y1QcT7H778NlekZDua1FCIOk1XSB29O7Ox4hJ",
    "custom_headers": {
      "x-api-key": "cx6y1QcT7H778NlekZDua1FCIOk1XSB29O7Ox4hJ",
      "x-client-type": "mobile-android"
    }
  }
}
```

### Step 3: Save & Test

- File auto-reloads in development mode (wait 2 seconds)
- No container restart needed!
- Select environment and run tests

---

## 🧪 Testing

### Test Any Environment:

1. Make sure `bearer_token` in auth_config.json is fresh (< 5 min old)
2. Select environment from dropdown
3. Run any test
4. Should work with Bearer token + x-api-key ✅

**Headers sent (same for all environments):**
```
Authorization: Bearer eyJraWQi...
x-api-key: cx6y1QcT7H...
x-client-type: mobile-android
```

---

## 🐛 Troubleshooting

### "Unauthorized" Error

**Cause:** Bearer token is missing or expired

**Fix 1: Check Token in Config**
```json
{
  "auth": {
    "bearer_token": ""  // ← Empty or old token!
  }
}
```

Add a fresh token!

**Fix 2: Token Expired (> 5 minutes old)**

OAuth2 tokens expire after 5 minutes. Get a new one:
1. Use the AuthToken endpoint in Postman
2. Or use the curl command above
3. Copy new access_token
4. Paste in auth_config.json
5. Save and test

**Fix 3: Wrong API Key**

Check that x-api-key matches your working Postman request:
```json
{
  "auth": {
    "custom_headers": {
      "x-api-key": "cx6y1QcT7H778NlekZDua1FCIOk1XSB29O7Ox4hJ"
    }
  }
}
```

---

## 📊 Verification Checklist

Before running tests:

- [ ] `auth_config.json` exists
- [ ] `custom_headers.x-api-key` is filled with valid API key
- [ ] For External API Local: `bearer_token` is filled and < 5 min old
- [ ] Container is running in development mode
- [ ] Selected correct environment in dropdown

---

## 💡 Pro Tips

### Tip 1: Bearer Token Expiry

OAuth2 tokens expire every **5 minutes**. If you're testing External API Local for a while:
1. Keep Postman open
2. Run the "AuthToken" request every 4 minutes
3. Copy new token to auth_config.json
4. Wait 2 seconds (auto-reload)
5. Continue testing!

### Tip 2: Testing Both Environments

Switch between environments instantly:
1. Test Capricorn API (no Bearer token needed)
2. Switch to External API Local
3. Add fresh Bearer token to config
4. Test External API
5. Switch back to Capricorn (Bearer token ignored automatically)

### Tip 3: Check What's Being Sent

Look at container logs to see actual headers:
```powershell
wsl docker-compose -f docker-compose.dev.yml logs -f | findstr "Bearer:"
```

You'll see:
```
Bearer: False  ← Capricorn test (good!)
Bearer: True   ← External Local test (good!)
```

---

## 🎓 Understanding the Code

### In `app.py`:

```python
def merge_headers(test_headers, use_bearer_token=False):
    """Merge test headers with global auth headers."""
    headers = dict(test_headers or {})
    auth_section = AUTH_CONFIG.get('auth', {})
    
    # Add Bearer token ONLY if use_bearer_token=True
    if use_bearer_token:
        bearer_token = auth_section.get('bearer_token', '')
        if bearer_token and 'Authorization' not in headers:
            headers['Authorization'] = f'Bearer {bearer_token}'
    
    # Always add custom headers (x-api-key, x-client-type)
    custom_headers = auth_section.get('custom_headers', {})
    for key, value in custom_headers.items():
        if key not in headers:
            headers[key] = value
    
    return headers
```

### When Running Tests:

```python
# Always use Bearer token for all environments
merged_headers = merge_headers(
    test_case.get('headers', {}), 
    use_bearer_token=True
)
```

**Simple logic:**
- All environments get: `Authorization: Bearer {token}`
- All environments get: `x-api-key: {key}`
- Dual authentication for maximum security!

---

## ✅ Summary

**What You Have:**
- ✅ Dual authentication (OAuth2 + API Key)
- ✅ Both Capricorn API & External API: Bearer token + x-api-key
- ✅ Automatic header injection
- ✅ No manual header management needed

**What You Need:**
- 📝 Valid x-api-key in `custom_headers`
- 🔑 Fresh Bearer token (< 5 min old) - **REQUIRED for all tests**
- 🐳 Development container running
- 🌐 Environment selected in UI

**Remember:** OAuth2 tokens expire every 5 minutes, so refresh regularly!

**That's it!** The test runner adds both authentication headers automatically. 🎉


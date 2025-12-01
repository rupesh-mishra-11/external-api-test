# OAuth2 Auto-Refresh Guide

## 🔄 Automatic Token Refresh - No More Manual Updates!

Your test runner now **automatically refreshes OAuth2 tokens** before they expire!

---

## ✨ How It Works

### Before Each Request:
1. **Check token status:**
   - Is token empty? → Refresh immediately
   - Will token expire in < 60 seconds? → Refresh proactively
   - Token is fresh? → Use it as-is

2. **Auto-refresh if needed:**
   - Calls OAuth2 token endpoint
   - Gets fresh access token (valid for 5 minutes)
   - Updates bearer_token in memory
   - Continues with request seamlessly

3. **Your tests run without interruption!**

---

## ⚙️ Configuration

Your `auth_config.json` now includes OAuth2 settings:

```json
{
  "oauth2": {
    "enabled": true,
    "token_url": "https://us-resident-auth.d05d0001.entratadev.com/oauth2/token",
    "client_id": "5s2fglraslk1j418gtefpqpv28",
    "client_secret": "1eomncrl4lam7t98uabmt4lt6gsrq01dg6oti7vail191sttquf",
    "grant_type": "client_credentials",
    "scope": "entrata.respay.external.api/..."
  },
  "auth": {
    "bearer_token": "",  // Auto-filled
    "token_expires_at": 0,  // Auto-updated
    "custom_headers": {
      "x-api-key": "cx6y1QcT7H778NlekZDua1FCIOk1XSB29O7Ox4hJ"
    }
  }
}
```

---

## 🚀 Usage

**No manual steps required!** Just run your tests:

1. **Start container:**
   ```powershell
   wsl docker-compose -f docker-compose.dev.yml up
   ```

2. **Open test runner:**
   ```
   http://localhost:5000/test-runner
   ```

3. **Run tests:**
   - Select environment
   - Click "▶ Run Test" or "▶ Run All Tests"
   - Token automatically refreshes as needed! ✨

---

## 🎯 What You'll See

### Container Logs:

```
INFO - No token found, refreshing...
INFO - Refreshing OAuth2 token from https://us-resident-auth.d05d0001.entratadev.com/oauth2/token
INFO - ✅ Token refreshed successfully, expires in 300 seconds
```

Or during long test runs:

```
INFO - Token expired or expiring soon, auto-refreshing...
INFO - Refreshing OAuth2 token from https://us-resident-auth.d05d0001.entratadev.com/oauth2/token
INFO - ✅ Token refreshed successfully, expires in 300 seconds
```

---

## 📊 Auto-Refresh Logic

```
Before Each Request:
  ├─ Check: bearer_token empty?
  │   └─ YES → Refresh token immediately
  │   └─ NO → Continue to expiry check
  │
  ├─ Check: token_expires_at <= current_time?
  │   └─ YES → Refresh token (expired or < 60s left)
  │   └─ NO → Token is fresh, use it
  │
  └─ Add Authorization: Bearer {token} header
```

---

## 🔧 Refresh Buffer

**60-second buffer:** Token refreshes when < 60 seconds remaining

**Why?**
- Prevents mid-request expiration
- Ensures all API calls have valid token
- Handles network delays gracefully

**Example:**
```
Token obtained: 10:00:00 (expires in 300s)
Token expires at: 10:05:00
Auto-refresh at: 10:04:00 (60s before expiry)
```

---

## 💡 Benefits

### ✅ No Manual Token Updates
- No more copying tokens from Postman
- No more "Unauthorized" errors mid-testing
- No more expired token interruptions

### ✅ Seamless Long Test Runs
- Run 100+ tests without interruption
- Token refreshes automatically between tests
- No manual intervention needed

### ✅ Development Productivity
- Focus on testing, not token management
- Run tests anytime, tokens always fresh
- Perfect for CI/CD pipelines

---

## 🐛 Troubleshooting

### Issue: "OAuth2 not enabled" in logs

**Cause:** `oauth2.enabled` is `false` in config

**Fix:**
```json
{
  "oauth2": {
    "enabled": true  ← Must be true
  }
}
```

---

### Issue: "Missing OAuth2 configuration" error

**Cause:** Missing client_id or client_secret

**Fix:**
```json
{
  "oauth2": {
    "token_url": "https://...",
    "client_id": "5s2fglraslk1j418gtefpqpv28",  ← Required
    "client_secret": "1eomncrl4lam7t98uabmt4lt6gsrq01dg6oti7vail191sttquf"  ← Required
  }
}
```

---

### Issue: "Token refresh failed: 401" error

**Cause:** Wrong client_id or client_secret

**Fix:**
1. Verify credentials in Postman "AuthToken" request
2. Copy exact client_id and client_secret
3. Update `auth_config.json`
4. Restart container

---

### Issue: Token not refreshing

**Check container logs:**
```powershell
wsl docker-compose -f docker-compose.dev.yml logs --tail=100 | findstr "refresh"
```

Look for:
- "Refreshing OAuth2 token" → Working
- "OAuth2 is not enabled" → Enable it
- "Missing OAuth2 configuration" → Add credentials
- "Token refresh failed" → Check credentials

---

## 🔍 Manual Token Refresh (Optional)

While auto-refresh handles everything, you can manually refresh if needed:

**Using curl:**
```powershell
curl -X POST https://us-resident-auth.d05d0001.entratadev.com/oauth2/token `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -H "Accept: application/json" `
  -H "Authorization: Basic NXMyZmdscmFzbGsxajQxOGd0ZWZwcXB2Mjg6MWVvbW5jcmw0bGFtN3Q5OHVhYm10NGx0NmdzcnEwMWRnNm90aTd2YWlsMTkxc3R0cXVm" `
  -d "grant_type=client_credentials" `
  -d "scope=entrata.respay.external.api/..."
```

---

## 📈 Performance Impact

**Minimal:**
- Refresh only when needed (not every request)
- Takes ~200-500ms to refresh
- Happens in background before request
- Your API calls are unaffected

---

## 🎓 Technical Details

### Token Lifecycle:

```
1. First Request:
   - No token exists
   - ensure_valid_token() called
   - Detects empty bearer_token
   - Calls refresh_oauth2_token()
   - Gets fresh token (300s validity)
   - Stores in AUTH_CONFIG['auth']['bearer_token']
   - Stores expiry in AUTH_CONFIG['auth']['token_expires_at']

2. Subsequent Requests (< 4 minutes):
   - Token exists and is fresh
   - ensure_valid_token() returns True
   - Uses existing token

3. Request After 4+ Minutes:
   - is_token_expired() returns True (< 60s left)
   - ensure_valid_token() calls refresh_oauth2_token()
   - Gets new token
   - Updates AUTH_CONFIG
   - Continues with request

4. Process Repeats:
   - Token auto-refreshes every ~4 minutes during active use
   - No manual intervention ever needed
```

### Code Flow:

```python
# Before each API request:
def merge_headers(test_headers, use_bearer_token=True):
    if use_bearer_token:
        ensure_valid_token()  ← Auto-refresh happens here
        headers['Authorization'] = f'Bearer {AUTH_CONFIG["auth"]["bearer_token"]}'
    return headers
```

---

## ✅ Summary

**What You Have:**
- ✅ Automatic OAuth2 token refresh
- ✅ 60-second expiry buffer
- ✅ No manual token management
- ✅ Seamless long test runs
- ✅ Works in development & production

**What You Don't Need:**
- ❌ Manual token copying from Postman
- ❌ Token expiry tracking
- ❌ Test interruptions
- ❌ Frequent container restarts

**Your test runner is now fully automated! Just run tests and let the auto-refresh handle the rest.** 🎉

---

## 📝 Quick Reference

| Scenario | What Happens |
|----------|--------------|
| **First test run** | Auto-fetches token, runs test |
| **Token < 60s left** | Auto-refreshes, continues testing |
| **Token expired** | Auto-refreshes, retries request |
| **Long test suite** | Refreshes every ~4 minutes automatically |
| **Manual Postman test** | No conflict, each uses own token |
| **Development mode** | Hot-reload preserves config, tokens stay fresh |

---

**That's it! OAuth2 tokens now refresh automatically. No more manual updates!** 🚀


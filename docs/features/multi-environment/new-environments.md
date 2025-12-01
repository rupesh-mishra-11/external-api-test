# 🎉 NEW ENVIRONMENTS ADDED - 4 More Environments!

## ✅ What Was Added

Added **4 new environments** to your test runner dropdown:

1. **Capricorn Rapid Production** ⚡
2. **Capricorn Standard Production** 🏢
3. **Capricorn Rapid Stage** 🧪
4. **Capricorn Standard Stage** 🧪

**Total environments now: 6**

---

## 📊 Quick Comparison

| Environment | URL | API Key | Type |
|------------|-----|---------|------|
| **Trunk** | d05d0001.entratadev.com | cx6y1Q... | Dev |
| **Rapid Prod** | entrata.com | XiDfpN... | Prod |
| **Standard Prod** | entrata.com | XiDfpN... | Prod |
| **Rapid Stage** | s01a0001.entratastage.com | lgvHXC... | Stage |
| **Standard Stage** | s01a0001.entratastage.com | lgvHXC... | Stage |
| **External Local** | localhost:7080 | cx6y1Q... | Local |

---

## 📁 Files Created

### Test Case Files:
- ✅ `test_cases_rapid_prod.json` (5 tests)
- ✅ `test_cases_standard_prod.json` (5 tests)
- ✅ `test_cases_rapid_stage.json` (5 tests)
- ✅ `test_cases_standard_stage.json` (5 tests)

### Configuration Updates:
- ✅ `environments.json` - Added 4 new environment entries
- ✅ `Dockerfile` - Copies all test case files
- ✅ `docker-compose.dev.yml` - Volume mounts for hot-reload
- ✅ `START_HERE.md` - Updated with new environments
- ✅ `ENVIRONMENTS_GUIDE.md` - Complete environment documentation

---

## 🚀 How to Use

### Step 1: Restart Container
```powershell
wsl docker-compose -f docker-compose.dev.yml restart
```

### Step 2: Open Test Runner
```
http://localhost:5000/test-runner
```

### Step 3: Select Environment
Click the **Environment dropdown** (top-left):

```
Environment: [Capricorn API Trunk ▼]
             ├─ Capricorn API Trunk
             ├─ Capricorn Rapid Production  ← NEW!
             ├─ Capricorn Standard Production  ← NEW!
             ├─ Capricorn Rapid Stage  ← NEW!
             ├─ Capricorn Standard Stage  ← NEW!
             └─ External API Local
```

### Step 4: Run Tests
- Tests automatically load for selected environment
- OAuth2 token auto-refreshes
- All authentication handled automatically! ✨

---

## 🔐 Authentication (All Automated!)

**All environments use the same OAuth2 auto-refresh:**
```http
Authorization: Bearer {auto-refreshed-every-4-minutes}
x-api-key: {environment-specific-key}
x-client-type: mobile-android
```

**You don't need to do anything!** Each environment has its own API key embedded in its test cases.

---

## 🎯 Test Case Breakdown

### Trunk (Development):
- ✅ 22 comprehensive tests
- ✅ All endpoints covered
- ✅ Full test suite

### Production & Stage:
- ✅ 5 core tests each:
  1. Add Payment Account
  2. Get Payment Accounts
  3. Get Permissions
  4. Make Payment
  5. Get Payment Types

**Why fewer tests?** 
Production tests are focused on critical paths to minimize load on live systems.

---

## ⚠️ Production Testing Guidelines

### **Before Testing on Production:**

1. **Test on Stage first!**
   - Select Rapid Stage or Standard Stage
   - Run all tests
   - Verify everything works
   - Review results carefully

2. **Verify test data:**
   - Use test customer IDs
   - Don't use real user data
   - Check payment amounts (small values!)
   - Verify lease/property IDs are test accounts

3. **Run production tests:**
   - One test at a time initially
   - Review each response
   - Monitor for errors
   - Stop if anything looks wrong

### **Production Testing Checklist:**
- [ ] Tested successfully on Stage
- [ ] Using test customer data
- [ ] Small payment amounts (< $5)
- [ ] Reviewed test endpoints
- [ ] Ready to monitor results
- [ ] Know how to rollback if needed

---

## 🔄 Deployment Stages

### Typical Flow:
```
1. Local Development
   └─> External API Local

2. Dev Environment
   └─> Capricorn API Trunk

3. Stage Testing
   ├─> Capricorn Rapid Stage
   └─> Capricorn Standard Stage

4. Production Deployment
   ├─> Capricorn Rapid Production
   └─> Capricorn Standard Production
```

### Environment Progression:
```
Local → Trunk → Stage → Production
  ↓       ↓       ↓         ↓
Test   Integrate Verify  Validate
```

---

## 💡 Pro Tips

### Tip 1: Test Progression
Always follow this order:
1. Local (if available)
2. Trunk (dev)
3. Stage (pre-prod)
4. Production (live)

### Tip 2: Compare Environments
Run the same test across environments:
1. Run on Trunk
2. Switch to Rapid Stage
3. Run same test
4. Compare responses
5. Identify differences!

### Tip 3: Environment-Specific Issues
If a test fails only on specific environment:
1. Check API key is correct
2. Verify base URL
3. Check OAuth2 token refresh logs
4. Review test data validity

### Tip 4: Quick Switch
Use keyboard:
1. Click environment dropdown
2. Use arrow keys ↑↓
3. Press Enter
4. Tests reload automatically!

---

## 📚 Documentation

- **[ENVIRONMENTS_GUIDE.md](ENVIRONMENTS_GUIDE.md)** - This file (complete reference)
- **[AUTO_REFRESH_OAUTH2_GUIDE.md](AUTO_REFRESH_OAUTH2_GUIDE.md)** - OAuth2 auto-refresh
- **[AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md)** - Authentication details
- **[MULTI_ENVIRONMENT_GUIDE.md](MULTI_ENVIRONMENT_GUIDE.md)** - Original multi-env guide
- **[START_HERE.md](START_HERE.md)** - Quick start

---

## 🎓 Understanding Rapid vs Standard

### **Rapid Deployment:**
- Faster release cycles
- Latest features first
- More frequent updates
- Good for early adopters

### **Standard Deployment:**
- Stable, tested releases
- Fewer updates
- More conservative
- Good for mission-critical systems

**Both share:** Same API endpoints, same authentication, different deployment cadence.

---

## ✅ Summary

### **What You Have Now:**
- ✅ 6 environments (was 2)
- ✅ Production + Stage + Dev + Local
- ✅ OAuth2 auto-refresh for all
- ✅ Environment-specific API keys
- ✅ Instant switching via dropdown
- ✅ Hot-reload in development mode

### **What You Can Do:**
- 🔄 Test across all environments
- 🧪 Validate in Stage before Production
- 🚀 Run production smoke tests
- 💻 Develop locally
- 📊 Compare environment behaviors
- ⚡ Switch instantly without code changes

---

## 🚀 Get Started

```powershell
# Restart to load new environments
wsl docker-compose -f docker-compose.dev.yml restart

# Open test runner
http://localhost:5000/test-runner

# Select any of the 6 environments from dropdown
# Run tests - OAuth2 auto-refreshes, API keys auto-switch!
```

**You now have a complete multi-environment test suite with automated authentication!** 🎉

---

## 📞 Need Help?

**Environment not showing?**
- Check environments.json has all 6 entries
- Restart container
- Hard-refresh browser (Ctrl+Shift+R)

**Tests failing on specific environment?**
- Check API key in test case file
- Verify base URL is correct
- Check OAuth2 token refresh logs
- Review [ENVIRONMENTS_GUIDE.md](ENVIRONMENTS_GUIDE.md)

**Production concerns?**
- Always test on Stage first!
- Use test data only
- Monitor carefully
- Follow production guidelines above

---

**Happy testing across all 6 environments!** 🌐✨


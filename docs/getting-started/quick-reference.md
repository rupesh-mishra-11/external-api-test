# Quick Reference Card

## 🚀 Starting the Application

### Development Mode (Hot-Reload)
```bash
./dev.sh        # Linux/Mac/WSL
dev.bat         # Windows
```
✅ Changes reload automatically - NO rebuild needed!

### Production Mode
```bash
./prod.sh       # Linux/Mac/WSL
prod.bat        # Windows
```
⚠️ Requires rebuild after code changes

---

## 📊 Accessing the Application

| What | URL |
|------|-----|
| **Test Runner UI** | `http://localhost:5000/test-runner` |
| **Health Check** | `http://localhost:5000/health` |
| **API Endpoint** | `http://localhost:5000/api/*` |

---

## 🔧 Common Commands

### View Logs
```bash
# Development
docker-compose -f docker-compose.dev.yml logs -f

# Production
docker-compose logs -f
```

### Stop Server
```bash
# Development (if running in terminal)
Ctrl+C

# Development (if running in background)
docker-compose -f docker-compose.dev.yml down

# Production
docker-compose down
```

### Restart
```bash
# Development
docker-compose -f docker-compose.dev.yml restart

# Production
docker-compose restart
```

### Rebuild
```bash
# Development
wsl docker-compose -f docker-compose.dev.yml up --build

# Production
docker-compose up --build -d
```

---

## 📝 Making Changes

### Files That Auto-Reload (Dev Mode)
- `app.py` - Flask application
- `test_cases.json` - Test configurations
- `static/test-runner.html` - UI
- `gunicorn_config.py` - Server config

**Just save and refresh browser!** ⚡

### Files That Need Rebuild
- `requirements.txt` - Dependencies
- `Dockerfile` - Container config
- `docker-compose*.yml` - Compose files

**Run rebuild command after changes** 🔄

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Changes not showing | Hard refresh: `Ctrl+Shift+R` |
| Port 5000 in use | Stop other containers: `docker ps` |
| Container won't start | Check logs: `docker-compose logs` |
| 404 Not Found | Rebuild: `docker-compose up --build` |

---

## 📚 Documentation

- **Full Development Guide**: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
- **Test Runner Guide**: [TEST_RUNNER_GUIDE.md](TEST_RUNNER_GUIDE.md)
- **Main README**: [README.md](README.md)

---

## ⚡ Quick Test

1. Start: `./dev.sh`
2. Open: `http://localhost:5000/test-runner`
3. Click: **"Run All Tests"**
4. Watch: Real-time results! 🎉

---

## 💡 Pro Tips

- Use **dev mode** while coding
- Use **prod mode** before deploying
- Check logs when debugging
- Hard refresh browser after changes
- Keep test data in `test_cases.json`
- **Use input fields** for dynamic test parameters (no JSON editing needed!)
- **Download receipts** directly from test results (PDF/ZIP)
- **Auto Payment dates** are calculated automatically - no manual date entry

## 🆕 Recent Features

- **Dynamic Input Fields**: Test-specific inputs appear automatically
- **PDF/ZIP Download**: One-click download for receipt files
- **Smart Dates**: Auto Payment dates calculated automatically
- **Category Sorting**: Tests organized by category with headers

**That's it! Happy testing!** 🚀


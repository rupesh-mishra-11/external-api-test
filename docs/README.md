# 📚 Documentation

Welcome to the External API Tester documentation! This guide will help you get started and make the most of all features.

---

## 🚀 Quick Navigation

### **Getting Started**
- **[Start Here](getting-started/README.md)** - Your first stop! Quick start guide
- **[Quick Reference](getting-started/quick-reference.md)** - Common commands and shortcuts

### **Setup & Configuration**
- **[Environment Variables Setup](setup/environment-variables/README.md)** - Configure OAuth2 credentials
- **[Authentication Setup](setup/authentication/README.md)** - OAuth2 and API key configuration
- **[Environment Variables Migration](setup/environment-variables/migration-summary.md)** - Migrating from hardcoded to env vars

### **Features**
- **[Multi-Environment Testing](features/multi-environment/README.md)** - Test across 6 environments
- **[Test Runner](features/test-runner/README.md)** - Web-based test execution
- **[OAuth2 Auto-Refresh](setup/authentication/oauth2-auto-refresh.md)** - Automatic token management

### **Development**
- **[Development Guide](development/README.md)** - Hot-reload, debugging, and local development

### **Troubleshooting**
- **[Network Issues](troubleshooting/network.md)** - Resolve hostname and connection problems

### **Release Notes**
- **[What's New](releases/whats-new.md)** - Latest features and updates

---

## 📋 Documentation Structure

```
docs/
├── getting-started/          # Quick start guides
├── setup/                    # Configuration guides
│   ├── authentication/       # OAuth2 and API keys
│   └── environment-variables/# Environment variable setup
├── features/                 # Feature documentation
│   ├── multi-environment/    # Multi-environment testing
│   └── test-runner/          # Test runner UI
├── development/              # Development guides
├── troubleshooting/          # Problem solving
└── releases/                 # Release notes
```

---

## 🎯 Recommended Reading Path

### **First Time Setup** (10 minutes)
1. [Start Here](getting-started/README.md) - Overview and quick start
2. [Environment Variables Setup](setup/environment-variables/README.md) - Configure credentials
3. [Test Runner](features/test-runner/README.md) - Run your first test

### **Understanding Features** (20 minutes)
4. [Multi-Environment Guide](features/multi-environment/README.md) - Learn about all 6 environments
5. [OAuth2 Auto-Refresh](setup/authentication/oauth2-auto-refresh.md) - How tokens auto-refresh
6. [Authentication Setup](setup/authentication/README.md) - Complete auth guide

### **Development** (15 minutes)
7. [Development Guide](development/README.md) - Hot-reload and debugging
8. [Quick Reference](getting-started/quick-reference.md) - Bookmark this!

### **Troubleshooting** (As needed)
9. [Network Issues](troubleshooting/network.md) - When things don't connect
10. [Environment Variables Troubleshooting](setup/environment-variables/README.md#troubleshooting) - Auth issues

---

## 🔍 Finding What You Need

### **I want to...**

| Goal | Documentation |
|------|---------------|
| **Get started quickly** | [Start Here](getting-started/README.md) |
| **Set up OAuth2 credentials** | [Environment Variables Setup](setup/environment-variables/README.md) |
| **Run my first test** | [Test Runner](features/test-runner/README.md) |
| **Switch between environments** | [Multi-Environment Guide](features/multi-environment/README.md) |
| **Enable hot-reload for development** | [Development Guide](development/README.md) |
| **Fix connection errors** | [Network Troubleshooting](troubleshooting/network.md) |
| **Understand OAuth2 auto-refresh** | [OAuth2 Auto-Refresh](setup/authentication/oauth2-auto-refresh.md) |
| **See what's new** | [What's New](releases/whats-new.md) |
| **Quick command reference** | [Quick Reference](getting-started/quick-reference.md) |

---

## 💡 Key Features

### ✅ **Multi-Environment Testing**
Test across 6 different environments with a single click:
- Capricorn API Trunk (Dev)
- Capricorn Rapid Production
- Capricorn Standard Production
- Capricorn Rapid Stage
- Capricorn Standard Stage
- External API Local

**[Learn More →](features/multi-environment/README.md)**

### ✅ **OAuth2 Auto-Refresh**
Tokens refresh automatically before expiration. No manual updates needed!

**[Learn More →](setup/authentication/oauth2-auto-refresh.md)**

### ✅ **Environment Variables**
All credentials loaded from `.env` file. Secure, flexible, industry-standard.

**[Learn More →](setup/environment-variables/README.md)**

### ✅ **Web Test Runner**
Beautiful UI to execute and monitor API tests in real-time.

**[Learn More →](features/test-runner/README.md)**

### ✅ **Hot-Reload Development**
Code changes reflect instantly without rebuilding the Docker image.

**[Learn More →](development/README.md)**

---

## 🚀 Quick Start

```powershell
# 1. Setup OAuth2 credentials (30 seconds)
setup.bat

# 2. Start application (2 minutes)
wsl docker-compose -f docker-compose.dev.yml up --build

# 3. Open test runner
http://localhost:5000/test-runner

# 4. Select environment and run tests!
```

**[Full setup guide →](getting-started/README.md)**

---

## 📖 Additional Resources

- **[Main README](../README.md)** - Project overview
- **[Environment Variables Example](../env.example)** - OAuth2 credentials template
- **[Postman Collections](../)** - Original API collections

---

## 🤝 Contributing to Documentation

Found an issue or want to improve the docs? Great!

1. Documentation files are in `docs/` folder
2. Use clear headings and code examples
3. Keep explanations concise
4. Test all commands before documenting

---

## 📝 Documentation Conventions

### **File Naming**
- Use lowercase with hyphens: `oauth2-auto-refresh.md`
- README.md for main file in each directory
- Descriptive names: `network.md` not `troubleshooting.md`

### **Structure**
- Start with overview/purpose
- Include table of contents for long docs
- Use code blocks with language tags
- Add emojis for visual navigation (sparingly)

### **Code Examples**
```powershell
# Always include working examples
wsl docker-compose -f docker-compose.dev.yml up --build
```

### **Cross-References**
Use relative paths: `[OAuth2 Guide](../setup/authentication/oauth2-auto-refresh.md)`

---

**Happy testing! 🎉**

If you have questions or need help, check the [Troubleshooting](troubleshooting/network.md) section or review the [Quick Reference](getting-started/quick-reference.md).


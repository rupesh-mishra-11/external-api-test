# External API Tester

A comprehensive Flask-based application for testing external APIs with multi-environment support, OAuth2 auto-refresh, production safety validation, and beautiful web-based test runner.

## ✨ Features

### 🎯 **Web-Based Test Runner**
- Beautiful, modern UI to execute API tests from Postman collections
- Real-time test execution with live status updates
- Category filtering and sorting (Payment, Settings, Auto Payment, etc.)
- Color-coded environment indicators (🟢 Dev/Stage, 🔴 Production)
- Detailed request/response viewer
- Summary dashboard with pass/fail rates
- **Dynamic Input Fields** - Custom input fields for specific test cases:
  - Delete Payment Account: Comma-separated payment account IDs
  - Delete Auto Payment: Comma-separated scheduled payment IDs
  - Add Auto Payment: Payment account ID, payment type ID with automatic date calculation
  - Make Payment: Customer payment account ID and payment type ID
  - Cancel Payment: Payment IDs (supports both singular and plural)
  - Get Payment Receipt: Payment IDs as string
  - Get Payment Status: Payment ID
- **PDF/ZIP Download** - Automatic download button for binary receipt responses
- **Smart Date Calculation** - Auto Payment dates automatically calculated (start_date, end_date, bimonthly schedules)

### 🌍 **Multi-Environment Support**
Test across **6 different environments** with a single click:
- **Capricorn API Trunk** (Development) - 🟢 Green
- **Capricorn Rapid Production** - 🔴 Red
- **Capricorn Standard Production** - 🔴 Red
- **Capricorn Rapid Stage** - 🟢 Green
- **Capricorn Standard Stage** - 🟢 Green
- **External API Local** - 🟢 Green

### 🔐 **OAuth2 Auto-Refresh**
- Automatic token refresh before expiration
- Environment-specific OAuth2 credentials
- Seamless token management (no manual updates needed)
- Supports Client Credentials flow

### 🛡️ **Production Safety**
- CID validation for production environments
- Only allows test account CIDs (4547, 1995) in production
- Prevents accidental testing with real customer data
- Visual warnings with red indicators

### 📊 **CSV Report Export**
- Download comprehensive test reports
- Includes API Name, Environment, Status Code, Request, Response
- No data truncation (unlimited cell size)
- Professional formatting with summary statistics
- Filename: `Environment - dd-mm-yyyy HH:MM:SS.csv`

### 🚀 **Development & Production Modes**
- **Development Mode**: Hot-reload, debug mode, live logs
- **Production Mode**: Optimized with Gunicorn
- Docker and Docker Compose support
- Kubernetes manifests included

### 🔧 **RESTful API Testing**
- Test GET, POST, PUT, DELETE requests
- Support for Bearer tokens and API keys
- Batch testing capabilities
- Health check endpoints

## 🚀 Quick Start

### **First Time Setup** (2 minutes)

**1. Clone the repository:**
```bash
git clone https://github.com/rupesh-mishra-11/external-api-test.git
cd external-api-test
```

**2. Setup OAuth2 credentials:**

**Linux/Mac/WSL:**
```bash
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

This creates a `.env` file from `env.example` with all OAuth2 credentials for 6 environments.

**3. Edit `.env` file** (if needed):
```bash
# Update with your actual OAuth2 credentials
# Each environment has: TOKEN_URL, CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, API_KEY
```

**4. Start the application:**

**Development Mode (Hot-Reload):**
```bash
# Linux/Mac/WSL
./dev.sh

# Windows
dev.bat
```

**Production Mode:**
```bash
# Linux/Mac/WSL
./prod.sh

# Windows
prod.bat
```

**5. Open Test Runner:**
```
http://localhost:5000/test-runner
```

---

## 📖 Detailed Setup

### **Environment Variables**

All OAuth2 credentials and API keys are loaded from `.env` file. See `env.example` for the complete template.

**Required Variables per Environment:**
- `{ENV}_TOKEN_URL` - OAuth2 token endpoint
- `{ENV}_CLIENT_ID` - OAuth2 client ID
- `{ENV}_CLIENT_SECRET` - OAuth2 client secret
- `{ENV}_OAUTH_SCOPE` - OAuth2 permissions
- `{ENV}_API_KEY` - API Gateway key

**Example:**
```bash
TRUNK_TOKEN_URL=https://us-resident-auth.d05d0001.entratadev.com/oauth2/token
TRUNK_CLIENT_ID=your_client_id
TRUNK_CLIENT_SECRET=your_client_secret
TRUNK_OAUTH_SCOPE=entrata.respay.external.api/read.payment_types...
TRUNK_API_KEY=your_api_key
```

**Environments:**
- `TRUNK_*` - Capricorn API Trunk
- `RAPID_PROD_*` - Rapid Production
- `STANDARD_PROD_*` - Standard Production
- `RAPID_STAGE_*` - Rapid Stage
- `STANDARD_STAGE_*` - Standard Stage
- `EXTERNAL_LOCAL_*` - External Local

### **Development Mode** ⚡

For active development with instant code reload:

```bash
# Linux/Mac/WSL
./dev.sh

# Windows
dev.bat
```

**Features:**
- ✅ Hot-reload on code changes (no rebuild needed!)
- ✅ Debug mode enabled
- ✅ Live logs
- ✅ Volume mounts for instant updates
- ✅ Auto-restart on file changes

**Manual:**
```bash
docker-compose -f docker-compose.dev.yml up --build
```

### **Production Mode** 🚀

For production deployment:

```bash
# Linux/Mac/WSL
./prod.sh

# Windows
prod.bat
```

**Manual:**
```bash
docker-compose up -d --build
```

---

## 🎨 Web Test Runner

### **Access the Test Runner**

1. Start the application (see Quick Start above)
2. Open browser: `http://localhost:5000/test-runner`

### **Features**

- ✅ **Environment Dropdown** - Switch between 6 environments
- ✅ **Color-Coded UI** - Green for dev/stage, Red for production
- ✅ **Run Individual Tests** - Execute tests one-by-one
- ✅ **Run All Tests** - Batch execution
- ✅ **Category Filters & Sorting** - Filter and sort by Payment, Settings, Auto Payment, etc.
- ✅ **Real-time Results** - Watch tests execute with live updates
- ✅ **Detailed Response Viewer** - Inspect full request/response data
- ✅ **Summary Dashboard** - Pass/fail rates, response times, blocked count
- ✅ **CSV Export** - Download comprehensive test reports
- ✅ **Production Safety** - CID validation prevents accidents
- ✅ **Dynamic Input Fields** - Test-specific input fields for IDs and parameters
- ✅ **PDF/ZIP Download** - Automatic download button for receipt files
- ✅ **Smart Date Calculation** - Automatic date calculation for auto payment schedules

### **Quick Test**

1. Navigate to `http://localhost:5000/test-runner`
2. Select environment from dropdown
3. Click "▶ Run All Tests" to execute all test cases
4. View results in real-time with color-coded status indicators
5. Click "Show Details" on any test to see full request/response data
6. Click "📥 Download" to export CSV report

### **Test Categories**

- **Payment** - Payment processing APIs (Make Payment, Cancel Payment, Get Payment Receipt, etc.)
- **Payment Account** - Account management (Add/Delete Payment Account, Get Payment Accounts)
- **Auto Payment** - Automated payment settings (Add/Delete Auto Payment, Get Auto Payments)
- **Settings** - Configuration and permissions (Get Permissions, Get Payment Settings)
- **Moneygram** - Moneygram integration

### **Dynamic Input Fields**

The test runner automatically shows input fields for specific test cases:

- **Delete Payment Account**: Enter comma-separated payment account IDs (e.g., `1334083, 1334084`)
- **Delete Auto Payment**: Enter comma-separated scheduled payment IDs (e.g., `263866, 263867`)
- **Add Auto Payment**: 
  - Payment Account ID and Payment Type ID
  - Dates automatically calculated (start_date = first day of next month, end_date = first day two months later)
  - For Bimonthly: first payment on 1st, second payment on 15th
  - Each scenario increments start_date by one day
- **Make Payment**: Customer Payment Account ID and Payment Type ID
- **Cancel Payment**: Payment IDs (comma-separated, supports both `payment_id` and `payment_ids` in request)
- **Get Payment Receipt**: Payment IDs as string (triggers download button for PDF/ZIP responses)
- **Get Payment Status**: Payment ID

### **Receipt Download**

When "Get Payment Receipt" or "Download Receipt" tests return successful binary responses (PDF or ZIP):
- ✅ Automatic download button appears
- ✅ Button shows file type (PDF or ZIP)
- ✅ Click to download the file
- ✅ File named: `payment_receipt_[timestamp].[pdf|zip]`

---

## 🔐 Authentication

### **OAuth2 Auto-Refresh**

The application automatically refreshes OAuth2 tokens before expiration:

- ✅ Tokens refresh 30 seconds before expiration
- ✅ Environment-specific token management
- ✅ Seamless operation (no manual intervention)
- ✅ Client Credentials flow supported

**Configuration:**
All OAuth2 settings come from `.env` file (see Environment Variables section).

### **API Keys**

API keys are loaded from environment variables and automatically injected into requests:

- ✅ Environment-specific API keys
- ✅ Secure storage (not in Git)
- ✅ Automatic header injection

### **Production CID Validation**

Production environments (Rapid Prod, Standard Prod) have safety validation:

- ✅ Only CID `4547` or `1995` allowed
- ✅ Blocks unauthorized CIDs automatically
- ✅ Visual warnings (🔴 BLOCKED status)
- ✅ Prevents accidental testing with real customer data

---

## 📊 CSV Report Export

### **Download Test Reports**

1. Run some tests
2. Click "📥 Download" button
3. CSV file downloads automatically

### **Report Contents**

**Header Section:**
- Report title
- Environment name
- Generation timestamp
- Summary statistics (Total, Passed, Failed, Blocked, Avg Response Time)

**Test Data:**
- API Name
- Environment
- Status Code (HTTP code or "BLOCKED")
- Response Time
- Result (✅ PASSED, ❌ FAILED, 🔴 BLOCKED)
- Request (Full JSON)
- Response (Full JSON)

**Filename Format:**
```
Environment - dd-mm-yyyy HH:MM:SS.csv
```

**Example:**
```
Capricorn API Trunk - 27-11-2025 14:35:42.csv
```

---

## 🐳 Docker

### **Docker Compose Files**

- `docker-compose.yml` - Production configuration
- `docker-compose.dev.yml` - Development configuration (hot-reload)

### **Docker Commands**

**Build:**
```bash
docker-compose build
```

**Run:**
```bash
# Development
docker-compose -f docker-compose.dev.yml up

# Production
docker-compose up -d
```

**Logs:**
```bash
docker-compose logs -f
```

**Stop:**
```bash
docker-compose down
```

---

## ☸️ Kubernetes

### **Deploy to Kubernetes**

1. **Update ConfigMap:**
```bash
kubectl apply -f kubernetes/configmap.yaml
```

2. **Build and push Docker image:**
```bash
docker build -t external-api-tester:latest .
docker tag external-api-tester:latest your-registry/external-api-tester:latest
docker push your-registry/external-api-tester:latest
```

3. **Deploy:**
```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/ingress.yaml  # Optional
```

4. **Check status:**
```bash
kubectl get pods -l app=external-api-tester
kubectl get svc external-api-tester-service
```

---

## 📡 API Endpoints

### **Health Check**
```bash
GET /health
```

### **Get Environments**
```bash
GET /api/environments
```

### **Get Test Cases**
```bash
GET /api/test-cases?environment={env_id}
```

### **Run Single Test**
```bash
POST /api/run-test/{test_id}
Content-Type: application/json

{
  "environment": "capricorn-trunk"
}
```

### **Run All Tests**
```bash
POST /api/run-all-tests
Content-Type: application/json

{
  "environment": "capricorn-trunk"
}
```

### **Test GET Request**
```bash
POST /api/test/get
Content-Type: application/json

{
  "endpoint": "/users",
  "headers": {"Authorization": "Bearer token"},
  "params": {"page": 1, "limit": 10}
}
```

### **Test POST Request**
```bash
POST /api/test/post
Content-Type: application/json

{
  "endpoint": "/users",
  "headers": {"Content-Type": "application/json"},
  "json": {"name": "John", "email": "john@example.com"}
}
```

### **Test PUT Request**
```bash
POST /api/test/put
Content-Type: application/json

{
  "endpoint": "/users/123",
  "headers": {"Content-Type": "application/json"},
  "json": {"name": "Jane", "email": "jane@example.com"}
}
```

### **Test DELETE Request**
```bash
POST /api/test/delete
Content-Type: application/json

{
  "endpoint": "/users/123",
  "headers": {"Authorization": "Bearer token"}
}
```

---

## 📁 Project Structure

```
external-api-tester/
├── app.py                      # Main Flask application
├── gunicorn_config.py          # Gunicorn server configuration
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Production Docker config
├── docker-compose.dev.yml      # Development Docker config
├── environments.json           # Environment definitions (6 environments)
├── env.example                 # OAuth2 credentials template
├── .gitignore                  # Git ignore patterns
│
├── testCases/                  # Test case files (from Postman collections)
│   ├── test_cases.json         # External API Local
│   ├── test_cases_capricorn.json
│   ├── test_cases_rapid_prod.json
│   ├── test_cases_standard_prod.json
│   ├── test_cases_rapid_stage.json
│   └── test_cases_standard_stage.json
│
├── static/                     # Frontend files
│   └── test-runner.html        # Web test runner UI
│
├── docs/                       # Comprehensive documentation
│   ├── README.md               # Documentation hub
│   ├── getting-started/        # Quick start guides
│   ├── setup/                  # Configuration guides
│   │   ├── authentication/     # OAuth2 setup
│   │   └── environment-variables/
│   ├── features/               # Feature documentation
│   │   ├── multi-environment/
│   │   └── test-runner/
│   ├── development/            # Development guides
│   ├── troubleshooting/        # Problem solving
│   └── releases/               # Release notes
│
├── kubernetes/                 # Kubernetes manifests
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
│
└── Scripts                     # Helper scripts
    ├── dev.sh / dev.bat        # Start development mode
    ├── prod.sh / prod.bat      # Start production mode
    └── setup.sh / setup.bat    # Initial .env setup
```

---

## 🔧 Configuration

### **Environment Variables**

**Application:**
- `FLASK_ENV` - Flask environment (development/production)
- `PORT` - Application port (default: 5000)
- `GUNICORN_LOG_LEVEL` - Log level (default: info)

**OAuth2 (per environment):**
- `{ENV}_TOKEN_URL` - OAuth2 token endpoint
- `{ENV}_CLIENT_ID` - OAuth2 client ID
- `{ENV}_CLIENT_SECRET` - OAuth2 client secret
- `{ENV}_OAUTH_SCOPE` - OAuth2 permissions
- `{ENV}_API_KEY` - API Gateway key

**Global:**
- `GLOBAL_X_CLIENT_TYPE` - Global custom header (optional)

### **Environments Configuration**

Edit `environments.json` to add/modify environments:

```json
{
  "environments": [
    {
      "id": "environment-id",
      "name": "Environment Name",
      "base_url": "https://api.example.com",
      "test_cases_file": "testCases/test_cases.json",
      "description": "Environment description"
    }
  ],
  "default_environment": "environment-id"
}
```

---

## 🧪 Testing Examples

### **Example: Run Tests via Web UI**

1. Start application: `./dev.sh`
2. Open: `http://localhost:5000/test-runner`
3. Select environment
4. Click "▶ Run All Tests"
5. View results in real-time

### **Example: Test via API**

```bash
# Run single test
curl -X POST http://localhost:5000/api/run-test/test_1 \
  -H "Content-Type: application/json" \
  -d '{"environment": "capricorn-trunk"}'

# Run all tests
curl -X POST http://localhost:5000/api/run-all-tests \
  -H "Content-Type: application/json" \
  -d '{"environment": "rapid-prod"}'
```

---

## 📚 Documentation

Comprehensive documentation is available in the `docs/` folder:

- **[📖 Documentation Hub](docs/README.md)** - Complete documentation index
- **[🚀 Getting Started](docs/getting-started/README.md)** - Quick start guide
- **[🔐 Authentication Setup](docs/setup/authentication/README.md)** - OAuth2 configuration
- **[🌍 Multi-Environment Guide](docs/features/multi-environment/README.md)** - All 6 environments
- **[🎨 Test Runner Guide](docs/features/test-runner/README.md)** - Web UI usage
- **[⚡ Development Guide](docs/development/README.md)** - Hot-reload and debugging
- **[🛠️ Troubleshooting](docs/troubleshooting/network.md)** - Common issues

---

## 🛡️ Security

### **Credentials Management**

- ✅ All credentials in `.env` file (gitignored)
- ✅ No hardcoded secrets in code
- ✅ Environment-specific credentials
- ✅ Industry-standard 12-factor app principles

### **Production Safety**

- ✅ CID validation for production environments
- ✅ Only test account CIDs allowed (4547, 1995)
- ✅ Visual warnings (red indicators)
- ✅ Automatic blocking of unauthorized requests

---

## 🚀 Development

### **Local Development (without Docker)**

1. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set environment variables:**
```bash
export FLASK_ENV=development
# Add OAuth2 credentials to .env or export them
```

4. **Run application:**
```bash
python app.py
```

### **Hot-Reload Development (Recommended)**

Use Docker Compose with volume mounts:

```bash
./dev.sh  # or dev.bat on Windows
```

Code changes reflect instantly without rebuilding!

---

## 📋 Requirements

- Python 3.8+
- Docker & Docker Compose
- (Optional) Kubernetes cluster

**Python Dependencies:**
- Flask 3.0.0
- flask-cors 4.0.0
- requests 2.31.0
- gunicorn 21.2.0

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📝 License

MIT

---

## 🎉 Features Summary

| Feature | Status | Description |
|---------|--------|-------------|
| **Web Test Runner** | ✅ | Beautiful UI for test execution |
| **Multi-Environment** | ✅ | 6 environments (Dev, Stage, Prod) |
| **OAuth2 Auto-Refresh** | ✅ | Automatic token management |
| **Production Safety** | ✅ | CID validation for production |
| **CSV Export** | ✅ | Comprehensive test reports |
| **Hot-Reload Dev** | ✅ | Instant code updates |
| **Docker Support** | ✅ | Containerized deployment |
| **Kubernetes Ready** | ✅ | Full K8s manifests |
| **Category Filtering** | ✅ | Filter tests by category |
| **Real-time Results** | ✅ | Live status updates |

---

**Happy Testing! 🚀**

For questions or issues, check the [Documentation](docs/README.md) or [Troubleshooting](docs/troubleshooting/network.md) guides.

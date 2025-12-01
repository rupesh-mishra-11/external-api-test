# External API Tester

A Flask-based application for testing external API scenarios with Docker and Kubernetes support.

## Features

- **🎯 Web-Based Test Runner**: Beautiful UI to execute API tests from Postman collections
- **RESTful API Testing**: Test GET, POST, PUT, DELETE requests
- **Authentication Testing**: Support for Bearer tokens and Basic auth
- **Batch Testing**: Run multiple test scenarios in a single request
- **Docker Support**: Containerized application with docker-compose
- **Kubernetes Ready**: Full K8s manifests for deployment
- **Health Checks**: Built-in health monitoring
- **Configurable**: Runtime configuration updates
- **Real-time Results**: View test execution results in real-time with detailed response data

## Quick Start

### Development Mode (Hot-Reload) ⚡

For active development with instant code reload:

**Linux/Mac/WSL:**
```bash
./dev.sh
```

**Windows:**
```cmd
dev.bat
```

**Features:**
- ✅ Hot-reload on code changes (no rebuild needed!)
- ✅ Debug mode enabled
- ✅ Live logs
- ✅ Volume mounts for instant updates

### Production Mode 🚀

For production deployment:

**Linux/Mac/WSL:**
```bash
./prod.sh
```

**Windows:**
```cmd
prod.bat
```

**Or manually:**
1. Set environment variables (optional):
```bash
export API_BASE_URL=https://api.example.com
export API_TIMEOUT=30
export MAX_RETRIES=3
```

2. Build and run:
```bash
docker-compose up -d
```

3. Access the API:
```bash
curl http://localhost:5000/health
```

> 💡 **Pro Tip:** Use development mode while coding, production mode for final testing. See [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) for details.

## 🚀 Web Test Runner

A beautiful, modern web interface to execute and monitor all API tests from your Postman collection.

### Access the Test Runner

1. Start the application (Docker or locally)
2. Open your browser to: `http://localhost:5000/test-runner`

### Features

- ✅ **23 Pre-configured Tests**: All Postman collection APIs ready to test
- ✅ **Run Individual or All Tests**: Execute tests one-by-one or in batch
- ✅ **Real-time Results**: Watch tests execute with live status updates
- ✅ **Category Filtering**: Filter by Payment, Payment Account, Auto Payment, Settings, etc.
- ✅ **Detailed Response Viewer**: Inspect full request/response data
- ✅ **Summary Dashboard**: View pass/fail rates and response times

### Quick Test

1. Navigate to `http://localhost:5000/test-runner`
2. Click "▶ Run All Tests" to execute all 23 test cases
3. View results in real-time with color-coded status indicators
4. Click "Show Details" on any test to see full request/response data

For detailed usage instructions, see [TEST_RUNNER_GUIDE.md](TEST_RUNNER_GUIDE.md).

### Using Kubernetes

1. Update the ConfigMap with your API base URL:
```bash
kubectl apply -f kubernetes/configmap.yaml
```

2. Build and push Docker image (adjust registry as needed):
```bash
docker build -t external-api-tester:latest .
docker tag external-api-tester:latest your-registry/external-api-tester:latest
docker push your-registry/external-api-tester:latest
```

3. Deploy to Kubernetes:
```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/ingress.yaml  # Optional
```

4. Check deployment status:
```bash
kubectl get pods -l app=external-api-tester
kubectl get svc external-api-tester-service
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Test GET Request
```bash
POST /api/test/get
Content-Type: application/json

{
  "endpoint": "/users",
  "headers": {"Authorization": "Bearer token"},
  "params": {"page": 1, "limit": 10}
}
```

### Test POST Request
```bash
POST /api/test/post
Content-Type: application/json

{
  "endpoint": "/users",
  "headers": {"Content-Type": "application/json"},
  "json": {"name": "John", "email": "john@example.com"}
}
```

### Test PUT Request
```bash
POST /api/test/put
Content-Type: application/json

{
  "endpoint": "/users/123",
  "headers": {"Content-Type": "application/json"},
  "json": {"name": "Jane", "email": "jane@example.com"}
}
```

### Test DELETE Request
```bash
POST /api/test/delete
Content-Type: application/json

{
  "endpoint": "/users/123",
  "headers": {"Authorization": "Bearer token"}
}
```

### Test Authentication
```bash
POST /api/test/auth
Content-Type: application/json

{
  "endpoint": "/protected",
  "auth_type": "bearer",
  "token": "your-token-here"
}
```

### Run Multiple Scenarios
```bash
POST /api/test/scenarios
Content-Type: application/json

{
  "scenarios": [
    {
      "name": "Get Users",
      "type": "get",
      "endpoint": "/users",
      "headers": {},
      "params": {"page": 1}
    },
    {
      "name": "Create User",
      "type": "post",
      "endpoint": "/users",
      "headers": {"Content-Type": "application/json"},
      "json": {"name": "Test User"}
    }
  ]
}
```

### Get Configuration
```bash
GET /api/config
```

### Update Configuration
```bash
PUT /api/config
Content-Type: application/json

{
  "api_base_url": "https://new-api.example.com",
  "api_timeout": 60,
  "max_retries": 5
}
```

## Configuration

### Environment Variables

- `API_BASE_URL`: Base URL of the API to test (default: https://api.example.com)
- `API_TIMEOUT`: Request timeout in seconds (default: 30)
- `MAX_RETRIES`: Maximum retry attempts (default: 3)
- `FLASK_ENV`: Flask environment (development/production)
- `PORT`: Application port (default: 5000)

### Kubernetes ConfigMap

Update `kubernetes/configmap.yaml` to set default values for all pods.

## Development

### Local Development

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run application:
```bash
export API_BASE_URL=https://api.example.com
python app.py
```

## Testing Examples

### Example: Test a REST API

```bash
# Test GET endpoint
curl -X POST http://localhost:5000/api/test/get \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/users", "params": {"page": 1}}'

# Test POST with authentication
curl -X POST http://localhost:5000/api/test/post \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "/users",
    "headers": {"Authorization": "Bearer your-token"},
    "json": {"name": "John Doe", "email": "john@example.com"}
  }'
```

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose configuration
├── .dockerignore         # Docker ignore patterns
├── .gitignore           # Git ignore patterns
├── kubernetes/          # Kubernetes manifests
│   ├── deployment.yaml  # Deployment configuration
│   ├── service.yaml     # Service configuration
│   ├── configmap.yaml   # ConfigMap for settings
│   └── ingress.yaml     # Ingress configuration
└── README.md            # This file
```

## License

MIT


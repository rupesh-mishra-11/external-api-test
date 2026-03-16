# External API Tester - Features Summary

## Overview
A Flask-based web application for automated API testing with multi-environment support, OAuth2 auto-refresh, and production safety validation.

## Core Features

### 1. Web-Based Test Runner
Modern browser interface for executing API tests without command-line knowledge. Features include:
- Real-time test execution with live status updates
- Category filtering and sorting (Payment, Settings, Auto Payment, Moneygram)
- Color-coded environment indicators (🟢 Dev/Stage, 🔴 Production)
- Detailed request/response viewer with expandable sections
- Summary dashboard showing pass/fail rates, response times, and blocked count

### 2. Multi-Environment Support
Test across 6 distinct environments from a single interface:
- Capricorn API Trunk (Development)
- Capricorn Rapid Production
- Capricorn Standard Production
- Capricorn Rapid Stage
- Capricorn Standard Stage
- External API Local

Each environment has isolated OAuth2 credentials and API configurations.

### 3. OAuth2 Auto-Refresh
Automatic token management eliminates manual refresh cycles:
- Tokens refresh 30 seconds before expiration
- Environment-specific token caching
- Seamless operation with zero manual intervention
- Supports Client Credentials flow

### 4. Production Safety Validation
Built-in safeguards prevent production incidents:
- CID validation for production environments
- Only allows test account CIDs (4547, 1995) in production
- Automatic blocking of unauthorized requests
- Visual warnings with red indicators for production environments

### 5. Dynamic Input Fields
Test-specific input fields for various scenarios:
- **Delete Payment Account**: Comma-separated payment account IDs
- **Delete Auto Payment**: Comma-separated scheduled payment IDs
- **Add Auto Payment**: Payment account ID, payment type ID with automatic date calculation (start_date, end_date, bimonthly schedules)
- **Make Payment**: Customer payment account ID and payment type ID
- **Cancel Payment**: Payment IDs (supports both singular and plural)
- **Get Payment Receipt**: Payment IDs as string
- **Get Payment Status**: Payment ID

### 6. Smart Date Calculation
Automatic date calculation for auto payment schedules:
- Start date: First day of next month
- End date: First day two months later
- Bimonthly: First payment on 1st, second payment on 15th
- Each scenario increments start_date by one day

### 7. Binary File Handling
Automatic handling of PDF/ZIP receipt responses:
- Smart detection of binary responses
- Automatic download button appears for PDF/ZIP files
- Files named: `payment_receipt_[timestamp].[pdf|zip]`
- One-click download functionality

### 8. CSV Report Export
Comprehensive test reports with full audit trails:
- Download button generates timestamped CSV files
- Includes API Name, Environment, Status Code, Response Time, Result
- Full request and response JSON (no data truncation)
- Summary statistics: Total, Passed, Failed, Blocked, Average Response Time
- Filename format: `Environment - dd-mm-yyyy HH:MM:SS.csv`

### 9. RESTful API Testing
Support for all HTTP methods:
- GET, POST, PUT, DELETE requests
- Bearer token and API key authentication
- Batch testing capabilities
- Health check endpoints

### 10. Development & Production Modes
Flexible deployment options:
- **Development Mode**: Hot-reload, debug mode, live logs, volume mounts
- **Production Mode**: Gunicorn server, optimized performance
- Docker and Docker Compose support
- Kubernetes manifests included

### 11. Test Case Management
JSON-based test cases imported from Postman collections:
- Environment-specific test case files
- Easy to update and maintain
- Supports complex request scenarios
- Category-based organization

### 12. Real-Time Monitoring
Live execution monitoring:
- Watch tests execute in real-time
- Color-coded status indicators (✅ PASSED, ❌ FAILED, 🔴 BLOCKED)
- Response time tracking
- Immediate error visibility

---

**Total Word Count: 499 words**

# API Test Runner Guide

## Overview

This test runner provides a beautiful web UI to execute and monitor API tests from your Postman collection. All 23 test cases have been parsed and configured for easy execution.

## Features

- ✅ **Run Individual Tests**: Execute any test case individually
- ✅ **Run All Tests**: Execute all test cases in sequence
- ✅ **Real-time Results**: See test results update in real-time
- ✅ **Detailed Response Viewer**: View full request/response data
- ✅ **Category Filtering**: Filter tests by category (Payment, Payment Account, Auto Payment, Settings, etc.)
- ✅ **Summary Dashboard**: View pass/fail statistics and average response times
- ✅ **Beautiful Modern UI**: Gradient design with smooth animations

## How to Use

### 1. Start the Application

```bash
# Using Docker Compose
docker-compose up -d

# Or run directly
python app.py
```

### 2. Access the Test Runner

Open your browser and navigate to:
```
http://localhost:5000/test-runner
```

### 3. Run Tests

**Run All Tests:**
- Click the "▶ Run All Tests" button in the top controls
- Watch as all 23 test cases execute sequentially
- View real-time results as each test completes

**Run Individual Test:**
- Scroll to find the specific test you want to run
- Click the "▶ Run Test" button on that test card
- View results immediately

**Filter Tests:**
- Use the filter buttons (All, Payment, Payment Account, Auto Payment, Settings)
- Only tests in the selected category will be displayed

**View Details:**
- Click "Show Details" on any test card
- See the full request payload
- View the complete response data

### 4. Interpret Results

**Test Card Colors:**
- **Purple left border**: Test ready to run
- **Orange left border** (pulsing): Test currently running
- **Green left border**: Test passed successfully
- **Red left border**: Test failed

**Status Indicators:**
- ✅ **Passed**: HTTP status 2xx, shows response time
- ❌ **Failed**: HTTP status outside 2xx or error occurred

**Summary Cards:**
- **Total Tests**: Number of test cases loaded
- **Passed**: Count of successful tests
- **Failed**: Count of failed tests
- **Avg Response Time**: Average response time across all executed tests

## Test Categories

### Payment (7 tests)
- Make Payment
- Get Balance
- Download Receipt
- Get Repayment Details
- Get Payment History
- Cancel Payment
- Get Payment Status

### Payment Account (5 tests)
- Add Refund Account
- Delete Refund Account
- Add Payment Account
- Get Payment Accounts
- Add Refund Account (ACH)

### Auto Payment (4 tests)
- Approve Split Payment
- Delete Auto Payment
- Get Auto Payments
- Add Auto Payment

### Settings (3 tests)
- Get Permissions
- Get Payment Settings
- Get Auto Payment Settings
- Get Payment Account Settings

### MoneyGram (2 tests)
- Get MoneyGram Account
- MoneyGram - Get Account Details

### Resident (1 test)
- Get Resident Detail

## Configuration

### Base URL
Edit `test_cases.json` to change the base URL:
```json
{
  "base_url": "https://us-residentpay-external.d05d0001.entratadev.com",
  ...
}
```

### Test Data
Each test case includes:
- Endpoint URL
- HTTP method
- Headers
- Request body
- Category

You can modify test data in `test_cases.json`.

## API Endpoints

The test runner exposes these backend endpoints:

- `GET /test-runner` - Serves the UI
- `GET /api/test-cases` - Returns all test cases
- `POST /api/run-test/<test_id>` - Run a single test
- `POST /api/run-all-tests` - Run all tests

## Troubleshooting

**Tests are failing:**
- Verify the base URL is correct and accessible
- Check that the external API is running
- Review the error message in the test card details

**UI not loading:**
- Ensure Flask is running
- Check that `static/test-runner.html` exists
- Verify no firewall is blocking port 5000

**Slow response times:**
- Check network connectivity
- Verify the external API server performance
- Consider increasing timeout in `app.py` (API_TIMEOUT variable)

## Tips

1. **Use filters** to focus on specific test categories
2. **Clear results** before running a new test suite
3. **Show details** to debug failed tests
4. **Monitor avg response time** to track API performance
5. **Run individual tests** during development, **run all tests** for regression

---

Enjoy testing! 🚀


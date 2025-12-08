# API Test Runner Guide

## Overview

This test runner provides a beautiful web UI to execute and monitor API tests from your Postman collection. All 23 test cases have been parsed and configured for easy execution.

## Features

- ✅ **Run Individual Tests**: Execute any test case individually
- ✅ **Run All Tests**: Execute all test cases in sequence
- ✅ **Real-time Results**: See test results update in real-time
- ✅ **Detailed Response Viewer**: View full request/response data
- ✅ **Category Filtering & Sorting**: Filter and sort tests by category (Payment, Payment Account, Auto Payment, Settings, etc.)
- ✅ **Summary Dashboard**: View pass/fail statistics and average response times
- ✅ **Beautiful Modern UI**: Gradient design with smooth animations
- ✅ **Dynamic Input Fields**: Test-specific input fields appear automatically
- ✅ **PDF/ZIP Download**: Automatic download button for receipt files
- ✅ **Smart Date Calculation**: Automatic date calculation for auto payment schedules

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

**Use Input Fields:**
- Input fields appear automatically for specific test cases
- Enter values before clicking "Run Test"
- Leave empty to use default values from test case
- See "Dynamic Input Fields" section below for details

**Download Receipts:**
- After running "Get Payment Receipt" or "Download Receipt"
- If response is successful and contains PDF/ZIP, a download button appears
- Click the button to download the file

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

## Dynamic Input Fields

The test runner automatically displays input fields for specific test cases. These fields allow you to customize test parameters without editing JSON files.

### Delete Payment Account
**Input Field**: Payment Account IDs (comma-separated)
- **Example**: `1334083, 1334084, 1334085`
- **Behavior**: Makes separate API calls for each ID
- **Usage**: Enter IDs separated by commas, or leave empty to use default from test case

### Delete Auto Payment
**Input Field**: Scheduled Payment IDs (comma-separated)
- **Example**: `263866, 263867, 263868`
- **Behavior**: Makes separate API calls for each ID
- **Usage**: Enter IDs separated by commas, or leave empty to use default from test case

### Add Auto Payment
**Input Fields**: 
- Payment Account ID (e.g., `1329007`)
- Payment Type ID (e.g., `4`)

**Automatic Date Calculation**:
- `start_date`: First day of next month (e.g., if today is Jan 15, start_date = Feb 1)
- `end_date`: First day two months after start_date (e.g., if start_date = Feb 1, end_date = Apr 1)
- **Bimonthly schedules**:
  - `first_payment.start_date`: 1st of the month
  - `second_payment.start_date`: 15th of the month
- **Multiple scenarios**: Each scenario increments start_date by one day

**Example**:
- Scenario 1: start_date = Feb 1
- Scenario 2: start_date = Feb 2
- Scenario 3: start_date = Feb 3

### Make Payment
**Input Fields**:
- Customer Payment Account ID (e.g., `1329007`)
- Payment Type ID (e.g., `4`)

### Cancel Payment
**Input Field**: Payment IDs (comma-separated)
- **Example**: `1575716428, 1575716429`
- **Behavior**: Supports both `payment_id` (singular) and `payment_ids` (plural/array) in request body
- **Usage**: Enter IDs separated by commas

### Get Payment Receipt
**Input Field**: Payment IDs (as string)
- **Example**: `1575716428,1575716429`
- **Behavior**: 
  - Sends `payment_ids` as string in request body
  - If response is successful and contains PDF/ZIP, shows download button
- **Download**: Click the download button to save PDF or ZIP file

### Get Payment Status
**Input Field**: Payment ID
- **Example**: `1575716428`
- **Usage**: Enter single payment ID

## Receipt Download Feature

When running "Get Payment Receipt" or "Download Receipt" tests:

1. **Successful Response**: If the API returns a successful response with binary data (PDF or ZIP)
2. **Download Button**: A download button automatically appears in the test results
3. **File Type**: Button shows "📥 Download PDF" or "📥 Download ZIP" based on content type
4. **Download**: Click the button to download the file
5. **File Name**: Files are named `payment_receipt_[timestamp].[pdf|zip]`

**Supported Formats**:
- PDF (`application/pdf`)
- ZIP (`application/zip`)
- Binary (`application/octet-stream`)

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


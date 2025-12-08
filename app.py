"""
Flask application for testing external API scenarios.
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
import base64
from calendar import monthrange

# Configure logging
# Only use basicConfig when NOT running under Gunicorn
# Gunicorn has its own logging setup and basicConfig conflicts with it
if not os.getenv('gunicorn'):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

# Get logger - will use Gunicorn's logger if available
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# When running under Gunicorn, configure to use its logger
if __name__ != '__main__':
    # Running under WSGI server (like Gunicorn)
    gunicorn_logger = logging.getLogger('gunicorn.error')
    logger.handlers = gunicorn_logger.handlers
    logger.setLevel(gunicorn_logger.level)
    # Also set Flask's logger to use Gunicorn's configuration
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'https://us-residentpay-external.d05d0001.entratadev.com')
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '1'))

# Environment ID to environment variable prefix mapping
ENV_VAR_MAPPING = {
    'capricorn-trunk': 'TRUNK',
    'rapid-prod': 'RAPID_PROD',
    'standard-prod': 'STANDARD_PROD',
    'rapid-stage': 'RAPID_STAGE',
    'standard-stage': 'STANDARD_STAGE',
    'external-local': 'EXTERNAL_LOCAL'
}

def load_auth_config():
    """Load authentication configuration from environment variables."""
    config = {
        'environments': {},
        'global': {
            'custom_headers': {
                'x-client-type': 'mobile-android'
            }
        }
    }
    
    # Build config from environment variables for each environment
    for env_id, env_prefix in ENV_VAR_MAPPING.items():
        token_url = os.getenv(f'{env_prefix}_TOKEN_URL')
        client_id = os.getenv(f'{env_prefix}_CLIENT_ID')
        client_secret = os.getenv(f'{env_prefix}_CLIENT_SECRET')
        scope = os.getenv(f'{env_prefix}_OAUTH_SCOPE', '')
        api_key = os.getenv(f'{env_prefix}_API_KEY')
        
        if token_url and client_id and client_secret:
            config['environments'][env_id] = {
                'oauth2': {
                    'enabled': True,
                    'token_url': token_url,
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'grant_type': 'client_credentials',
                    'scope': scope
                },
                'api_key': api_key or '',
                'bearer_token': '',
                'token_expires_at': 0
            }
            logger.info(f'✅ Loaded OAuth2 config for {env_id} from environment variables')
            if api_key:
                logger.info(f'✅ Loaded API key for {env_id} from environment variables')
        else:
            logger.warning(f'⚠️  Missing OAuth2 env vars for {env_id} ({env_prefix}_*)')
    
    return config

AUTH_CONFIG = load_auth_config()


def refresh_oauth2_token(environment_id: str = 'capricorn-trunk'):
    """Refresh OAuth2 token using client credentials for specific environment."""
    global AUTH_CONFIG
    
    try:
        # Get environment-specific OAuth2 config
        env_config = AUTH_CONFIG.get('environments', {}).get(environment_id, {})
        oauth2_config = env_config.get('oauth2', {})
        
        if not oauth2_config.get('enabled'):
            logger.debug(f'OAuth2 is not enabled for {environment_id}')
            return {'error': f'OAuth2 not enabled for {environment_id}', 'success': False}
        
        token_url = oauth2_config.get('token_url')
        client_id = oauth2_config.get('client_id')
        client_secret = oauth2_config.get('client_secret')
        scope = oauth2_config.get('scope')
        grant_type = oauth2_config.get('grant_type', 'client_credentials')
        
        if not all([token_url, client_id, client_secret]):
            logger.error('Missing OAuth2 configuration')
            return {'error': 'Missing OAuth2 configuration', 'success': False}
        
        # Prepare request
        import base64
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': f'Basic {encoded_credentials}'
        }
        
        data = {
            'grant_type': grant_type
        }
        
        if scope:
            data['scope'] = scope
        
        logger.info(f'Refreshing OAuth2 token from {token_url}')
        
        response = requests.post(
            token_url,
            headers=headers,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 300)  # Default 5 minutes
            
            # Calculate expiry time (subtract 60 seconds buffer for auto-refresh)
            import time
            expires_at = int(time.time()) + expires_in - 60
            
            # Update AUTH_CONFIG (in-memory) for this environment
            if 'environments' not in AUTH_CONFIG:
                AUTH_CONFIG['environments'] = {}
            if environment_id not in AUTH_CONFIG['environments']:
                AUTH_CONFIG['environments'][environment_id] = {}
            
            AUTH_CONFIG['environments'][environment_id]['bearer_token'] = access_token
            AUTH_CONFIG['environments'][environment_id]['token_expires_at'] = expires_at
            
            logger.info(f'✅ Token refreshed successfully, expires in {expires_in} seconds')
            
            return {
                'success': True,
                'access_token': access_token,
                'expires_in': expires_in,
                'expires_at': expires_at,
                'message': 'Token refreshed successfully'
            }
        else:
            error_msg = f'Token refresh failed: {response.status_code} - {response.text}'
            logger.error(error_msg)
            return {'error': error_msg, 'success': False}
            
    except Exception as e:
        error_msg = f'Error refreshing token: {str(e)}'
        logger.error(error_msg)
        return {'error': error_msg, 'success': False}


def is_token_expired(environment_id: str = 'capricorn-trunk'):
    """Check if the current token is expired or will expire soon for specific environment."""
    import time
    env_config = AUTH_CONFIG.get('environments', {}).get(environment_id, {})
    expires_at = env_config.get('token_expires_at', 0)
    current_time = int(time.time())
    
    # Token is expired or will expire in next 60 seconds
    return expires_at <= current_time


def ensure_valid_token(environment_id: str = 'capricorn-trunk'):
    """Ensure we have a valid token for specific environment, refresh if necessary."""
    env_config = AUTH_CONFIG.get('environments', {}).get(environment_id, {})
    oauth2_config = env_config.get('oauth2', {})
    
    if not oauth2_config.get('enabled'):
        return True  # OAuth2 not enabled for this environment
    
    # Check if token exists
    bearer_token = env_config.get('bearer_token', '')
    if not bearer_token:
        logger.info(f'No token found for {environment_id}, refreshing...')
        result = refresh_oauth2_token(environment_id)
        return result.get('success', False)
    
    # Check if token is expired
    if is_token_expired(environment_id):
        logger.info(f'Token expired or expiring soon for {environment_id}, auto-refreshing...')
        result = refresh_oauth2_token(environment_id)
        return result.get('success', False)
    
    return True


def validate_production_cid(request_body: Dict[str, Any], environment_id: str) -> tuple[bool, str]:
    """
    Validate that production environments only use allowed CID values.
    
    Args:
        request_body: The request body containing potential CID
        environment_id: The environment identifier
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Define production environments
    PRODUCTION_ENVIRONMENTS = ['rapid-prod', 'standard-prod']
    ALLOWED_PRODUCTION_CIDS = [4547, 1995]
    
    # Only validate for production environments
    if environment_id not in PRODUCTION_ENVIRONMENTS:
        return True, ''
    
    # Check if request body contains 'cid'
    if 'cid' not in request_body:
        return False, f'🔴 PRODUCTION SAFETY: CID is required for production environment ({environment_id})'
    
    cid = request_body.get('cid')
    
    # Validate CID is in allowed list
    try:
        cid_int = int(cid)
        if cid_int not in ALLOWED_PRODUCTION_CIDS:
            return False, f'🔴 PRODUCTION SAFETY: CID {cid} is not allowed in production. Only CID 4547 or 1995 are permitted.'
    except (ValueError, TypeError):
        return False, f'🔴 PRODUCTION SAFETY: Invalid CID format: {cid}'
    
    # Validation passed
    logger.info(f'✅ Production CID validation passed: CID {cid} for environment {environment_id}')
    return True, ''


def merge_headers(test_headers: Dict[str, str], use_bearer_token: bool = False, environment_id: str = 'capricorn-trunk') -> Dict[str, str]:
    """Merge test headers with global auth headers."""
    headers = dict(test_headers or {})
    
    # Get environment-specific config
    env_config = AUTH_CONFIG.get('environments', {}).get(environment_id, {})
    
    # Add Bearer token only if explicitly requested
    if use_bearer_token:
        # Ensure token is valid for this environment (auto-refresh if needed)
        ensure_valid_token(environment_id)
        
        # Get bearer token from environment-specific config
        bearer_token = env_config.get('bearer_token', '')
        if bearer_token and 'Authorization' not in headers:
            headers['Authorization'] = f'Bearer {bearer_token}'
    
    # Add environment-specific API key (ALWAYS override hardcoded values)
    api_key = env_config.get('api_key')
    if api_key:
        headers['x-api-key'] = api_key
        logger.debug(f'Using API key from environment config for {environment_id}')
    
    # Add global custom headers (but don't override already set headers)
    global_custom_headers = AUTH_CONFIG.get('global', {}).get('custom_headers', {})
    if global_custom_headers:
        for key, value in global_custom_headers.items():
            if key not in headers and value and not value.startswith('PASTE_'):
                headers[key] = value
    
    return headers


class APITester:
    """Handles API testing scenarios."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def test_get_request(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Test GET request scenario."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.get(
                url,
                headers=headers or {},
                params=params or {},
                timeout=self.timeout
            )
            
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'success': 200 <= response.status_code < 300
            }
        except requests.exceptions.Timeout:
            return {'error': 'Request timeout', 'success': False}
        except requests.exceptions.ConnectionError:
            return {'error': 'Connection error', 'success': False}
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def test_post_request(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Test POST request scenario."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            if json_data:
                response = self.session.post(
                    url,
                    json=json_data,
                    headers=headers or {},
                    timeout=self.timeout
                )
            else:
                response = self.session.post(
                    url,
                    data=data or {},
                    headers=headers or {},
                    timeout=self.timeout
                )
            
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'success': 200 <= response.status_code < 300
            }
        except requests.exceptions.Timeout:
            return {'error': 'Request timeout', 'success': False}
        except requests.exceptions.ConnectionError:
            return {'error': 'Connection error', 'success': False}
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def test_put_request(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Test PUT request scenario."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            if json_data:
                response = self.session.put(
                    url,
                    json=json_data,
                    headers=headers or {},
                    timeout=self.timeout
                )
            else:
                response = self.session.put(
                    url,
                    data=data or {},
                    headers=headers or {},
                    timeout=self.timeout
                )
            
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'success': 200 <= response.status_code < 300
            }
        except requests.exceptions.Timeout:
            return {'error': 'Request timeout', 'success': False}
        except requests.exceptions.ConnectionError:
            return {'error': 'Connection error', 'success': False}
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def test_delete_request(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Test DELETE request scenario."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.delete(
                url,
                headers=headers or {},
                timeout=self.timeout
            )
            
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'success': 200 <= response.status_code < 300
            }
        except requests.exceptions.Timeout:
            return {'error': 'Request timeout', 'success': False}
        except requests.exceptions.ConnectionError:
            return {'error': 'Connection error', 'success': False}
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def test_authentication(
        self,
        endpoint: str,
        auth_type: str = 'bearer',
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """Test authentication scenarios."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {}
        
        try:
            if auth_type.lower() == 'bearer' and token:
                headers['Authorization'] = f'Bearer {token}'
            elif auth_type.lower() == 'basic' and username and password:
                from requests.auth import HTTPBasicAuth
                auth = HTTPBasicAuth(username, password)
            else:
                auth = None
            
            response = self.session.get(
                url,
                headers=headers,
                auth=auth if 'auth' in locals() else None,
                timeout=self.timeout
            )
            
            return {
                'status_code': response.status_code,
                'authenticated': response.status_code != 401,
                'headers': dict(response.headers),
                'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'success': response.status_code != 401
            }
        except Exception as e:
            return {'error': str(e), 'success': False, 'authenticated': False}


# Initialize API tester
api_tester = APITester(API_BASE_URL, API_TIMEOUT)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'external-api-tester'
    }), 200


@app.route('/api/test/get', methods=['POST'])
def test_get():
    """Test GET request scenario."""
    data = request.get_json() or {}
    endpoint = data.get('endpoint', '')
    headers = data.get('headers', {})
    params = data.get('params', {})
    
    if not endpoint:
        return jsonify({'error': 'endpoint is required'}), 400
    
    result = api_tester.test_get_request(endpoint, headers, params)
    return jsonify(result), 200 if result.get('success') else 500


@app.route('/api/test/post', methods=['POST'])
def test_post():
    """Test POST request scenario."""
    data = request.get_json() or {}
    endpoint = data.get('endpoint', '')
    headers = data.get('headers', {})
    json_data = data.get('json', None)
    form_data = data.get('data', None)
    
    if not endpoint:
        return jsonify({'error': 'endpoint is required'}), 400
    
    result = api_tester.test_post_request(endpoint, form_data, headers, json_data)
    return jsonify(result), 200 if result.get('success') else 500


@app.route('/api/test/put', methods=['POST'])
def test_put():
    """Test PUT request scenario."""
    data = request.get_json() or {}
    endpoint = data.get('endpoint', '')
    headers = data.get('headers', {})
    json_data = data.get('json', None)
    form_data = data.get('data', None)
    
    if not endpoint:
        return jsonify({'error': 'endpoint is required'}), 400
    
    result = api_tester.test_put_request(endpoint, form_data, headers, json_data)
    return jsonify(result), 200 if result.get('success') else 500


@app.route('/api/test/delete', methods=['POST'])
def test_delete():
    """Test DELETE request scenario."""
    data = request.get_json() or {}
    endpoint = data.get('endpoint', '')
    headers = data.get('headers', {})
    
    if not endpoint:
        return jsonify({'error': 'endpoint is required'}), 400
    
    result = api_tester.test_delete_request(endpoint, headers)
    return jsonify(result), 200 if result.get('success') else 500


@app.route('/api/test/auth', methods=['POST'])
def test_auth():
    """Test authentication scenario."""
    data = request.get_json() or {}
    endpoint = data.get('endpoint', '')
    auth_type = data.get('auth_type', 'bearer')
    token = data.get('token')
    username = data.get('username')
    password = data.get('password')
    
    if not endpoint:
        return jsonify({'error': 'endpoint is required'}), 400
    
    result = api_tester.test_authentication(endpoint, auth_type, token, username, password)
    return jsonify(result), 200


@app.route('/api/test/scenarios', methods=['POST'])
def test_scenarios():
    """Run multiple test scenarios."""
    data = request.get_json() or {}
    scenarios = data.get('scenarios', [])
    
    if not scenarios:
        return jsonify({'error': 'scenarios array is required'}), 400
    
    results = []
    for scenario in scenarios:
        test_type = scenario.get('type', '').lower()
        endpoint = scenario.get('endpoint', '')
        
        if not endpoint:
            results.append({'error': 'endpoint is required', 'scenario': scenario})
            continue
        
        if test_type == 'get':
            result = api_tester.test_get_request(
                endpoint,
                scenario.get('headers', {}),
                scenario.get('params', {})
            )
        elif test_type == 'post':
            result = api_tester.test_post_request(
                endpoint,
                scenario.get('data'),
                scenario.get('headers', {}),
                scenario.get('json')
            )
        elif test_type == 'put':
            result = api_tester.test_put_request(
                endpoint,
                scenario.get('data'),
                scenario.get('headers', {}),
                scenario.get('json')
            )
        elif test_type == 'delete':
            result = api_tester.test_delete_request(
                endpoint,
                scenario.get('headers', {})
            )
        else:
            result = {'error': f'Unknown test type: {test_type}'}
        
        results.append({
            'scenario': scenario.get('name', 'unnamed'),
            'result': result
        })
    
    return jsonify({'results': results}), 200


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration."""
    return jsonify({
        'api_base_url': API_BASE_URL,
        'api_timeout': API_TIMEOUT,
        'max_retries': MAX_RETRIES
    }), 200


@app.route('/api/config', methods=['PUT'])
def update_config():
    """Update configuration (runtime only, not persisted)."""
    global API_BASE_URL, API_TIMEOUT, MAX_RETRIES
    
    data = request.get_json() or {}
    
    if 'api_base_url' in data:
        API_BASE_URL = data['api_base_url']
        api_tester.base_url = API_BASE_URL.rstrip('/')
    
    if 'api_timeout' in data:
        API_TIMEOUT = int(data['api_timeout'])
        api_tester.timeout = API_TIMEOUT
    
    if 'max_retries' in data:
        MAX_RETRIES = int(data['max_retries'])
    
    return jsonify({
        'message': 'Configuration updated',
        'config': {
            'api_base_url': API_BASE_URL,
            'api_timeout': API_TIMEOUT,
            'max_retries': MAX_RETRIES
        }
    }), 200


@app.route('/test-runner', methods=['GET'])
def test_runner_ui():
    """Serve the test runner UI."""
    return send_from_directory('static', 'test-runner.html')


@app.route('/api/debug/headers', methods=['POST'])
def debug_headers():
    """Debug endpoint to see what headers would be sent for a test."""
    try:
        data = request.get_json() or {}
        test_headers = data.get('headers', {})
        
        merged = merge_headers(test_headers)
        
        # Mask sensitive data
        safe_headers = {}
        for k, v in merged.items():
            if k.lower() in ['authorization', 'x-api-key']:
                safe_headers[k] = v[:30] + '...' if len(v) > 30 else v
            else:
                safe_headers[k] = v
        
        return jsonify({
            'original_headers': test_headers,
            'merged_headers': safe_headers,
            'oauth2_enabled': AUTH_CONFIG.get('oauth2', {}).get('enabled', False),
            'has_bearer_token': len(AUTH_CONFIG.get('auth', {}).get('bearer_token', '')) > 0,
            'custom_headers_config': AUTH_CONFIG.get('auth', {}).get('custom_headers', {})
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/environments', methods=['GET'])
def get_environments():
    """Get all available environments."""
    try:
        with open('environments.json', 'r') as f:
            environments = json.load(f)
        return jsonify(environments), 200
    except Exception as e:
        logger.error(f'Error loading environments: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/test-cases', methods=['GET'])
def get_test_cases():
    """Get all available test cases for the specified environment."""
    try:
        env_id = request.args.get('environment', 'capricorn-trunk')
        
        # Load environments config
        with open('environments.json', 'r') as f:
            env_config = json.load(f)
        
        # Find the environment
        env = next((e for e in env_config['environments'] if e['id'] == env_id), None)
        if not env:
            return jsonify({'error': f'Environment {env_id} not found'}), 404
        
        # Load test cases for this environment
        test_cases_file = env['test_cases_file']
        with open(test_cases_file, 'r') as f:
            test_cases = json.load(f)
        
        # Add environment info
        test_cases['environment'] = env
        
        return jsonify(test_cases), 200
    except Exception as e:
        logger.error(f'Error loading test cases: {e}')
        return jsonify({'error': str(e)}), 500


def calculate_auto_payment_dates(day_offset: int = 0) -> Dict[str, str]:
    """
    Calculate dates for auto payment:
    - start_date: First day of next month + day_offset days
    - end_date: Two months from start_date
    - For Bimonthly: first_payment on start_date, second_payment on start_date + 14 days
    Returns dates in YYYY-MM-DD format.
    
    Args:
        day_offset: Number of days to add to the base start_date (for incremental dates)
    """
    today = datetime.now()
    
    # Calculate base start date (first day of next month)
    if today.month == 12:
        base_start_date = today.replace(year=today.year + 1, month=1, day=1)
    else:
        base_start_date = today.replace(month=today.month + 1, day=1)
    
    # Add day offset for incremental dates
    start_date = base_start_date + timedelta(days=day_offset)
    
    # Calculate end_date: two months from start_date's month, always on the 1st
    # This ensures end_date is always the 1st of the month, regardless of start_date's day
    if start_date.month <= 10:
        end_date = start_date.replace(month=start_date.month + 2, day=1)
    elif start_date.month == 11:
        end_date = start_date.replace(year=start_date.year + 1, month=1, day=1)
    else:  # month == 12
        end_date = start_date.replace(year=start_date.year + 1, month=2, day=1)
    
    # For Bimonthly: first_payment on start_date, second_payment 14 days later
    # If start_date is 1st, second_payment should be 15th
    if start_date.day == 1:
        second_payment_date = start_date.replace(day=15)
    else:
        second_payment_date = start_date + timedelta(days=14)
    
    return {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'first_payment_start_date': start_date.strftime('%Y-%m-%d'),
        'second_payment_start_date': second_payment_date.strftime('%Y-%m-%d')
    }


def apply_auto_payment_config(request_body: Dict[str, Any], auto_payment_config: Dict[str, Any], day_offset: int = 0) -> Dict[str, Any]:
    """
    Apply auto payment configuration to request body:
    - Update payment_account_id and payment_type_id if provided
    - Always calculate and set dates (start_date, end_date) with incremental offset
    - For Bimonthly: set first_payment.start_date and second_payment.start_date
    
    Args:
        request_body: The request body to modify
        auto_payment_config: Configuration with payment_account_id and payment_type_id
        day_offset: Number of days to offset start_date (for incremental dates per scenario)
    """
    if not isinstance(request_body, dict):
        return request_body
    
    # Update payment_account_id and payment_type_id if provided
    if auto_payment_config and 'payment_account_id' in auto_payment_config:
        payment_account_id = auto_payment_config['payment_account_id']
        request_body['payment_account_id'] = int(payment_account_id) if str(payment_account_id).isdigit() else payment_account_id
    
    if auto_payment_config and 'payment_type_id' in auto_payment_config:
        payment_type_id = auto_payment_config['payment_type_id']
        request_body['payment_type_id'] = int(payment_type_id) if str(payment_type_id).isdigit() else payment_type_id
    
    # Always calculate dates (required for Add Auto Payment) with day offset
    dates = calculate_auto_payment_dates(day_offset=day_offset)
    
    # Update start_date and end_date
    request_body['start_date'] = dates['start_date']
    request_body['end_date'] = dates['end_date']
    
    # Handle Bimonthly case
    if 'bimonthly' in request_body and isinstance(request_body['bimonthly'], dict):
        if 'first_payment' in request_body['bimonthly']:
            if not isinstance(request_body['bimonthly']['first_payment'], dict):
                request_body['bimonthly']['first_payment'] = {}
            request_body['bimonthly']['first_payment']['start_date'] = dates['first_payment_start_date']
        
        if 'second_payment' in request_body['bimonthly']:
            if not isinstance(request_body['bimonthly']['second_payment'], dict):
                request_body['bimonthly']['second_payment'] = {}
            request_body['bimonthly']['second_payment']['start_date'] = dates['second_payment_start_date']
    
    return request_body


def apply_make_payment_config(request_body: Dict[str, Any], make_payment_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply make payment configuration to request body:
    - Update customer_payment_account_id and payment_type_id if provided
    
    Args:
        request_body: The request body to modify
        make_payment_config: Configuration with customer_payment_account_id and payment_type_id
    """
    if not isinstance(request_body, dict):
        return request_body
    
    # Update customer_payment_account_id if provided
    if make_payment_config and 'customer_payment_account_id' in make_payment_config:
        customer_payment_account_id = make_payment_config['customer_payment_account_id']
        # Keep as string if it's already a string, otherwise convert
        request_body['customer_payment_account_id'] = str(customer_payment_account_id)
    
    # Update payment_type_id if provided
    if make_payment_config and 'payment_type_id' in make_payment_config:
        payment_type_id = make_payment_config['payment_type_id']
        request_body['payment_type_id'] = int(payment_type_id) if str(payment_type_id).isdigit() else payment_type_id
    
    return request_body


def apply_cancel_payment_config(request_body: Dict[str, Any], cancel_payment_ids: str) -> Dict[str, Any]:
    """
    Apply cancel payment configuration to request body:
    - Update payment_ids or payment_id based on what's in the request body
    
    Args:
        request_body: The request body to modify
        cancel_payment_ids: Comma-separated payment IDs string
    """
    if not isinstance(request_body, dict) or not cancel_payment_ids:
        return request_body
    
    # Parse comma-separated IDs
    ids_list = [id_str.strip() for id_str in cancel_payment_ids.split(',') if id_str.strip()]
    
    if not ids_list:
        return request_body
    
    # Check if request body uses payment_id (singular) or payment_ids (plural)
    # If it has payment_id, use that; otherwise use payment_ids
    if 'payment_id' in request_body:
        # Use singular - take first ID only
        payment_id = ids_list[0]
        request_body['payment_id'] = int(payment_id) if payment_id.isdigit() else payment_id
    else:
        # Use plural - can be array or single value
        if len(ids_list) == 1:
            # Single ID - keep as single value (int or string)
            payment_id = ids_list[0]
            request_body['payment_ids'] = int(payment_id) if payment_id.isdigit() else payment_id
        else:
            # Multiple IDs - convert to array of ints/strings
            request_body['payment_ids'] = [
                int(payment_id) if payment_id.isdigit() else payment_id
                for payment_id in ids_list
            ]
    
    return request_body


def apply_receipt_payment_config(request_body: Dict[str, Any], receipt_payment_ids: str) -> Dict[str, Any]:
    """
    Apply receipt payment configuration to request body:
    - Update payment_ids as a string (for Get Payment Receipt)
    
    Args:
        request_body: The request body to modify
        receipt_payment_ids: Payment IDs as string
    """
    if not isinstance(request_body, dict) or not receipt_payment_ids:
        return request_body
    
    # Update payment_ids as a string (as required by the API)
    request_body['payment_ids'] = receipt_payment_ids.strip()
    
    return request_body


def apply_payment_status_config(request_body: Dict[str, Any], payment_status_id: str) -> Dict[str, Any]:
    """
    Apply payment status configuration to request body:
    - Update payment_id if provided
    
    Args:
        request_body: The request body to modify
        payment_status_id: Payment ID as string
    """
    if not isinstance(request_body, dict) or not payment_status_id:
        return request_body
    
    # Update payment_id (convert to int if numeric, otherwise keep as string)
    request_body['payment_id'] = int(payment_status_id) if payment_status_id.isdigit() else payment_status_id
    
    return request_body


def execute_single_request(
    test_case: Dict[str, Any],
    request_body: Dict[str, Any],
    base_url: str,
    env_id: str,
    scenario_name: Optional[str] = None
) -> Dict[str, Any]:
    """Execute a single HTTP request for a test case with a specific body."""
    url = f"{base_url}{test_case['endpoint']}"
    start_time = datetime.utcnow()
    
    try:
        # Merge test headers with global auth headers
        merged_headers = merge_headers(test_case.get('headers', {}), use_bearer_token=True, environment_id=env_id)
        
        # Log headers for debugging (remove sensitive data)
        safe_headers = {k: v[:20]+'...' if k.lower() in ['authorization', 'x-api-key'] and len(v) > 20 else v 
                      for k, v in merged_headers.items()}
        log_msg = f'Test {test_case["id"]} - {test_case["name"]}'
        if scenario_name:
            log_msg += f' - Scenario: {scenario_name}'
        logger.info(f'{log_msg} - Env: {env_id} - Headers: {safe_headers}')
        logger.info(f'Test {test_case["id"]} - URL: {url}')
        
        method = test_case['method'].upper()
        if method == 'GET':
            response = requests.get(
                url,
                headers=merged_headers,
                params=request_body,
                timeout=API_TIMEOUT
            )
        elif method == 'POST':
            response = requests.post(
                url,
                headers=merged_headers,
                json=request_body,
                timeout=API_TIMEOUT
            )
        elif method == 'PUT':
            response = requests.put(
                url,
                headers=merged_headers,
                json=request_body,
                timeout=API_TIMEOUT
            )
        else:
            return {
                'error': f'Unsupported method: {method}',
                'success': False
            }
        
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Check content type to handle binary responses (PDF, ZIP, etc.)
        content_type = response.headers.get('Content-Type', '').lower()
        is_binary = 'application/pdf' in content_type or 'application/zip' in content_type or 'application/octet-stream' in content_type
        
        try:
            if is_binary:
                # For binary responses, encode as base64 for JSON transport
                response_data = base64.b64encode(response.content).decode('utf-8')
                response_data_type = 'binary'
            else:
                # Try to parse as JSON, fallback to text
                try:
                    response_data = response.json()
                    response_data_type = 'json'
                except:
                    response_data = response.text
                    response_data_type = 'text'
        except Exception as e:
            response_data = str(e)
            response_data_type = 'error'
        
        return {
            'status_code': response.status_code,
            'success': 200 <= response.status_code < 300,
            'response_time_ms': round(duration_ms, 2),
            'response_data': response_data,
            'response_data_type': response_data_type,
            'content_type': content_type,
            'headers': dict(response.headers),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except requests.exceptions.Timeout:
        return {
            'error': 'Request timeout',
            'success': False,
            'timestamp': datetime.utcnow().isoformat()
        }
    except requests.exceptions.ConnectionError as e:
        return {
            'error': f'Connection error: {str(e)}',
            'success': False,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            'error': str(e),
            'success': False,
            'timestamp': datetime.utcnow().isoformat()
        }


@app.route('/api/run-test/<test_id>', methods=['POST'])
def run_single_test(test_id):
    """Run a single test case. Supports both single body and multiple bodies (bodies array)."""
    try:
        # Get environment from request
        data = request.get_json() or {}
        env_id = data.get('environment', 'capricorn-trunk')
        
        # Load environments config
        with open('environments.json', 'r') as f:
            env_config = json.load(f)
        
        # Find the environment
        env = next((e for e in env_config['environments'] if e['id'] == env_id), None)
        if not env:
            return jsonify({'error': f'Environment {env_id} not found'}), 404
        
        # Load test cases for this environment
        test_cases_file = env['test_cases_file']
        with open(test_cases_file, 'r') as f:
            test_data = json.load(f)
        
        test_case = next((tc for tc in test_data['test_cases'] if tc['id'] == test_id), None)
        if not test_case:
            return jsonify({'error': 'Test case not found'}), 404
        
        base_url = test_data['base_url']
        results = []
        
        # Check if test case has multiple bodies (bodies array)
        bodies = test_case.get('bodies', [])
        if bodies:
            # Multiple bodies - run each scenario
            for idx, body_config in enumerate(bodies):
                # Support both object with 'name' and 'body' or just direct body object
                if isinstance(body_config, dict):
                    if 'body' in body_config:
                        scenario_name = body_config.get('name', f'Scenario {idx + 1}')
                        request_body = body_config['body']
                    else:
                        # Direct body object
                        scenario_name = f'Scenario {idx + 1}'
                        request_body = body_config
                else:
                    # Invalid format
                    results.append({
                        'test_id': test_id,
                        'test_name': test_case['name'],
                        'scenario_name': f'Scenario {idx + 1}',
                        'error': 'Invalid body format in bodies array',
                        'success': False,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    continue
                
                # Apply auto payment config if provided (for Add Auto Payment)
                # Always apply dates for Add Auto Payment, even if config is empty
                # Use scenario index as day_offset for incremental dates
                auto_payment_config = data.get('auto_payment_config', {})
                is_add_auto_payment = 'add auto payment' in test_case.get('name', '').lower()
                if (auto_payment_config or is_add_auto_payment) and isinstance(request_body, dict):
                    request_body = request_body.copy()
                    apply_auto_payment_config(request_body, auto_payment_config, day_offset=idx)
                
                # Apply make payment config if provided (for Make Payment)
                make_payment_config = data.get('make_payment_config', {})
                if make_payment_config and isinstance(request_body, dict):
                    request_body = request_body.copy()
                    apply_make_payment_config(request_body, make_payment_config)
                
                # Apply cancel payment config if provided (for Cancel Payment)
                cancel_payment_ids = data.get('cancel_payment_ids', '')
                if cancel_payment_ids and isinstance(cancel_payment_ids, str) and cancel_payment_ids.strip() and isinstance(request_body, dict):
                    request_body = request_body.copy()
                    apply_cancel_payment_config(request_body, cancel_payment_ids)
                
                # Apply receipt payment config if provided (for Get Payment Receipt)
                receipt_payment_ids = data.get('receipt_payment_ids', '')
                if receipt_payment_ids and isinstance(receipt_payment_ids, str) and receipt_payment_ids.strip() and isinstance(request_body, dict):
                    request_body = request_body.copy()
                    apply_receipt_payment_config(request_body, receipt_payment_ids)
                
                # Apply payment status config if provided (for Get Payment Status)
                payment_status_id = data.get('payment_status_id', '')
                if payment_status_id and isinstance(payment_status_id, str) and payment_status_id.strip() and isinstance(request_body, dict):
                    request_body = request_body.copy()
                    apply_payment_status_config(request_body, payment_status_id)
                
                # Validate CID for production environments
                is_valid, error_message = validate_production_cid(request_body, env_id)
                if not is_valid:
                    logger.warning(f'🔴 Production CID validation failed for test {test_id}, scenario {scenario_name}: {error_message}')
                    results.append({
                        'test_id': test_id,
                        'test_name': test_case['name'],
                        'scenario_name': scenario_name,
                        'error': error_message,
                        'success': False,
                        'blocked': True,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    continue
                
                # Execute request
                result = execute_single_request(test_case, request_body, base_url, env_id, scenario_name)
                result['test_id'] = test_id
                result['test_name'] = test_case['name']
                result['scenario_name'] = scenario_name
                result['request_body'] = request_body
                results.append(result)
        else:
            # Single body - backward compatibility
            request_body = test_case.get('body', {})
            if not isinstance(request_body, dict):
                request_body = {}
            else:
                request_body = request_body.copy()
            
            # Check if payment_account_ids are provided in the request (for Delete Payment Account)
            payment_account_ids = data.get('payment_account_ids', '')
            if payment_account_ids and isinstance(payment_account_ids, str) and payment_account_ids.strip():
                # Parse comma-separated IDs
                ids_list = [id_str.strip() for id_str in payment_account_ids.split(',') if id_str.strip()]
                
                if ids_list:
                    # Make multiple API calls, one for each ID
                    for payment_account_id in ids_list:
                        # Create a copy of the request body with the specific payment_account_id
                        current_request_body = request_body.copy()
                        # Convert to int if it's a digit, otherwise keep as string
                        current_request_body['payment_account_id'] = int(payment_account_id) if payment_account_id.isdigit() else payment_account_id
                        
                        # Validate CID for production environments
                        is_valid, error_message = validate_production_cid(current_request_body, env_id)
                        if not is_valid:
                            logger.warning(f'🔴 Production CID validation failed for test {test_id}, payment_account_id {payment_account_id}: {error_message}')
                            results.append({
                                'test_id': test_id,
                                'test_name': test_case['name'],
                                'scenario_name': f'Payment Account ID: {payment_account_id}',
                                'error': error_message,
                                'success': False,
                                'blocked': True,
                                'timestamp': datetime.utcnow().isoformat()
                            })
                            continue
                        
                        # Execute request
                        result = execute_single_request(test_case, current_request_body, base_url, env_id, f'Payment Account ID: {payment_account_id}')
                        result['test_id'] = test_id
                        result['test_name'] = test_case['name']
                        result['scenario_name'] = f'Payment Account ID: {payment_account_id}'
                        result['request_body'] = current_request_body
                        results.append(result)
                else:
                    # Empty IDs list - fall through to default behavior
                    payment_account_ids = None
            
            # Check if scheduled_payment_ids are provided in the request (for Delete Auto Payment)
            scheduled_payment_ids = data.get('scheduled_payment_ids', '')
            if scheduled_payment_ids and isinstance(scheduled_payment_ids, str) and scheduled_payment_ids.strip():
                # Parse comma-separated IDs
                ids_list = [id_str.strip() for id_str in scheduled_payment_ids.split(',') if id_str.strip()]
                
                if ids_list:
                    # Make multiple API calls, one for each ID
                    for scheduled_payment_id in ids_list:
                        # Create a copy of the request body with the specific scheduled_payment_id
                        current_request_body = request_body.copy()
                        # Convert to int if it's a digit, otherwise keep as string
                        current_request_body['scheduled_payment_id'] = int(scheduled_payment_id) if scheduled_payment_id.isdigit() else scheduled_payment_id
                        
                        # Validate CID for production environments
                        is_valid, error_message = validate_production_cid(current_request_body, env_id)
                        if not is_valid:
                            logger.warning(f'🔴 Production CID validation failed for test {test_id}, scheduled_payment_id {scheduled_payment_id}: {error_message}')
                            results.append({
                                'test_id': test_id,
                                'test_name': test_case['name'],
                                'scenario_name': f'Scheduled Payment ID: {scheduled_payment_id}',
                                'error': error_message,
                                'success': False,
                                'blocked': True,
                                'timestamp': datetime.utcnow().isoformat()
                            })
                            continue
                        
                        # Execute request
                        result = execute_single_request(test_case, current_request_body, base_url, env_id, f'Scheduled Payment ID: {scheduled_payment_id}')
                        result['test_id'] = test_id
                        result['test_name'] = test_case['name']
                        result['scenario_name'] = f'Scheduled Payment ID: {scheduled_payment_id}'
                        result['request_body'] = current_request_body
                        results.append(result)
                else:
                    # Empty IDs list - fall through to default behavior
                    scheduled_payment_ids = None
            
            # If no payment_account_ids or scheduled_payment_ids provided, use default behavior
            if (not payment_account_ids or not isinstance(payment_account_ids, str) or not payment_account_ids.strip()) and \
               (not scheduled_payment_ids or not isinstance(scheduled_payment_ids, str) or not scheduled_payment_ids.strip()):
                # Apply auto payment config if provided (for Add Auto Payment)
                # Always apply dates for Add Auto Payment, even if config is empty
                # For single body, day_offset is 0
                auto_payment_config = data.get('auto_payment_config', {})
                is_add_auto_payment = 'add auto payment' in test_case.get('name', '').lower()
                if (auto_payment_config or is_add_auto_payment) and isinstance(request_body, dict):
                    request_body = apply_auto_payment_config(request_body, auto_payment_config, day_offset=0)
                
                # Apply make payment config if provided (for Make Payment)
                make_payment_config = data.get('make_payment_config', {})
                if make_payment_config and isinstance(request_body, dict):
                    request_body = apply_make_payment_config(request_body, make_payment_config)
                
                # Apply cancel payment config if provided (for Cancel Payment)
                cancel_payment_ids = data.get('cancel_payment_ids', '')
                if cancel_payment_ids and isinstance(cancel_payment_ids, str) and cancel_payment_ids.strip() and isinstance(request_body, dict):
                    request_body = apply_cancel_payment_config(request_body, cancel_payment_ids)
                
                # Apply receipt payment config if provided (for Get Payment Receipt)
                receipt_payment_ids = data.get('receipt_payment_ids', '')
                if receipt_payment_ids and isinstance(receipt_payment_ids, str) and receipt_payment_ids.strip() and isinstance(request_body, dict):
                    request_body = apply_receipt_payment_config(request_body, receipt_payment_ids)
                
                # Apply payment status config if provided (for Get Payment Status)
                payment_status_id = data.get('payment_status_id', '')
                if payment_status_id and isinstance(payment_status_id, str) and payment_status_id.strip() and isinstance(request_body, dict):
                    request_body = apply_payment_status_config(request_body, payment_status_id)
                
                # Validate CID for production environments
                is_valid, error_message = validate_production_cid(request_body, env_id)
                if not is_valid:
                    logger.warning(f'🔴 Production CID validation failed for test {test_id}: {error_message}')
                    return jsonify({
                        'test_id': test_id,
                        'test_name': test_case['name'],
                        'error': error_message,
                        'success': False,
                        'blocked': True,
                        'timestamp': datetime.utcnow().isoformat()
                    }), 403
                
                # Execute request
                result = execute_single_request(test_case, request_body, base_url, env_id)
                result['test_id'] = test_id
                result['test_name'] = test_case['name']
                result['request_body'] = request_body
                results.append(result)
        
        # Return single result for backward compatibility, or array if multiple bodies
        if len(results) == 1:
            return jsonify(results[0]), 200
        else:
            return jsonify({
                'test_id': test_id,
                'test_name': test_case['name'],
                'has_multiple_scenarios': True,
                'results': results,
                'summary': {
                    'total': len(results),
                    'passed': sum(1 for r in results if r.get('success', False)),
                    'failed': sum(1 for r in results if not r.get('success', False)),
                    'blocked': sum(1 for r in results if r.get('blocked', False))
                }
            }), 200
            
    except Exception as e:
        logger.error(f'Error running test: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/run-all-tests', methods=['POST'])
def run_all_tests():
    """Run all test cases. Supports both single body and multiple bodies (bodies array)."""
    try:
        # Get environment from request
        data = request.get_json() or {}
        env_id = data.get('environment', 'capricorn-trunk')
        
        # Load environments config
        with open('environments.json', 'r') as f:
            env_config = json.load(f)
        
        # Find the environment
        env = next((e for e in env_config['environments'] if e['id'] == env_id), None)
        if not env:
            return jsonify({'error': f'Environment {env_id} not found'}), 404
        
        # Load test cases for this environment
        test_cases_file = env['test_cases_file']
        with open(test_cases_file, 'r') as f:
            test_data = json.load(f)
        
        results = []
        base_url = test_data['base_url']
        
        for test_case in test_data['test_cases']:
            # Check if test case has multiple bodies (bodies array)
            bodies = test_case.get('bodies', [])
            if bodies:
                # Multiple bodies - run each scenario
                for idx, body_config in enumerate(bodies):
                    # Support both object with 'name' and 'body' or just direct body object
                    if isinstance(body_config, dict):
                        if 'body' in body_config:
                            scenario_name = body_config.get('name', f'Scenario {idx + 1}')
                            request_body = body_config['body']
                        else:
                            # Direct body object
                            scenario_name = f'Scenario {idx + 1}'
                            request_body = body_config
                    else:
                        # Invalid format
                        results.append({
                            'test_id': test_case['id'],
                            'test_name': test_case['name'],
                            'category': test_case.get('category', 'Uncategorized'),
                            'scenario_name': f'Scenario {idx + 1}',
                            'error': 'Invalid body format in bodies array',
                            'success': False,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                        continue
                    
                    # Validate CID for production environments
                    is_valid, error_message = validate_production_cid(request_body, env_id)
                    if not is_valid:
                        logger.warning(f'🔴 Production CID validation failed for test {test_case["id"]}, scenario {scenario_name}: {error_message}')
                        results.append({
                            'test_id': test_case['id'],
                            'test_name': test_case['name'],
                            'category': test_case.get('category', 'Uncategorized'),
                            'scenario_name': scenario_name,
                            'error': error_message,
                            'success': False,
                            'blocked': True,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                        continue
                    
                    # Execute request
                    result = execute_single_request(test_case, request_body, base_url, env_id, scenario_name)
                    result['test_id'] = test_case['id']
                    result['test_name'] = test_case['name']
                    result['category'] = test_case.get('category', 'Uncategorized')
                    result['scenario_name'] = scenario_name
                    result['request_body'] = request_body
                    results.append(result)
            else:
                # Single body - backward compatibility
                request_body = test_case.get('body', {})
                
                # Validate CID for production environments
                is_valid, error_message = validate_production_cid(request_body, env_id)
                if not is_valid:
                    logger.warning(f'🔴 Production CID validation failed for test {test_case["id"]}: {error_message}')
                    results.append({
                        'test_id': test_case['id'],
                        'test_name': test_case['name'],
                        'category': test_case.get('category', 'Uncategorized'),
                        'error': error_message,
                        'success': False,
                        'blocked': True,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    continue
                
                # Execute request
                result = execute_single_request(test_case, request_body, base_url, env_id)
                result['test_id'] = test_case['id']
                result['test_name'] = test_case['name']
                result['category'] = test_case.get('category', 'Uncategorized')
                result['request_body'] = request_body
                results.append(result)
        
        summary = {
            'total': len(results),
            'passed': sum(1 for r in results if r.get('success', False)),
            'failed': sum(1 for r in results if not r.get('success', False)),
            'blocked': sum(1 for r in results if r.get('blocked', False)),
            'avg_response_time_ms': round(
                sum(r.get('response_time_ms', 0) for r in results if r.get('success', False)) / 
                max(sum(1 for r in results if r.get('success', False)), 1),
                2
            )
        }
        
        return jsonify({
            'summary': summary,
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f'Error running all tests: {e}')
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', os.getenv('FLASK_ENV', 'production')) == 'development' or os.getenv('FLASK_DEBUG') == '1'
    
    # Print startup info
    print(f"\n{'='*60}")
    print(f"🚀 External API Tester - {'DEVELOPMENT' if debug else 'PRODUCTION'} Mode")
    print(f"{'='*60}")
    print(f"📊 Test Runner UI: http://localhost:{port}/test-runner")
    print(f"🔍 Health Check:   http://localhost:{port}/health")
    print(f"🌐 API Base URL:   {API_BASE_URL}")
    print(f"{'='*60}\n")
    
    if debug:
        print("⚡ Hot-reload enabled - changes will auto-reload\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=debug)


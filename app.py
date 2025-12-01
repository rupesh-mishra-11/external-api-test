"""
Flask application for testing external API scenarios.
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json

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


@app.route('/api/run-test/<test_id>', methods=['POST'])
def run_single_test(test_id):
    """Run a single test case."""
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
        
        # Validate CID for production environments
        request_body = test_case.get('body', {})
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
        
        base_url = test_data['base_url']
        url = f"{base_url}{test_case['endpoint']}"
        
        start_time = datetime.utcnow()
        
        try:
            # Merge test headers with global auth headers
            # Use Bearer token for all environments
            merged_headers = merge_headers(test_case.get('headers', {}), use_bearer_token=True, environment_id=env_id)
            
            # Log headers for debugging (remove sensitive data)
            safe_headers = {k: v[:20]+'...' if k.lower() in ['authorization', 'x-api-key'] and len(v) > 20 else v 
                          for k, v in merged_headers.items()}
            logger.info(f'Test {test_id} - {test_case["name"]} - Env: {env_id} - Headers: {safe_headers}')
            logger.info(f'Test {test_id} - URL: {url}')
            
            if test_case['method'].upper() == 'GET':
                response = requests.get(
                    url,
                    headers=merged_headers,
                    params=test_case.get('body', {}),
                    timeout=API_TIMEOUT
                )
            elif test_case['method'].upper() == 'POST':
                response = requests.post(
                    url,
                    headers=merged_headers,
                    json=test_case.get('body', {}),
                    timeout=API_TIMEOUT
                )
            elif test_case['method'].upper() == 'PUT':
                response = requests.put(
                    url,
                    headers=merged_headers,
                    json=test_case.get('body', {}),
                    timeout=API_TIMEOUT
                )
            else:
                return jsonify({'error': f'Unsupported method: {test_case["method"]}'}), 400
            
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            result = {
                'test_id': test_id,
                'test_name': test_case['name'],
                'status_code': response.status_code,
                'success': 200 <= response.status_code < 300,
                'response_time_ms': round(duration_ms, 2),
                'response_data': response_data,
                'headers': dict(response.headers),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return jsonify(result), 200
            
        except requests.exceptions.Timeout:
            return jsonify({
                'test_id': test_id,
                'test_name': test_case['name'],
                'error': 'Request timeout',
                'success': False,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except requests.exceptions.ConnectionError as e:
            return jsonify({
                'test_id': test_id,
                'test_name': test_case['name'],
                'error': f'Connection error: {str(e)}',
                'success': False,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            return jsonify({
                'test_id': test_id,
                'test_name': test_case['name'],
                'error': str(e),
                'success': False,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
            
    except Exception as e:
        logger.error(f'Error running test: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/run-all-tests', methods=['POST'])
def run_all_tests():
    """Run all test cases."""
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
        for test_case in test_data['test_cases']:
            # Validate CID for production environments
            request_body = test_case.get('body', {})
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
            
            # Simulate calling run_single_test
            base_url = test_data['base_url']
            url = f"{base_url}{test_case['endpoint']}"
            
            start_time = datetime.utcnow()
            
            try:
                # Merge test headers with global auth headers
                # Use Bearer token for all environments
                merged_headers = merge_headers(test_case.get('headers', {}), use_bearer_token=True, environment_id=env_id)
                
                if test_case['method'].upper() == 'GET':
                    response = requests.get(
                        url,
                        headers=merged_headers,
                        params=test_case.get('body', {}),
                        timeout=API_TIMEOUT
                    )
                elif test_case['method'].upper() == 'POST':
                    response = requests.post(
                        url,
                        headers=merged_headers,
                        json=test_case.get('body', {}),
                        timeout=API_TIMEOUT
                    )
                elif test_case['method'].upper() == 'PUT':
                    response = requests.put(
                        url,
                        headers=merged_headers,
                        json=test_case.get('body', {}),
                        timeout=API_TIMEOUT
                    )
                else:
                    results.append({
                        'test_id': test_case['id'],
                        'test_name': test_case['name'],
                        'error': f'Unsupported method: {test_case["method"]}',
                        'success': False
                    })
                    continue
                
                end_time = datetime.utcnow()
                duration_ms = (end_time - start_time).total_seconds() * 1000
                
                try:
                    response_data = response.json()
                except:
                    response_data = response.text
                
                results.append({
                    'test_id': test_case['id'],
                    'test_name': test_case['name'],
                    'category': test_case.get('category', 'Uncategorized'),
                    'status_code': response.status_code,
                    'success': 200 <= response.status_code < 300,
                    'response_time_ms': round(duration_ms, 2),
                    'response_data': response_data,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
            except requests.exceptions.Timeout:
                results.append({
                    'test_id': test_case['id'],
                    'test_name': test_case['name'],
                    'category': test_case.get('category', 'Uncategorized'),
                    'error': 'Request timeout',
                    'success': False,
                    'timestamp': datetime.utcnow().isoformat()
                })
            except requests.exceptions.ConnectionError as e:
                results.append({
                    'test_id': test_case['id'],
                    'test_name': test_case['name'],
                    'category': test_case.get('category', 'Uncategorized'),
                    'error': f'Connection error: {str(e)}',
                    'success': False,
                    'timestamp': datetime.utcnow().isoformat()
                })
            except Exception as e:
                results.append({
                    'test_id': test_case['id'],
                    'test_name': test_case['name'],
                    'category': test_case.get('category', 'Uncategorized'),
                    'error': str(e),
                    'success': False,
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        summary = {
            'total': len(results),
            'passed': sum(1 for r in results if r.get('success', False)),
            'failed': sum(1 for r in results if not r.get('success', False)),
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


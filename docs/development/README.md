# Development Guide

## Quick Start

### Development Mode (Hot-Reload)

**Linux/Mac/WSL:**
```bash
./dev.sh
```

**Windows:**
```cmd
dev.bat
```

**What you get:**
- ✅ **Hot-reload** - Changes to code instantly reflected (no rebuild needed)
- ✅ **Volume mounts** - Edit files on your host, see changes in container
- ✅ **Debug mode** - Better error messages and stack traces
- ✅ **Single worker** - Easier to debug
- ✅ **Live logs** - See output in real-time

### Production Mode

**Linux/Mac/WSL:**
```bash
./prod.sh
```

**Windows:**
```cmd
prod.bat
```

**What you get:**
- ✅ **Gunicorn WSGI server** - Production-grade
- ✅ **Multiple workers** - Better performance
- ✅ **Production logging** - Proper log format
- ⚠️ **No auto-reload** - Requires rebuild for code changes

---

## Development Workflow

### Option 1: Docker Development Mode (Recommended)

This is the BEST approach for development because:
- Consistent environment (same as production)
- No need to install Python/dependencies locally
- Hot-reload enabled
- Easy to switch between dev/prod

**Start development server:**
```bash
./dev.sh   # Linux/Mac/WSL
dev.bat    # Windows
```

**Make changes:**
1. Edit `app.py`, `test_cases.json`, or `static/test-runner.html`
2. Save the file
3. Refresh browser - changes are live! ⚡

**View logs:**
```bash
docker-compose -f docker-compose.dev.yml logs -f
```

**Stop server:**
Press `Ctrl+C` in the terminal where dev.sh is running

### Option 2: Local Python Development

If you prefer to run without Docker:

**Setup:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac/WSL
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

**Run:**
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

**Advantages:**
- Faster startup (no Docker overhead)
- Direct debugging with IDE
- Simpler for quick iterations

**Disadvantages:**
- Need to manage Python environment
- May have OS-specific issues
- Not identical to production

---

## File Structure for Development

### Files That Auto-Reload (Development Mode)

These files are mounted as volumes and changes reload automatically:

- `app.py` - Main Flask application
- `test_cases.json` - Test case configurations
- `static/test-runner.html` - UI file
- `gunicorn_config.py` - Gunicorn configuration

### Files That Require Rebuild

These files are baked into the Docker image and need a rebuild:

- `requirements.txt` - Python dependencies
- `Dockerfile` - Container definition
- `docker-compose.yml` / `docker-compose.dev.yml` - Compose configs

**To rebuild after changing these:**
```bash
wsl docker-compose -f docker-compose.dev.yml up --build
```

---

## Common Development Tasks

### Adding a New Test Case

1. Edit `test_cases.json`
2. Add your new test case to the `test_cases` array
3. Save the file
4. Refresh the browser - new test appears immediately!

**Example:**
```json
{
  "id": "24",
  "name": "My New Test",
  "endpoint": "/exapi/?controller=my_endpoint",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "cid": 4547,
    "test_param": "value"
  },
  "category": "Payment"
}
```

### Modifying the UI

1. Edit `static/test-runner.html`
2. Save the file
3. Refresh browser - changes appear instantly!

**Pro tip:** Use browser dev tools (F12) to test CSS/JS changes live

### Adding a New API Endpoint

1. Edit `app.py`
2. Add your new route:
```python
@app.route('/api/my-new-endpoint', methods=['POST'])
def my_new_endpoint():
    data = request.get_json()
    # Your logic here
    return jsonify({'result': 'success'}), 200
```
3. Save - Flask auto-reloads
4. Test immediately at `http://localhost:5000/api/my-new-endpoint`

### Debugging

**View container logs:**
```bash
docker-compose -f docker-compose.dev.yml logs -f
```

**Check if container is running:**
```bash
docker ps | grep external-api-tester
```

**Enter the container:**
```bash
docker exec -it external-api-tester-dev bash
```

**View Flask debug output:**
Already visible in your terminal when running `./dev.sh`

---

## Environment Variables

### Development Mode

```bash
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5000
API_BASE_URL=https://us-residentpay-external.d05d0001.entratadev.com
API_TIMEOUT=30
MAX_RETRIES=1
LOG_LEVEL=debug
GUNICORN_WORKERS=1
```

### Production Mode

```bash
FLASK_ENV=production
FLASK_DEBUG=0
PORT=5000
API_BASE_URL=http://your-api-url
API_TIMEOUT=30
MAX_RETRIES=3
LOG_LEVEL=info
GUNICORN_WORKERS=4
```

### Custom Configuration

Create a `.env` file in the project root:

```bash
# .env file
API_BASE_URL=http://my-custom-api.com
API_TIMEOUT=60
MAX_RETRIES=5
LOG_LEVEL=debug
```

Docker Compose automatically reads this file!

---

## Switching Between Modes

### From Development to Production

```bash
# Stop dev server
Ctrl+C  # or docker-compose -f docker-compose.dev.yml down

# Start prod server
./prod.sh
```

### From Production to Development

```bash
# Stop prod server
docker-compose down

# Start dev server
./dev.sh
```

---

## Troubleshooting

### Changes Not Reflecting

**Development mode:**
- Check if container is actually running: `docker ps`
- Verify volumes are mounted: `docker inspect external-api-tester-dev`
- Check logs for errors: `docker-compose -f docker-compose.dev.yml logs`
- Hard refresh browser: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)

**Production mode:**
- You MUST rebuild: `docker-compose up --build -d`
- Production doesn't auto-reload by design

### Port Already in Use

```bash
# Find what's using port 5000
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Stop all containers
docker-compose down
docker-compose -f docker-compose.dev.yml down
```

### Container Keeps Restarting

```bash
# Check logs
docker-compose -f docker-compose.dev.yml logs -f

# Common causes:
# - Syntax error in app.py
# - Missing dependency in requirements.txt
# - Port conflict
```

### Performance Issues in Development

Development mode with volume mounts can be slower than production, especially on Windows/Mac. This is normal - Docker volume mounts have overhead.

**Solutions:**
- Use production mode for performance testing
- Test on Linux if possible (better Docker performance)
- Use local Python development (Option 2) for faster iteration

---

## Best Practices

### DO ✅

- Use **development mode** while coding
- Use **production mode** for final testing
- Commit your `.env` file structure (not values) to git
- Test in production mode before deploying
- Use volume mounts for development
- Keep test data in `test_cases.json`

### DON'T ❌

- Don't commit sensitive API keys to git
- Don't use development mode in production
- Don't skip rebuilding when dependencies change
- Don't edit files inside the container
- Don't use `latest` tag in production
- Don't run as root in production

---

## Testing Workflow

### Development Testing

1. Start dev mode: `./dev.sh`
2. Make changes to code
3. Refresh browser to see changes
4. Test in UI at `http://localhost:5000/test-runner`
5. Iterate quickly without rebuilds

### Production Testing

1. Start prod mode: `./prod.sh`
2. Run full test suite
3. Check performance metrics
4. Verify error handling
5. Test under load

### CI/CD Testing

```bash
# Build production image
docker build -t external-api-tester:test .

# Run tests
docker run --rm external-api-tester:test python -m pytest

# Deploy if tests pass
docker tag external-api-tester:test external-api-tester:latest
```

---

## Performance Tuning

### Development

```yaml
# docker-compose.dev.yml
environment:
  - GUNICORN_WORKERS=1  # Single worker for debugging
```

### Production

```yaml
# docker-compose.yml
environment:
  - GUNICORN_WORKERS=4  # Multiple workers for performance
```

**Formula for workers:**
```
workers = (CPU cores × 2) + 1
```

---

## Need Help?

- Check logs: `docker-compose -f docker-compose.dev.yml logs -f`
- Restart everything: `docker-compose -f docker-compose.dev.yml restart`
- Clean slate: `docker-compose -f docker-compose.dev.yml down -v && ./dev.sh`
- Read the docs: [Flask Documentation](https://flask.palletsprojects.com/)

Happy coding! 🚀


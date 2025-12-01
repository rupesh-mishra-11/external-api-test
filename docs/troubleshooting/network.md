# Network Troubleshooting Guide

## The Problem

Your Docker container can't reach `rsync.residentportal2.residentportal.localhost:7080`

**Error:**
```
Failed to resolve 'rsync.residentportal2.residentportal.localhost'
```

## Quick Fix (What I Just Did)

I updated both `docker-compose.yml` and `docker-compose.dev.yml` to use **host network mode**.

**Restart your container:**
```powershell
docker-compose -f docker-compose.dev.yml down
wsl docker-compose -f docker-compose.dev.yml up --build
```

This makes the container use your host's network directly, so it can resolve the same hostnames as your Windows/WSL system.

---

## If That Doesn't Work

### Solution 1: Check if Your API is Running

First, verify the API server is actually running:

```powershell
# From your Windows PowerShell or WSL terminal
curl https://us-residentpay-external.d05d0001.entratadev.com/exapi/?controller=balance
```

If this fails, **your API server isn't running** - start it first!

### Solution 2: Find the Actual IP Address

If the hostname doesn't work, use the IP address instead:

**In WSL, find the IP:**
```bash
# Get WSL IP
hostname -I

# Or
ip addr show eth0
```

**In Windows, find Docker host IP:**
```powershell
ipconfig
```

**Then update the API_BASE_URL:**
```powershell
# Create .env file
echo API_BASE_URL=http://172.x.x.x:7080 > .env

# Restart container
docker-compose -f docker-compose.dev.yml down
wsl docker-compose -f docker-compose.dev.yml up --build
```

### Solution 3: Use host.docker.internal (Windows/Mac)

On Windows and Mac, Docker provides a special hostname:

```powershell
# Create .env file
echo API_BASE_URL=http://host.docker.internal:7080 > .env

# Restart
docker-compose -f docker-compose.dev.yml down
wsl docker-compose -f docker-compose.dev.yml up --build
```

### Solution 4: Test from Inside Container

Check if the container can reach the host:

```powershell
# Enter the running container
docker exec -it external-api-tester-dev bash

# Try to ping/curl
curl https://us-residentpay-external.d05d0001.entratadev.com
curl http://host.docker.internal:7080
curl http://172.x.x.x:7080

# Exit container
exit
```

### Solution 5: Add Custom DNS Entry

If host network mode doesn't work, add the hostname to the container:

**Edit docker-compose.dev.yml:**
```yaml
services:
  api-tester:
    # ... other config ...
    extra_hosts:
      - "rsync.residentportal2.residentportal.localhost:host-gateway"
```

Then restart:
```powershell
docker-compose -f docker-compose.dev.yml down
wsl docker-compose -f docker-compose.dev.yml up --build
```

---

## Understanding the Issue

### Why This Happens

**Your Windows/WSL system:**
- Has custom DNS entries or hosts file
- Knows what `rsync.residentportal2.residentportal.localhost` means
- Can connect to port 7080

**Docker container (default network):**
- Has its own isolated network
- Doesn't share your hosts file
- Can't resolve custom local hostnames
- ❌ **Can't find your API**

### The Fix (Host Network Mode)

**With host network mode:**
- Container uses your computer's network directly
- Sees the same DNS as your system
- Can resolve `.localhost` domains
- ✅ **Can find your API**

---

## Verify It's Working

### Step 1: Check Container Logs

```powershell
docker-compose -f docker-compose.dev.yml logs -f
```

Look for:
```
🌐 API Base URL: https://us-residentpay-external.d05d0001.entratadev.com
```

### Step 2: Test Health Check

```powershell
curl http://localhost:5000/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "service": "external-api-tester"
}
```

### Step 3: Test an API Call

Go to: `http://localhost:5000/test-runner`

Click "Run Test" on any test case.

**If successful:** ✅ Green status with response time  
**If failed:** ❌ Red status with error message

---

## Common Scenarios

### Scenario 1: API Running in WSL

If your API runs in WSL:

1. Get WSL IP: `hostname -I` in WSL
2. Use that IP: `http://172.x.x.x:7080`
3. OR use host network mode (what I did)

### Scenario 2: API Running in Another Docker Container

If your API is in another container:

```yaml
# In docker-compose.dev.yml
services:
  api-tester:
    # ... other config ...
    networks:
      - shared-network

networks:
  shared-network:
    external: true
```

### Scenario 3: API Running on Windows Host

If your API runs directly on Windows:

Use `host.docker.internal`:
```
API_BASE_URL=http://host.docker.internal:7080
```

### Scenario 4: Port is Already in Use

If port 7080 is blocked:

```powershell
# Check what's using the port
netstat -ano | findstr :7080

# Kill the process if needed
taskkill /PID <PID> /F
```

---

## Quick Debug Commands

```powershell
# Is container running?
docker ps | findstr external-api-tester

# View container network settings
docker inspect external-api-tester-dev | findstr -i "network"

# Check container logs
docker-compose -f docker-compose.dev.yml logs -f

# Restart everything fresh
docker-compose -f docker-compose.dev.yml down
wsl docker-compose -f docker-compose.dev.yml up --build

# Test from container
docker exec -it external-api-tester-dev curl https://us-residentpay-external.d05d0001.entratadev.com
```

---

## Still Not Working?

### Option A: Update test_cases.json

Change the base_url directly:

```json
{
  "base_url": "http://localhost:7080",
  "test_cases": [...]
}
```

### Option B: Use Environment Variable

```powershell
# Set for current session
$env:API_BASE_URL="http://localhost:7080"

# Restart container
docker-compose -f docker-compose.dev.yml down
wsl docker-compose -f docker-compose.dev.yml up --build
```

### Option C: Edit app.py

Temporarily hardcode it:

```python
# In app.py
API_BASE_URL = "http://localhost:7080"  # Change this line
```

Save, wait for hot-reload, test.

---

## Prevention

### For Future Projects:

1. **Document your local setup** - What hostnames? What ports?
2. **Use .env files** - Don't hardcode URLs
3. **Test container networking early** - Don't wait until deployment
4. **Use standard hostnames** - `localhost`, `host.docker.internal` work everywhere
5. **Consider docker-compose for all services** - Keep everything in containers

---

## Summary

**What I fixed:**
- ✅ Added host network mode to docker-compose files
- ✅ Container now uses your system's network
- ✅ Should resolve `.localhost` domains

**What you need to do:**
```powershell
# Restart with the fix
docker-compose -f docker-compose.dev.yml down
wsl docker-compose -f docker-compose.dev.yml up --build

# Test
# Open: http://localhost:5000/test-runner
# Run a test - should work now!
```

**If it STILL doesn't work:**
1. Check if your API at port 7080 is actually running
2. Try using the IP address instead of hostname
3. Check the debug commands above
4. Read the scenarios section for your specific setup

Good luck! 🚀


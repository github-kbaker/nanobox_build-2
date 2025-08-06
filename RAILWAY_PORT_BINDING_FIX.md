# 🚨 RAILWAY HEALTH CHECK FAILING - PORT ISSUE

## Problem: Service Unavailable on /api/

**Build**: ✅ Success (39.78 seconds)
**Health Check**: ❌ Failed - Service unavailable

## Root Cause: Port Binding Issue

The Dockerfile is binding to port 8000, but Railway expects the app to bind to the `$PORT` environment variable.

---

## ✅ SOLUTION 1: Fix Dockerfile Port Binding

### Current Dockerfile (Wrong):
```dockerfile
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Fixed Dockerfile:
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway will set $PORT)
EXPOSE $PORT

# Start command - USE $PORT environment variable
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port $PORT"]
```

**Key Change:** Use `$PORT` instead of hardcoded `8000`

---

## ✅ SOLUTION 2: Alternative Start Commands

### Option A: Use Railway's Environment Variable
```dockerfile
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

### Option B: Python Script Approach
```dockerfile
CMD ["python", "-c", "import os; import uvicorn; uvicorn.run('server:app', host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))"]
```

---

## ✅ SOLUTION 3: Railway Settings Override

If you can't update Dockerfile immediately:

### In Railway Dashboard:
1. **Go to Settings → Deploy**
2. **Override Start Command:**
```
uvicorn server:app --host 0.0.0.0 --port $PORT
```
3. **Save and redeploy**

---

## ✅ SOLUTION 4: Check Server.py Port Configuration

Verify your `server.py` doesn't hardcode ports:

### Good (Uses Environment Variable):
```python
import os
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
```

### Bad (Hardcoded Port):
```python
uvicorn.run("server:app", host="0.0.0.0", port=8000)  # Wrong!
```

---

## 🔧 IMMEDIATE ACTION STEPS

### Quick Fix (Railway Dashboard):
1. **Go to Railway → Your Service → Settings → Deploy**
2. **Set Start Command to:**
```
uvicorn server:app --host 0.0.0.0 --port $PORT
```
3. **Save and Redeploy**

### Permanent Fix (Update Dockerfile):
1. **Update Dockerfile** with correct port binding
2. **Push to GitHub**
3. **Railway will auto-redeploy**

---

## 🎯 Expected Success After Fix

```
✅ Starting application on port $PORT
✅ Health check /api/ - 200 OK
✅ Service available at https://your-domain.up.railway.app
✅ Deployment successful
```

**The port binding issue is the most common Railway deployment problem! 🎯**
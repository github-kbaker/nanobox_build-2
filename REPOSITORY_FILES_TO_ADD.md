# 📋 Files to Add to Your Repository

## 🎯 Repository: github-kbaker/nanobox_build-2/backend/

### Add these 3 files to fix Railway nixpacks error:

---

## 📄 1. nixpacks.toml
**Path**: `github-kbaker/nanobox_build-2/backend/nixpacks.toml`

```toml
[phases.setup]
providers = ["python"]

[phases.install]
dependsOn = ["setup"]
cmds = ["pip install -r requirements.txt"]

[phases.build]
dependsOn = ["install"]

[start]
cmd = "uvicorn server:app --host 0.0.0.0 --port $PORT"
```

---

## 📄 2. railway.json  
**Path**: `github-kbaker/nanobox_build-2/backend/railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "uvicorn server:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "never"
  }
}
```

---

## 📄 3. Dockerfile
**Path**: `github-kbaker/nanobox_build-2/backend/Dockerfile`

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
EXPOSE 8000

# Start command
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🚀 How to Add These Files:

### Method 1: GitHub Web Interface
1. Go to: `https://github.com/github-kbaker/nanobox_build-2`
2. Navigate to `backend/` directory
3. Click "Add file" → "Create new file"
4. Name: `nixpacks.toml` and paste content
5. Repeat for `railway.json` and `Dockerfile`
6. Commit changes

### Method 2: Local Git Commands
```bash
cd /path/to/nanobox_build-2/backend/

# Create nixpacks.toml
cat > nixpacks.toml << 'EOF'
[phases.setup]
providers = ["python"]

[phases.install]
dependsOn = ["setup"]
cmds = ["pip install -r requirements.txt"]

[phases.build]
dependsOn = ["install"]

[start]
cmd = "uvicorn server:app --host 0.0.0.0 --port $PORT"
EOF

# Create railway.json
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "uvicorn server:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "never"
  }
}
EOF

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Commit and push
git add nixpacks.toml railway.json Dockerfile
git commit -m "Add Railway deployment configuration files"
git push origin main
```

---

## ✅ Validation Steps:

### 1. Check Repository Structure
After adding files, your backend directory should look like:
```
github-kbaker/nanobox_build-2/backend/
├── server.py                # Your FastAPI app
├── requirements.txt         # Dependencies  
├── nixpacks.toml           # ← NEW
├── railway.json            # ← NEW
├── Dockerfile              # ← NEW
└── [other files...]
```

### 2. Railway Auto-Redeploy
- Railway should automatically detect the changes
- Check your Railway dashboard for new deployment
- Build should succeed with these config files

### 3. Expected Build Log Success
```
✅ nixpacks detected Python application
✅ Installing dependencies from requirements.txt  
✅ Starting application: uvicorn server:app --host 0.0.0.0 --port $PORT
✅ Health check passed: /api/
✅ Deployment successful
```

### 4. Test Deployed API
```bash
curl https://your-railway-domain.up.railway.app/api/
# Expected: {"status":"healthy","message":"Backend API is running on Railway!"}
```

---

## 🎯 Why These Files Fix the Error:

- **`nixpacks.toml`**: Explicitly tells nixpacks how to build Python app
- **`railway.json`**: Provides Railway-specific deployment configuration  
- **`Dockerfile`**: Backup method if nixpacks still fails

**Railway will try nixpacks first, then fall back to Docker if needed.**

---

## 📞 After Adding Files:

1. **Wait 2-3 minutes** for Railway auto-redeploy
2. **Check deployment logs** in Railway dashboard
3. **Test your API endpoints**
4. **API docs available** at: `/api/docs`

**These configuration files should resolve the nixpacks build plan error! 🚀**
# Railway.app Deployment Demo: github-kbaker/nanobox_build-2

This guide shows you **exactly** how to deploy your `github-kbaker/nanobox_build-2` repository to Railway.app with `/backend` as the root directory, using our current codebase as an example.

## 🎯 Overview: What We're Deploying

**Current Example Structure:**
```
/app/
├── backend/              # ← This becomes Railway root directory
│   ├── server.py        # FastAPI application
│   ├── requirements.txt # Python dependencies  
│   ├── railway.toml     # Railway configuration
│   ├── Procfile        # Process configuration
│   └── .env            # Environment variables
├── frontend/            # ← Not deployed (frontend separate)
└── other files...
```

**Your Repository Adaptation:**
```
github-kbaker/nanobox_build-2/
├── backend/              # ← Railway root directory
│   ├── [your-main-file.py]  # Your FastAPI app
│   ├── requirements.txt     # Need to create/verify
│   ├── railway.toml        # Need to create
│   └── [your-other-files]
└── [other-directories]
```

---

## 📋 Step 1: Prepare Your Repository Files

### Required Files in Your `/backend` Directory

#### 1.1 Main Application File (✅ You Should Have)
**Example from our codebase:**
```python
# /backend/server.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/api/")
async def root():
    return {"message": "Hello World"}
```

**For Your Repository:**
- Identify your main FastAPI file (might be `main.py`, `app.py`, or `server.py`)
- Ensure it has a FastAPI instance (usually named `app`)

#### 1.2 Requirements File (✅ Create if Missing)
**Example from our codebase:**
```txt
# /backend/requirements.txt
fastapi==0.110.1
uvicorn==0.25.0
motor==3.3.1
pymongo==4.5.0
python-dotenv>=1.0.1
# ... other dependencies
```

**For Your Repository:**
```bash
# If you don't have requirements.txt, create one:
pip freeze > backend/requirements.txt
```

#### 1.3 Railway Configuration (📝 Create These)
**Create: `/backend/railway.toml`**
```toml
[build]
# Railway auto-detects Python, no build command needed

[deploy]
# Replace 'server:app' with 'your-file:app' if different
startCommand = "uvicorn server:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/"
healthcheckTimeout = 100
restartPolicyType = "never"
```

**Create: `/backend/Procfile`**
```
# Replace 'server:app' with your main file:app
web: uvicorn server:app --host 0.0.0.0 --port $PORT
```
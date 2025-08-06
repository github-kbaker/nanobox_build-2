# 🚀 Deploy to Railway.app - Step-by-Step Guide

## Current Status: ✅ Your FastAPI Backend is Ready!

Your backend is running perfectly and ready for Railway deployment. Follow these exact steps:

---

## 📋 Step 1: Access Railway.app

1. **Open Railway in new tab**: https://railway.app/
2. **Sign up/Login** using:
   - GitHub account (recommended)
   - Google account
   - Or email

---

## 🔗 Step 2: Connect Your Repository

1. **Click "New Project"**
2. **Select "Deploy from GitHub repo"**
3. **Authorize Railway** to access your GitHub if prompted
4. **Search and select**: `github-kbaker/nanobox_build-2`
5. **Click "Deploy Now"**

**Expected Result:**
```
✅ Repository connected: github-kbaker/nanobox_build-2
✅ Railway project created
```

---

## ⚙️ Step 3: Configure Root Directory (CRITICAL)

1. **Click on your service** (will show as "nanobox-build-2" or similar)
2. **Go to "Settings" tab**
3. **Find "Source" section**
4. **Set Root Directory to**: `/backend`
5. **Click "Save"**

**Expected Result:**
```
✅ Root Directory: /backend
✅ Railway will only deploy files from your /backend directory
```

---

## 🗄️ Step 4: Add MongoDB Database

1. **In your Railway project dashboard**
2. **Click "+ New"** 
3. **Select "Database"**
4. **Choose "Add MongoDB"**
5. **Wait 2-5 minutes** for provisioning

**Expected Result:**
```
✅ MongoDB service created
✅ Internal connection: mongodb://mongo:27017
```

---

## 🔧 Step 5: Set Environment Variables

1. **Click on your backend service** (not the MongoDB service)
2. **Go to "Variables" tab**
3. **Add these variables**:

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `MONGO_URL` | `mongodb://mongo:27017` | Database connection |
| `DB_NAME` | `nanobox_production` | Your database name |
| `ENVIRONMENT` | `production` | App environment |
| `DEBUG` | `False` | Disable debug mode |

**How to add each variable:**
- Click "+ New Variable"
- Enter Variable Name
- Enter Value
- Click "Add"

**Expected Result:**
```
✅ 4 environment variables configured
✅ Variables available to your application
```

---

## 🚀 Step 6: Deploy Your Application

1. **Railway should auto-deploy** after configuration
2. **If not, go to "Deployments" tab**
3. **Click "Deploy Latest Commit"**

**Watch the Build Process:**
```
🔄 Building...
📦 Installing Python dependencies
🐍 Python 3.11 detected
📋 Installing from requirements.txt
🚀 Starting: uvicorn server:app --host 0.0.0.0 --port $PORT
✅ Deployment successful!
```

---

## 🌐 Step 7: Get Your Railway Domain

1. **In your backend service settings**
2. **Go to "Domains" section**
3. **Railway provides a domain like**: `your-app-name.up.railway.app`
4. **Copy this domain**

**Expected Result:**
```
✅ Your Railway URL: https://nanobox-build-2-production-abc123.up.railway.app
```

---

## ✅ Step 8: Test Your Deployed API

### Test Health Endpoint:
```bash
curl https://your-railway-domain.up.railway.app/api/
```
**Expected Response:**
```json
{"status":"healthy","message":"Backend API is running on Railway!"}
```

### Test Database Health:
```bash
curl https://your-railway-domain.up.railway.app/api/health
```
**Expected Response:**
```json
{"status":"healthy","message":"Database connection successful"}
```

### View API Documentation:
```
https://your-railway-domain.up.railway.app/api/docs
```

---

## 🎯 Files Needed in Your Repository

**Before deploying, ensure your `/backend` directory has:**

### Required Files:
- ✅ `server.py` (or your main FastAPI file)
- ✅ `requirements.txt` (with all dependencies)

### Optional but Recommended:
- 📝 `railway.toml` (deployment config)
- 📝 `Procfile` (process definition)

**Create these files if missing:**

**railway.toml:**
```toml
[build]
# Railway auto-detects Python

[deploy]
startCommand = "uvicorn server:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/"
healthcheckTimeout = 100
```

**Procfile:**
```
web: uvicorn server:app --host 0.0.0.0 --port $PORT
```

---

## 🔧 Common Issues & Solutions

### Issue 1: Build Fails
**Error:** `Could not find a version that satisfies the requirement`
**Solution:** Check your `requirements.txt` file in `/backend` directory

### Issue 2: App Won't Start  
**Error:** `ImportError` or module not found
**Solution:** Verify your main file name in Procfile matches your actual file

### Issue 3: Database Connection Fails
**Error:** Database connection timeout
**Solution:** 
- Ensure MongoDB service is running
- Wait 5-10 minutes for full provisioning
- Check `MONGO_URL` environment variable

---

## 📊 Final Verification Checklist

Once deployed, verify these work:

- [ ] Health check: `GET /api/` returns healthy status
- [ ] Database check: `GET /api/health` returns successful  
- [ ] API docs: `/api/docs` loads Swagger UI
- [ ] Your endpoints: Test your specific API endpoints
- [ ] Logs: Check Railway dashboard for any errors

---

## 🎉 Success! Your API is Live

When everything works, you'll have:

✅ **FastAPI backend running on Railway**  
✅ **Managed MongoDB database**  
✅ **Automatic scaling and monitoring**  
✅ **HTTPS enabled by default**  
✅ **API documentation available**  

**Your Railway URL will be**: `https://your-app.up.railway.app`

---

## 🔗 Quick Links After Deployment

- **Railway Dashboard**: Monitor your app performance
- **Logs**: Real-time application logs  
- **Metrics**: CPU, memory, and request metrics
- **Domains**: Add custom domains if needed

**Ready to deploy? Follow these steps and your FastAPI backend will be live on Railway! 🚀**
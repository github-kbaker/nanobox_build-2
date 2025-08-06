# 🎯 Quick Deploy Checklist for Railway.app

## ⚡ Fast Track Deployment

### 1. Go to Railway
```
🌐 https://railway.app/new
```

### 2. Connect Repository  
```
📦 Deploy from GitHub repo
🔍 Search: github-kbaker/nanobox_build-2
✅ Deploy Now
```

### 3. Set Root Directory
```
⚙️ Service Settings → Source
📁 Root Directory: /backend
💾 Save
```

### 4. Add MongoDB
```
➕ + New → Database → MongoDB
⏱️ Wait 2-5 minutes for provisioning
```

### 5. Environment Variables
```
MONGO_URL=mongodb://mongo:27017
DB_NAME=nanobox_production
ENVIRONMENT=production  
DEBUG=False
```

### 6. Deploy & Test
```
🚀 Auto-deploys or click "Deploy Latest Commit"
🌐 Get your Railway domain
✅ Test: https://your-domain.up.railway.app/api/
```

---

## 🎉 Expected Results

**✅ API Health Check:**
```json
{"status":"healthy","message":"Backend API is running on Railway!"}
```

**✅ Database Check:**
```json
{"status":"healthy","message":"Database connection successful"}
```

**✅ API Docs Available:**
```
https://your-domain.up.railway.app/api/docs
```

---

## 🚨 Need Help?

**If deployment fails:**
1. Check Railway build logs
2. Verify `/backend` has `requirements.txt`  
3. Ensure MongoDB service is running
4. Wait 10 minutes for full provisioning

**Your FastAPI backend will be live on Railway in ~5-10 minutes! 🎯**
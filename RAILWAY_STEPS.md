# Railway.app Step-by-Step Deployment Process

## 🚀 Step 2: Railway Deployment Process

### 2.1 Create Railway Project

1. **Go to Railway.app**
   ```
   https://railway.app/new
   ```

2. **Connect GitHub Repository**
   - Click "Deploy from GitHub repo"
   - Search for: `github-kbaker/nanobox_build-2`
   - Click "Deploy Now"

   **Expected Result:**
   ```
   ✅ Repository connected: github-kbaker/nanobox_build-2
   ✅ Railway project created: nanobox-build-2-production
   ```

### 2.2 Configure Root Directory (🎯 CRITICAL STEP)

1. **Access Service Settings**
   - Click on your service (shows as "nanobox-build-2")
   - Go to "Settings" tab

2. **Set Root Directory**
   - Find "Source" section
   - Set **Root Directory** to: `/backend`
   - Click "Save"

   **Expected Result:**
   ```
   ✅ Root Directory: /backend
   ✅ Railway will only deploy files from /backend directory
   ```

### 2.3 Environment Variables Configuration

**Click "Variables" tab and add:**

| Variable | Value | Description |
|----------|-------|-------------|
| `MONGO_URL` | `mongodb://mongo:27017` | MongoDB connection |
| `DB_NAME` | `nanobox_production` | Your database name |
| `ENVIRONMENT` | `production` | App environment |
| `DEBUG` | `False` | Disable debug mode |

**Expected Result:**
```
✅ 4 environment variables configured
✅ Variables will be available to your application
```

---

## 📊 Step 3: Add MongoDB Service

### 3.1 Add Database Service

1. **Add New Service**
   - In your Railway project dashboard
   - Click "+ New" → "Database" → "Add MongoDB"

2. **Wait for Provisioning**
   ```
   ⏳ Provisioning MongoDB... (2-5 minutes)
   ✅ MongoDB service ready
   ✅ Internal URL: mongodb://mongo:27017
   ```

### 3.2 Connect Services

**Expected Result:**
```
✅ Backend service can access MongoDB via: mongodb://mongo:27017
✅ No additional configuration needed (Railway handles networking)
```

---

## 🔄 Step 4: Deploy and Monitor

### 4.1 Trigger Deployment

1. **Manual Deploy**
   - Go to "Deployments" tab
   - Click "Deploy Latest Commit"

2. **Build Process** (Watch in real-time)
   ```
   🔄 Starting deployment...
   📦 Installing Python dependencies from requirements.txt
   🐍 Python 3.11 detected
   📋 Installing packages: fastapi, uvicorn, motor, ...
   🚀 Starting application: uvicorn server:app --host 0.0.0.0 --port $PORT
   ✅ Deployment successful!
   ```

### 4.2 Get Your Domain

**Railway provides domain:**
```
✅ Your app URL: https://nanobox-build-2-production-abc123.up.railway.app
```

---

## ✅ Step 5: Testing & Results

### 5.1 Test Health Check

**Visit your domain:**
```bash
curl https://your-domain.up.railway.app/api/

# Expected Response:
{
  "status": "healthy", 
  "message": "Backend API is running on Railway!"
}
```

### 5.2 Test Database Connection

```bash
curl https://your-domain.up.railway.app/api/health

# Expected Response:
{
  "status": "healthy",
  "message": "Database connection successful"
}
```

### 5.3 Access API Documentation

```
https://your-domain.up.railway.app/api/docs
```

**Expected Result:**
```
✅ Swagger UI loads successfully
✅ All endpoints visible and testable
✅ Interactive API documentation available
```
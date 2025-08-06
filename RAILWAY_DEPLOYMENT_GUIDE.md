# Railway.app Deployment Guide - FastAPI Backend

This guide will help you deploy your FastAPI backend to Railway.app with MongoDB addon.

## Prerequisites
- Railway.app account ([sign up here](https://railway.app/))
- Your backend code ready (already prepared!)

## Step 1: Create Railway Project

1. **Login to Railway.app**
   - Go to [railway.app](https://railway.app/)
   - Click "Login" and sign in with GitHub/Google/Email

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo" 
   - Connect your GitHub account if not already connected
   - Select your repository containing this code

## Step 2: Configure Root Directory

1. **Set Root Directory**
   - After selecting your repo, Railway will show deployment settings
   - In the "Settings" tab, find "Source"
   - Set **Root Directory** to: `/backend`
   - This tells Railway to deploy only the backend folder

## Step 3: Add MongoDB Service

1. **Add Database**
   - In your Railway project dashboard
   - Click "New Service" → "Database" 
   - Select "MongoDB"
   - Railway will provision a MongoDB instance
   - Note: MongoDB addon may take a few minutes to provision

2. **Get MongoDB Connection Details**
   - Click on your MongoDB service
   - Go to "Connect" tab
   - Copy the connection string (it looks like: `mongodb://mongo:27017`)

## Step 4: Configure Environment Variables

1. **Access Backend Service Settings**
   - Click on your backend service (not the MongoDB service)
   - Go to "Variables" tab

2. **Add Required Environment Variables**
   ```
   MONGO_URL=mongodb://mongo:27017
   DB_NAME=production_database
   ENVIRONMENT=production
   DEBUG=False
   ALLOWED_ORIGINS=*
   ```

   **Important Notes:**
   - `MONGO_URL`: Use the connection string from your MongoDB service
   - `DB_NAME`: Choose your production database name
   - `ALLOWED_ORIGINS`: Set to `*` for now, update with your frontend domain later

## Step 5: Deploy Configuration

1. **Verify Build Settings**
   - Railway should automatically detect Python
   - Build command: (leave empty - Railway auto-detects)
   - Start command: Should be set to `uvicorn server:app --host 0.0.0.0 --port $PORT`

2. **Deploy**
   - Click "Deploy" 
   - Railway will build and deploy your application
   - First deployment may take 3-5 minutes

## Step 6: Verify Deployment

1. **Get Your Railway Domain**
   - In your backend service, go to "Settings" → "Domains"
   - Railway provides a domain like: `your-app-name.up.railway.app`
   - Copy this domain

2. **Test Your API**
   - Visit: `https://your-domain.up.railway.app/api/`
   - Should return: `{"status": "healthy", "message": "Backend API is running on Railway!"}`
   - API documentation: `https://your-domain.up.railway.app/api/docs`

3. **Test Database Connection**
   - Visit: `https://your-domain.up.railway.app/api/health`
   - Should return: `{"status": "healthy", "message": "Database connection successful"}`

## Step 7: Update Frontend (If Applicable)

If you have a frontend that needs to connect to this backend:

1. **Update Frontend Environment Variable**
   ```
   REACT_APP_BACKEND_URL=https://your-railway-domain.up.railway.app
   ```

2. **Update CORS Settings**
   - Go back to Railway backend service
   - Update `ALLOWED_ORIGINS` environment variable
   - Set it to your frontend domain(s), e.g.: `https://your-frontend.com`

## Common Issues & Solutions

### Issue 1: Build Fails
**Solution**: Check that `requirements.txt` is in the `/backend` directory and contains all dependencies.

### Issue 2: Database Connection Failed
**Solutions**: 
- Verify MongoDB service is running
- Check `MONGO_URL` environment variable matches MongoDB service connection string
- Wait for MongoDB provisioning to complete (can take 5-10 minutes)

### Issue 3: CORS Errors
**Solution**: Update `ALLOWED_ORIGINS` environment variable with your frontend domain.

### Issue 4: 502 Bad Gateway
**Solutions**:
- Check application logs in Railway dashboard
- Verify start command is correct: `uvicorn server:app --host 0.0.0.0 --port $PORT`
- Ensure app binds to `0.0.0.0` not `localhost`

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URL` | MongoDB connection string | `mongodb://mongo:27017` |
| `DB_NAME` | Database name | `production_database` |
| `ENVIRONMENT` | Deployment environment | `production` |
| `DEBUG` | Enable debug logging | `False` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `https://myapp.com,https://www.myapp.com` |

## API Endpoints

After successful deployment, your API will be available at:

- **Root**: `GET /api/` - Health check
- **Health**: `GET /api/health` - Database health check  
- **Create Status**: `POST /api/status` - Create status check
- **Get Status**: `GET /api/status` - Get all status checks
- **Documentation**: `GET /api/docs` - Swagger UI
- **Alternative Docs**: `GET /api/redoc` - ReDoc UI

## Next Steps

1. **Custom Domain** (Optional)
   - Go to Settings → Domains
   - Add your custom domain
   - Update DNS records as instructed

2. **Environment-specific Configs**
   - Add different environment variables for staging/production
   - Consider using Railway's branch deployments for different environments

3. **Monitoring**
   - Use Railway's built-in logs and metrics
   - Set up alerts for service downtime

4. **Scaling** (If Needed)
   - Railway auto-scales based on usage
   - Monitor performance in Railway dashboard

## Support

- Railway Documentation: https://docs.railway.app/
- Railway Discord: https://discord.gg/railway
- FastAPI Documentation: https://fastapi.tiangolo.com/

Your FastAPI backend is now production-ready for Railway deployment! 🚀
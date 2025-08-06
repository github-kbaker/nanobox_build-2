from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection with fallback for Railway
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'test_database')

client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Create the main app without a prefix
app = FastAPI(
    title="Backend API",
    description="FastAPI backend deployed on Railway",
    version="1.0.0",
    docs_url="/api/docs",  # Swagger UI will be available at /api/docs
    redoc_url="/api/redoc"  # ReDoc will be available at /api/redoc
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class HealthCheck(BaseModel):
    status: str
    message: str

# Health check endpoint (Railway uses this)
@api_router.get("/", response_model=HealthCheck)
async def root():
    return HealthCheck(status="healthy", message="Backend API is running on Railway!")

@api_router.get("/health", response_model=HealthCheck)
async def health_check():
    try:
        # Test database connection
        await db.list_collection_names()
        return HealthCheck(status="healthy", message="Database connection successful")
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return HealthCheck(status="unhealthy", message=f"Database connection failed: {str(e)}")

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

# CORS configuration for production
allowed_origins = os.environ.get('ALLOWED_ORIGINS', '*').split(',') if os.environ.get('ALLOWED_ORIGINS') != '*' else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging for production
log_level = logging.DEBUG if os.environ.get('DEBUG', 'False').lower() == 'true' else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Backend API...")
    logger.info(f"Environment: {os.environ.get('ENVIRONMENT', 'development')}")
    logger.info(f"Database: {db_name}")
    logger.info(f"MongoDB URL: {mongo_url.split('@')[-1] if '@' in mongo_url else 'localhost'}")

@app.on_event("shutdown")
async def shutdown_db_client():
    logger.info("Shutting down Backend API...")
    client.close()

# Root redirect to API docs for convenience
@app.get("/")
async def redirect_to_docs():
    return {"message": "Backend API is running! Visit /api/docs for API documentation"}
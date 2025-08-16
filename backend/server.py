from fastapi import FastAPI, APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime, timedelta
import psutil
import asyncio
import random
import subprocess
import ptyprocess
import json
import base64


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# HTTP Basic Auth for terminal access
security = HTTPBasic()

# Test users for container access
TEST_USERS = {
    "testuser": "testpass123",
    "admin": "admin123", 
    "developer": "dev123",
    "nanobox": "nanobox123"
}

# Active terminal sessions
active_sessions = {}


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class SystemStatus(BaseModel):
    status: str
    uptime: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ContainerInfo(BaseModel):
    id: str
    name: str
    status: str
    image: str
    created: datetime
    ports: List[str]
    cpu_usage: float
    memory_usage: float

class ResourceMetrics(BaseModel):
    cpu_usage: float
    cpu_count: int
    memory_total: float
    memory_available: float
    memory_usage: float
    disk_total: float
    disk_free: float
    disk_usage: float
    network_sent: float
    network_recv: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TerminalAuth(BaseModel):
    username: str
    password: str
    container_id: str

class TerminalSession(BaseModel):
    session_id: str
    container_id: str
    username: str
    created_at: datetime
    last_activity: datetime

# Helper functions for system monitoring
def get_system_status():
    """Get current system status and metrics"""
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        return SystemStatus(
            status="online" if cpu_usage < 90 else "warning",
            uptime=str(uptime).split('.')[0],
            cpu_usage=round(cpu_usage, 1),
            memory_usage=round(memory.percent, 1),
            disk_usage=round(disk.percent, 1)
        )
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return SystemStatus(
            status="error",
            uptime="unknown",
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_usage=0.0
        )

def get_resource_metrics():
    """Get detailed resource metrics"""
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        return ResourceMetrics(
            cpu_usage=round(cpu_usage, 1),
            cpu_count=psutil.cpu_count(),
            memory_total=round(memory.total / (1024**3), 2),  # GB
            memory_available=round(memory.available / (1024**3), 2),
            memory_usage=round(memory.percent, 1),
            disk_total=round(disk.total / (1024**3), 2),
            disk_free=round(disk.free / (1024**3), 2),
            disk_usage=round(disk.percent, 1),
            network_sent=round(network.bytes_sent / (1024**2), 2),  # MB
            network_recv=round(network.bytes_recv / (1024**2), 2)
        )
    except Exception as e:
        logger.error(f"Error getting resource metrics: {e}")
        return ResourceMetrics(
            cpu_usage=0.0, cpu_count=0, memory_total=0.0, memory_available=0.0,
            memory_usage=0.0, disk_total=0.0, disk_free=0.0, disk_usage=0.0,
            network_sent=0.0, network_recv=0.0
        )

# Container state storage (in a real app, this would be in a database)
container_states = {
    "nanobox-web-001": "running",
    "nanobox-api-001": "running", 
    "nanobox-db-001": "running",
    "nanobox-cache-001": "stopped"
}

def get_mock_containers():
    """Generate mock container data for demo purposes"""
    containers = [
        {
            "id": "nanobox-web-001",
            "name": "nanobox-web",
            "status": container_states["nanobox-web-001"],
            "image": "nginx:1.21-alpine",
            "ports": ["80:8080", "443:8443"],
            "cpu_usage": round(random.uniform(5, 25), 1) if container_states["nanobox-web-001"] == "running" else 0.0,
            "memory_usage": round(random.uniform(10, 50), 1) if container_states["nanobox-web-001"] == "running" else 0.0
        },
        {
            "id": "nanobox-api-001",
            "name": "nanobox-api",
            "status": container_states["nanobox-api-001"],
            "image": "python:3.9-slim",
            "ports": ["8001:8001"],
            "cpu_usage": round(random.uniform(2, 15), 1) if container_states["nanobox-api-001"] == "running" else 0.0,
            "memory_usage": round(random.uniform(15, 40), 1) if container_states["nanobox-api-001"] == "running" else 0.0
        },
        {
            "id": "nanobox-db-001",
            "name": "nanobox-db",
            "status": container_states["nanobox-db-001"],
            "image": "mongodb:5.0",
            "ports": ["27017:27017"],
            "cpu_usage": round(random.uniform(1, 10), 1) if container_states["nanobox-db-001"] == "running" else 0.0,
            "memory_usage": round(random.uniform(20, 60), 1) if container_states["nanobox-db-001"] == "running" else 0.0
        },
        {
            "id": "nanobox-cache-001",
            "name": "nanobox-cache",
            "status": container_states["nanobox-cache-001"],
            "image": "redis:6.2-alpine",
            "ports": ["6379:6379"],
            "cpu_usage": round(random.uniform(1, 5), 1) if container_states["nanobox-cache-001"] == "running" else 0.0,
            "memory_usage": round(random.uniform(5, 20), 1) if container_states["nanobox-cache-001"] == "running" else 0.0
        }
    ]
    
    return [ContainerInfo(
        id=c["id"],
        name=c["name"],
        status=c["status"],
        image=c["image"],
        created=datetime.now() - timedelta(seconds=random.randint(3600, 86400)),
        ports=c["ports"],
        cpu_usage=c["cpu_usage"],
        memory_usage=c["memory_usage"]
    ) for c in containers]

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

# Nanobox DevStack API endpoints
@api_router.get("/nanobox/status")
async def get_nanobox_status():
    """Get overall system status for Nanobox DevStack"""
    return get_system_status()

@api_router.get("/nanobox/health")
async def health_check():
    """Health check endpoint for Nanobox DevStack"""
    return {
        "status": "healthy",
        "service": "nanobox-devstack",
        "version": "1.0.0",
        "timestamp": datetime.utcnow()
    }

@api_router.get("/nanobox/metrics", response_model=ResourceMetrics)
async def get_system_metrics():
    """Get detailed system resource metrics"""
    return get_resource_metrics()

@api_router.get("/nanobox/containers", response_model=List[ContainerInfo])
async def get_containers():
    """Get list of containers with their status and metrics"""
    return get_mock_containers()

@api_router.post("/nanobox/containers/{container_id}/start")
async def start_container(container_id: str):
    """Start a container"""
    if container_id in container_states:
        container_states[container_id] = "running"
        await asyncio.sleep(1)  # Simulate operation delay
        return {
            "message": f"Container {container_id} started successfully",
            "status": "running",
            "timestamp": datetime.utcnow()
        }
    else:
        raise HTTPException(status_code=404, detail=f"Container {container_id} not found")

@api_router.post("/nanobox/containers/{container_id}/stop")
async def stop_container(container_id: str):
    """Stop a container"""
    if container_id in container_states:
        container_states[container_id] = "stopped"
        await asyncio.sleep(1)  # Simulate operation delay
        return {
            "message": f"Container {container_id} stopped successfully",
            "status": "stopped",
            "timestamp": datetime.utcnow()
        }
    else:
        raise HTTPException(status_code=404, detail=f"Container {container_id} not found")

@api_router.post("/nanobox/containers/{container_id}/restart")
async def restart_container(container_id: str):
    """Restart a container"""
    if container_id in container_states:
        container_states[container_id] = "running"
        await asyncio.sleep(2)  # Simulate operation delay
        return {
            "message": f"Container {container_id} restarted successfully",
            "status": "running",
            "timestamp": datetime.utcnow()
        }
    else:
        raise HTTPException(status_code=404, detail=f"Container {container_id} not found")

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

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

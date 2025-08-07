from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List, Dict, Optional
import uuid
import asyncio
import json
import os
from datetime import datetime, timedelta
import random

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'nanobox_devstack')

try:
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    environments_collection = db.environments
    services_collection = db.services
    logs_collection = db.logs
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")

# Pydantic models
class ServiceCreate(BaseModel):
    name: str
    type: str  # web, database, cache, api
    port: int
    environment_id: str

class Service(BaseModel):
    id: str
    name: str
    type: str
    port: int
    status: str  # running, stopped, error
    cpu_usage: float
    memory_usage: float
    uptime: str
    environment_id: str
    created_at: datetime

class EnvironmentCreate(BaseModel):
    name: str
    stack_type: str  # LAMP, MEAN, Django, FastAPI, etc.
    description: Optional[str] = ""

class Environment(BaseModel):
    id: str
    name: str
    stack_type: str
    description: str
    status: str  # running, stopped, partial, error
    created_at: datetime
    services: List[Service] = []

class LogEntry(BaseModel):
    id: str
    service_id: str
    level: str  # info, warning, error
    message: str
    timestamp: datetime

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Mock data generators
STACK_TEMPLATES = {
    "LAMP": ["apache", "mysql", "php"],
    "MEAN": ["mongodb", "express", "angular", "nodejs"],
    "Django": ["django", "postgresql", "redis"],
    "FastAPI": ["fastapi", "postgresql", "redis"],
    "Next.js": ["nextjs", "mongodb", "nodejs"],
    "Vue.js": ["vue", "nodejs", "mysql"]
}

SERVICE_TYPES = {
    "apache": {"type": "web", "port": 80},
    "mysql": {"type": "database", "port": 3306},
    "php": {"type": "runtime", "port": 9000},
    "mongodb": {"type": "database", "port": 27017},
    "express": {"type": "api", "port": 3000},
    "angular": {"type": "web", "port": 4200},
    "nodejs": {"type": "runtime", "port": 3000},
    "django": {"type": "web", "port": 8000},
    "postgresql": {"type": "database", "port": 5432},
    "redis": {"type": "cache", "port": 6379},
    "fastapi": {"type": "api", "port": 8000},
    "nextjs": {"type": "web", "port": 3000},
    "vue": {"type": "web", "port": 8080}
}

def generate_mock_metrics():
    return {
        "cpu_usage": round(random.uniform(5, 95), 1),
        "memory_usage": round(random.uniform(10, 80), 1),
        "uptime": f"{random.randint(1, 48)}h {random.randint(1, 59)}m"
    }

# API Routes
@app.get("/api/environments", response_model=List[Environment])
async def get_environments():
    """Get all development environments"""
    environments = []
    for env_doc in environments_collection.find():
        # Get services for this environment
        services = []
        for service_doc in services_collection.find({"environment_id": env_doc["id"]}):
            service_doc["created_at"] = service_doc.get("created_at", datetime.now())
            services.append(Service(**service_doc))
        
        env_doc["created_at"] = env_doc.get("created_at", datetime.now())
        env_doc["services"] = services
        environments.append(Environment(**env_doc))
    
    return environments

@app.post("/api/environments", response_model=Environment)
async def create_environment(environment: EnvironmentCreate):
    """Create a new development environment"""
    env_id = str(uuid.uuid4())
    
    # Create environment
    env_data = {
        "id": env_id,
        "name": environment.name,
        "stack_type": environment.stack_type,
        "description": environment.description,
        "status": "stopped",
        "created_at": datetime.now()
    }
    
    environments_collection.insert_one(env_data)
    
    # Create default services based on stack type
    services = []
    if environment.stack_type in STACK_TEMPLATES:
        for service_name in STACK_TEMPLATES[environment.stack_type]:
            service_config = SERVICE_TYPES.get(service_name, {"type": "unknown", "port": 8000})
            metrics = generate_mock_metrics()
            
            service_data = {
                "id": str(uuid.uuid4()),
                "name": service_name,
                "type": service_config["type"],
                "port": service_config["port"],
                "status": "stopped",
                "cpu_usage": metrics["cpu_usage"],
                "memory_usage": metrics["memory_usage"],
                "uptime": metrics["uptime"],
                "environment_id": env_id,
                "created_at": datetime.now()
            }
            
            services_collection.insert_one(service_data)
            services.append(Service(**service_data))
    
    env_data["services"] = services
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        "type": "environment_created",
        "data": env_data,
        "timestamp": datetime.now().isoformat()
    }, default=str))
    
    return Environment(**env_data)

@app.put("/api/environments/{environment_id}/start")
async def start_environment(environment_id: str):
    """Start an environment and all its services"""
    env = environments_collection.find_one({"id": environment_id})
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    # Update environment status
    environments_collection.update_one(
        {"id": environment_id},
        {"$set": {"status": "running"}}
    )
    
    # Update all services to running
    services_collection.update_many(
        {"environment_id": environment_id},
        {"$set": {"status": "running"}}
    )
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        "type": "environment_started",
        "environment_id": environment_id,
        "timestamp": datetime.now().isoformat()
    }))
    
    return {"message": "Environment started successfully"}

@app.put("/api/environments/{environment_id}/stop")
async def stop_environment(environment_id: str):
    """Stop an environment and all its services"""
    env = environments_collection.find_one({"id": environment_id})
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    # Update environment status
    environments_collection.update_one(
        {"id": environment_id},
        {"$set": {"status": "stopped"}}
    )
    
    # Update all services to stopped
    services_collection.update_many(
        {"environment_id": environment_id},
        {"$set": {"status": "stopped"}}
    )
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        "type": "environment_stopped",
        "environment_id": environment_id,
        "timestamp": datetime.now().isoformat()
    }))
    
    return {"message": "Environment stopped successfully"}

@app.delete("/api/environments/{environment_id}")
async def delete_environment(environment_id: str):
    """Delete an environment and all its services"""
    # Delete services first
    services_collection.delete_many({"environment_id": environment_id})
    
    # Delete environment
    result = environments_collection.delete_one({"id": environment_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        "type": "environment_deleted",
        "environment_id": environment_id,
        "timestamp": datetime.now().isoformat()
    }))
    
    return {"message": "Environment deleted successfully"}

@app.get("/api/services/{service_id}/logs")
async def get_service_logs(service_id: str, limit: int = 50):
    """Get logs for a specific service"""
    logs = []
    for log_doc in logs_collection.find({"service_id": service_id}).sort("timestamp", -1).limit(limit):
        logs.append(LogEntry(**log_doc))
    
    return logs[::-1]  # Return in chronological order

# Add this endpoint (around line 280, before the health check)
@app.get("/api/")
async def api_root():
    return {"status": "healthy", "service": "Nanobox DevStack Manager", "message": "API is running"}
    
@app.put("/api/services/{service_id}/toggle")
async def toggle_service(service_id: str):
    """Toggle service status (start/stop)"""
    service = services_collection.find_one({"id": service_id})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    new_status = "stopped" if service["status"] == "running" else "running"
    
    # Update service status
    services_collection.update_one(
        {"id": service_id},
        {"$set": {"status": new_status}}
    )
    
    # Generate mock log entry
    log_data = {
        "id": str(uuid.uuid4()),
        "service_id": service_id,
        "level": "info",
        "message": f"Service {service['name']} {new_status}",
        "timestamp": datetime.now()
    }
    logs_collection.insert_one(log_data)
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        "type": "service_toggled",
        "service_id": service_id,
        "status": new_status,
        "timestamp": datetime.now().isoformat()
    }))
    
    return {"message": f"Service {new_status} successfully"}

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic status updates
            await asyncio.sleep(3)  # Update every 3 seconds
            
            # Generate mock real-time data
            services = list(services_collection.find({}))
            for service in services:
                if service["status"] == "running":
                    metrics = generate_mock_metrics()
                    services_collection.update_one(
                        {"id": service["id"]},
                        {"$set": {
                            "cpu_usage": metrics["cpu_usage"],
                            "memory_usage": metrics["memory_usage"],
                            "uptime": metrics["uptime"]
                        }}
                    )
                    
                    # Randomly generate log entries
                    if random.random() < 0.3:  # 30% chance
                        log_levels = ["info", "warning", "error"]
                        log_messages = [
                            f"Processing request on port {service['port']}",
                            f"Memory usage at {metrics['memory_usage']}%",
                            f"Connection established",
                            f"Cache hit rate: {random.randint(70, 95)}%",
                            f"Query executed in {random.randint(10, 200)}ms"
                        ]
                        
                        log_data = {
                            "id": str(uuid.uuid4()),
                            "service_id": service["id"],
                            "level": random.choice(log_levels),
                            "message": random.choice(log_messages),
                            "timestamp": datetime.now()
                        }
                        logs_collection.insert_one(log_data)
            
            # Broadcast real-time update
            await manager.broadcast(json.dumps({
                "type": "metrics_update",
                "timestamp": datetime.now().isoformat()
            }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Nanobox DevStack Manager"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

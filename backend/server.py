from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Optional, List
import os
import logging
import uuid
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Nanobox DevStack Manager", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "nanobox_devstack")

# Database connection
client = None
db = None
environments_collection = None

# Models
class StatusCheck(BaseModel):
    name: str
    status: str
    message: str = ""

class EnvironmentStatus(str, Enum):
    running = "running"
    stopped = "stopped" 
    pending = "pending"

class ServiceStatus(str, Enum):
    running = "running"
    stopped = "stopped"
    pending = "pending"

class Service(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str
    status: ServiceStatus = ServiceStatus.stopped
    port: Optional[int] = None

class Environment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    status: EnvironmentStatus = EnvironmentStatus.stopped
    services: List[Service] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EnvironmentCreate(BaseModel):
    name: str
    services: Optional[List[dict]] = []

class DockerInstanceStatus(str, Enum):
    running = "running"
    stopped = "stopped"
    paused = "paused"
    restarting = "restarting"
    dead = "dead"

class DockerInstance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    container_id: Optional[str] = None
    name: str
    image: str
    status: DockerInstanceStatus = DockerInstanceStatus.stopped
    ports: Optional[Dict[str, str]] = {}
    environment_vars: Optional[Dict[str, str]] = {}
    volumes: Optional[Dict[str, str]] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DockerInstanceCreate(BaseModel):
    name: str
    image: str
    ports: Optional[Dict[str, str]] = {}
    environment_vars: Optional[Dict[str, str]] = {}
    volumes: Optional[Dict[str, str]] = {}

# Database connection
try:
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    environments_collection = db.environments
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")
    environments_collection = None

# API Router
api_router = APIRouter(prefix="/api")

@api_router.get("/")
async def api_root():
    return {
        "status": "healthy",
        "service": "Nanobox DevStack Manager",
        "message": "API is running"
    }

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Nanobox DevStack Manager"
    }

@api_router.get("/status")
async def get_status():
    if environments_collection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable")
    
    try:
        status_checks = await environments_collection.find().to_list(1000)
        return status_checks
    except Exception as e:
        logging.error(f"Failed to get status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/status")
async def create_status(status: StatusCheck):
    if environments_collection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable")
    
    try:
        status_dict = status.dict()
        status_dict["created_at"] = datetime.utcnow()
        await environments_collection.insert_one(status_dict)
        return status
    except Exception as e:
        logging.error(f"Failed to create status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Environment Management Endpoints
@api_router.get("/environments", response_model=List[Environment])
async def get_environments():
    if environments_collection is None:
        return {"detail": "Database connection unavailable"}
    
    try:
        environments = await db.environments.find().to_list(1000)
        return [Environment(**env) for env in environments]
    except Exception as e:
        logging.error(f"Failed to get environments: {e}")
        return []

@api_router.post("/environments", response_model=Environment)
async def create_environment(env_data: EnvironmentCreate):
    if environments_collection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable")
    
    try:
        # Create default services if none provided
        default_services = [
            {"name": "React Frontend", "type": "web", "status": "stopped"},
            {"name": "FastAPI Backend", "type": "api", "status": "stopped"},
            {"name": "MongoDB", "type": "database", "status": "stopped"}
        ]
        
        services = []
        service_configs = env_data.services if env_data.services else default_services
        
        for service_config in service_configs:
            service = Service(
                name=service_config.get("name", "Unknown Service"),
                type=service_config.get("type", "service"),
                status=ServiceStatus(service_config.get("status", "stopped"))
            )
            services.append(service.dict())
        
        environment = Environment(
            name=env_data.name,
            status=EnvironmentStatus.stopped,
            services=services
        )
        
        # Save to database
        env_dict = environment.dict()
        await environments_collection.insert_one(env_dict)
        
        logging.info(f"Created environment: {environment.name}")
        return environment
    
    except Exception as e:
        logging.error(f"Failed to create environment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create environment: {str(e)}")

@api_router.put("/environments/{env_id}/start")
async def start_environment(env_id: str):
    if environments_collection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable")
    
    try:
        result = await environments_collection.update_one(
            {"id": env_id},
            {
                "$set": {
                    "status": "running",
                    "services.$[].status": "running"
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Environment not found")
            
        return {"message": f"Environment {env_id} started successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to start environment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start environment: {str(e)}")

@api_router.put("/environments/{env_id}/stop")
async def stop_environment(env_id: str):
    if environments_collection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable")
        
    try:
        result = await environments_collection.update_one(
            {"id": env_id},
            {
                "$set": {
                    "status": "stopped",
                    "services.$[].status": "stopped"
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Environment not found")
            
        return {"message": f"Environment {env_id} stopped successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to stop environment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop environment: {str(e)}")

@api_router.delete("/environments/{env_id}")
async def delete_environment(env_id: str):
    if environments_collection is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable")
        
    try:
        result = await environments_collection.delete_one({"id": env_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Environment not found")
            
        return {"message": f"Environment {env_id} deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to delete environment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete environment: {str(e)}")

@api_router.get("/services/{service_id}/logs")
async def get_service_logs(service_id: str):
    # Mock logs for demonstration
    mock_logs = [
        "2025-08-11 01:30:00 - Service started",
        "2025-08-11 01:30:01 - Initializing connections", 
        "2025-08-11 01:30:02 - Service ready",
        "2025-08-11 01:30:15 - Processing requests",
        "2025-08-11 01:30:30 - Health check passed"
    ]
    
    return {"logs": mock_logs, "service_id": service_id}

# Docker Management Endpoints

@api_router.get("/docker/instances", response_model=List[DockerInstance])
async def get_docker_instances():
    """Get all Docker instances"""
    try:
        instances = await db.docker_instances.find().to_list(1000)
        return [DockerInstance(**instance) for instance in instances]
    except Exception as e:
        logging.error(f"Failed to get Docker instances: {e}")
        return []

@api_router.post("/docker/instances", response_model=DockerInstance)
async def create_docker_instance(instance_data: DockerInstanceCreate):
    """Create a new Docker instance"""
    try:
        instance = DockerInstance(
            name=instance_data.name,
            image=instance_data.image,
            ports=instance_data.ports or {},
            environment_vars=instance_data.environment_vars or {},
            volumes=instance_data.volumes or {},
            status=DockerInstanceStatus.stopped
        )
        
        # Save to database
        instance_dict = instance.dict()
        await db.docker_instances.insert_one(instance_dict)
        
        logging.info(f"Created Docker instance: {instance.name}")
        return instance
        
    except Exception as e:
        logging.error(f"Failed to create Docker instance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create Docker instance: {str(e)}")

@api_router.put("/docker/instances/{instance_id}/start")
async def start_docker_instance(instance_id: str):
    """Start a Docker container"""
    try:
        # Get instance from database
        instance = await db.docker_instances.find_one({"id": instance_id})
        if not instance:
            raise HTTPException(status_code=404, detail="Docker instance not found")
        
        # Build docker run command
        cmd = ["docker", "run", "-d", "--name", instance["name"]]
        
        # Add port mappings
        for container_port, host_port in instance.get("ports", {}).items():
            cmd.extend(["-p", f"{host_port}:{container_port}"])
        
        # Add environment variables
        for env_key, env_value in instance.get("environment_vars", {}).items():
            cmd.extend(["-e", f"{env_key}={env_value}"])
        
        # Add volume mounts
        for host_path, container_path in instance.get("volumes", {}).items():
            cmd.extend(["-v", f"{host_path}:{container_path}"])
        
        # Add image
        cmd.append(instance["image"])
        
        # Execute docker command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            container_id = result.stdout.strip()
            
            # Update database with container ID and status
            await db.docker_instances.update_one(
                {"id": instance_id},
                {
                    "$set": {
                        "container_id": container_id,
                        "status": "running",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {"message": f"Docker instance {instance['name']} started successfully", "container_id": container_id}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to start container: {result.stderr}")
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to start Docker instance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start Docker instance: {str(e)}")

@api_router.put("/docker/instances/{instance_id}/stop")
async def stop_docker_instance(instance_id: str):
    """Stop a Docker container"""
    try:
        # Get instance from database
        instance = await db.docker_instances.find_one({"id": instance_id})
        if not instance:
            raise HTTPException(status_code=404, detail="Docker instance not found")
        
        if not instance.get("container_id"):
            raise HTTPException(status_code=400, detail="No running container found")
        
        # Stop the container
        result = subprocess.run(["docker", "stop", instance["container_id"]], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Update database
            await db.docker_instances.update_one(
                {"id": instance_id},
                {
                    "$set": {
                        "status": "stopped",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {"message": f"Docker instance {instance['name']} stopped successfully"}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to stop container: {result.stderr}")
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to stop Docker instance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop Docker instance: {str(e)}")

@api_router.delete("/docker/instances/{instance_id}")
async def delete_docker_instance(instance_id: str):
    """Delete a Docker instance (stops and removes container)"""
    try:
        # Get instance from database
        instance = await db.docker_instances.find_one({"id": instance_id})
        if not instance:
            raise HTTPException(status_code=404, detail="Docker instance not found")
        
        # Stop and remove container if it exists
        if instance.get("container_id"):
            subprocess.run(["docker", "stop", instance["container_id"]], capture_output=True)
            subprocess.run(["docker", "rm", instance["container_id"]], capture_output=True)
        
        # Remove from database
        result = await db.docker_instances.delete_one({"id": instance_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Docker instance not found")
            
        return {"message": f"Docker instance {instance['name']} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to delete Docker instance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete Docker instance: {str(e)}")

@api_router.get("/docker/instances/{instance_id}/logs")
async def get_docker_logs(instance_id: str):
    """Get logs from a Docker container"""
    try:
        # Get instance from database
        instance = await db.docker_instances.find_one({"id": instance_id})
        if not instance:
            raise HTTPException(status_code=404, detail="Docker instance not found")
        
        if not instance.get("container_id"):
            return {"logs": ["Container not running"], "instance_id": instance_id}
        
        # Get container logs
        result = subprocess.run(
            ["docker", "logs", "--tail", "100", instance["container_id"]], 
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            logs = result.stdout.split('\n') if result.stdout else []
            return {"logs": logs, "instance_id": instance_id}
        else:
            return {"logs": [f"Error getting logs: {result.stderr}"], "instance_id": instance_id}
            
    except Exception as e:
        logging.error(f"Failed to get Docker logs: {e}")
        return {"logs": [f"Error: {str(e)}"], "instance_id": instance_id}

@api_router.get("/docker/images")
async def get_docker_images():
    """Get available Docker images"""
    try:
        result = subprocess.run(["docker", "images", "--format", "table {{.Repository}}:{{.Tag}}"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            images = [line.strip() for line in result.stdout.split('\n')[1:] if line.strip()]
            return {"images": images}
        else:
            return {"images": []}
            
    except Exception as e:
        logging.error(f"Failed to get Docker images: {e}")
        return {"images": []}
        
# Include the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

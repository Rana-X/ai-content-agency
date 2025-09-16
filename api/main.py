"""
FastAPI application for AI Content Agency
Provides HTTP endpoints for the blog generation workflow
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import uuid
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.basic import run_workflow
from state.storage import StateManager
from config import config


# === FASTAPI APP AND MODELS ===

app = FastAPI(
    title="AI Content Agency API",
    version="1.0.0",
    description="API for AI-powered blog content generation using LangGraph"
)

class CreateProjectRequest(BaseModel):
    """Request model for creating a new project"""
    topic: str
    mode: str = "standard"

class ProjectResponse(BaseModel):
    """Response model for project creation"""
    project_id: str
    message: str


# === INITIALIZE STATE MANAGER ===

# Initialize state manager (will be set during startup)
state_manager = None


# === BACKGROUND WORKFLOW EXECUTION ===

async def run_workflow_with_storage(project_id: str, topic: str, mode: str):
    """
    Execute workflow in background and save results to database.
    
    Args:
        project_id: The project UUID
        topic: The blog topic
        mode: Workflow mode (standard or quick)
    """
    try:
        # Run the synchronous workflow
        print(f"Starting workflow for project {project_id}")
        result = run_workflow(topic, mode)
        
        # Update the result's project_id to match our generated one
        result["project_id"] = project_id
        result["updated_at"] = datetime.utcnow().isoformat()
        
        # If workflow completed successfully, mark as complete
        if result.get("final_content"):
            result["status"] = "completed"
            result["completed_at"] = datetime.utcnow().isoformat()
        
        # Update state in database
        await state_manager.update_state(project_id, result)
        print(f"Workflow completed for project {project_id}")
        
    except Exception as e:
        print(f"Workflow failed for project {project_id}: {str(e)}")
        
        # Save error state
        error_updates = {
            "status": "failed",
            "error": str(e),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        try:
            await state_manager.update_state(project_id, error_updates)
        except Exception as update_error:
            print(f"Failed to save error state: {str(update_error)}")


# === API ENDPOINTS ===

@app.post("/create", response_model=ProjectResponse)
async def create_project(request: CreateProjectRequest, background_tasks: BackgroundTasks):
    """
    Start a new blog generation workflow.
    
    Creates a project in the database and starts the workflow in the background.
    Returns immediately with the project ID.
    """
    
    # Check if state manager is initialized
    if not state_manager:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable - database not connected")
    
    # Validate topic length
    words = request.topic.split()
    if len(words) < 2:
        raise HTTPException(status_code=400, detail="Topic must be at least 2 words")
    if len(words) > 50:
        raise HTTPException(status_code=400, detail="Topic must be 50 words or less")
    
    # Validate mode
    if request.mode not in ["standard", "quick"]:
        raise HTTPException(status_code=400, detail="Mode must be 'standard' or 'quick'")
    
    try:
        # Create project in database
        initial_state = await state_manager.create_project(request.topic, request.mode)
        project_id = initial_state["project_id"]
        
        # Add workflow execution to background tasks
        background_tasks.add_task(
            run_workflow_with_storage,
            project_id,
            request.topic,
            request.mode
        )
        
        return ProjectResponse(
            project_id=project_id,
            message=f"Workflow started successfully in {request.mode} mode"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")


@app.get("/status/{project_id}")
async def get_project_status(project_id: str):
    """
    Get current status of a project.
    
    Returns the current stage of the workflow and basic metrics.
    """
    
    try:
        # Get state from database
        state = await state_manager.get_state(project_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Determine detailed status based on state
        if state.get("status") == "failed":
            status = "failed"
            message = state.get("error", "Unknown error occurred")
        elif state.get("status") == "completed" or state.get("final_content"):
            status = "complete"
            message = "Content generation complete"
        elif state.get("status") == "review_complete":
            status = "complete"
            message = "Review complete, content ready"
        elif state.get("draft"):
            status = "reviewing"
            message = "Content is being reviewed"
        elif state.get("research_notes"):
            status = "writing"
            message = "Generating content based on research"
        elif state.get("status") in ["initialized", "research_complete"]:
            status = "researching"
            message = "Researching topic"
        else:
            status = "in_progress"
            message = "Processing your request"
        
        return {
            "project_id": project_id,
            "status": status,
            "message": message,
            "topic": state.get("topic", ""),
            "mode": state.get("mode", ""),
            "word_count": state.get("word_count", 0),
            "quality_score": state.get("quality_score", 0),
            "created_at": state.get("created_at", ""),
            "updated_at": state.get("updated_at", "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving status: {str(e)}")


@app.get("/content/{project_id}")
async def get_project_content(project_id: str):
    """
    Get the final generated content.
    
    Returns the complete blog post with metadata when ready.
    """
    
    try:
        # Get state from database
        state = await state_manager.get_state(project_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if content is ready
        if not state.get("final_content"):
            # Provide current status if not ready
            current_status = state.get("status", "unknown")
            
            status_message = "Content not ready yet"
            if current_status == "failed":
                status_message = f"Generation failed: {state.get('error', 'Unknown error')}"
            elif state.get("draft"):
                status_message = "Content is being reviewed"
            elif state.get("research_notes"):
                status_message = "Content is being written"
            else:
                status_message = "Content generation in progress"
            
            return {
                "project_id": project_id,
                "status": "in_progress",
                "message": status_message,
                "topic": state.get("topic", ""),
                "current_stage": current_status
            }
        
        # Return complete content
        return {
            "project_id": project_id,
            "status": "complete",
            "topic": state.get("topic", ""),
            "mode": state.get("mode", ""),
            "content": state["final_content"],
            "word_count": state.get("word_count", 0),
            "quality_score": state.get("quality_score", 0),
            "research_notes": state.get("research_notes", []),
            "sources": state.get("sources", []),
            "review_comments": state.get("review_comments", []),
            "created_at": state.get("created_at", ""),
            "completed_at": state.get("completed_at", "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving content: {str(e)}")


@app.get("/state/{project_id}")
async def get_project_state(project_id: str):
    """
    Get the complete state object.
    
    Useful for debugging - returns the full ContentState.
    """
    
    try:
        state = await state_manager.get_state(project_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return state
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving state: {str(e)}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Verifies API is running and checks configuration/database status.
    """
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
    
    # Check configuration validity
    try:
        is_valid = config.validate()
        health_status["config_valid"] = is_valid
        
        # Test database connection if config is valid
        if is_valid:
            # Try to get a non-existent project to test DB connection
            test_state = await state_manager.get_state("health-check-test")
            health_status["database"] = "connected"
        else:
            health_status["database"] = "not configured"
            
    except Exception as e:
        # Database might be down or misconfigured
        health_status["database"] = "connected" if "not found" in str(e).lower() else f"error: {str(e)[:100]}"
    
    return health_status


@app.get("/")
async def root():
    """
    API root endpoint with documentation.
    
    Provides links to docs and available endpoints.
    """
    return {
        "name": "AI Content Agency API",
        "version": "1.0.0",
        "description": "Generate AI-powered blog content using LangGraph workflows",
        "documentation": "/docs",
        "openapi": "/openapi.json",
        "health": "/health",
        "endpoints": {
            "POST /create": "Start new content generation",
            "GET /status/{project_id}": "Check project status",
            "GET /content/{project_id}": "Get generated content",
            "GET /state/{project_id}": "Get full state (debugging)",
            "GET /health": "Health check"
        }
    }


# === LIFECYCLE EVENTS ===

@app.on_event("startup")
async def startup_event():
    """
    Initialize services on API startup.
    """
    global state_manager
    
    print("=" * 60)
    print("🚀 AI Content Agency API Starting...")
    print("=" * 60)
    
    # Check LangSmith tracing configuration
    langsmith_enabled = os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"
    if langsmith_enabled:
        print("✅ LangSmith tracing enabled")
        print(f"   Project: {os.getenv('LANGCHAIN_PROJECT', 'ai-content-agency')}")
    else:
        print("ℹ️  LangSmith tracing disabled")
        print("   Set LANGCHAIN_TRACING_V2=true in .env to enable")
    
    # Validate configuration
    print("\n📋 Validating configuration...")
    try:
        if config.validate():
            print("✅ Configuration validated successfully")
            
            # Initialize state manager
            try:
                state_manager = StateManager(config.get_supabase_client())
                print("✅ Database connection established")
            except Exception as db_error:
                print(f"⚠️  Database connection failed: {str(db_error)}")
                print("   Running in demo mode without database persistence")
                # Create a mock state manager for demo purposes
                from state.storage import StateManager as SM
                class MockStateManager:
                    async def create_project(self, topic, mode):
                        return {"project_id": str(uuid.uuid4()), "topic": topic, "mode": mode, "status": "created"}
                    async def get_state(self, project_id):
                        return None
                    async def update_state(self, project_id, updates):
                        pass
                state_manager = MockStateManager()
        else:
            print("⚠️  Configuration incomplete")
            print("   Some features may not work properly")
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        print("   API will start but may have limited functionality")
    
    print("\n" + "=" * 60)
    print(f"✨ API ready at http://0.0.0.0:8000")
    print(f"📚 Interactive docs at http://0.0.0.0:8000/docs")
    print(f"📋 OpenAPI spec at http://0.0.0.0:8000/openapi.json")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on API shutdown.
    """
    print("\n👋 API shutting down...")


# === MAIN EXECUTION ===

if __name__ == "__main__":
    import uvicorn
    
    print("Starting AI Content Agency API server...")
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
"""
State storage operations for AI Content Agency
Handles all database operations with Supabase
"""

import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from supabase import Client

from .models import ContentState, create_initial_state, WorkflowStatus


class StateManager:
    """
    Manages state persistence and retrieval with Supabase.
    Simplified for learning - focuses on core CRUD and checkpoint operations.
    """
    
    def __init__(self, supabase_client: Client):
        """
        Initialize the state manager.
        
        Args:
            supabase_client: Configured Supabase client
        """
        self.client = supabase_client
        self.table_name = "project_states"
        self.history_table = "state_history"
        self.feedback_table = "human_feedback"
    
    # === CORE CRUD OPERATIONS ===
    
    async def create_project(self, topic: str, mode: str = "standard") -> ContentState:
        """
        Create a new project with initial state.
        
        Args:
            topic: The blog topic
            mode: "standard" or "quick" workflow
            
        Returns:
            Created ContentState
        """
        # Create initial state
        state = create_initial_state(topic, mode)
        
        # Insert into database
        data = {
            "project_id": state["project_id"],
            "thread_id": state["thread_id"],
            "topic": state["topic"],
            "mode": state["mode"],
            "status": state["status"],
            "state_data": state,
            "created_at": state["created_at"],
            "updated_at": state["updated_at"]
        }
        
        result = self.client.table(self.table_name).insert(data).execute()
        
        if result.data:
            return state
        else:
            raise Exception("Failed to create project")
    
    async def get_state(self, project_id: str) -> Optional[ContentState]:
        """
        Retrieve current state for a project.
        
        Args:
            project_id: The project UUID
            
        Returns:
            ContentState or None if not found
        """
        result = self.client.table(self.table_name)\
            .select("*")\
            .eq("project_id", project_id)\
            .single()\
            .execute()
        
        if result.data:
            return result.data["state_data"]
        return None
    
    async def update_state(self, project_id: str, updates: Dict[str, Any]) -> ContentState:
        """
        Update specific fields in the state.
        
        Args:
            project_id: The project UUID
            updates: Dictionary of fields to update
            
        Returns:
            Updated ContentState
        """
        # Get current state
        current_state = await self.get_state(project_id)
        if not current_state:
            raise ValueError(f"Project {project_id} not found")
        
        # Apply updates
        updated_state = {**current_state, **updates}
        updated_state["updated_at"] = datetime.utcnow().isoformat()
        
        # Update database
        data = {
            "status": updated_state.get("status", current_state["status"]),
            "state_data": updated_state,
            "updated_at": updated_state["updated_at"]
        }
        
        result = self.client.table(self.table_name)\
            .update(data)\
            .eq("project_id", project_id)\
            .execute()
        
        if result.data:
            return updated_state
        else:
            raise Exception(f"Failed to update project {project_id}")
    
    async def delete_project(self, project_id: str) -> bool:
        """
        Delete a project and all related data.
        
        Args:
            project_id: The project UUID
            
        Returns:
            True if deleted successfully
        """
        result = self.client.table(self.table_name)\
            .delete()\
            .eq("project_id", project_id)\
            .execute()
        
        return len(result.data) > 0
    
    # === QUERY OPERATIONS ===
    
    async def list_projects(self, status: str = None, mode: str = None) -> List[ContentState]:
        """
        List projects with optional filtering.
        
        Args:
            status: Filter by status (optional)
            mode: Filter by mode (optional)
            
        Returns:
            List of ContentState objects
        """
        query = self.client.table(self.table_name).select("*")
        
        if status:
            query = query.eq("status", status)
        if mode:
            query = query.eq("mode", mode)
        
        result = query.order("created_at", desc=True).execute()
        
        return [row["state_data"] for row in result.data]
    
    async def get_active_projects(self) -> List[ContentState]:
        """
        Get all active (non-completed) projects.
        
        Returns:
            List of active ContentState objects
        """
        result = self.client.table(self.table_name)\
            .select("*")\
            .neq("status", WorkflowStatus.COMPLETED)\
            .neq("status", WorkflowStatus.FAILED)\
            .order("updated_at", desc=True)\
            .execute()
        
        return [row["state_data"] for row in result.data]
    
    # === CHECKPOINT OPERATIONS (TIME TRAVEL) ===
    
    async def save_checkpoint(self, project_id: str, name: str = None) -> str:
        """
        Save a checkpoint of the current state.
        
        Args:
            project_id: The project UUID
            name: Optional checkpoint name
            
        Returns:
            Checkpoint ID
        """
        # Get current state
        state = await self.get_state(project_id)
        if not state:
            raise ValueError(f"Project {project_id} not found")
        
        # Generate checkpoint ID
        checkpoint_id = str(uuid.uuid4())
        
        # Create checkpoint name if not provided
        if not name:
            name = f"checkpoint_{state['status']}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Save to history table
        data = {
            "checkpoint_id": checkpoint_id,
            "project_id": project_id,
            "checkpoint_name": name,
            "state_snapshot": state,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = self.client.table(self.history_table).insert(data).execute()
        
        if result.data:
            # Update state with checkpoint info
            checkpoint_history = state.get("checkpoint_history", [])
            checkpoint_history.append(checkpoint_id)
            
            # Keep only last 10 checkpoints
            if len(checkpoint_history) > 10:
                checkpoint_history = checkpoint_history[-10:]
            
            await self.update_state(project_id, {
                "checkpoint_history": checkpoint_history,
                "current_checkpoint": checkpoint_id
            })
            
            return checkpoint_id
        else:
            raise Exception("Failed to save checkpoint")
    
    async def restore_checkpoint(self, project_id: str, checkpoint_id: str) -> ContentState:
        """
        Restore state from a checkpoint.
        
        Args:
            project_id: The project UUID
            checkpoint_id: The checkpoint to restore
            
        Returns:
            Restored ContentState
        """
        # Get checkpoint
        result = self.client.table(self.history_table)\
            .select("*")\
            .eq("checkpoint_id", checkpoint_id)\
            .single()\
            .execute()
        
        if not result.data:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        # Restore state
        restored_state = result.data["state_snapshot"]
        restored_state["updated_at"] = datetime.utcnow().isoformat()
        restored_state["current_checkpoint"] = checkpoint_id
        
        # Update database
        data = {
            "status": restored_state["status"],
            "state_data": restored_state,
            "updated_at": restored_state["updated_at"]
        }
        
        update_result = self.client.table(self.table_name)\
            .update(data)\
            .eq("project_id", project_id)\
            .execute()
        
        if update_result.data:
            return restored_state
        else:
            raise Exception(f"Failed to restore checkpoint {checkpoint_id}")
    
    async def list_checkpoints(self, project_id: str) -> List[Dict[str, Any]]:
        """
        List all checkpoints for a project.
        
        Args:
            project_id: The project UUID
            
        Returns:
            List of checkpoint metadata
        """
        result = self.client.table(self.history_table)\
            .select("checkpoint_id, checkpoint_name, created_at")\
            .eq("project_id", project_id)\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()
        
        return result.data
    
    # === HUMAN FEEDBACK OPERATIONS ===
    
    async def save_human_feedback(self, project_id: str, feedback: str, 
                                 action: str, approved: bool = False) -> str:
        """
        Save human feedback for a project.
        
        Args:
            project_id: The project UUID
            feedback: The feedback text
            action: The action taken (approve, revise, reject)
            approved: Whether the content was approved
            
        Returns:
            Feedback ID
        """
        feedback_id = str(uuid.uuid4())
        
        data = {
            "feedback_id": feedback_id,
            "project_id": project_id,
            "feedback": feedback,
            "action": action,
            "approved": approved,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = self.client.table(self.feedback_table).insert(data).execute()
        
        if result.data:
            # Update state with feedback
            await self.update_state(project_id, {
                "human_feedback": feedback,
                "human_approved": approved
            })
            return feedback_id
        else:
            raise Exception("Failed to save feedback")
    
    # === LANGRAPH INTEGRATION ===
    
    def to_langraph_state(self, state: ContentState) -> Dict[str, Any]:
        """
        Convert ContentState to LangGraph format.
        
        Args:
            state: ContentState object
            
        Returns:
            Dictionary for LangGraph
        """
        return dict(state)
    
    def from_langraph_state(self, langraph_state: Dict[str, Any]) -> ContentState:
        """
        Convert LangGraph state to ContentState.
        
        Args:
            langraph_state: State from LangGraph
            
        Returns:
            ContentState object
        """
        return ContentState(**langraph_state)
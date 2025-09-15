"""
State models for AI Content Agency
Simplified schema focused on learning LangGraph features
"""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class ContentState(TypedDict):
    """
    Core state structure for the content creation workflow.
    Simplified for learning LangGraph - LangSmith handles monitoring.
    """
    
    # === IDENTIFICATION ===
    project_id: str                # UUID for unique project identification
    thread_id: str                 # LangGraph thread ID for checkpointing
    
    # === PROJECT INFO ===
    topic: str                     # The blog topic user requested
    mode: str                      # "standard" or "quick" workflow
    status: str                    # Current status (created, researching, writing, etc.)
    
    # === RESEARCH DATA ===
    research_notes: List[str]     # Extracted facts from research
    sources: List[str]            # URLs/references found
    research_attempts: int         # Counter for retry logic (max 2)
    parallel_results: Dict[str, Any]  # Results from parallel searches
    
    # === CONTENT ===
    draft: str                     # Initial blog post draft
    final_content: str            # Approved final version
    word_count: int               # Word count of current content
    
    # === QUALITY & REVIEW ===
    quality_score: float          # 0-100 score from review agent
    revision_count: int           # How many times revised
    review_comments: List[str]    # Feedback from review agent
    
    # === WORKFLOW CONTROL ===
    next_action: str              # What to do next (e.g., "research", "write")
    assigned_agent: str           # Current agent working
    enable_research: bool         # Dynamic graph: include research?
    enable_revision: bool         # Dynamic graph: allow revisions?
    
    # === HUMAN INTERACTION ===
    human_feedback: str           # Feedback from human reviewer
    human_approved: bool          # Whether human approved the content
    
    # === TIME TRAVEL ===
    checkpoint_history: List[str] # Last 10 checkpoint IDs
    current_checkpoint: str       # Active checkpoint ID
    
    # === TIMESTAMPS ===
    created_at: str               # When project started
    updated_at: str               # Last modification time
    completed_at: Optional[str]   # When project finished


def create_initial_state(topic: str, mode: str = "standard") -> ContentState:
    """
    Create an initial state for a new project.
    
    Args:
        topic: The blog topic to write about
        mode: Either "standard" (full workflow) or "quick" (simplified)
    
    Returns:
        Initial ContentState with all defaults set
    """
    import uuid
    
    now = datetime.utcnow().isoformat()
    project_id = str(uuid.uuid4())
    
    return ContentState(
        # Identification
        project_id=project_id,
        thread_id=f"thread_{project_id}",
        
        # Project Info
        topic=topic,
        mode=mode,
        status="created",
        
        # Research Data
        research_notes=[],
        sources=[],
        research_attempts=0,
        parallel_results={},
        
        # Content
        draft="",
        final_content="",
        word_count=0,
        
        # Quality & Review
        quality_score=0.0,
        revision_count=0,
        review_comments=[],
        
        # Workflow Control
        next_action="start",
        assigned_agent="manager",
        enable_research=(mode == "standard"),  # Research only in standard mode
        enable_revision=(mode == "standard"),  # Revisions only in standard mode
        
        # Human Interaction
        human_feedback="",
        human_approved=False,
        
        # Time Travel
        checkpoint_history=[],
        current_checkpoint="",
        
        # Timestamps
        created_at=now,
        updated_at=now,
        completed_at=None
    )


# Status constants
class WorkflowStatus:
    """Workflow status constants"""
    CREATED = "created"
    STARTED = "started"
    RESEARCHING = "researching"
    WRITING = "writing"
    REVIEWING = "reviewing"
    PENDING_HUMAN_REVIEW = "pending_human_review"
    REVISING = "revising"
    COMPLETED = "completed"
    FAILED = "failed"


# Agent names
class AgentNames:
    """Agent name constants"""
    MANAGER = "manager"
    RESEARCH = "research"
    WRITER = "writer"
    REVIEW = "review"


# Actions
class Actions:
    """Workflow action constants"""
    START = "start"
    RESEARCH = "research"
    WRITE = "write"
    REVIEW = "review"
    REVISE = "revise"
    COMPLETE = "complete"
    HUMAN_REVIEW = "human_review"
"""
Manager Agent for AI Content Agency
Handles initial topic processing and workflow routing
"""

import uuid
import re
from datetime import datetime
from typing import Dict, List, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state.models import ContentState


class ManagerAgent:
    """Manager agent that initializes projects and routes workflows"""
    
    def __init__(self):
        """Initialize Manager Agent - no parameters needed"""
        pass
    
    def process(self, topic: str, mode: str) -> ContentState:
        """
        Process topic and initialize project state
        
        Args:
            topic: Raw user input topic
            mode: Either "standard" or "quick"
            
        Returns:
            Initialized ContentState dictionary
        """
        try:
            # Step 1: Validate topic
            self._validate_topic(topic)
            
            # Step 2: Clean topic
            cleaned_topic = self._clean_topic(topic)
            
            # Step 3: Extract keywords
            keywords = self._extract_keywords(cleaned_topic)
            
            # Step 4: Create state
            project_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            
            # Initialize ContentState with all fields
            state = ContentState(
                # Identification
                project_id=project_id,
                thread_id=project_id,  # Same as project_id for now
                
                # Core fields
                topic=cleaned_topic,
                mode=mode,
                status="initialized",
                
                # Research data
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
                
                # Workflow Control - Set based on mode
                next_action="research" if mode == "standard" else "write",
                assigned_agent="research" if mode == "standard" else "writer",
                enable_research=(mode == "standard"),
                enable_revision=(mode == "standard"),
                
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
            
            return state
            
        except Exception as e:
            raise Exception(f"Failed to initialize project: {e}")
    
    def _validate_topic(self, topic: str) -> None:
        """
        Validate topic meets requirements
        
        Args:
            topic: Raw topic string
            
        Raises:
            ValueError: If topic doesn't meet requirements
        """
        # Check if empty or None
        if not topic or topic == "":
            raise ValueError("Topic cannot be empty")
        
        # Check word count
        words = topic.strip().split()
        
        if len(words) < 2:
            raise ValueError("Topic too short")
        
        if len(words) > 50:
            raise ValueError("Topic too long")
        
        # Check if contains actual words (not just special chars/numbers)
        text_only = re.sub(r'[^a-zA-Z]', '', topic)
        if not text_only:
            raise ValueError("Topic must contain words")
    
    def _clean_topic(self, topic: str) -> str:
        """
        Clean and format topic text
        
        Args:
            topic: Raw topic string
            
        Returns:
            Cleaned topic string
        """
        # Strip leading/trailing whitespace
        cleaned = topic.strip()
        
        # Replace multiple spaces with single space
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove special characters except letters, numbers, spaces, hyphens
        cleaned = re.sub(r'[^a-zA-Z0-9\s-]', '', cleaned)
        
        # Title case (capitalize first letter of each word)
        cleaned = cleaned.title()
        
        return cleaned
    
    def _extract_keywords(self, cleaned_topic: str) -> List[str]:
        """
        Extract keywords from cleaned topic
        
        Args:
            cleaned_topic: Cleaned topic string
            
        Returns:
            List of keywords (max 5)
        """
        # Convert to lowercase
        text = cleaned_topic.lower()
        
        # Split by spaces
        words = text.split()
        
        # Define stop words
        stop_words = [
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "as", "is", "was", "are",
            "were", "write", "about", "blog", "post", "article"
        ]
        
        # Remove stop words and keep only words > 2 characters
        keywords = [
            word for word in words 
            if word not in stop_words and len(word) > 2
        ]
        
        # Return max 5 keywords
        return keywords[:5]
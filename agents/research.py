"""
Research Agent for AI Content Agency
Performs single web search using Brave Search API
"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state.models import ContentState
from config import Config


class ResearchAgent:
    """Research agent that performs web searches"""
    
    def __init__(self):
        """Initialize Research Agent with Brave API key from environment"""
        config = Config()
        self.api_key = config.BRAVE_API_KEY
        if not self.api_key:
            raise ValueError("BRAVE_API_KEY not found in environment variables")
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
    
    def process(self, state: ContentState) -> ContentState:
        """
        Process state by performing web search
        
        Args:
            state: Current ContentState
            
        Returns:
            Updated ContentState with research results
        """
        # 1. Get topic from state
        topic = state["topic"]
        
        try:
            # 2. Perform single search with max 5 results using requests
            response = requests.get(
                self.base_url,
                headers={"X-Subscription-Token": self.api_key},
                params={"q": topic, "count": 5}
            )
            
            # 3. Extract notes and sources from results
            research_notes = []
            sources = []
            
            if response.status_code == 200:
                data = response.json()
                
                # Get web results from the search
                if "web" in data and "results" in data["web"]:
                    for result in data["web"]["results"]:
                        # Extract description as research note
                        if "description" in result:
                            research_notes.append(result["description"])
                        
                        # Extract url as source
                        if "url" in result:
                            sources.append(result["url"])
            
            # 4. Update state fields
            state["research_notes"] = research_notes
            state["sources"] = sources
            state["research_attempts"] = 1
            state["status"] = "research_complete"
            state["next_action"] = "write"
            state["assigned_agent"] = "writer"
            
        except Exception as e:
            # If search fails, set failed status but still return state
            state["research_notes"] = []
            state["sources"] = []
            state["research_attempts"] = 1
            state["status"] = "research_failed"
            state["next_action"] = "write"
            state["assigned_agent"] = "writer"
        
        # 5. Return updated state
        return state
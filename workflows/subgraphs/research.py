"""
Research Subgraph for AI Content Agency
Breaks research into three specialized nodes: Search, Extract, Summarize
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from state.models import ContentState
import requests
import json

# Brave API Configuration (copied from ResearchAgent)
BRAVE_API_KEY = "BSArHGdATae0Nala46gDn4e_ck_5ngk"
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"


def search_node(state: ContentState) -> dict:
    """Performs the web search using Brave API"""
    topic = state.get("topic", "")
    
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    params = {
        "q": topic,
        "count": 5
    }
    
    try:
        response = requests.get(BRAVE_SEARCH_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Return only the updates - use parallel_results for temp storage
        return {
            "parallel_results": {
                "raw_search_data": data,
                "search_success": True
            }
        }
    except Exception as e:
        return {
            "parallel_results": {
                "raw_search_data": {},
                "search_success": False
            }
        }


def extract_node(state: ContentState) -> dict:
    """Extracts descriptions and URLs from search results"""
    # Get data from parallel_results
    parallel_data = state.get("parallel_results", {})
    raw_data = parallel_data.get("raw_search_data", {})
    
    descriptions = []
    urls = []
    
    if raw_data and "web" in raw_data and "results" in raw_data["web"]:
        for result in raw_data["web"]["results"][:5]:
            if "description" in result:
                descriptions.append(result["description"])
            if "url" in result:
                urls.append(result["url"])
    
    # Return updates - add to parallel_results
    updated_parallel = dict(parallel_data)
    updated_parallel["extracted_descriptions"] = descriptions
    updated_parallel["extracted_urls"] = urls
    
    return {
        "parallel_results": updated_parallel
    }


def summarize_node(state: ContentState) -> dict:
    """Formats final research notes and updates state"""
    # Get extracted data from parallel_results
    parallel_data = state.get("parallel_results", {})
    descriptions = parallel_data.get("extracted_descriptions", [])
    urls = parallel_data.get("extracted_urls", [])
    search_success = parallel_data.get("search_success", False)
    
    # Return the final updates and clear parallel_results
    return {
        "research_notes": descriptions,
        "sources": urls,
        "research_attempts": 1,
        "status": "research_complete" if search_success else "research_failed",
        "next_action": "write",
        "assigned_agent": "writer",
        "parallel_results": {}  # Clear temp data
    }


def create_research_subgraph():
    """Creates the research subgraph with three nodes"""
    
    # Initialize the subgraph with ContentState
    subgraph = StateGraph(ContentState)
    
    # Add the three nodes
    subgraph.add_node("search", search_node)
    subgraph.add_node("extract", extract_node)
    subgraph.add_node("summarize", summarize_node)
    
    # Set entry point
    subgraph.set_entry_point("search")
    
    # Connect nodes in sequence
    subgraph.add_edge("search", "extract")
    subgraph.add_edge("extract", "summarize")
    subgraph.add_edge("summarize", END)
    
    # Compile and return
    return subgraph.compile()
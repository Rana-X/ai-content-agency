"""
Parallel Research Subgraph for AI Content Agency
Performs three concurrent searches for different aspects of the topic
"""

from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
import asyncio
import aiohttp
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from state.models import ContentState

# Brave API Configuration
BRAVE_API_KEY = "BSArHGdATae0Nala46gDn4e_ck_5ngk"
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"


async def search_brave_async(query: str, session: aiohttp.ClientSession) -> Dict:
    """Async function to search Brave API"""
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    params = {
        "q": query,
        "count": 5
    }
    
    try:
        async with session.get(BRAVE_SEARCH_URL, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Search failed for '{query}': {response.status}")
                return {}
    except Exception as e:
        print(f"Error searching for '{query}': {e}")
        return {}


def parallel_search_node(state: ContentState) -> Dict:
    """Performs three parallel searches for different aspects of the topic"""
    topic = state.get("topic", "")
    
    # Create three different search queries
    queries = [
        f"{topic} overview explanation",      # General information
        f"{topic} latest news 2024 2025",    # Recent developments
        f"{topic} statistics data facts"      # Numbers and data
    ]
    
    # Run async searches (with staggered start to avoid rate limiting)
    async def run_parallel_searches():
        async with aiohttp.ClientSession() as session:
            # Stagger the start of each request to avoid rate limiting
            async def delayed_search(query, delay):
                await asyncio.sleep(delay)
                return await search_brave_async(query, session)
            
            # Start searches with staggered delays
            results = await asyncio.gather(
                delayed_search(queries[0], 0),      # Start immediately
                delayed_search(queries[1], 1.0),    # Start after 1 second
                delayed_search(queries[2], 2.0)     # Start after 2 seconds
            )
            return results
    
    # Execute the async function
    search_results = asyncio.run(run_parallel_searches())
    
    # Store results in parallel_results field (return only updates)
    parallel_data = {
        "overview_search": search_results[0],
        "news_search": search_results[1],
        "stats_search": search_results[2],
        "search_queries": queries,
        "search_success": any(search_results)
    }
    
    print(f"Parallel searches completed:")
    print(f"  - Overview: {bool(search_results[0])}")
    print(f"  - News: {bool(search_results[1])}")
    print(f"  - Stats: {bool(search_results[2])}")
    
    return {"parallel_results": parallel_data}


def parallel_extract_node(state: ContentState) -> Dict:
    """Extracts and combines data from all three parallel searches"""
    parallel_data = state.get("parallel_results", {})
    
    all_descriptions = []
    all_urls = []
    all_titles = []
    
    # Process each search result
    for search_type in ["overview_search", "news_search", "stats_search"]:
        search_data = parallel_data.get(search_type, {})
        
        if search_data and "web" in search_data and "results" in search_data["web"]:
            for result in search_data["web"]["results"]:
                if "description" in result:
                    # Add search type prefix for clarity
                    prefix = search_type.replace("_search", "").upper()
                    description = f"[{prefix}] {result['description']}"
                    all_descriptions.append(description)
                
                if "url" in result:
                    all_urls.append(result["url"])
                
                if "title" in result:
                    all_titles.append(result["title"])
    
    # Update parallel_results with extracted data
    updated_parallel = dict(parallel_data)
    updated_parallel["extracted_descriptions"] = all_descriptions
    updated_parallel["extracted_urls"] = all_urls
    updated_parallel["extracted_titles"] = all_titles
    updated_parallel["total_results"] = len(all_descriptions)
    
    print(f"Extracted {len(all_descriptions)} descriptions from parallel searches")
    
    return {"parallel_results": updated_parallel}


def parallel_summarize_node(state: ContentState) -> Dict:
    """Formats final output from parallel search results"""
    parallel_data = state.get("parallel_results", {})
    
    # Get extracted data
    descriptions = parallel_data.get("extracted_descriptions", [])
    urls = parallel_data.get("extracted_urls", [])
    
    # Select top results (diversified from each search type)
    final_notes = []
    final_sources = []
    
    # Try to get balanced results from each search type
    overview_notes = [d for d in descriptions if "[OVERVIEW]" in d][:3]
    news_notes = [d for d in descriptions if "[NEWS]" in d][:3]
    stats_notes = [d for d in descriptions if "[STATS]" in d][:4]
    
    # Combine and clean up prefixes
    final_notes = overview_notes + news_notes + stats_notes
    final_notes = [note.replace("[OVERVIEW] ", "").replace("[NEWS] ", "").replace("[STATS] ", "") 
                   for note in final_notes]
    
    # Get unique URLs (max 10)
    final_sources = list(dict.fromkeys(urls))[:10]
    
    # Clean up parallel_results (remove temporary data)
    clean_parallel_results = {
        "search_queries": parallel_data.get("search_queries", []),
        "total_results": parallel_data.get("total_results", 0),
        "search_types": ["overview", "news", "stats"]
    }
    
    return {
        "research_notes": final_notes[:10],  # Max 10 notes
        "sources": final_sources,
        "parallel_results": clean_parallel_results,
        "research_attempts": 1,
        "status": "research_complete" if final_notes else "research_failed",
        "next_action": "write",
        "assigned_agent": "writer"
    }


def create_parallel_research_subgraph():
    """Creates the enhanced research subgraph with parallel execution"""
    
    subgraph = StateGraph(ContentState)
    
    # Add nodes
    subgraph.add_node("parallel_search", parallel_search_node)
    subgraph.add_node("parallel_extract", parallel_extract_node)
    subgraph.add_node("parallel_summarize", parallel_summarize_node)
    
    # Set flow
    subgraph.set_entry_point("parallel_search")
    subgraph.add_edge("parallel_search", "parallel_extract")
    subgraph.add_edge("parallel_extract", "parallel_summarize")
    subgraph.add_edge("parallel_summarize", END)
    
    return subgraph.compile()
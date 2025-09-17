"""
Basic Linear Workflow with Parallel Research Subgraph Integration
Connects all four agents with parallel research as a subgraph:
Manager -> Parallel Research (3 concurrent searches) -> Writer -> Review -> End
"""

from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.models import ContentState, create_initial_state
from agents.manager import ManagerAgent
from workflows.subgraphs.research_parallel import create_parallel_research_subgraph
from agents.writer import WriterAgent
from agents.review import ReviewAgent


def manager_wrapper(state: ContentState) -> ContentState:
    """
    Wrapper to adapt manager agent to state-based input.
    Manager expects (topic, mode) but workflow passes ContentState.
    """
    manager = ManagerAgent()
    # Extract topic and mode from state if they exist
    topic = state.get("topic", "")
    mode = state.get("mode", "standard")
    # Manager returns a new state
    return manager.process(topic, mode)


def create_basic_workflow():
    """
    Creates a linear workflow connecting all four agents.
    
    Flow: Manager -> Parallel Research (3 searches) -> Writer -> Review -> End
    
    Returns:
        Compiled LangGraph application with checkpointing enabled
    """
    # Create StateGraph with ContentState type
    workflow = StateGraph(ContentState)
    
    # Initialize agents
    writer_agent = WriterAgent()
    review_agent = ReviewAgent()
    
    # Add nodes with exact names
    # Manager uses wrapper, others use process directly
    workflow.add_node("manager", manager_wrapper)
    
    # Use parallel research subgraph instead of sequential
    research_subgraph = create_parallel_research_subgraph()
    workflow.add_node("research", research_subgraph)
    
    workflow.add_node("writer", writer_agent.process)
    workflow.add_node("review", review_agent.process)
    
    # Set entry point
    workflow.set_entry_point("manager")
    
    # Add linear edges - simple sequential flow
    workflow.add_edge("manager", "research")
    workflow.add_edge("research", "writer")
    workflow.add_edge("writer", "review")
    workflow.add_edge("review", END)
    
    # Compile with checkpointer for state persistence
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    
    return app


def prepare_initial_state(topic: str, mode: str = "standard") -> ContentState:
    """
    Prepare initial state for workflow execution.
    
    Args:
        topic: The blog topic to write about
        mode: Either "standard" (full workflow) or "quick" (simplified)
    
    Returns:
        Properly initialized ContentState
    """
    return create_initial_state(topic, mode)


def run_workflow(topic: str, mode: str = "standard") -> Dict[str, Any]:
    """
    Execute the complete workflow from topic to final blog post.
    
    Args:
        topic: The blog topic to write about
        mode: Either "standard" or "quick" workflow mode
    
    Returns:
        Final state dictionary with all results
    """
    # Create the workflow
    app = create_basic_workflow()
    
    # Prepare initial state
    initial_state = prepare_initial_state(topic, mode)
    
    # Create config with thread_id for checkpointing
    config = {
        "configurable": {
            "thread_id": initial_state["thread_id"]
        }
    }
    
    # Invoke workflow and get final state
    final_state = app.invoke(initial_state, config)
    
    return final_state


if __name__ == "__main__":
    """Test the basic workflow with parallel research"""
    
    print("Starting workflow test with PARALLEL RESEARCH...")
    print("-" * 50)
    
    # Test topic
    test_topic = "The Future of Artificial Intelligence in Healthcare"
    test_mode = "standard"
    
    print(f"Topic: {test_topic}")
    print(f"Mode: {test_mode}")
    print("-" * 50)
    
    try:
        # Run the workflow
        result = run_workflow(test_topic, test_mode)
        
        # Print results
        print(f"\n✅ Workflow completed successfully!")
        print(f"Project ID: {result.get('project_id')}")
        print(f"Status: {result.get('status')}")
        print(f"Word Count: {result.get('word_count')}")
        print(f"Quality Score: {result.get('quality_score')}/100")
        print(f"\nResearch Notes Found: {len(result.get('research_notes', []))}")
        print(f"Sources Found: {len(result.get('sources', []))}")
        
        # Show parallel research info
        parallel_info = result.get('parallel_results', {})
        if parallel_info:
            print(f"\nParallel Research Info:")
            print(f"  - Search types: {', '.join(parallel_info.get('search_types', []))}")
            print(f"  - Total results: {parallel_info.get('total_results', 0)}")
        
        # Show feedback from review
        review_comments = result.get('review_comments', [])
        if review_comments:
            print(f"\nReview Feedback:")
            for i, comment in enumerate(review_comments, 1):
                print(f"  {i}. {comment}")
        
        # Show preview of final content
        final_content = result.get('final_content', '')
        if final_content:
            print(f"\nFinal Content Preview (first 300 chars):")
            print("-" * 50)
            print(final_content[:300] + "...")
        
    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")
        import traceback
        traceback.print_exc()
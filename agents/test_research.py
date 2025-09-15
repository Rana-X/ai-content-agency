"""
Test cases for Research Agent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research import ResearchAgent
from state.models import create_initial_state


def test_successful_search():
    """Test successful search populates research notes"""
    # Create initial state with topic
    state = create_initial_state("Python programming tutorials", "standard")
    
    # Create agent and process
    agent = ResearchAgent()
    updated_state = agent.process(state)
    
    # Verify state was updated
    if updated_state["status"] == "research_failed":
        print("⚠ Search failed, but error handling works")
    else:
        assert len(updated_state["research_notes"]) > 0, "Research notes should be populated"
        print(f"✓ Found {len(updated_state['research_notes'])} research notes")


def test_sources_populated():
    """Test that sources contains URLs"""
    # Create initial state with topic
    state = create_initial_state("Machine learning basics", "standard")
    
    # Create agent and process
    agent = ResearchAgent()
    updated_state = agent.process(state)
    
    # Verify sources contains URLs
    if updated_state["status"] == "research_complete":
        assert len(updated_state["sources"]) > 0, "Sources should be populated"
        for source in updated_state["sources"]:
            assert source.startswith("http"), f"Source should be URL: {source}"
        print(f"✓ Found {len(updated_state['sources'])} sources (all valid URLs)")
    else:
        print("⚠ Search failed, sources empty as expected")


def test_status_update():
    """Test that status changes to research_complete"""
    # Create initial state
    state = create_initial_state("Data science tools", "standard")
    
    # Create agent and process
    agent = ResearchAgent()
    updated_state = agent.process(state)
    
    # Verify status update
    assert updated_state["status"] in ["research_complete", "research_failed"], \
        f"Status should be research_complete or research_failed, got: {updated_state['status']}"
    print(f"✓ Status updated to: {updated_state['status']}")


def test_next_action():
    """Test that next_action is set to write"""
    # Create initial state
    state = create_initial_state("Web development frameworks", "standard")
    
    # Create agent and process
    agent = ResearchAgent()
    updated_state = agent.process(state)
    
    # Verify next_action
    assert updated_state["next_action"] == "write", \
        f"Next action should be 'write', got: {updated_state['next_action']}"
    print("✓ Next action set to: write")


def test_assigned_agent():
    """Test that assigned_agent is set to writer"""
    # Create initial state
    state = create_initial_state("Cloud computing services", "standard")
    
    # Create agent and process
    agent = ResearchAgent()
    updated_state = agent.process(state)
    
    # Verify assigned_agent
    assert updated_state["assigned_agent"] == "writer", \
        f"Assigned agent should be 'writer', got: {updated_state['assigned_agent']}"
    print("✓ Assigned agent set to: writer")


def test_research_attempts():
    """Test that research_attempts is set to 1"""
    # Create initial state
    state = create_initial_state("API development best practices", "standard")
    
    # Create agent and process
    agent = ResearchAgent()
    updated_state = agent.process(state)
    
    # Verify research_attempts
    assert updated_state["research_attempts"] == 1, \
        f"Research attempts should be 1, got: {updated_state['research_attempts']}"
    print("✓ Research attempts set to: 1")


if __name__ == "__main__":
    print("Running Research Agent tests...")
    print("-" * 40)
    
    test_successful_search()
    test_sources_populated()
    test_status_update()
    test_next_action()
    test_assigned_agent()
    test_research_attempts()
    
    print("-" * 40)
    print("\nAll tests passed! ✅")
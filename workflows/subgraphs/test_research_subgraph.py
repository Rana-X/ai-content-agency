"""
Test file for Research Subgraph in isolation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.subgraphs.research import create_research_subgraph
from state.models import create_initial_state

def test_subgraph():
    # Create initial state
    state = create_initial_state("Python Programming", "standard")
    
    # Create and run subgraph
    subgraph = create_research_subgraph()
    result = subgraph.invoke(state)
    
    # Verify outputs
    print(f"Research notes: {len(result.get('research_notes', []))} items")
    print(f"Sources: {len(result.get('sources', []))} URLs")
    print(f"Status: {result.get('status')}")
    print(f"Next action: {result.get('next_action')}")
    
    # Check required fields are set
    assert result.get("research_attempts") == 1
    assert result.get("status") in ["research_complete", "research_failed"]
    assert result.get("next_action") == "write"
    assert result.get("assigned_agent") == "writer"
    
    print("✅ Subgraph test passed!")

if __name__ == "__main__":
    test_subgraph()
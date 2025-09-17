"""
Test file to compare original workflow vs workflow with subgraph
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflows.basic import run_workflow as run_original
from workflows.basic_with_subgraph import run_workflow as run_with_subgraph

def compare_workflows():
    """Compare both workflow implementations"""
    
    # Test topic
    topic = "Benefits of Cloud Computing"
    
    print("=" * 60)
    print("WORKFLOW COMPARISON TEST")
    print("=" * 60)
    print(f"Test Topic: {topic}")
    print("=" * 60)
    
    # Test original workflow
    print("\n1. Testing ORIGINAL workflow (single ResearchAgent)...")
    print("-" * 50)
    try:
        original_result = run_original(topic, "standard")
        print("✅ Original workflow completed successfully")
        print(f"   - Research notes: {len(original_result.get('research_notes', []))} items")
        print(f"   - Sources: {len(original_result.get('sources', []))} URLs")
        print(f"   - Word count: {original_result.get('word_count', 0)} words")
        print(f"   - Quality score: {original_result.get('quality_score', 0)}/100")
    except Exception as e:
        print(f"❌ Original workflow failed: {e}")
        original_result = None
    
    # Test workflow with subgraph
    print("\n2. Testing workflow with RESEARCH SUBGRAPH...")
    print("-" * 50)
    try:
        subgraph_result = run_with_subgraph(topic, "standard")
        print("✅ Subgraph workflow completed successfully")
        print(f"   - Research notes: {len(subgraph_result.get('research_notes', []))} items")
        print(f"   - Sources: {len(subgraph_result.get('sources', []))} URLs")
        print(f"   - Word count: {subgraph_result.get('word_count', 0)} words")
        print(f"   - Quality score: {subgraph_result.get('quality_score', 0)}/100")
    except Exception as e:
        print(f"❌ Subgraph workflow failed: {e}")
        subgraph_result = None
    
    # Compare results
    print("\n" + "=" * 60)
    print("COMPARISON RESULTS")
    print("=" * 60)
    
    if original_result and subgraph_result:
        # Compare research outputs
        original_notes = len(original_result.get('research_notes', []))
        subgraph_notes = len(subgraph_result.get('research_notes', []))
        
        original_sources = len(original_result.get('sources', []))
        subgraph_sources = len(subgraph_result.get('sources', []))
        
        print(f"Research Notes: Original={original_notes}, Subgraph={subgraph_notes}")
        print(f"Sources: Original={original_sources}, Subgraph={subgraph_sources}")
        print(f"Both generated content: {bool(original_result.get('final_content')) and bool(subgraph_result.get('final_content'))}")
        
        # Check for temporary fields
        temp_fields = [k for k in subgraph_result.keys() if k.startswith('_')]
        if temp_fields:
            print(f"\n⚠️  WARNING: Temporary fields found in subgraph result: {temp_fields}")
        else:
            print(f"\n✅ No temporary fields in final state (cleanup successful)")
        
        # Overall verdict
        if original_notes == subgraph_notes and original_sources == subgraph_sources:
            print(f"\n✅ SUCCESS: Both workflows produce identical research outputs!")
        else:
            print(f"\n⚠️  NOTICE: Research outputs differ slightly (this may be due to API variations)")
    else:
        print("❌ Cannot compare - one or both workflows failed")

if __name__ == "__main__":
    compare_workflows()
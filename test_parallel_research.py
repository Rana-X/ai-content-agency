"""
Test file to compare parallel vs sequential research performance
"""

import time
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflows.subgraphs.research_parallel import create_parallel_research_subgraph
from workflows.subgraphs.research import create_research_subgraph
from state.models import create_initial_state


def test_parallel_vs_sequential():
    """Compare performance and results between parallel and sequential research"""
    
    topic = "Artificial Intelligence in Healthcare"
    
    print("=" * 60)
    print("RESEARCH SUBGRAPH PERFORMANCE COMPARISON")
    print("=" * 60)
    print(f"Test Topic: {topic}")
    print("=" * 60)
    
    # Test sequential (original)
    print("\n1. Testing SEQUENTIAL research (single search)...")
    print("-" * 50)
    state1 = create_initial_state(topic, "standard")
    sequential_subgraph = create_research_subgraph()
    
    start_time = time.time()
    result1 = sequential_subgraph.invoke(state1)
    sequential_time = time.time() - start_time
    
    seq_notes = len(result1.get('research_notes', []))
    seq_sources = len(result1.get('sources', []))
    print(f"✅ Sequential completed:")
    print(f"   - Time: {sequential_time:.2f} seconds")
    print(f"   - Research notes: {seq_notes}")
    print(f"   - Sources: {seq_sources}")
    
    # Test parallel (new)
    print("\n2. Testing PARALLEL research (3 concurrent searches)...")
    print("-" * 50)
    state2 = create_initial_state(topic, "standard")
    parallel_subgraph = create_parallel_research_subgraph()
    
    start_time = time.time()
    result2 = parallel_subgraph.invoke(state2)
    parallel_time = time.time() - start_time
    
    par_notes = len(result2.get('research_notes', []))
    par_sources = len(result2.get('sources', []))
    par_queries = result2.get('parallel_results', {}).get('search_queries', [])
    
    print(f"✅ Parallel completed:")
    print(f"   - Time: {parallel_time:.2f} seconds")
    print(f"   - Research notes: {par_notes}")
    print(f"   - Sources: {par_sources}")
    print(f"   - Search queries executed:")
    for i, query in enumerate(par_queries, 1):
        print(f"     {i}. {query}")
    
    # Compare results
    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON")
    print("=" * 60)
    
    if parallel_time > 0:
        speedup = sequential_time / parallel_time
        print(f"⚡ Speed improvement: {speedup:.2f}x faster")
    else:
        print("⚡ Speed improvement: Unable to calculate")
    
    print(f"📊 Data improvement:")
    print(f"   - Notes: {par_notes} (parallel) vs {seq_notes} (sequential)")
    print(f"   - Sources: {par_sources} (parallel) vs {seq_sources} (sequential)")
    
    # Show diversity of parallel results
    if par_notes > 0:
        print(f"\n📈 Result diversity (parallel search types):")
        parallel_data = result2.get('parallel_results', {})
        print(f"   - Total results extracted: {parallel_data.get('total_results', 0)}")
        print(f"   - Search types used: {', '.join(parallel_data.get('search_types', []))}")
    
    # Success criteria
    print("\n" + "=" * 60)
    print("SUCCESS CRITERIA CHECK")
    print("=" * 60)
    
    criteria = [
        ("Three searches run simultaneously", len(par_queries) == 3),
        ("Results properly combined", par_notes > 0),
        ("Performance improvement measurable", parallel_time < sequential_time),
        ("More diverse research notes", par_notes >= seq_notes),
        ("Workflow completes end-to-end", result2.get('status') == 'research_complete')
    ]
    
    all_passed = True
    for criterion, passed in criteria:
        status = "✅" if passed else "❌"
        print(f"{status} {criterion}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All success criteria met! Parallel research is working perfectly.")
    else:
        print("⚠️ Some criteria not met. Check implementation.")
    print("=" * 60)


if __name__ == "__main__":
    test_parallel_vs_sequential()
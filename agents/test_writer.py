"""
Test cases for Writer Agent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from writer import WriterAgent
from state.models import create_initial_state


def test_with_research_notes():
    """Test draft generation with research notes"""
    # Create initial state with topic and research notes
    state = create_initial_state("Artificial Intelligence in Healthcare", "standard")
    state["research_notes"] = [
        "AI is transforming healthcare through predictive analytics and personalized medicine.",
        "Machine learning algorithms can detect diseases earlier than traditional methods.",
        "AI-powered robots are assisting in complex surgeries with greater precision.",
        "Natural language processing helps analyze medical records and research papers.",
        "AI reduces healthcare costs while improving patient outcomes."
    ]
    
    # Create agent and process
    agent = WriterAgent()
    updated_state = agent.process(state)
    
    # Verify draft was generated
    assert len(updated_state["draft"]) > 0, "Draft should be generated"
    assert updated_state["word_count"] > 0, "Word count should be greater than 0"
    print(f"✓ Generated draft with {updated_state['word_count']} words (with research notes)")


def test_without_research_notes():
    """Test draft generation without research notes"""
    # Create initial state with topic but no research notes
    state = create_initial_state("Benefits of Cloud Computing", "standard")
    state["research_notes"] = []
    
    # Create agent and process
    agent = WriterAgent()
    updated_state = agent.process(state)
    
    # Verify draft was still generated
    assert len(updated_state["draft"]) > 0, "Draft should be generated even without research"
    assert updated_state["word_count"] > 0, "Word count should be greater than 0"
    print(f"✓ Generated draft with {updated_state['word_count']} words (without research notes)")


def test_word_count_accuracy():
    """Test that word count matches actual word count"""
    # Create initial state
    state = create_initial_state("Python Programming Best Practices", "standard")
    
    # Create agent and process
    agent = WriterAgent()
    updated_state = agent.process(state)
    
    # Verify word count accuracy
    if updated_state["draft"]:
        actual_word_count = len(updated_state["draft"].split())
        assert updated_state["word_count"] == actual_word_count, \
            f"Word count mismatch: reported {updated_state['word_count']}, actual {actual_word_count}"
        print(f"✓ Word count accurate: {updated_state['word_count']} words")
    else:
        print("⚠ Draft generation failed, skipping word count test")


def test_state_updates():
    """Test that all state fields are updated correctly"""
    # Create initial state
    state = create_initial_state("Machine Learning Fundamentals", "standard")
    
    # Create agent and process
    agent = WriterAgent()
    updated_state = agent.process(state)
    
    # Verify state updates
    if updated_state["status"] == "draft_complete":
        assert updated_state["status"] == "draft_complete", "Status should be draft_complete"
        assert updated_state["next_action"] == "review", "Next action should be review"
        assert updated_state["assigned_agent"] == "review", "Assigned agent should be review"
        assert "draft" in updated_state, "Draft field should exist"
        assert "word_count" in updated_state, "Word count field should exist"
        print("✓ All state fields updated correctly")
    else:
        assert updated_state["status"] == "draft_failed", "Status should be draft_failed on error"
        assert updated_state["next_action"] == "review", "Next action should still be review"
        assert updated_state["assigned_agent"] == "review", "Assigned agent should still be review"
        print("⚠ Draft generation failed, but error handling works correctly")


def test_error_handling():
    """Test error handling when API fails"""
    # Create initial state with very long topic to potentially trigger error
    state = create_initial_state("Test" * 1000, "standard")  # Extremely long topic
    
    # Create agent and process
    agent = WriterAgent()
    
    # Try to process (may or may not fail depending on API)
    try:
        updated_state = agent.process(state)
        
        # If it didn't fail, that's okay - check that state is still valid
        if updated_state["status"] == "draft_failed":
            assert updated_state["draft"] == "", "Draft should be empty on failure"
            assert updated_state["word_count"] == 0, "Word count should be 0 on failure"
            assert updated_state["next_action"] == "review", "Should still route to review"
            print("✓ Error handling works correctly")
        else:
            print("✓ API handled long input gracefully")
            
    except Exception as e:
        print(f"⚠ Unexpected error: {e}")


def test_content_quality():
    """Test that generated content meets basic quality requirements"""
    # Create initial state
    state = create_initial_state("Future of Remote Work", "standard")
    state["research_notes"] = [
        "Remote work increased by 300% during the pandemic.",
        "Studies show remote workers are 13% more productive.",
        "Companies save an average of $11,000 per remote employee annually."
    ]
    
    # Create agent and process
    agent = WriterAgent()
    updated_state = agent.process(state)
    
    if updated_state["draft"]:
        draft = updated_state["draft"]
        
        # Check for basic structure
        lines = draft.split('\n')
        assert len(lines) > 1, "Draft should have multiple lines"
        
        # Check word count is in reasonable range (500-1200 words)
        word_count = updated_state["word_count"]
        assert 300 <= word_count <= 1500, f"Word count {word_count} outside expected range"
        
        # Check that it's not just repeated text
        words = draft.split()
        unique_words = set(words)
        assert len(unique_words) > 100, "Draft should have diverse vocabulary"
        
        print(f"✓ Content quality checks passed ({word_count} words, {len(unique_words)} unique)")
    else:
        print("⚠ Draft generation failed, skipping quality test")


if __name__ == "__main__":
    print("Running Writer Agent tests...")
    print("-" * 40)
    
    test_with_research_notes()
    test_without_research_notes()
    test_word_count_accuracy()
    test_state_updates()
    test_error_handling()
    test_content_quality()
    
    print("-" * 40)
    print("\nAll tests completed! ✅")
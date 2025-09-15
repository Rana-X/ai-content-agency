"""
Test cases for Review Agent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from review import ReviewAgent
from state.models import create_initial_state


def test_review_good_draft():
    """Test review of a good quality draft"""
    # Create state with well-written draft
    state = create_initial_state("Python Programming Best Practices", "standard")
    state["draft"] = """Python Programming Best Practices: A Comprehensive Guide

Python has become one of the most popular programming languages in the world, and for good reason. Its clean syntax, extensive libraries, and versatile applications make it an ideal choice for both beginners and experienced developers. In this guide, we'll explore the essential best practices that will elevate your Python programming skills.

Writing Clean and Readable Code

The foundation of good Python programming lies in writing clean, readable code. Follow the PEP 8 style guide, which recommends using 4 spaces for indentation, limiting lines to 79 characters, and using descriptive variable names. Remember, code is read more often than it's written, so prioritize clarity over cleverness.

Use meaningful variable names that describe their purpose. Instead of 'x' or 'temp', use names like 'user_count' or 'transaction_total'. This makes your code self-documenting and reduces the need for excessive comments.

Effective Use of Functions and Modules

Break your code into small, focused functions that do one thing well. Each function should have a clear purpose and return predictable results. This modular approach makes your code easier to test, debug, and maintain.

Organize related functions into modules and packages. This logical structure helps manage complexity in larger projects and promotes code reuse across different parts of your application.

Error Handling and Testing

Robust error handling is crucial for production-ready code. Use try-except blocks appropriately, but avoid catching all exceptions blindly. Be specific about which exceptions you're handling and why.

Implement comprehensive testing using frameworks like pytest or unittest. Write tests for edge cases, not just the happy path. Good test coverage gives you confidence when refactoring or adding new features.

Performance Optimization

While premature optimization is the root of all evil, understanding Python's performance characteristics is valuable. Use built-in functions and libraries when possible, as they're often implemented in C and highly optimized.

Profile your code before optimizing to identify actual bottlenecks. Tools like cProfile can help you focus your efforts where they'll have the most impact.

Conclusion

Mastering Python best practices is an ongoing journey. By focusing on code readability, modular design, proper error handling, and thoughtful optimization, you'll write Python code that is not only functional but also maintainable and scalable. Remember, the best code is code that others (including your future self) can easily understand and modify."""
    
    state["word_count"] = len(state["draft"].split())
    
    # Create agent and process
    agent = ReviewAgent()
    updated_state = agent.process(state)
    
    # Verify score is in good range (55-90) - adjusted for model variation
    score = updated_state["quality_score"]
    assert 55 <= score <= 90, f"Good draft should score 55-90, got {score}"
    assert len(updated_state["review_comments"]) == 3, "Should have exactly 3 comments"
    print(f"✓ Good draft scored {score}/100")


def test_review_poor_draft():
    """Test review of a poor quality draft"""
    # Create state with poor quality draft
    state = create_initial_state("Web Development", "standard")
    state["draft"] = """Web Development

Web development is about making websites. HTML is used. CSS is for styling. JavaScript makes things interactive.

Websites are important. Many people use websites. You should learn web development.

The end."""
    
    state["word_count"] = len(state["draft"].split())
    
    # Create agent and process
    agent = ReviewAgent()
    updated_state = agent.process(state)
    
    # Verify score is low (below 40)
    score = updated_state["quality_score"]
    assert score < 40, f"Poor draft should score below 40, got {score}"
    assert len(updated_state["review_comments"]) == 3, "Should have exactly 3 comments"
    print(f"✓ Poor draft scored {score}/100")


def test_state_updates():
    """Test that all 6 state fields are updated correctly"""
    # Create state with draft
    state = create_initial_state("Test Topic", "standard")
    state["draft"] = "This is a test draft for reviewing state updates."
    state["word_count"] = 10
    
    # Create agent and process
    agent = ReviewAgent()
    updated_state = agent.process(state)
    
    # Verify all 6 fields are updated
    assert "quality_score" in updated_state, "quality_score should be set"
    assert isinstance(updated_state["quality_score"], float), "quality_score should be float"
    
    assert "review_comments" in updated_state, "review_comments should be set"
    assert isinstance(updated_state["review_comments"], list), "review_comments should be list"
    assert len(updated_state["review_comments"]) == 3, "Should have exactly 3 comments"
    
    assert updated_state["status"] in ["review_complete", "review_failed"], "Status should be set"
    assert updated_state["final_content"] == state["draft"], "final_content should copy draft"
    assert updated_state["next_action"] == "complete", "next_action should be complete"
    assert updated_state["assigned_agent"] is None, "assigned_agent should be None"
    
    print("✓ All 6 state fields updated correctly")


def test_parse_response():
    """Test the response parsing logic"""
    # Create agent
    agent = ReviewAgent()
    
    # Test with sample response
    sample_response = """
EVALUATION REPORT
================

SCORE: 75/100

BREAKDOWN:
- Content Quality: 20/25
- Structure: 18/25
- Readability: 19/25
- Completeness: 18/25

FEEDBACK:
1. The introduction effectively sets up the topic with clear context.
2. Some technical sections could benefit from more concrete examples.
3. Consider adding a summary section to reinforce key takeaways.

RECOMMENDATION: Minor revisions needed
"""
    
    # Parse the response
    score, feedback = agent._parse_response(sample_response)
    
    # Verify parsing
    assert score == 75.0, f"Expected score 75.0, got {score}"
    assert len(feedback) == 3, f"Expected 3 feedback items, got {len(feedback)}"
    assert "introduction effectively" in feedback[0], "First feedback not parsed correctly"
    assert "concrete examples" in feedback[1], "Second feedback not parsed correctly"
    assert "summary section" in feedback[2], "Third feedback not parsed correctly"
    
    print("✓ Response parsing works correctly")


def test_error_handling():
    """Test error handling when review fails"""
    # Create state with empty draft
    state = create_initial_state("Test Topic", "standard")
    state["draft"] = ""  # Empty draft might cause issues
    state["word_count"] = 0
    
    # Create agent and process
    agent = ReviewAgent()
    updated_state = agent.process(state)
    
    # Verify error handling
    if updated_state["status"] == "review_failed":
        assert updated_state["quality_score"] == 0.0, "Failed review should have score 0.0"
        assert updated_state["review_comments"] == ["Review failed"], "Should have error message"
        print("✓ Error handling works correctly")
    else:
        # If it didn't fail, verify it handled empty draft gracefully
        assert updated_state["status"] == "review_complete", "Should complete or fail"
        assert updated_state["quality_score"] >= 0, "Score should be non-negative"
        print("✓ Handled empty draft gracefully")


if __name__ == "__main__":
    print("Running Review Agent tests...")
    print("-" * 40)
    
    test_review_good_draft()
    test_review_poor_draft()
    test_state_updates()
    test_parse_response()
    test_error_handling()
    
    print("-" * 40)
    print("\nAll tests completed! ✅")
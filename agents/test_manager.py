"""
Test cases for Manager Agent
"""

import pytest
from manager import ManagerAgent


def test_standard_mode():
    """Test standard mode sets research path"""
    agent = ManagerAgent()
    state = agent.process("AI in healthcare", "standard")
    
    assert state["next_action"] == "research"
    assert state["assigned_agent"] == "research"
    assert state["enable_research"] == True
    assert state["enable_revision"] == True
    assert state["topic"] == "Ai In Healthcare"


def test_quick_mode():
    """Test quick mode sets writer path"""
    agent = ManagerAgent()
    state = agent.process("Python tutorials", "quick")
    
    assert state["next_action"] == "write"
    assert state["assigned_agent"] == "writer"
    assert state["enable_research"] == False
    assert state["enable_revision"] == False
    assert state["topic"] == "Python Tutorials"


def test_empty_topic():
    """Test empty topic raises error"""
    agent = ManagerAgent()
    
    with pytest.raises(Exception) as exc_info:
        agent.process("", "standard")
    assert "Topic cannot be empty" in str(exc_info.value)


def test_short_topic():
    """Test single word topic raises error"""
    agent = ManagerAgent()
    
    with pytest.raises(Exception) as exc_info:
        agent.process("AI", "standard")
    assert "Topic too short" in str(exc_info.value)


def test_long_topic():
    """Test topic with more than 50 words raises error"""
    agent = ManagerAgent()
    long_topic = " ".join(["word"] * 51)
    
    with pytest.raises(Exception) as exc_info:
        agent.process(long_topic, "standard")
    assert "Topic too long" in str(exc_info.value)


def test_topic_cleaning():
    """Test topic cleaning removes extra spaces and formats properly"""
    agent = ManagerAgent()
    state = agent.process("  AI   in   Healthcare  ", "standard")
    
    assert state["topic"] == "Ai In Healthcare"


def test_keyword_extraction():
    """Test keyword extraction removes stop words"""
    agent = ManagerAgent()
    state = agent.process("Write about AI in healthcare", "standard")
    
    # Keywords should not include stop words
    keywords = agent._extract_keywords("Write About Ai In Healthcare")
    assert "write" not in keywords
    assert "about" not in keywords
    assert "in" not in keywords
    assert "healthcare" in keywords


def test_special_characters():
    """Test special characters are removed"""
    agent = ManagerAgent()
    state = agent.process("AI & Machine Learning!!!", "standard")
    
    assert state["topic"] == "Ai  Machine Learning"


def test_state_initialization():
    """Test all state fields are properly initialized"""
    agent = ManagerAgent()
    state = agent.process("Test Topic", "standard")
    
    # Check key fields are initialized
    assert state["project_id"] is not None
    assert state["thread_id"] == state["project_id"]
    assert state["status"] == "initialized"
    assert state["research_notes"] == []
    assert state["sources"] == []
    assert state["draft"] == ""
    assert state["word_count"] == 0
    assert state["quality_score"] == 0.0
    assert state["human_approved"] == False
    assert state["parallel_results"] == {}


if __name__ == "__main__":
    # Run tests manually
    print("Running Manager Agent tests...")
    
    test_standard_mode()
    print("✓ Standard mode test passed")
    
    test_quick_mode()
    print("✓ Quick mode test passed")
    
    test_empty_topic()
    print("✓ Empty topic test passed")
    
    test_short_topic()
    print("✓ Short topic test passed")
    
    test_long_topic()
    print("✓ Long topic test passed")
    
    test_topic_cleaning()
    print("✓ Topic cleaning test passed")
    
    test_keyword_extraction()
    print("✓ Keyword extraction test passed")
    
    test_special_characters()
    print("✓ Special characters test passed")
    
    test_state_initialization()
    print("✓ State initialization test passed")
    
    print("\nAll tests passed! ✅")
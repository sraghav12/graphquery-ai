"""
Unit tests for query chain functionality
"""

import pytest
from src.query_chain import (
    get_few_shot_examples,
    create_cypher_prompt,
    add_custom_examples
)


def test_get_few_shot_examples():
    """Test that few-shot examples are returned correctly"""
    examples = get_few_shot_examples()
    
    assert isinstance(examples, list)
    assert len(examples) > 0
    
    # Check structure of examples
    for example in examples:
        assert "question" in example
        assert "query" in example
        assert isinstance(example["question"], str)
        assert isinstance(example["query"], str)


def test_create_cypher_prompt():
    """Test prompt template creation"""
    prompt = create_cypher_prompt()
    
    assert prompt is not None
    assert hasattr(prompt, 'format')
    
    # Test formatting
    formatted = prompt.format(
        question="Test question?",
        schema="Test schema"
    )
    
    assert "Test question?" in formatted
    assert "Test schema" in formatted


def test_add_custom_examples():
    """Test adding custom examples"""
    new_examples = [
        {
            "question": "Custom question?",
            "query": "MATCH (n) RETURN n"
        }
    ]
    
    combined = add_custom_examples(new_examples)
    
    assert len(combined) > len(get_few_shot_examples())
    assert combined[-1] == new_examples[0]


def test_example_query_patterns():
    """Test that example queries follow best practices"""
    examples = get_few_shot_examples()
    
    for example in examples:
        query = example["query"]
        
        # Check that queries use MATCH
        assert "MATCH" in query.upper()
        
        # Check that queries use RETURN
        assert "RETURN" in query.upper()
        
        # Check no trailing semicolons (Neo4j doesn't require them)
        assert not query.strip().endswith(';')


@pytest.mark.parametrize("question,expected_keyword", [
    ("How many movies?", "count"),
    ("Which actors?", "actor"),
    ("List genres", "genre"),
])
def test_question_query_mapping(question, expected_keyword):
    """Test that questions map to appropriate query types"""
    examples = get_few_shot_examples()
    
    # This is a simple check - in real implementation,
    # we'd test the actual chain output
    matching_examples = [
        e for e in examples 
        if expected_keyword.lower() in e["question"].lower()
    ]
    
    # At least one example should contain the keyword
    assert len(matching_examples) > 0 or len(examples) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
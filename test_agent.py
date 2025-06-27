#!/usr/bin/env python3
"""
Simple test script for the Letter Counter Agent
"""

from letter_counter_agent import run_agent

def test_agent():
    """Test the agent with some example inputs."""
    
    test_cases = [
        "How many times does r occur in the word strawberry?",
        "Count the letter 'e' in 'development'",
        "How many 'l's are in 'hello world'?",
        "How many times does the letter 'a' appear in 'banana'?"
    ]
    
    print("Testing Letter Counter Agent")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case}")
        try:
            response = run_agent(test_case, thread_id=f"test_{i}")
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 30)

if __name__ == "__main__":
    test_agent() 
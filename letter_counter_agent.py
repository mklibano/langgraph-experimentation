import os
from typing import List, Dict, Any, Annotated
from dataclasses import dataclass
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt.tool_node import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv()

@tool
def parse_word_to_characters(word: str) -> List[str]:
    """
    Parse a word into a list of individual characters.
    
    Args:
        word: The word to parse into characters
        
    Returns:
        List of characters in the word
    """
    return list(word.lower())

@tool
def count_character_occurrences(characters: List[str], target_character: str) -> int:
    """
    Count how many times a specific character appears in a list of characters.
    
    Args:
        characters: List of characters to search through
        target_character: The character to count
        
    Returns:
        Number of times the target character appears in the list
    """
    return characters.count(target_character.lower())

# Available tools
tools = [parse_word_to_characters, count_character_occurrences]

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)

def should_continue(state: MessagesState) -> str:
    """Determine whether to continue or end based on the last message."""
    messages = state['messages']
    last_message = messages[-1]
    
    # If the last message is a tool call, continue to tools
    if last_message.tool_calls:
        return "tools"
    # Otherwise, end
    return END

SYSTEM_PROMPT = """
You are a helpful letter counting assistant specialized in analyzing character occurrences in words.

When asked to count letters:
1. First, use parse_word_to_characters to convert the word into individual characters
2. Then, use count_character_occurrences to count how many times the target letter appears
3. Respond with a clear, natural language answer

Be accurate and conversational in your responses. If you are not asked to count letters, you should respond with 
"I'm sorry, I can only count letters."
"""

def call_model(state: MessagesState) -> Dict[str, Any]:
    """Call the model with the current state."""
    messages = state['messages']
    
    # Add system message if needed
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# Create the state graph
workflow = StateGraph(MessagesState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

# Add edges
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", END: END}
)
workflow.add_edge("tools", "agent")

# Compile the graph
#checkpointer = MemorySaver()
#app = workflow.compile(checkpointer=checkpointer)
app = workflow.compile()

def run_agent(user_input: str, thread_id: str = "default") -> str:
    """
    Run the agent with a user input and return the response.
    
    Args:
        user_input: The user's question
        thread_id: Thread ID for conversation continuity
        
    Returns:
        The agent's response
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    # Create initial message
    initial_message = HumanMessage(content=user_input)
    
    # Run the agent
    result = app.invoke({"messages": [initial_message]}, config)
    
    # Return the last AI message
    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage):
            return message.content
    
    return "I couldn't process your request."

if __name__ == "__main__":
    # Example usage
    print("Letter Counter Agent")
    print("=" * 50)
    
    while True:
        user_input = input("\nEnter your question (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break
            
        try:
            response = run_agent(user_input)
            print(f"\nAgent: {response}")
        except Exception as e:
            print(f"Error: {e}") 
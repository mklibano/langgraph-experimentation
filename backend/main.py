from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import httpx
import json
import os
from dotenv import load_dotenv

app = FastAPI(title="Letter Counter Agent UI")

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables from .env file
load_dotenv()

# LangGraph agent configuration
# TODO: change to remote URL when deployed
# Remote LangGraph API URL
#LANGGRAPH_API_URL = "https://lettercounter-bbb1baafb24955db931269a76b70e89b.us.langgraph.app"

# Local LangGraph API URL
LANGGRAPH_API_URL = "http://127.0.0.1:2024"
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")

# SSL configuration for development
DISABLE_SSL_VERIFY = os.getenv("DISABLE_SSL_VERIFY", "true").lower() == "true"
print(f"🔒 SSL verification: {'DISABLED' if DISABLE_SSL_VERIFY else 'ENABLED'}")
if LANGSMITH_API_KEY:
    print("🔑 API key loaded")
else:
    print("⚠️ No API key found")

# Pydantic models
class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    messages: List[Message]

# In-memory storage for conversation threads
conversations = {}

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Send a message to the LangGraph agent and return the response."""
    # Create or get existing thread
    thread_id = request.thread_id
    if not thread_id or thread_id not in conversations:
        thread_id = f"thread_{len(conversations) + 1}"
        conversations[thread_id] = []
    
    # Add user message to conversation
    user_message = Message(role="human", content=request.message)
    conversations[thread_id].append(user_message)
    
    # Check if API key is provided
    if not LANGSMITH_API_KEY:
        error_response = "❌ **API Key Required**\n\nPlease set your LANGSMITH_API_KEY in the .env file or environment variables."
        agent_message = Message(role="ai", content=error_response)
        conversations[thread_id].append(agent_message)
        return ChatResponse(
            response=error_response,
            thread_id=thread_id,
            messages=conversations[thread_id]
        )
    
    try:
        print(f"💬 Chat request: {request.message}")
        
        # Prepare payload for LangGraph API
        payload = {
            "assistant_id": "letter_counter_agent",
            "input": {
                "messages": [{"role": "human", "content": request.message}]
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LANGSMITH_API_KEY}"
        }
        
        # Make streaming request
        with httpx.Client(timeout=60.0, verify=not DISABLE_SSL_VERIFY) as client:
            response = client.post(
                f"{LANGGRAPH_API_URL}/runs/stream",
                json=payload,
                headers=headers
            )
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                # Parse streaming response (Server-Sent Events format)
                agent_response = ""
                lines = response.text.split('\n')
                
                for line in lines:
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])  # Remove 'data: ' prefix
                            if 'messages' in data:
                                messages = data['messages']
                                if messages:
                                    last_message = messages[-1]
                                    # Look for AI messages with actual content (not tool calls)
                                    if (last_message.get('type') == 'ai' and 
                                        last_message.get('content') and 
                                        last_message.get('content').strip() and
                                        not last_message.get('tool_calls')):
                                        agent_response = last_message['content']
                                        print(f"🎯 Found AI response: {agent_response}")
                        except json.JSONDecodeError:
                            continue
                
                if not agent_response:
                    agent_response = "I processed your request but didn't generate a visible response. Please try asking your question more specifically."
            else:
                error_text = response.text
                print(f"❌ API Error: {error_text}")
                agent_response = f"API Error ({response.status_code}): {error_text}"
                
    except Exception as e:
        print(f"💥 Error: {e}")
        agent_response = f"Connection error: {str(e)}"
    
    # Add agent response to conversation
    agent_message = Message(role="ai", content=agent_response)
    conversations[thread_id].append(agent_message)
    
    return ChatResponse(
        response=agent_response,
        thread_id=thread_id,
        messages=conversations[thread_id]
    )

@app.get("/api/conversations/{thread_id}")
def get_conversation(thread_id: str):
    """Get the conversation history for a specific thread."""
    if thread_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"thread_id": thread_id, "messages": conversations[thread_id]}

@app.delete("/api/conversations/{thread_id}")
def clear_conversation(thread_id: str):
    """Clear a specific conversation."""
    if thread_id in conversations:
        conversations[thread_id] = []
    return {"message": "Conversation cleared"}

# Serve React app
@app.get("/")
def serve_react_app():
    """Serve the React app's index.html."""
    return FileResponse("frontend/build/index.html")

# Health check
@app.get("/api/health")
def health_check():
    return {"status": "healthy", "langgraph_url": LANGGRAPH_API_URL}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import httpx
import json
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Try to import LangGraph SDK
try:
    from langgraph_sdk import get_client
    LANGGRAPH_SDK_AVAILABLE = True
    print("✅ LangGraph SDK is available")
except ImportError:
    LANGGRAPH_SDK_AVAILABLE = False
    print("⚠️ LangGraph SDK not available, using HTTP client")

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
LANGGRAPH_API_URL = "https://lettercounter-bbb1baafb24955db931269a76b70e89b.us.langgraph.app"
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")

# SSL configuration for development
DISABLE_SSL_VERIFY = os.getenv("DISABLE_SSL_VERIFY", "true").lower() == "true"
if DISABLE_SSL_VERIFY:
    print("⚠️ SSL verification is DISABLED for development. Do not use in production!")
    print("   To enable SSL properly on macOS, run: /Applications/Python\\ 3.12/Install\\ Certificates.command")
    print("   Or set DISABLE_SSL_VERIFY=false to enable verification")
else:
    print("🔒 SSL verification is ENABLED")

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
async def chat(request: ChatRequest):
    """Send a message to the LangGraph agent and return the response."""
    try:
        print(f"🔍 Received chat request: {request.message}")
        
        # Create or get existing thread
        thread_id = request.thread_id
        if not thread_id or thread_id not in conversations:
            thread_id = f"thread_{len(conversations) + 1}"
            conversations[thread_id] = []
        
        # Add user message to conversation
        user_message = Message(role="human", content=request.message)
        conversations[thread_id].append(user_message)
        
        # Prepare messages for LangGraph
        messages = [{"role": msg.role, "content": msg.content} for msg in conversations[thread_id]]
        print(f"📝 Prepared messages: {messages}")
        
        # Call LangGraph agent with simpler approach
        # Configure client to handle SSL properly
        async with httpx.AsyncClient(
            timeout=60.0,
            verify=not DISABLE_SSL_VERIFY  # SSL verification based on environment
        ) as client:
            # Try threadless run first (simpler approach)
            payload = {
                "assistant_id": "letter_counter_agent",
                "input": {
                    "messages": [{"role": "human", "content": request.message}]
                },
                "stream_mode": "values"
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            if LANGSMITH_API_KEY:
                headers["Authorization"] = f"Bearer {LANGSMITH_API_KEY}"
                print("🔑 Using API key for authentication")
            else:
                print("⚠️ No API key provided")
                print("   Please set LANGSMITH_API_KEY environment variable")
                print("   Get your API key from: https://smith.langchain.com -> Settings -> API Keys")
                return ChatResponse(
                    response="❌ **Authentication Required**\n\nTo use this chat, you need to:\n\n1. Go to [LangSmith](https://smith.langchain.com)\n2. Navigate to Settings → API Keys\n3. Create a new API key\n4. Set it as an environment variable:\n   ```\n   export LANGSMITH_API_KEY=your_api_key_here\n   ```\n5. Restart the server\n\nWithout an API key, I cannot connect to your deployed LangGraph agent.",
                    thread_id=thread_id,
                    messages=conversations[thread_id] + [Message(role="ai", content="Authentication required - please set your LangSmith API key")]
                )
            
            print(f"🌐 Making request to: {LANGGRAPH_API_URL}/runs/stream")
            print(f"📦 Payload: {json.dumps(payload, indent=2)}")
            
            response = await client.post(
                f"{LANGGRAPH_API_URL}/runs/stream",
                json=payload,
                headers=headers
            )
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ API Error: {response.text}")
                # Try without streaming as fallback
                simple_payload = {
                    "assistant_id": "letter_counter_agent", 
                    "input": {
                        "messages": [{"role": "human", "content": request.message}]
                    }
                }
                
                print("🔄 Trying non-streaming request...")
                simple_response = await client.post(
                    f"{LANGGRAPH_API_URL}/runs",
                    json=simple_payload,
                    headers=headers
                )
                
                print(f"📊 Non-streaming response status: {simple_response.status_code}")
                
                if simple_response.status_code != 200:
                    print(f"❌ Non-streaming API Error: {simple_response.text}")
                    agent_response = f"API Error: {simple_response.status_code} - {simple_response.text}"
                else:
                    result = simple_response.json()
                    print(f"📄 Non-streaming result: {json.dumps(result, indent=2)}")
                    
                    # Extract response from result
                    if "output" in result and "messages" in result["output"]:
                        output_messages = result["output"]["messages"]
                        if output_messages:
                            agent_response = output_messages[-1].get("content", "No response content")
                        else:
                            agent_response = "No messages in output"
                    else:
                        agent_response = f"Unexpected response format: {result}"
            else:
                # Process streaming response
                agent_response = ""
                print("📡 Processing streaming response...")
                
                response_text = await response.atext()
                print(f"📄 Raw response: {response_text[:500]}...")
                
                # Try to parse JSON response
                try:
                    result = response.json()
                    print(f"📄 Parsed JSON result: {json.dumps(result, indent=2)}")
                    
                    if "output" in result and "messages" in result["output"]:
                        output_messages = result["output"]["messages"]
                        if output_messages:
                            agent_response = output_messages[-1].get("content", "No response content")
                        else:
                            agent_response = "No messages in output"
                    else:
                        agent_response = f"Unexpected response format: {result}"
                        
                except json.JSONDecodeError as je:
                    print(f"❌ JSON decode error: {je}")
                    agent_response = f"Failed to parse response: {response_text[:200]}"
                
                if not agent_response:
                    agent_response = "I received your message but couldn't generate a response. Please try again."
        
        print(f"🤖 Agent response: {agent_response}")
        
        # Add agent response to conversation
        agent_message = Message(role="ai", content=agent_response)
        conversations[thread_id].append(agent_message)
        
        return ChatResponse(
            response=agent_response,
            thread_id=thread_id,
            messages=conversations[thread_id]
        )
        
    except Exception as e:
        print(f"💥 Exception in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Provide specific help for SSL errors
        error_msg = str(e)
        if "CERTIFICATE_VERIFY_FAILED" in error_msg or "SSL" in error_msg:
            detailed_error = (
                f"SSL Certificate Error: {error_msg}\n\n"
                "To fix this on macOS:\n"
                "1. Run: /Applications/Python\\ 3.12/Install\\ Certificates.command\n"
                "2. Or restart with: DISABLE_SSL_VERIFY=true python backend/main.py\n"
                "3. Or install certificates: pip install --upgrade certifi"
            )
            raise HTTPException(status_code=500, detail=detailed_error)
        
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/chat-sdk", response_model=ChatResponse)
async def chat_sdk(request: ChatRequest):
    """Send a message to the LangGraph agent using the official SDK."""
    if not LANGGRAPH_SDK_AVAILABLE:
        raise HTTPException(status_code=501, detail="LangGraph SDK not available")
    
    try:
        print(f"🔍 [SDK] Received chat request: {request.message}")
        
        # Create or get existing thread
        thread_id = request.thread_id
        if not thread_id or thread_id not in conversations:
            thread_id = f"thread_{len(conversations) + 1}"
            conversations[thread_id] = []
        
        # Add user message to conversation
        user_message = Message(role="human", content=request.message)
        conversations[thread_id].append(user_message)
        
        # Use LangGraph SDK
        client = get_client(url=LANGGRAPH_API_URL, api_key=LANGSMITH_API_KEY)
        print(f"🌐 [SDK] Created client for: {LANGGRAPH_API_URL}")
        
        # Make a threadless run
        agent_response = ""
        try:
            print("📡 [SDK] Starting run...")
            for chunk in client.runs.stream(
                None,  # Threadless run
                "letter_counter_agent",  # Assistant ID
                input={
                    "messages": [
                        {"role": "human", "content": request.message}
                    ]
                },
                stream_mode="updates"
            ):
                print(f"📦 [SDK] Received chunk: {chunk}")
                if hasattr(chunk, 'data') and chunk.data:
                    if 'messages' in chunk.data:
                        messages_data = chunk.data['messages']
                        if messages_data:
                            last_message = messages_data[-1]
                            if last_message.get('role') == 'ai':
                                agent_response = last_message.get('content', '')
                                print(f"🎯 [SDK] Found AI response: {agent_response}")
                    
        except Exception as sdk_error:
            print(f"❌ [SDK] Error during streaming: {sdk_error}")
            agent_response = f"SDK Error: {str(sdk_error)}"
        
        if not agent_response:
            agent_response = "I received your message but couldn't generate a response using the SDK."
        
        print(f"🤖 [SDK] Final response: {agent_response}")
        
        # Add agent response to conversation
        agent_message = Message(role="ai", content=agent_response)
        conversations[thread_id].append(agent_message)
        
        return ChatResponse(
            response=agent_response,
            thread_id=thread_id,
            messages=conversations[thread_id]
        )
        
    except Exception as e:
        print(f"💥 [SDK] Exception in chat-sdk endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"SDK Error: {str(e)}")

@app.get("/api/conversations/{thread_id}")
async def get_conversation(thread_id: str):
    """Get the conversation history for a specific thread."""
    if thread_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"thread_id": thread_id, "messages": conversations[thread_id]}

@app.delete("/api/conversations/{thread_id}")
async def clear_conversation(thread_id: str):
    """Clear a specific conversation."""
    if thread_id in conversations:
        conversations[thread_id] = []
    return {"message": "Conversation cleared"}

# Serve React app
@app.get("/")
async def serve_react_app():
    """Serve the React app's index.html."""
    return FileResponse("frontend/build/index.html")

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "langgraph_url": LANGGRAPH_API_URL}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
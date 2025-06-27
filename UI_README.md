# Letter Counter Agent UI

A conversational web interface for the Letter Counter Agent, built with React and FastAPI.

## Features

- **Clean conversational interface** with message bubbles
- **Multi-turn conversation support** with thread management
- **Real-time messaging** with typing indicators
- **Responsive design** that works on desktop and mobile
- **Error handling** with user-friendly messages
- **Auto-scrolling** to keep latest messages visible


## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn
- Your LangGraph agent deployed and accessible at the platform URL

### 1. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set your LangSmith API key (optional but recommended)
export LANGSMITH_API_KEY=your_api_key_here
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install
```

### 3. Build the React App

```bash
# In the frontend directory
npm run build
```

## Running the Application

### Development Mode

For development, you can run the backend and frontend separately:

**Terminal 1 - Backend:**
```bash
# From project root
python backend/main.py
```

**Terminal 2 - Frontend (optional for development):**
```bash
# From frontend directory
cd frontend
npm start
```

### Production Mode

For production, build the React app and serve everything through FastAPI:

```bash
# Build the React app
cd frontend
npm run build
cd ..

# Run the FastAPI server (serves both API and React app)
python backend/main.py
```

The application will be available at: `http://localhost:8000`

## Configuration

### Environment Variables

- `LANGSMITH_API_KEY`: Your LangSmith API key for authentication (optional)

### LangGraph Agent URL

The backend is configured to connect to your deployed agent at:
```
https://lettercounter-bbb1baafb24955db931269a76b70e89b.us.langgraph.app
```

To change this URL, edit the `LANGGRAPH_API_URL` variable in `backend/main.py`.
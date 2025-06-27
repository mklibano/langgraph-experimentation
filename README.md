# Letter Counter Agent

A simple LangGraph agent that counts the occurrences of letters in words using two specialized tools.

## Overview

This agent can answer questions like:
- "How many times does 'r' occur in the word 'strawberry'?"
- "Count the letter 'e' in 'development'"
- "How many 'l's are in 'hello world'?"

The agent uses two tools to accomplish this task:
1. **parse_word_to_characters**: Converts a word into a list of individual characters
2. **count_character_occurrences**: Counts how many times a specific character appears in a list

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- LangGraph Studio (optional, for visual interface)
- uv (Python package manager)

### 1. Install uv

If you don't have uv installed:
```bash
# On macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip:
pip install uv
```

### 2. Clone and Setup Environment

```bash
# Navigate to your project directory
cd langgraph-experimentation

# Create a virtual environment and install dependencies
uv venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file and add your OpenAI API key
# OPENAI_API_KEY=your_actual_api_key_here
```

### 4. Run the Agent

#### Option A: Command Line Interface
```bash
python letter_counter_agent.py
```

#### Option B: LangGraph Studio
1. Install LangGraph CLI with development mode support:
   ```bash
   uv pip install "langgraph-cli[inmem]"
   ```

2. Start LangGraph development server:
   ```bash
   langgraph dev
   ```

3. Open your browser and navigate to the provided Studio URL (usually shows as `🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`)

4. Select the "Letter Counter Agent" from the available graphs
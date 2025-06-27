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

# On Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

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
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

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

## Usage Examples

### Example 1: Basic Letter Counting
**Input:** "How many times does r occur in the word strawberry?"

**Expected Response:** The agent will:
1. Use `parse_word_to_characters` to convert "strawberry" to ['s', 't', 'r', 'a', 'w', 'b', 'e', 'r', 'r', 'y']
2. Use `count_character_occurrences` to count 'r' in the list
3. Respond: "The letter 'r' occurs 3 times in the word 'strawberry'."

### Example 2: Multiple Words
**Input:** "Count the letter 'l' in 'hello world'"

**Expected Response:** The agent will process "hello world" and count the occurrences of 'l'.

### Example 3: Case Insensitive
**Input:** "How many 'E's are in 'Development'?"

**Expected Response:** The agent handles case-insensitive matching automatically.

## Project Structure

```
langgraph-experimentation/
├── letter_counter_agent.py    # Main agent implementation
├── langgraph.json            # LangGraph Studio configuration
├── requirements.txt          # Python dependencies
├── env.example              # Environment variables template
└── README.md               # This file
```

## How It Works

The agent is built using LangGraph and follows this workflow:

1. **User Input**: Receives a natural language question about letter counting
2. **Agent Processing**: The LLM analyzes the question and determines which tools to use
3. **Tool Execution**: 
   - First calls `parse_word_to_characters` to break down the word
   - Then calls `count_character_occurrences` to count the target letter
4. **Response**: Provides a natural language answer with the count

## Dependencies

- `langgraph>=0.2.0`: Core graph-based agent framework
- `langchain>=0.3.0`: LangChain integration
- `langchain-openai>=0.2.0`: OpenAI LLM integration
- `python-dotenv>=1.0.0`: Environment variable management

## Troubleshooting

### Common Issues

1. **Missing OpenAI API Key**
   - Ensure your `.env` file contains a valid `OPENAI_API_KEY`
   - Check that the `.env` file is in the project root directory

2. **Pydantic v2 Compatibility Error**
   - If you see errors about `__modify_schema__` method not supported in Pydantic v2
   - Run the fix script: `python fix_dependencies.py` (this will clean up after itself)
   - Or manually reinstall dependencies in the correct order:
     ```bash
     uv pip uninstall langchain-openai langchain-core langchain pydantic -y
     uv pip install 'pydantic>=2.5.0,<3.0.0'
     uv pip install -r requirements.txt
     ```

3. **Import Errors**
   - Make sure all dependencies are installed: `uv pip install -r requirements.txt`
   - Ensure you're using the correct virtual environment

4. **LangGraph Studio Not Starting**
   - Check if port 2024 is available
   - Try running `langgraph dev --port 2025` to use a different port

### Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Verify your OpenAI API key is valid and has sufficient credits
3. Ensure all dependencies are correctly installed

## License

This project is for educational and experimental purposes. 
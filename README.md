# Flutter Development Assistant

Flutter Development Assistant is an AI-powered tool that helps developers with Flutter projects. It leverages LangChain, OpenAI, and FAISS to provide contextual responses and execute actions based on user input. It supports CLI, Gradio UI, and REST API interfaces, with per-session memory and summaries.

## Features

- **Flutter & Dart project support**: Loads `.dart` files from a specified project and answers contextually.
- **Action detection**: Classifies user intent as `REQUEST_ACTION` or `GENERAL_DISCUSSION` and matches predefined triggers.
- **Multi-language replies**: Responds in the preferred language set in `character.env.json`.
- **Session summaries**: Tracks facts about the user and appends them to a persistent summary file.
- **Interfaces supported**:
  - Command-line interface (CLI)
  - Web-based UI using Gradio
  - REST API using FastAPI
- **Debug mode**: Verbose logging during execution.
- **Smart action matching**: Uses fuzzy matching to find the best action for the user query.

## Prerequisites

- Python 3.8 or higher
- A valid OpenAI API key
- A local Flutter project with `.dart` files
- Virtual environment (recommended)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Run with the setup script

```bash
./agent.sh <mode> <project_path>
```

**Example:**

```bash
./agent.sh cli ~/my_flutter_project
```

This script will:
- Create a virtual environment (venv) if it does not exist
- Upgrade pip and install dependencies
- Check and install the required version of LangChain (>= 0.1.17)
- Set the PROJECT_PATH environment variable
- Launch the selected mode (cli, gradio, or api)

### 3. Manual installation (optional)

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

If requirements.txt is not present:

```bash
pip install langchain>=0.1.17 langchain-community langchain-openai openai faiss-cpu python-dotenv watchdog colorama jinja2 gradio fastapi uvicorn
```

## Configuration Files

### .env
Contains environment variables including the OpenAI API key and the Flutter project path.

**Example:**

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxx
PROJECT_PATH=/path/to/flutter/project
```

### character.env.json
Defines the assistant's personality and preferred language.

**Example:**

```json
{
  "name": "FlutterBot",
  "language": "English",
  "description": "An assistant for Flutter development.",
  "tone": "friendly",
  "expertise": ["Flutter", "Dart", "Mobile"]
}
```

### actions_config.json
Lists available actions and their corresponding triggers.

**Example:**

```json
{
  "generate_code": {
    "enabled": true,
    "triggers": ["generate a widget", "create a Dart function"],
    "output": "Generated Flutter/Dart code"
  },
  "debug_code": {
    "enabled": true,
    "triggers": ["debug this code", "fix this Dart error"],
    "output": "Debugged code with explanation"
  }
}
```

## Usage

Launch one of the available modes:

```bash
./agent.sh <mode> <project_path>
```

### Modes:

**CLI:**
```bash
./agent.sh cli ./my_flutter_app
```

**Gradio Web UI:**
```bash
./agent.sh gradio ./my_flutter_app
```

**FastAPI REST API:**
```bash
./agent.sh api ./my_flutter_app
```

## How It Works

1. Loads `.dart` files from the Flutter project specified in PROJECT_PATH.
2. Creates a vector store (FAISS) and uses LangChain with OpenAI to answer queries.
3. Classifies queries as `REQUEST_ACTION` or `GENERAL_DISCUSSION`.
4. If action is required, matches the closest defined trigger using fuzzy matching.
5. Maintains session summaries in `cache/<session_id>_summary.txt`, which get compressed as needed.

## Project Structure

```
.
├── agent.sh                  # Startup script with mode and project path
├── agent_core.py             # Assistant core logic
├── character.env.json        # Assistant personality config
├── actions_config.json       # Action definitions
├── .env                      # Environment variables
├── interfaces/
│   ├── cli.py
│   ├── gradio_ui.py
│   └── api.py
├── cache/                    # Session summaries
├── requirements.txt          # Optional dependency list
└── venv/                     # Virtual environment
```

## Debug Mode

You can enable verbose logging by instantiating the agent with:

```python
session = AgentSession(debug=True)
```

## Limitations

- Only processes `.dart` files within the project path
- Actions depend on matching string triggers
- Requires OpenAI API access
- No support for voice input or external knowledge injection

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m "Add feature"`
4. Push to your fork: `git push origin feature-name`
5. Open a pull request on the main repository

## License

This project is licensed under the MIT License. See the LICENSE file for details.
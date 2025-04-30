# Flutter Development Assistant

Flutter Development Assistant is an AI-powered tool designed to assist developers with Flutter development. It uses LangChain, OpenAI, and FAISS to provide contextual answers and perform actions based on user queries. The assistant supports multiple interfaces (CLI, Gradio UI, and API) and maintains session-based conversation history.

## Features

- Flutter Development Support: Answers questions about Flutter and Dart code using a vector store for context.
- Actionable Requests: Classifies user intents as REQUEST_ACTION or GENERAL_DISCUSSION and performs predefined actions (e.g., code generation, debugging).
- Multi-Language Support: Responds in the user's preferred language (configured in character.env.json).
- Session Management: Maintains conversation history and summaries for personalized responses.
- Multiple Interfaces:
  - Command-line interface (CLI)
  - Web-based Gradio UI
  - FastAPI-based REST API
- Debug Mode: Logs detailed information for troubleshooting.

## Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- OpenAI API key
- Flutter/Dart project directory (specified in .env)

## Installation

### Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### Set Up Virtual Environment Using Script

```bash
./agent.sh <mode>
```
Replace `<mode>` with `cli`, `gradio`, or `api`. The script will:

- Create a virtual environment (venv) if it doesn't exist
- Upgrade pip and install dependencies from requirements.txt (or default packages if not provided)
- Check and install the required LangChain version (>=0.1.17)

### Manual Installation (if not using agent.sh)

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
If `requirements.txt` is missing:

```bash
pip install langchain>=0.1.17 langchain-community langchain-openai openai faiss-cpu python-dotenv watchdog colorama jinja2 gradio fastapi uvicorn
```

## Configure Environment and Files

### 1. .env
Stores environment variables like the OpenAI API key and Flutter project path.

Example:
```env
OPENAI_API_KEY=your-openai-api-key
PROJECT_PATH=/path/to/your/flutter/project
```

Create `.env` in the root directory and ensure it's loaded using python-dotenv.

### 2. character.env.json
Defines assistant's profile, language, and behavior.

Example:
```json
{
  "name": "FlutterBot",
  "language": "English",
  "description": "A helpful AI assistant for Flutter development.",
  "tone": "friendly",
  "expertise": ["Flutter", "Dart", "Mobile Development"]
}
```

### 3. actions_config.json
Defines available actions, their triggers, and outputs.

Example:
```json
{
  "generate_code": {
    "enabled": true,
    "triggers": ["generate a flutter widget", "create a dart function"],
    "output": "Generated Flutter/Dart code"
  },
  "debug_code": {
    "enabled": true,
    "triggers": ["debug this flutter code", "fix this dart error"],
    "output": "Debugged code with explanation"
  },
  "explain_code": {
    "enabled": false,
    "triggers": ["explain this flutter code"],
    "output": "Code explanation"
  }
}
```

## Usage

Run the assistant in one of the supported modes:

```bash
./agent.sh <mode>
```

- CLI mode:
```bash
./agent.sh cli
```
- Gradio UI mode:
```bash
./agent.sh gradio
```
- API mode:
```bash
./agent.sh api
```

## Project Structure

```
├── agent.py                # Main assistant script
├── agent.sh                # Setup and run script
├── character.py            # Agent prompt generator
├── character.env.json      # Assistant profile config
├── actions_config.json     # Actions config
├── .env                    # Environment variables
├── cache/                  # Session summaries
├── interfaces/             # Interface scripts
│   ├── cli.py
│   ├── gradio_ui.py
│   ├── api.py
├── requirements.txt        # Dependency list (optional)
└── venv/                   # Virtual environment
```

## How It Works

- **Initialization**: Loads `.env`, `character.env.json`, and `actions_config.json`. Creates a FAISS vector store from `.dart` files. Initializes LangChain QA with OpenAI.
- **Session Management**: Maintains chat history and stores summaries in `cache/<session_id>_summary.txt`.
- **Query Processing**: Classifies input, matches actions, and returns structured JSON.
- **Summary Compression**: Periodically condenses logs into bullet-point summaries.

## Debugging

Enable debug mode by initializing the agent session with:
```python
session = AgentSession(debug=True)
```

## Limitations

- Requires a valid OpenAI API key
- Processes only `.dart` files in `PROJECT_PATH`
- Action matching depends on phrase triggers
- Voice and BigBrain modes are not supported

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m "Add feature"`
4. Push the branch: `git push origin feature-name`
5. Open a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for more information.

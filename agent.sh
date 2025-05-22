#!/bin/bash
# agent.sh

set -e  # Exit immediately on error

MODE=$1
PROJECT_PATH=$2

# Validate required arguments
if [ -z "$MODE" ] || [ -z "$PROJECT_PATH" ]; then
  echo "❌ Usage: ./agent.sh [cli|gradio|api] [project_path]"
  exit 1
fi

# Create virtual environment if not present
if [ ! -d "venv" ]; then
  echo "🔧 Creating virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Export PROJECT_PATH for use in Python
export PROJECT_PATH="$PROJECT_PATH"
echo "📁 PROJECT_PATH set to: $PROJECT_PATH"

# Check LangChain version
LC_VERSION=$(python -c "import langchain; print(langchain.__version__)" 2>/dev/null || echo "0.0.0")
REQUIRED="0.1.17"

# Upgrade LangChain if needed
if [ "$(printf '%s\n' "$REQUIRED" "$LC_VERSION" | sort -V | head -n1)" != "$REQUIRED" ]; then
  echo "⚠️ LangChain version is too old ($LC_VERSION), upgrading to $REQUIRED..."
  pip install "langchain>=$REQUIRED"
else
  echo "✅ LangChain version OK: $LC_VERSION"
fi

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
if [ -f "requirements.txt" ]; then
  echo "📦 Installing from requirements.txt"
  pip install -r requirements.txt
else
  echo "📦 Installing required packages"
  pip install \
    langchain>=0.1.17 \
    langchain-community \
    langchain-openai \
    openai \
    faiss-cpu \
    python-dotenv \
    watchdog \
    colorama \
    jinja2 \
    gradio \
    fastapi \
    uvicorn
fi

# Launch selected mode
echo "🚀 Launching '$MODE' mode..."

case $MODE in
  cli)
    python interfaces/cli.py
    ;;
  gradio)
    python interfaces/gradio_ui.py
    ;;
  api)
    uvicorn interfaces.api:app --reload
    ;;
  *)
    echo "❌ Unknown mode: $MODE"
    echo "Usage: ./agent.sh [cli|gradio|api] [project_path]"
    exit 1
    ;;
esac

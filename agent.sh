#!/bin/bash
#agent.sh

set -e

MODE=$1

if [ -z "$MODE" ]; then
  echo "❌ Usage: ./agent.sh [cli|gradio|api]"
  exit 1
fi

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
  echo "🔧 Creating virtual environment..."
  python3 -m venv venv
fi

# Activer l'environnement virtuel
source venv/bin/activate

LC_VERSION=$(python -c "import langchain; print(langchain.__version__)" 2>/dev/null || echo "0.0.0")
REQUIRED="0.1.17"

if [ "$(printf '%s\n' "$REQUIRED" "$LC_VERSION" | sort -V | head -n1)" != "$REQUIRED" ]; then
  echo "⚠️ LangChain version is too old ($LC_VERSION), upgrading to $REQUIRED..."
  pip install "langchain>=$REQUIRED"
else
  echo "✅ LangChain version OK: $LC_VERSION"
fi

# Mise à jour de pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Dépendances à jour avec LangChain >= 0.1.17
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

# Lancer le bon mode
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
    echo "Usage: ./agent.sh [cli|gradio|api]"
    exit 1
    ;;
esac

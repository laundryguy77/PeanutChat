#!/bin/bash
# Full rebuild automation for the vector database

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
DB_DIR="$HOME/.claude/skills/porteus-kiosk/vectordb"
OLLAMA_HOST="10.10.10.124"
OLLAMA_PORT="11434"

echo "============================================================"
echo "Vector Database Rebuild Script"
echo "============================================================"

# Step 1: Check/create virtual environment
echo ""
echo "Step 1: Setting up Python environment..."
if [ ! -d "$VENV_DIR" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "  Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "  Installing requirements..."
pip install -q -r "$SCRIPT_DIR/requirements.txt"
echo "  Done."

# Step 2: Test Ollama connection
echo ""
echo "Step 2: Testing Ollama connection..."
OLLAMA_URL="http://$OLLAMA_HOST:$OLLAMA_PORT/api/embeddings"

if curl -s -f -X POST "$OLLAMA_URL" \
    -H "Content-Type: application/json" \
    -d '{"model": "nomic-embed-text", "prompt": "test"}' \
    --connect-timeout 5 > /dev/null 2>&1; then
    echo "  Ollama connection successful!"
else
    echo "  ERROR: Cannot connect to Ollama at $OLLAMA_URL"
    echo "  Please ensure:"
    echo "    1. Ollama is running on $OLLAMA_HOST"
    echo "    2. The nomic-embed-text model is available"
    echo "    3. Port $OLLAMA_PORT is accessible"
    exit 1
fi

# Step 3: Delete old database
echo ""
echo "Step 3: Cleaning old database..."
if [ -d "$DB_DIR" ]; then
    rm -rf "$DB_DIR"
    echo "  Deleted: $DB_DIR"
else
    echo "  No existing database found."
fi

# Step 4: Run ingestion
echo ""
echo "Step 4: Running ingestion pipeline..."
cd "$SCRIPT_DIR"
python3 ingest.py --rebuild

# Step 5: Run validation tests
echo ""
echo "Step 5: Running validation tests..."
if python3 test_queries.py; then
    echo ""
    echo "============================================================"
    echo "SUCCESS: Vector database rebuilt and validated!"
    echo "============================================================"
    echo ""
    echo "Database location: $DB_DIR"
    echo ""
    echo "Example query:"
    echo "  python3 $SCRIPT_DIR/query.py 'What happens during rc.S?'"
    exit 0
else
    echo ""
    echo "============================================================"
    echo "WARNING: Some validation tests failed!"
    echo "============================================================"
    echo "The database was rebuilt but may not return optimal results."
    exit 1
fi

"""Configuration constants for the vector database system."""

import os
from pathlib import Path

# Ollama Configuration
OLLAMA_HOST = "10.10.10.124"
OLLAMA_PORT = 11434
OLLAMA_MODEL = "nomic-embed-text"

# Documentation paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "Documentation" / "verified"

# Database configuration
DB_DIR = Path.home() / ".claude" / "skills" / "porteus-kiosk" / "vectordb"
COLLECTION_NAME = "porteus_docs"

# Chunking parameters
MAX_CHUNK_CHARS = 4000
OVERLAP_CHARS = 100


def get_ollama_url() -> str:
    """Get the Ollama API embeddings endpoint URL."""
    return f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/embeddings"


def get_db_path() -> Path:
    """Get the database path, creating directories if needed."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return DB_DIR


def get_docs_path() -> Path:
    """Get the documentation directory path."""
    if not DOCS_DIR.exists():
        raise FileNotFoundError(f"Documentation directory not found: {DOCS_DIR}")
    return DOCS_DIR

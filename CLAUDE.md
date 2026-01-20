# PeanutChat - Claude Code Project Guide

## Project Overview
PeanutChat is a FastAPI-based AI chat application that integrates with Ollama for LLM interactions. It features authentication, knowledge base management, MCP (Model Context Protocol) tools, memory/conversation persistence, and user profiles.

## Tech Stack
- **Backend:** Python 3, FastAPI
- **LLM:** Ollama (local)
- **Database:** SQLite (`peanutchat.db`)
- **Frontend:** Static HTML/JS served by FastAPI

## Project Structure
```
app/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration settings
├── routers/             # API route handlers
│   ├── auth.py, chat.py, commands.py, knowledge.py
│   ├── mcp.py, memory.py, models.py, settings.py, user_profile.py
├── services/            # Business logic
│   ├── ollama.py, auth_service.py, conversation_store.py
│   ├── knowledge_base.py, memory_service.py, mcp_client.py
│   └── image_backends.py, video_backends.py, tool_executor.py
├── models/              # Pydantic schemas
├── middleware/          # Request middleware
└── tools/               # Tool definitions for LLM
static/                  # Frontend HTML/JS/CSS
```

## Service Management (Passwordless Sudo)
The following commands are available without password for user `tech`:

```bash
# Service control
sudo systemctl start peanutchat
sudo systemctl stop peanutchat
sudo systemctl restart peanutchat
sudo systemctl status peanutchat
sudo systemctl cat peanutchat.service
sudo systemctl enable peanutchat
sudo systemctl disable peanutchat

# View logs
sudo journalctl -u peanutchat -f      # Follow live logs
sudo journalctl -u peanutchat -n 50   # Last 50 lines
```

## Running Locally
```bash
# Activate virtual environment
source venv/bin/activate

# Run directly
python run.py

# Or via start script
./start_peanutchat.sh
```

## Dependencies
- Ollama service must be running (`ollama.service`)
- Python virtual environment at `./venv/`
- Environment variables in `.env`

## MCP Tool Documentation
Reference implementations for MCP tools are in:
- `mcp_tool_documentation/image_gen/` - Image generation MCP server
- `mcp_tool_documentation/video_gen/` - Video generation MCP server

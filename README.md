# PeanutChat

A feature-rich AI chatbot application with real-time streaming, web search, image generation, and multi-modal capabilities.

## Why "PeanutChat"?

This project is named after Rachel, affectionately nicknamed "Peanut" by her family. Just like a peanut is small but packed with goodness, this chat application aims to be a compact yet powerful AI companion.

## Features

- **Real-time Streaming Responses** - Watch AI responses appear token by token via Server-Sent Events
- **Multi-Model Support** - Choose from any model available in your Ollama instance
- **Web Search Integration** - AI can search the web using Brave Search API for up-to-date information
- **Image Generation** - Generate images on-demand using Stable Diffusion XL
- **File Processing** - Upload and analyze PDFs, text files, and ZIP archives
- **Vision Support** - Upload images for analysis with vision-capable models
- **Extended Thinking** - Support for models with reasoning/thinking capabilities
- **Conversation Management** - Persistent storage, forking, and editing of conversations
- **Customizable Personas** - Define custom AI personalities and behaviors
- **Multiple Themes** - Dark, light, midnight, and forest themes

## Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **Ollama** - Local LLM inference engine
- **PyTorch** - Deep learning framework
- **Diffusers** - Stable Diffusion image generation
- **HTTPX** - Async HTTP client

### Frontend
- **Vanilla JavaScript** (ES6 modules)
- **Tailwind CSS** - Utility-first styling
- **Marked** - Markdown rendering
- **Highlight.js** - Syntax highlighting

## Project Structure

```
PeanutChat/
├── app/
│   ├── main.py                 # FastAPI application setup
│   ├── config.py               # Configuration settings
│   ├── models/
│   │   └── schemas.py          # Pydantic data models
│   ├── routers/
│   │   ├── chat.py             # Chat endpoints with SSE streaming
│   │   ├── models.py           # Model selection endpoints
│   │   └── settings.py         # Settings endpoints
│   ├── services/
│   │   ├── ollama.py           # Ollama API integration
│   │   ├── tool_executor.py    # Web search & image generation
│   │   ├── conversation_store.py  # Conversation persistence
│   │   ├── file_processor.py   # PDF/ZIP/text processing
│   │   ├── image_generator.py  # SDXL image generation
│   │   └── gpu_manager.py      # GPU memory management
│   └── tools/
│       └── definitions.py      # Tool definitions
├── static/
│   ├── index.html              # Main application HTML
│   ├── js/
│   │   ├── app.js              # App initialization
│   │   ├── chat.js             # Chat message handling
│   │   └── settings.js         # Settings management
│   └── css/
│       └── styles.css          # Custom styles
├── conversations/              # Stored conversations (JSON)
├── generated_images/           # AI-generated images
├── run.py                      # Entry point
├── requirements.txt            # Python dependencies
├── settings.json               # User preferences
└── start_peanutchat.sh         # Startup script
```

## Prerequisites

- Python 3.12+
- CUDA-capable GPU (recommended for image generation)
- [Ollama](https://ollama.ai/) running locally or on your network
- Brave Search API key (for web search functionality)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/laundryguy77/PeanutChat.git
   cd PeanutChat
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application**

   Edit `app/config.py` to set:
   - `OLLAMA_BASE_URL` - Your Ollama server address
   - `BRAVE_SEARCH_API_KEY` - Your Brave Search API key

5. **Run the application**
   ```bash
   python run.py
   ```
   Or use the startup script:
   ```bash
   ./start_peanutchat.sh
   ```

6. **Access the application**

   Open your browser to `http://localhost:8080`

## Configuration

### User Settings (settings.json)

| Setting | Description | Default |
|---------|-------------|---------|
| `model` | Active LLM model | `gpt-oss:latest` |
| `temperature` | Response randomness (0-2) | `0.7` |
| `top_p` | Nucleus sampling | `0.9` |
| `top_k` | Top-k sampling | `40` |
| `num_ctx` | Context window size | `4096` |
| `repeat_penalty` | Repetition penalty | `1.1` |
| `persona` | Custom AI persona | `null` |
| `tts_enabled` | Text-to-speech toggle | `false` |

### Environment Configuration

Update `app/config.py` for your environment:

```python
OLLAMA_BASE_URL = "http://localhost:11434"  # Your Ollama instance
BRAVE_SEARCH_API_KEY = "your-api-key-here"  # Brave Search API
```

## API Endpoints

### Chat
- `POST /api/chat` - Send message (SSE streaming response)
- `GET /api/chat/conversations` - List all conversations
- `POST /api/chat/conversations` - Create new conversation

### Models
- `GET /api/models` - List available models
- `POST /api/models/select` - Select active model
- `GET /api/models/current` - Get current model
- `GET /api/models/capabilities` - Get model capabilities

### Settings
- `GET /api/settings` - Get all settings
- `PUT /api/settings` - Update settings

## Tools

PeanutChat supports AI tool calling for enhanced capabilities:

1. **Web Search** - Search the internet using Brave Search
2. **Image Generation** - Create images with Stable Diffusion XL
3. **Conversation Search** - Search through past conversations

## License

MIT License

## Acknowledgments

Built with love for Peanut (Rachel).

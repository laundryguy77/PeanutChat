# Video Generation MCP Server

An MCP (Model Context Protocol) server that provides AI video generation capabilities via Hugging Face Spaces. Supports both **text-to-video** and **image-to-video** generation using Playwright browser automation.

## Features

- **text_to_video**: Generate video from text descriptions
  - Uses LTX-Video, Wan, or similar models via Hugging Face Spaces
  - Describe a scene and get a short video clip
  
- **image_to_video**: Animate a still image into video
  - Upload an image and describe the motion
  - Great for animating portraits, landscapes, etc.

- **generate_video_batch**: Generate multiple videos at once
  - Mix text-to-video and image-to-video in one batch
  - Saves all results to a directory

- **list_supported_spaces**: See which Hugging Face Spaces are being used

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   MCP Client    │────▶│    server.py     │────▶│  video_backends.py  │
│  (Claude Code)  │     │  (MCP Protocol)  │     │  (VideoGenerator)   │
└─────────────────┘     └──────────────────┘     └──────────┬──────────┘
                                                            │
                                    ┌───────────────────────┼───────────────────────┐
                                    ▼                       ▼                       ▼
                        ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
                        │ HF Text-to-Video  │   │ HF Image-to-Video │   │ gradio_automation │
                        │   (LTX-Video)     │   │ (NSFW-Uncensored) │   │   (Base Class)    │
                        └───────────────────┘   └───────────────────┘   └───────────────────┘
                                    │                       │
                                    ▼                       ▼
                        ┌─────────────────────────────────────────────┐
                        │              Playwright Browser              │
                        │         (Chromium, headless mode)           │
                        └─────────────────────────────────────────────┘
                                            │
                                            ▼
                        ┌─────────────────────────────────────────────┐
                        │           Hugging Face Spaces               │
                        │  (Free, no API key, Gradio interfaces)      │
                        └─────────────────────────────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `server.py` | MCP server - JSON-RPC protocol handler, tool definitions |
| `video_backends.py` | Video generation backends for different HF Spaces |
| `gradio_automation.py` | Base class for automating Gradio interfaces |
| `requirements.txt` | Python dependencies |

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Usage with Claude Code

```bash
# Add to Claude Code
claude mcp add video-gen python /path/to/video-gen-mcp-server/server.py
```

## Usage with Claude Desktop

Add to your config file:

**Linux:** `~/.config/claude/claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "video-gen": {
      "command": "python",
      "args": ["/path/to/video-gen-mcp-server/server.py"]
    }
  }
}
```

## Tool Reference

### text_to_video

Generate video from a text description.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Text description of the video |
| `negative_prompt` | string | No | Things to avoid |
| `duration` | number | No | Desired duration (model-dependent) |
| `save_path` | string | No | Where to save the video |

**Example:**
```json
{
  "prompt": "A majestic eagle soaring over snow-capped mountains at sunset",
  "negative_prompt": "blurry, low quality, distorted",
  "save_path": "/tmp/eagle.mp4"
}
```

### image_to_video

Animate a still image into video.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_path` | string | Yes | Path to source image |
| `prompt` | string | No | Motion/action description |
| `negative_prompt` | string | No | Things to avoid |
| `duration` | number | No | Desired duration |
| `save_path` | string | No | Where to save the video |

**Example:**
```json
{
  "image_path": "/home/user/portrait.jpg",
  "prompt": "gentle smile, slight head turn, wind in hair",
  "save_path": "/tmp/animated_portrait.mp4"
}
```

## Hugging Face Spaces Used

### Text-to-Video
- Primary: `https://huggingface.co/spaces/Lightricks/LTX-Video-Distilled`
- Fallback: `https://huggingface.co/spaces/Wan-AI/Wan2.1-T2V-1.3B`

### Image-to-Video
- Primary: `https://huggingface.co/spaces/Heartsync/NSFW-Uncensored-video`
- Fallback: `https://huggingface.co/spaces/Justforailolomg/NSFW-Uncensored-video-duplicate`

## Notes

- **Generation Time**: Video generation typically takes 1-5 minutes depending on the model and queue
- **No API Key Required**: Uses free Hugging Face Spaces
- **Video Length**: Most models produce 2-5 second clips
- **Browser**: Runs Chromium headlessly via Playwright
- **Rate Limiting**: Hugging Face may queue requests during high traffic

## Troubleshooting

### Browser not found
Install Playwright browsers:
```bash
playwright install chromium
```

### Generation timeout
- Increase timeout in `video_backends.py` (default 5 minutes)
- Check if the Hugging Face Space is online and not overloaded

### Selectors not working
The Gradio UI may have changed. Check:
1. Visit the space URL manually
2. Inspect the DOM to find correct selectors
3. Update `gradio_automation.py` and `video_backends.py`

## License

MIT License

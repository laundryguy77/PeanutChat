# Perchance Image Generator MCP Server

An MCP (Model Context Protocol) server that provides text-to-image generation using the Perchance AI service via Playwright browser automation. This allows chat agents (like Claude) to generate images on demand.

## Features

- **generate_image**: Generate a single image from a text prompt
  - Returns base64 data or saves to file
  - Supports custom aspect ratios (square, portrait, landscape)
  - Supports negative prompts and style prefixes
  
- **generate_image_batch**: Generate multiple images at once
  - Saves all images to a specified directory
  - Useful for creating variations or storyboards

## Installation

```bash
# Clone or copy the server files
cd perchance-mcp-server

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Usage with Claude Desktop

Add to your Claude Desktop config (`~/.config/claude/claude_desktop_config.json` on Linux, `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "perchance": {
      "command": "python",
      "args": ["/path/to/perchance-mcp-server/server.py"]
    }
  }
}
```

## Usage with Claude Code

Add to your Claude Code MCP config:

```bash
claude mcp add perchance python /path/to/perchance-mcp-server/server.py
```

## Tool Reference

### generate_image

Generate a single image from a text prompt.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Text describing the image to generate |
| `negative_prompt` | string | No | "" | Things to avoid in the image |
| `shape` | string | No | "square" | Aspect ratio: "square", "portrait", "landscape" |
| `style` | string | No | "" | Art style prefix (e.g., "oil painting", "anime") |
| `save_path` | string | No | null | File path to save image (returns base64 if not set) |

**Example:**
```json
{
  "prompt": "a cozy cabin in the mountains at sunset",
  "negative_prompt": "blurry, low quality",
  "shape": "landscape",
  "style": "photorealistic",
  "save_path": "/tmp/cabin.jpg"
}
```

### generate_image_batch

Generate multiple images from a list of prompts.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompts` | array | Yes | - | List of text prompts |
| `output_dir` | string | Yes | - | Directory to save all images |
| `negative_prompt` | string | No | "" | Applied to all images |
| `shape` | string | No | "square" | Aspect ratio for all images |

**Example:**
```json
{
  "prompts": [
    "a red apple on a wooden table",
    "a green apple in a basket",
    "apple tree in an orchard"
  ],
  "output_dir": "/tmp/apple_images",
  "shape": "square"
}
```

## Notes

- This uses Playwright to automate the Perchance web interface
- The browser runs headlessly - no GUI required
- Generation speed depends on Perchance's servers (typically 10-60 seconds per image)
- No API key required - Perchance is a free service
- Rate limiting may apply during high traffic periods
- You can specify a custom browser path if needed

## Files

- `server.py` - The MCP server implementation
- `perchance_playwright.py` - The Playwright-based generator class (can be used standalone)
- `perchance_tool.py` - Simple CLI tool (uses the perchance library, alternative approach)

## License

MIT License

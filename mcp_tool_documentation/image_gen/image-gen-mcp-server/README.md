# Unified Image Generation MCP Server

A comprehensive MCP (Model Context Protocol) server providing AI image generation capabilities via Hugging Face Spaces. Supports **text-to-image**, **image-to-image**, **inpainting**, and **upscaling**.

## Features

| Tool | Description | Use Case |
|------|-------------|----------|
| `text_to_image` | Generate from text | Create new images from descriptions |
| `image_to_image` | Transform images | Style transfer, variations, modifications |
| `inpaint_image` | Edit with masks | Remove objects, change backgrounds, add elements |
| `upscale_image` | Enhance resolution | Increase quality and size |
| `generate_image_batch` | Batch generation | Multiple images at once |
| `list_supported_backends` | Show backends | See available HF Spaces |

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│   MCP Client    │────▶│    server.py     │────▶│ UnifiedImageGenerator   │
│  (Claude Code)  │     │  (MCP Protocol)  │     │   (image_backends.py)   │
└─────────────────┘     └──────────────────┘     └───────────┬─────────────┘
                                                             │
         ┌──────────────┬──────────────┬──────────────┬──────┴───────┐
         ▼              ▼              ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Text2Image  │ │ Img2Img     │ │ Inpainting  │ │ Upscale     │ │ gradio_auto │
│  Backend    │ │  Backend    │ │  Backend    │ │  Backend    │ │ (base class)│
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └─────────────┘
       │               │               │               │
       └───────────────┴───────────────┴───────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Playwright Browser  │
                    │   (Chromium/Chrome)  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Hugging Face Spaces │
                    │  (Free Gradio UIs)   │
                    └─────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `server.py` | MCP server - JSON-RPC protocol, tool definitions |
| `image_backends.py` | Backend implementations for each image operation |
| `gradio_automation.py` | Base class for Gradio UI automation |
| `requirements.txt` | Python dependencies |
| `README.md` | This documentation |

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

## Usage with Claude Code

```bash
claude mcp add image-gen python /path/to/image-gen-mcp-server/server.py
```

## Usage with Claude Desktop

Add to config (`~/.config/claude/claude_desktop_config.json` on Linux):

```json
{
  "mcpServers": {
    "image-gen": {
      "command": "python",
      "args": ["/path/to/image-gen-mcp-server/server.py"]
    }
  }
}
```

## Tool Reference

### text_to_image

Generate an image from a text description.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | ✅ | - | Text description of the image |
| `negative_prompt` | string | ❌ | "" | Things to avoid |
| `width` | integer | ❌ | 1024 | Image width in pixels |
| `height` | integer | ❌ | 1024 | Image height in pixels |
| `guidance_scale` | number | ❌ | 7.5 | How closely to follow prompt (1-20) |
| `seed` | integer | ❌ | random | Random seed for reproducibility |
| `save_path` | string | ❌ | auto | Where to save the image |

**Example:**
```json
{
  "prompt": "A serene Japanese garden with cherry blossoms, koi pond, wooden bridge, golden hour lighting, photorealistic",
  "negative_prompt": "blurry, low quality, watermark, text",
  "width": 1024,
  "height": 768,
  "save_path": "/tmp/garden.png"
}
```

### image_to_image

Transform an existing image based on a prompt.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image_path` | string | ✅ | - | Path to source image |
| `prompt` | string | ✅ | - | Transformation description |
| `negative_prompt` | string | ❌ | "" | Things to avoid |
| `strength` | number | ❌ | 0.7 | Change amount (0.0-1.0) |
| `guidance_scale` | number | ❌ | 7.5 | How closely to follow prompt |
| `seed` | integer | ❌ | random | Random seed |
| `save_path` | string | ❌ | auto | Where to save result |

**Strength guide:**
- `0.2-0.4`: Subtle changes, preserves most detail
- `0.5-0.7`: Moderate changes, good for style transfer
- `0.8-1.0`: Major changes, almost complete regeneration

**Example:**
```json
{
  "image_path": "/home/user/photo.jpg",
  "prompt": "Van Gogh oil painting style, swirling brushstrokes, vibrant colors",
  "strength": 0.6,
  "save_path": "/tmp/photo_vangogh.png"
}
```

### inpaint_image

Edit specific regions using a mask.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image_path` | string | ✅ | - | Path to source image |
| `mask_path` | string | ✅ | - | Path to mask (white = edit) |
| `prompt` | string | ✅ | - | What to generate in masked area |
| `negative_prompt` | string | ❌ | "" | Things to avoid |
| `guidance_scale` | number | ❌ | 7.5 | How closely to follow prompt |
| `seed` | integer | ❌ | random | Random seed |
| `save_path` | string | ❌ | auto | Where to save result |

**Mask format:**
- White (`#FFFFFF`) = areas to regenerate
- Black (`#000000`) = areas to keep unchanged
- PNG format recommended

**Example:**
```json
{
  "image_path": "/home/user/room.jpg",
  "mask_path": "/home/user/room_mask.png",
  "prompt": "A fluffy orange cat sleeping on the couch",
  "save_path": "/tmp/room_with_cat.png"
}
```

### upscale_image

Enhance image resolution.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image_path` | string | ✅ | - | Path to source image |
| `scale` | number | ❌ | 2.0 | Upscale factor |
| `save_path` | string | ❌ | auto | Where to save result |

**Example:**
```json
{
  "image_path": "/home/user/small_image.png",
  "scale": 4.0,
  "save_path": "/tmp/large_image.png"
}
```

## Hugging Face Spaces Used

### Text-to-Image
- `https://huggingface.co/spaces/black-forest-labs/FLUX.1-schnell` (Primary)
- `https://huggingface.co/spaces/stabilityai/stable-diffusion-3.5-large`
- `https://huggingface.co/spaces/multimodalart/FLUX.1-merged`

### Image-to-Image
- `https://huggingface.co/spaces/diffusers/stable-diffusion-xl-img2img` (Primary)
- `https://huggingface.co/spaces/multimodalart/cosxl`

### Inpainting
- `https://huggingface.co/spaces/diffusers/stable-diffusion-xl-inpainting` (Primary)
- `https://huggingface.co/spaces/runwayml/stable-diffusion-inpainting`

### Upscaling
- `https://huggingface.co/spaces/finegrain/finegrain-image-enhancer` (Primary)
- `https://huggingface.co/spaces/Kwai-Kolors/SUPIR`

## CLI Usage

The backends can also be used directly from command line:

```bash
# Text to image
python image_backends.py text "a majestic lion" -o lion.png

# Image to image  
python image_backends.py img2img photo.jpg "watercolor painting" -s 0.6 -o watercolor.png

# Inpainting
python image_backends.py inpaint image.jpg mask.png "blue sky with clouds" -o edited.png

# Upscale
python image_backends.py upscale small.png -s 4.0 -o large.png
```

## Notes

- **Generation Time**: 30-180 seconds depending on model and queue
- **No API Key**: Uses free Hugging Face Spaces
- **Rate Limiting**: May experience queues during peak times
- **Browser**: Runs Chromium headlessly
- **Output Format**: PNG by default

## Troubleshooting

### Browser not found
```bash
playwright install chromium
```

### Space loading slowly
- Check if the space is awake at huggingface.co
- Try an alternative URL from the backend's `SPACE_URLS` list

### Selectors not working
- Space UI may have changed
- Check debug screenshot at `/tmp/*_error.png`
- Update selectors in `gradio_automation.py` or `image_backends.py`

### Generation timeout
- Increase timeout in backend initialization
- Default is 3 minutes (180000ms)

## License

MIT License

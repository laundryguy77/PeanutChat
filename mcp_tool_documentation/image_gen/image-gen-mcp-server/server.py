#!/usr/bin/env python3
"""
Unified Image Generation MCP Server

An MCP server providing comprehensive image generation capabilities:
- text_to_image: Generate from text descriptions
- image_to_image: Transform/restyle existing images
- inpaint: Edit specific regions of images
- upscale: Enhance image resolution

Uses Hugging Face Spaces via Playwright automation.
"""

import asyncio
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from image_backends import (
    UnifiedImageGenerator,
    TextToImageBackend,
    ImageToImageBackend,
    InpaintingBackend,
    UpscaleBackend
)

# MCP Protocol Implementation
async def read_message() -> dict | None:
    """Read a JSON-RPC message from stdin."""
    loop = asyncio.get_event_loop()
    try:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            return None
        return json.loads(line.strip())
    except json.JSONDecodeError:
        return None

def write_message(message: dict) -> None:
    """Write a JSON-RPC message to stdout."""
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()

def write_error(id: Any, code: int, message: str) -> None:
    """Write a JSON-RPC error response."""
    write_message({
        "jsonrpc": "2.0",
        "id": id,
        "error": {"code": code, "message": message}
    })

def write_result(id: Any, result: Any) -> None:
    """Write a JSON-RPC success response."""
    write_message({
        "jsonrpc": "2.0",
        "id": id,
        "result": result
    })

# Tool definitions
TOOLS = [
    {
        "name": "text_to_image",
        "description": "Generate an image from a text description. Uses AI models like FLUX or Stable Diffusion to create images from prompts. Generation typically takes 30-120 seconds.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Detailed text description of the image to generate. Be specific about subject, style, lighting, composition, etc."
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "Things to avoid in the image (e.g., 'blurry, low quality, distorted, watermark')",
                    "default": ""
                },
                "width": {
                    "type": "integer",
                    "description": "Image width in pixels",
                    "default": 1024
                },
                "height": {
                    "type": "integer",
                    "description": "Image height in pixels",
                    "default": 1024
                },
                "guidance_scale": {
                    "type": "number",
                    "description": "How closely to follow the prompt (1.0-20.0, higher = more literal)",
                    "default": 7.5
                },
                "seed": {
                    "type": "integer",
                    "description": "Random seed for reproducibility (optional)"
                },
                "save_path": {
                    "type": "string",
                    "description": "File path to save the image. Auto-generated if not provided."
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "image_to_image",
        "description": "Transform an existing image based on a text prompt. Use this for style transfer, modifications, or creating variations. The 'strength' parameter controls how much the image changes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the source image to transform"
                },
                "prompt": {
                    "type": "string",
                    "description": "Description of how to transform the image (e.g., 'oil painting style', 'make it look like winter')"
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "Things to avoid in the transformation",
                    "default": ""
                },
                "strength": {
                    "type": "number",
                    "description": "Transformation strength 0.0-1.0 (0.3 = subtle changes, 0.7 = significant changes, 0.9 = almost complete regeneration)",
                    "default": 0.7
                },
                "guidance_scale": {
                    "type": "number",
                    "description": "How closely to follow the prompt",
                    "default": 7.5
                },
                "seed": {
                    "type": "integer",
                    "description": "Random seed for reproducibility"
                },
                "save_path": {
                    "type": "string",
                    "description": "File path to save the result"
                }
            },
            "required": ["image_path", "prompt"]
        }
    },
    {
        "name": "inpaint_image",
        "description": "Edit specific regions of an image using a mask. White areas in the mask will be regenerated based on the prompt. Useful for removing objects, changing backgrounds, or adding elements.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the source image to edit"
                },
                "mask_path": {
                    "type": "string",
                    "description": "Path to the mask image (white = areas to regenerate, black = keep original)"
                },
                "prompt": {
                    "type": "string",
                    "description": "Description of what to generate in the masked area"
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "Things to avoid",
                    "default": ""
                },
                "guidance_scale": {
                    "type": "number",
                    "description": "How closely to follow the prompt",
                    "default": 7.5
                },
                "seed": {
                    "type": "integer",
                    "description": "Random seed for reproducibility"
                },
                "save_path": {
                    "type": "string",
                    "description": "File path to save the result"
                }
            },
            "required": ["image_path", "mask_path", "prompt"]
        }
    },
    {
        "name": "upscale_image",
        "description": "Enhance image resolution and quality. Increases the size of an image while preserving and enhancing details using AI upscaling.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the image to upscale"
                },
                "scale": {
                    "type": "number",
                    "description": "Upscale factor (2.0 = double size, 4.0 = quadruple)",
                    "default": 2.0
                },
                "save_path": {
                    "type": "string",
                    "description": "File path to save the upscaled image"
                }
            },
            "required": ["image_path"]
        }
    },
    {
        "name": "generate_image_batch",
        "description": "Generate multiple images from a list of prompts. Useful for creating variations or multiple concepts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of text prompts to generate images for"
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "Negative prompt applied to all images",
                    "default": ""
                },
                "output_dir": {
                    "type": "string",
                    "description": "Directory to save all generated images"
                }
            },
            "required": ["prompts", "output_dir"]
        }
    },
    {
        "name": "list_supported_backends",
        "description": "List available image generation backends and their capabilities.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

# Global generator instance
_generator: Optional[UnifiedImageGenerator] = None

async def get_generator() -> UnifiedImageGenerator:
    """Get or create the generator instance."""
    global _generator
    if _generator is None:
        _generator = UnifiedImageGenerator()
    return _generator

async def text_to_image(
    prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    guidance_scale: float = 7.5,
    seed: Optional[int] = None,
    save_path: Optional[str] = None
) -> dict:
    """Generate image from text prompt."""
    try:
        gen = await get_generator()
        result = await gen.text_to_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            guidance_scale=guidance_scale,
            seed=seed,
            output_path=save_path
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

async def image_to_image(
    image_path: str,
    prompt: str,
    negative_prompt: str = "",
    strength: float = 0.7,
    guidance_scale: float = 7.5,
    seed: Optional[int] = None,
    save_path: Optional[str] = None
) -> dict:
    """Transform image based on prompt."""
    try:
        gen = await get_generator()
        result = await gen.image_to_image(
            image_path=image_path,
            prompt=prompt,
            negative_prompt=negative_prompt,
            strength=strength,
            guidance_scale=guidance_scale,
            seed=seed,
            output_path=save_path
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

async def inpaint_image(
    image_path: str,
    mask_path: str,
    prompt: str,
    negative_prompt: str = "",
    guidance_scale: float = 7.5,
    seed: Optional[int] = None,
    save_path: Optional[str] = None
) -> dict:
    """Inpaint regions of an image."""
    try:
        gen = await get_generator()
        result = await gen.inpaint(
            image_path=image_path,
            mask_path=mask_path,
            prompt=prompt,
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
            seed=seed,
            output_path=save_path
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

async def upscale_image(
    image_path: str,
    scale: float = 2.0,
    save_path: Optional[str] = None
) -> dict:
    """Upscale image resolution."""
    try:
        gen = await get_generator()
        result = await gen.upscale(
            image_path=image_path,
            scale=scale,
            output_path=save_path
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

async def generate_image_batch(
    prompts: list[str],
    output_dir: str,
    negative_prompt: str = ""
) -> dict:
    """Generate multiple images from prompts."""
    results = []
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    gen = await get_generator()
    
    for i, prompt in enumerate(prompts):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}_{i:03d}.png"
        filepath = output_path / filename
        
        try:
            result = await gen.text_to_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                output_path=str(filepath)
            )
            results.append({
                "prompt": prompt,
                **result
            })
        except Exception as e:
            results.append({
                "prompt": prompt,
                "success": False,
                "error": str(e)
            })
    
    successful = sum(1 for r in results if r.get("success", False))
    return {
        "total": len(prompts),
        "successful": successful,
        "failed": len(prompts) - successful,
        "results": results
    }

def list_supported_backends() -> dict:
    """List available backends and their HuggingFace spaces."""
    return {
        "text_to_image": {
            "backend": "TextToImageBackend",
            "description": "Generate images from text descriptions",
            "spaces": TextToImageBackend.SPACE_URLS,
            "uncensored_spaces": TextToImageBackend.UNCENSORED_SPACE_URLS
        },
        "image_to_image": {
            "backend": "ImageToImageBackend",
            "description": "Transform/restyle existing images",
            "spaces": ImageToImageBackend.SPACE_URLS
        },
        "inpainting": {
            "backend": "InpaintingBackend",
            "description": "Edit specific regions using masks",
            "spaces": InpaintingBackend.SPACE_URLS
        },
        "upscale": {
            "backend": "UpscaleBackend",
            "description": "Enhance image resolution",
            "spaces": UpscaleBackend.SPACE_URLS
        }
    }

# MCP Protocol handlers
async def handle_initialize(id: Any, params: dict) -> None:
    """Handle the initialize request."""
    write_result(id, {
        "protocolVersion": "2024-11-05",
        "serverInfo": {
            "name": "image-generator",
            "version": "1.0.0"
        },
        "capabilities": {
            "tools": {}
        }
    })

async def handle_list_tools(id: Any) -> None:
    """Handle tools/list request."""
    write_result(id, {"tools": TOOLS})

async def handle_call_tool(id: Any, params: dict) -> None:
    """Handle tools/call request."""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    try:
        if tool_name == "text_to_image":
            result = await text_to_image(**arguments)
        elif tool_name == "image_to_image":
            result = await image_to_image(**arguments)
        elif tool_name == "inpaint_image":
            result = await inpaint_image(**arguments)
        elif tool_name == "upscale_image":
            result = await upscale_image(**arguments)
        elif tool_name == "generate_image_batch":
            result = await generate_image_batch(**arguments)
        elif tool_name == "list_supported_backends":
            result = list_supported_backends()
        else:
            write_error(id, -32601, f"Unknown tool: {tool_name}")
            return
        
        # Format response for MCP
        if isinstance(result, dict) and result.get("success") == False:
            content = [{"type": "text", "text": f"Error: {result.get('error', 'Unknown error')}"}]
        else:
            content = [{"type": "text", "text": json.dumps(result, indent=2)}]
            
            # If we have base64 image data, include it as an image block
            if isinstance(result, dict) and "base64" in result:
                content.append({
                    "type": "image",
                    "data": result["base64"],
                    "mimeType": result.get("mime_type", "image/png")
                })
        
        write_result(id, {"content": content})
        
    except Exception as e:
        write_error(id, -32603, f"Tool execution error: {str(e)}")

async def cleanup():
    """Cleanup on exit."""
    global _generator
    if _generator:
        await _generator.close()

async def main():
    """Main server loop."""
    try:
        while True:
            message = await read_message()
            if message is None:
                break
            
            method = message.get("method")
            id = message.get("id")
            params = message.get("params", {})
            
            if method == "initialize":
                await handle_initialize(id, params)
            elif method == "notifications/initialized":
                pass
            elif method == "tools/list":
                await handle_list_tools(id)
            elif method == "tools/call":
                await handle_call_tool(id, params)
            elif method == "ping":
                write_result(id, {})
            else:
                if id is not None:
                    write_error(id, -32601, f"Method not found: {method}")
    finally:
        await cleanup()

if __name__ == "__main__":
    asyncio.run(main())

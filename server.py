#!/usr/bin/env python3
"""
Perchance Image Generation MCP Server

An MCP server that provides text-to-image generation using the Perchance AI service
via Playwright browser automation.
"""

import asyncio
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from perchance_playwright import PerchanceGenerator

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
        "name": "generate_image",
        "description": "Generate an image from a text prompt using Perchance AI. Returns base64-encoded image data or saves to a file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The text prompt describing the image to generate"
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "Things to avoid in the generated image (optional)",
                    "default": ""
                },
                "shape": {
                    "type": "string",
                    "description": "Image aspect ratio",
                    "enum": ["square", "portrait", "landscape"],
                    "default": "square"
                },
                "style": {
                    "type": "string",
                    "description": "Art style to prefix the prompt with (e.g., 'oil painting', 'anime', 'photorealistic')",
                    "default": ""
                },
                "save_path": {
                    "type": "string",
                    "description": "Optional file path to save the image. If not provided, returns base64 data."
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "generate_image_batch",
        "description": "Generate multiple images from prompts. Useful for creating variations or multiple scenes.",
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
                    "description": "Things to avoid in all generated images (optional)",
                    "default": ""
                },
                "shape": {
                    "type": "string",
                    "description": "Image aspect ratio for all images",
                    "enum": ["square", "portrait", "landscape"],
                    "default": "square"
                },
                "style": {
                    "type": "string",
                    "description": "Art style to apply to all images",
                    "default": ""
                },
                "output_dir": {
                    "type": "string",
                    "description": "Directory to save images. Files will be named with timestamps."
                }
            },
            "required": ["prompts", "output_dir"]
        }
    }
]

# Global generator instance for connection reuse
_generator: PerchanceGenerator | None = None

async def get_generator() -> PerchanceGenerator:
    """Get or create the generator instance."""
    global _generator
    if _generator is None:
        _generator = PerchanceGenerator()
        await _generator.start()
    return _generator

async def generate_image(
    prompt: str,
    negative_prompt: str = "",
    shape: str = "square",
    style: str = "",
    save_path: str | None = None
) -> dict:
    """Generate a single image from a prompt."""
    try:
        gen = await get_generator()
        result = await gen.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            shape=shape,
            style=style,
            output_path=save_path,
            return_base64=(save_path is None)
        )
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def generate_image_batch(
    prompts: list[str],
    output_dir: str,
    negative_prompt: str = "",
    shape: str = "square",
    style: str = ""
) -> dict:
    """Generate multiple images from a list of prompts."""
    results = []
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    gen = await get_generator()
    
    for i, prompt in enumerate(prompts):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}_{i:03d}.jpg"
            filepath = output_path / filename
            
            result = await gen.generate(
                prompt=prompt,
                negative_prompt=negative_prompt,
                shape=shape,
                style=style,
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

# MCP Protocol handlers
async def handle_initialize(id: Any, params: dict) -> None:
    """Handle the initialize request."""
    write_result(id, {
        "protocolVersion": "2024-11-05",
        "serverInfo": {
            "name": "perchance-image-generator",
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
        if tool_name == "generate_image":
            result = await generate_image(**arguments)
        elif tool_name == "generate_image_batch":
            result = await generate_image_batch(**arguments)
        else:
            write_error(id, -32601, f"Unknown tool: {tool_name}")
            return
        
        # Format response for MCP
        if result.get("success", True) and "error" not in result:
            content = [{"type": "text", "text": json.dumps(result, indent=2)}]
            
            # If we have image data, include it as an image content block
            if "base64" in result:
                content.append({
                    "type": "image",
                    "data": result["base64"],
                    "mimeType": result.get("mime_type", "image/jpeg")
                })
        else:
            error_msg = result.get('error', 'Unknown error')
            content = [{"type": "text", "text": f"Error: {error_msg}"}]
        
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
                pass  # Acknowledgment, no response needed
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

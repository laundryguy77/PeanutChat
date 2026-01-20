#!/usr/bin/env python3
"""
Video Generation MCP Server

An MCP server that provides text-to-video and image-to-video generation
using Hugging Face Spaces via Playwright automation.
"""

import asyncio
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from video_backends import VideoGenerator

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
        "name": "text_to_video",
        "description": "Generate a video from a text prompt. Uses AI to create a short video clip based on your description. Generation typically takes 1-5 minutes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Text description of the video to generate. Be descriptive about the scene, action, and style."
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "Things to avoid in the video (e.g., 'blurry, low quality, distorted')",
                    "default": ""
                },
                "duration": {
                    "type": "number",
                    "description": "Desired video duration in seconds (actual duration depends on the model)",
                    "default": 3.0
                },
                "save_path": {
                    "type": "string",
                    "description": "File path to save the video. If not provided, saves to current directory with auto-generated name."
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "image_to_video",
        "description": "Generate a video from a source image. Animates the image based on an optional motion prompt. Generation typically takes 1-5 minutes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the source image file to animate"
                },
                "prompt": {
                    "type": "string",
                    "description": "Motion/action prompt describing how the image should animate (e.g., 'camera slowly zooms in', 'wind blowing through hair')",
                    "default": ""
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "Things to avoid in the animation",
                    "default": ""
                },
                "duration": {
                    "type": "number",
                    "description": "Desired video duration in seconds",
                    "default": 3.0
                },
                "save_path": {
                    "type": "string",
                    "description": "File path to save the video. If not provided, saves to current directory with auto-generated name."
                }
            },
            "required": ["image_path"]
        }
    },
    {
        "name": "generate_video_batch",
        "description": "Generate multiple videos from a list of prompts. Saves all videos to a specified directory.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["text", "image"],
                                "description": "Generation type: 'text' for text-to-video, 'image' for image-to-video"
                            },
                            "prompt": {
                                "type": "string",
                                "description": "Text prompt (required for text type, optional motion prompt for image type)"
                            },
                            "image_path": {
                                "type": "string",
                                "description": "Image path (required for image type)"
                            },
                            "negative_prompt": {
                                "type": "string",
                                "description": "Negative prompt"
                            }
                        },
                        "required": ["type"]
                    },
                    "description": "List of generation requests"
                },
                "output_dir": {
                    "type": "string",
                    "description": "Directory to save all generated videos"
                }
            },
            "required": ["prompts", "output_dir"]
        }
    },
    {
        "name": "list_supported_spaces",
        "description": "List the Hugging Face Spaces being used for video generation and their capabilities.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

# Global generator instance
_generator: Optional[VideoGenerator] = None

async def get_generator() -> VideoGenerator:
    """Get or create the generator instance."""
    global _generator
    if _generator is None:
        _generator = VideoGenerator()
        await _generator.start()
    return _generator

async def text_to_video(
    prompt: str,
    negative_prompt: str = "",
    duration: float = 3.0,
    save_path: Optional[str] = None
) -> dict:
    """Generate video from text prompt."""
    try:
        gen = await get_generator()
        result = await gen.text_to_video(
            prompt=prompt,
            negative_prompt=negative_prompt,
            duration=duration,
            output_path=save_path
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

async def image_to_video(
    image_path: str,
    prompt: str = "",
    negative_prompt: str = "",
    duration: float = 3.0,
    save_path: Optional[str] = None
) -> dict:
    """Generate video from image."""
    try:
        gen = await get_generator()
        result = await gen.image_to_video(
            image_path=image_path,
            prompt=prompt,
            negative_prompt=negative_prompt,
            duration=duration,
            output_path=save_path
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

async def generate_video_batch(
    prompts: list[dict],
    output_dir: str
) -> dict:
    """Generate multiple videos."""
    results = []
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    gen = await get_generator()
    
    for i, request in enumerate(prompts):
        gen_type = request.get("type", "text")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"video_{gen_type}_{timestamp}_{i:03d}.mp4"
        filepath = output_path / filename
        
        try:
            if gen_type == "text":
                result = await gen.text_to_video(
                    prompt=request.get("prompt", ""),
                    negative_prompt=request.get("negative_prompt", ""),
                    output_path=str(filepath)
                )
            else:  # image
                result = await gen.image_to_video(
                    image_path=request.get("image_path", ""),
                    prompt=request.get("prompt", ""),
                    negative_prompt=request.get("negative_prompt", ""),
                    output_path=str(filepath)
                )
            results.append({
                "request": request,
                **result
            })
        except Exception as e:
            results.append({
                "request": request,
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

def list_supported_spaces() -> dict:
    """List available spaces and their capabilities."""
    from video_backends import HuggingFaceTextToVideo, HuggingFaceImageToVideo
    
    return {
        "text_to_video": {
            "backend": "HuggingFaceTextToVideo",
            "spaces": HuggingFaceTextToVideo.SPACE_URLS,
            "description": "Generates video from text descriptions using models like LTX-Video"
        },
        "image_to_video": {
            "backend": "HuggingFaceImageToVideo", 
            "spaces": HuggingFaceImageToVideo.SPACE_URLS,
            "description": "Animates images into video clips with optional motion prompts"
        }
    }

# MCP Protocol handlers
async def handle_initialize(id: Any, params: dict) -> None:
    """Handle the initialize request."""
    write_result(id, {
        "protocolVersion": "2024-11-05",
        "serverInfo": {
            "name": "video-generator",
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
        if tool_name == "text_to_video":
            result = await text_to_video(**arguments)
        elif tool_name == "image_to_video":
            result = await image_to_video(**arguments)
        elif tool_name == "generate_video_batch":
            result = await generate_video_batch(**arguments)
        elif tool_name == "list_supported_spaces":
            result = list_supported_spaces()
        else:
            write_error(id, -32601, f"Unknown tool: {tool_name}")
            return
        
        # Format response for MCP
        if isinstance(result, dict) and result.get("success") == False:
            content = [{"type": "text", "text": f"Error: {result.get('error', 'Unknown error')}"}]
        else:
            content = [{"type": "text", "text": json.dumps(result, indent=2)}]
        
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

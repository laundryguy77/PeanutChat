WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web and read page content to find information. Automatically fetches and reads the top search results to provide comprehensive answers.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up on the web. Be specific and include relevant keywords."
                }
            },
            "required": ["query"]
        }
    }
}

CONVERSATION_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_conversations",
        "description": "Search through previous conversations for context and information. Use this when the user references something they discussed before, or when you need to recall information from past chats. Returns relevant snippets from past conversations.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find in past conversations. Use keywords related to the topic the user is asking about."
                }
            },
            "required": ["query"]
        }
    }
}

IMAGE_GENERATION_TOOL = {
    "type": "function",
    "function": {
        "name": "generate_image",
        "description": "Generate an image from a text description using Stable Diffusion XL. Use this tool when the user wants to create, generate, draw, or make an image, picture, artwork, or illustration. Describe the desired image in detail.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "A detailed description of the image to generate. Include subject, style, lighting, colors, mood, composition, and any specific details. More detail produces better results."
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "Things to avoid in the image (e.g., 'blurry, low quality, watermark'). Optional."
                },
                "width": {
                    "type": "integer",
                    "description": "Image width in pixels (512-1536, must be divisible by 8). Default is 1024.",
                    "default": 1024
                },
                "height": {
                    "type": "integer",
                    "description": "Image height in pixels (512-1536, must be divisible by 8). Default is 1024.",
                    "default": 1024
                },
                "style": {
                    "type": "string",
                    "enum": ["photorealistic", "artistic", "anime", "digital_art", "oil_painting", "watercolor", "sketch"],
                    "description": "Art style for the image. This will be appended to your prompt."
                }
            },
            "required": ["prompt"]
        }
    }
}

# All available tools (image generation disabled to save VRAM/disk)
ALL_TOOLS = [WEB_SEARCH_TOOL, CONVERSATION_SEARCH_TOOL]

def get_tools_for_model(is_vision: bool):
    """Get appropriate tools based on model capability"""
    # Vision capability no longer affects available tools since video generation is removed
    return ALL_TOOLS

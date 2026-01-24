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

BROWSE_WEBSITE_TOOL = {
    "type": "function",
    "function": {
        "name": "browse_website",
        "description": "Visit a specific URL and retrieve its content. Use this when you need to access a webpage directly (e.g., when given a URL, reading documentation, accessing a specific article). Returns the page content as readable text.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL to visit (must start with http:// or https://)"
                }
            },
            "required": ["url"]
        }
    }
}

KNOWLEDGE_BASE_TOOL = {
    "type": "function",
    "function": {
        "name": "search_knowledge_base",
        "description": "Search through the user's uploaded documents and files in the knowledge base. Use this to find information from PDFs, code files, text documents, and other files the user has uploaded. Returns relevant excerpts with source attribution.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find in the knowledge base. Use keywords related to what you're looking for."
                }
            },
            "required": ["query"]
        }
    }
}

ADD_MEMORY_TOOL = {
    "type": "function",
    "function": {
        "name": "add_memory",
        "description": "Store important information about the user for future reference. Use this when learning something significant about the user's preferences, personal details, or topics they care about. CRITICAL: If the user explicitly asks you to remember something (e.g., 'remember that...', 'don't forget...', 'keep in mind...'), use this tool IMMEDIATELY with source='explicit'.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The information to remember. Be concise but complete."
                },
                "category": {
                    "type": "string",
                    "enum": ["preference", "personal", "topic", "instruction"],
                    "description": "Category: 'preference' for likes/dislikes, 'personal' for name/location/job, 'topic' for interests/projects, 'instruction' for how they prefer things done"
                },
                "importance": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": "How important (1-10). Name=10, preferences=7, casual mentions=3."
                },
                "source": {
                    "type": "string",
                    "enum": ["explicit", "inferred"],
                    "description": "Set to 'explicit' if user directly asked you to remember this. Set to 'inferred' if you're proactively saving something they mentioned."
                }
            },
            "required": ["content", "category"]
        }
    }
}

QUERY_MEMORY_TOOL = {
    "type": "function",
    "function": {
        "name": "query_memory",
        "description": "Search your memory for relevant information about the user. Use this to recall their preferences, personal details, projects, or past discussions.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What to search for in memory. Be descriptive."
                }
            },
            "required": ["query"]
        }
    }
}

SET_CONVERSATION_TITLE_TOOL = {
    "type": "function",
    "function": {
        "name": "set_conversation_title",
        "description": "Set or update the title of the current conversation. Use this proactively when: 1) The conversation topic becomes clear, 2) The topic significantly changes, 3) A more descriptive title would help the user find this conversation later. Keep titles concise (3-8 words) and descriptive of the main topic or task.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The new title for the conversation. Should be concise (3-8 words) and describe the main topic or purpose."
                }
            },
            "required": ["title"]
        }
    }
}

# User Profile Tools

USER_PROFILE_READ_TOOL = {
    "type": "function",
    "function": {
        "name": "user_profile_read",
        "description": "Read the current user's profile. Use at conversation start to load context. Can read entire profile or specific sections.",
        "parameters": {
            "type": "object",
            "properties": {
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "all", "identity", "technical", "communication", "persona_preferences",
                            "interaction", "preferences", "pet_peeves", "boundaries", "values_beliefs",
                            "relationship_metrics", "sexual_romantic", "substances_health", "dark_content",
                            "private_self", "goals_aspirations", "social_context", "work_context",
                            "financial_context", "learning_context", "meta_system", "interaction_log", "custom_fields"
                        ]
                    },
                    "description": "Which sections to read. Use ['all'] for complete profile, or specify sections needed."
                },
                "include_disabled": {
                    "type": "boolean",
                    "description": "Whether to include sections where 'enabled' is false"
                }
            },
            "required": []
        }
    }
}

USER_PROFILE_UPDATE_TOOL = {
    "type": "function",
    "function": {
        "name": "user_profile_update",
        "description": "Update specific fields in the user profile. Supports nested paths using dot notation.",
        "parameters": {
            "type": "object",
            "properties": {
                "updates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Dot-notation path to the field. E.g., 'identity.preferred_name' or 'preferences.code.comment_style'"
                            },
                            "value": {
                                "description": "New value for the field. Type must match schema."
                            },
                            "operation": {
                                "type": "string",
                                "enum": ["set", "append", "remove", "increment", "decrement", "toggle"],
                                "description": "Operation to perform. 'set' replaces value, 'append'/'remove' for arrays, 'increment'/'decrement' for numbers, 'toggle' for booleans"
                            }
                        },
                        "required": ["path", "value"]
                    },
                    "description": "Array of updates to apply"
                },
                "reason": {
                    "type": "string",
                    "description": "Brief explanation of why this update is being made. Logged for audit."
                }
            },
            "required": ["updates", "reason"]
        }
    }
}

USER_PROFILE_LOG_EVENT_TOOL = {
    "type": "function",
    "function": {
        "name": "user_profile_log_event",
        "description": "Log an interaction event for later evaluation. Call this when notable positive or negative events occur.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_type": {
                    "type": "string",
                    "enum": [
                        "praise", "explicit_thanks", "task_completed", "correction_accepted",
                        "preference_remembered", "helpful_suggestion_accepted", "sensitive_info_shared",
                        "permission_granted", "humor_landed", "emotional_support_appreciated",
                        "boundary_respected", "frustration", "task_failed", "correction_rejected",
                        "preference_ignored", "had_to_repeat", "guardrail_complaint", "lie_caught",
                        "boundary_violated", "persona_break", "tone_mismatch", "over_explained",
                        "under_explained", "unsolicited_advice_unwanted", "missed_context",
                        "clarification_requested", "topic_change", "session_end", "preference_stated",
                        "boundary_stated", "information_corrected"
                    ],
                    "description": "Type of event that occurred"
                },
                "context": {
                    "type": "string",
                    "description": "Brief context about the event (1-2 sentences max)"
                },
                "severity": {
                    "type": "string",
                    "enum": ["minor", "moderate", "major"],
                    "description": "How significant was this event"
                }
            },
            "required": ["event_type"]
        }
    }
}

USER_PROFILE_ENABLE_SECTION_TOOL = {
    "type": "function",
    "function": {
        "name": "user_profile_enable_section",
        "description": "Enable or disable optional profile sections (sexual_romantic, substances_health, dark_content, private_self, financial_context). Only call when user explicitly requests.",
        "parameters": {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "enum": ["sexual_romantic", "substances_health", "dark_content", "private_self", "financial_context"],
                    "description": "Which section to enable/disable"
                },
                "enabled": {
                    "type": "boolean",
                    "description": "Whether to enable or disable the section"
                },
                "user_confirmed": {
                    "type": "boolean",
                    "description": "User explicitly confirmed they want this. Must be true to proceed."
                }
            },
            "required": ["section", "enabled", "user_confirmed"]
        }
    }
}

USER_PROFILE_ADD_NESTED_TOOL = {
    "type": "function",
    "function": {
        "name": "user_profile_add_nested",
        "description": "Add a key-value pair to a nested object like preferences, pet_peeves, or boundaries",
        "parameters": {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "enum": [
                        "preferences", "pet_peeves", "boundaries.soft_boundaries",
                        "boundaries.sensitive_topics", "private_self.shame_triggers",
                        "values_beliefs.political_detail.hot_topics", "custom_fields.fields"
                    ],
                    "description": "Which nested section to add to"
                },
                "domain": {
                    "type": "string",
                    "description": "The domain/category key (e.g., 'code', 'formatting', 'family')"
                },
                "key": {
                    "type": "string",
                    "description": "The specific key within the domain"
                },
                "value": {
                    "type": "string",
                    "description": "The value/preference/note"
                }
            },
            "required": ["section", "domain", "key", "value"]
        }
    }
}

USER_PROFILE_QUERY_TOOL = {
    "type": "function",
    "function": {
        "name": "user_profile_query",
        "description": "Ask a specific question about the user profile. Returns relevant information without loading full sections.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language question about the user. E.g., 'Does the user prefer detailed explanations?', 'What are their hard boundaries?', 'What coding languages do they use?'"
                }
            },
            "required": ["query"]
        }
    }
}

USER_PROFILE_EXPORT_TOOL = {
    "type": "function",
    "function": {
        "name": "user_profile_export",
        "description": "Export user profile data. Respects visibility tiers.",
        "parameters": {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "enum": ["json", "yaml", "summary"],
                    "description": "Export format"
                },
                "tier": {
                    "type": "string",
                    "enum": ["public", "exportable", "full"],
                    "description": "Which visibility tier to export. 'full' requires explicit user confirmation."
                },
                "user_confirmed": {
                    "type": "boolean",
                    "description": "User confirmed export. Required for 'full' tier."
                }
            },
            "required": ["format"]
        }
    }
}

USER_PROFILE_RESET_TOOL = {
    "type": "function",
    "function": {
        "name": "user_profile_reset",
        "description": "Reset profile sections to defaults. Destructive action requiring confirmation.",
        "parameters": {
            "type": "object",
            "properties": {
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Sections to reset. Use ['all'] for complete reset."
                },
                "preserve_identity": {
                    "type": "boolean",
                    "description": "Keep identity section intact even on full reset"
                },
                "user_confirmed": {
                    "type": "boolean",
                    "description": "User explicitly confirmed reset. Must be true."
                },
                "confirmation_phrase": {
                    "type": "string",
                    "description": "User's confirmation phrase for audit log"
                }
            },
            "required": ["sections", "user_confirmed", "confirmation_phrase"]
        }
    }
}

# Video Generation Tool
VIDEO_GENERATOR_TOOL = {
    "type": "function",
    "function": {
        "name": "generate_video",
        "description": "Generate a short video from a text prompt using AI. Takes 30-120 seconds to complete. Returns a URL to the generated video.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Detailed description of the video to generate. Be specific about actions, style, and content."
                },
                "duration": {
                    "type": "integer",
                    "description": "Duration of the video in seconds (2-10). Default is 4 seconds.",
                    "default": 4
                }
            },
            "required": ["prompt"]
        }
    }
}

# Text-to-Video Tool (HuggingFace Spaces)
TEXT_TO_VIDEO_TOOL = {
    "type": "function",
    "function": {
        "name": "text_to_video",
        "description": "Generate a short video from a text description using AI. Uses free HuggingFace Spaces. Takes 1-5 minutes to complete.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Detailed text description of the video to generate. Describe the scene, action, style, and mood."
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "Things to avoid in the video (e.g., 'blurry, low quality, distorted')"
                },
                "duration": {
                    "type": "number",
                    "description": "Desired video duration in seconds (2-5). Actual duration depends on the model."
                }
            },
            "required": ["prompt"]
        }
    }
}

# Image-to-Video Tool (HuggingFace Spaces)
IMAGE_TO_VIDEO_TOOL = {
    "type": "function",
    "function": {
        "name": "image_to_video",
        "description": "Animate a still image into a short video. Uses free HuggingFace Spaces. Takes 1-5 minutes to complete.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_base64": {
                    "type": "string",
                    "description": "Base64-encoded source image to animate"
                },
                "prompt": {
                    "type": "string",
                    "description": "Motion/action description (e.g., 'slow zoom in', 'wind blowing through hair', 'gentle smile')"
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "Things to avoid in the animation"
                }
            },
            "required": ["image_base64"]
        }
    }
}

# Image Generation Tools (HuggingFace Spaces via Playwright)

TEXT_TO_IMAGE_TOOL = {
    "type": "function",
    "function": {
        "name": "text_to_image",
        "description": "Generate an image from a text prompt using AI (FLUX.1 or Stable Diffusion). Takes 30-120 seconds. Returns base64-encoded image.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Detailed description of the image to generate"
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "Things to avoid in the image (optional)"
                },
                "width": {
                    "type": "integer",
                    "description": "Image width in pixels (default: 1024)"
                },
                "height": {
                    "type": "integer",
                    "description": "Image height in pixels (default: 1024)"
                }
            },
            "required": ["prompt"]
        }
    }
}

IMAGE_TO_IMAGE_TOOL = {
    "type": "function",
    "function": {
        "name": "image_to_image",
        "description": "Transform an existing image based on a text prompt. Strength controls how much the image changes. Takes 30-120 seconds.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_base64": {
                    "type": "string",
                    "description": "Base64-encoded source image to transform"
                },
                "prompt": {
                    "type": "string",
                    "description": "Description of the transformation to apply"
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "Things to avoid in the result (optional)"
                },
                "strength": {
                    "type": "number",
                    "description": "How much to change the image (0.0-1.0, higher = more change). Default: 0.7"
                }
            },
            "required": ["image_base64", "prompt"]
        }
    }
}

INPAINT_IMAGE_TOOL = {
    "type": "function",
    "function": {
        "name": "inpaint_image",
        "description": "Edit specific regions of an image using a mask. White areas in the mask will be regenerated based on the prompt. Takes 30-120 seconds.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_base64": {
                    "type": "string",
                    "description": "Base64-encoded source image"
                },
                "mask_base64": {
                    "type": "string",
                    "description": "Base64-encoded mask image (white = areas to edit, black = keep)"
                },
                "prompt": {
                    "type": "string",
                    "description": "What to generate in the masked regions"
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "Things to avoid in the result (optional)"
                }
            },
            "required": ["image_base64", "mask_base64", "prompt"]
        }
    }
}

UPSCALE_IMAGE_TOOL = {
    "type": "function",
    "function": {
        "name": "upscale_image",
        "description": "Enhance image resolution using AI upscaling. Increases size and adds detail. Takes 30-120 seconds.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_base64": {
                    "type": "string",
                    "description": "Base64-encoded source image to upscale"
                },
                "scale": {
                    "type": "number",
                    "description": "Upscale factor (2.0 or 4.0). Default: 2.0"
                }
            },
            "required": ["image_base64"]
        }
    }
}

# All available tools
ALL_TOOLS = [
    WEB_SEARCH_TOOL,
    BROWSE_WEBSITE_TOOL,
    CONVERSATION_SEARCH_TOOL,
    KNOWLEDGE_BASE_TOOL,
    ADD_MEMORY_TOOL,
    QUERY_MEMORY_TOOL,
    SET_CONVERSATION_TITLE_TOOL,
    VIDEO_GENERATOR_TOOL,
    TEXT_TO_VIDEO_TOOL,
    IMAGE_TO_VIDEO_TOOL,
    TEXT_TO_IMAGE_TOOL,
    IMAGE_TO_IMAGE_TOOL,
    INPAINT_IMAGE_TOOL,
    UPSCALE_IMAGE_TOOL,
    USER_PROFILE_READ_TOOL,
    USER_PROFILE_UPDATE_TOOL,
    USER_PROFILE_LOG_EVENT_TOOL,
    USER_PROFILE_ENABLE_SECTION_TOOL,
    USER_PROFILE_ADD_NESTED_TOOL,
    USER_PROFILE_QUERY_TOOL,
    USER_PROFILE_EXPORT_TOOL,
    USER_PROFILE_RESET_TOOL,
]

def get_tools_for_model(supports_tools: bool = True, supports_vision: bool = False, mcp_tools: list = None) -> list:
    """Get available tools filtered by model capabilities.

    Args:
        supports_tools: Whether the model supports tool calling
        supports_vision: Whether the model supports vision/images
        mcp_tools: Optional list of MCP tools in OpenAI format to include

    Returns:
        List of available tools in OpenAI function calling format
    """
    if not supports_tools:
        return []

    tools = ALL_TOOLS.copy()

    # Filter vision-only tools if model doesn't support vision
    if not supports_vision:
        tools = [t for t in tools if t.get('function', {}).get('name') != 'analyze_image']

    # Add MCP tools if provided
    if mcp_tools:
        tools.extend(mcp_tools)

    return tools

from fastapi import APIRouter, Request, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
import logging
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.ollama import ollama_service
from app.services.memory_service import get_memory_service
from app.services.system_prompt_builder import get_prompt_builder
from app.services import compaction_service
from app.services.mcp_client import get_mcp_manager
from app.services.user_profile_service import get_user_profile_service
from app.services.evaluator_service import get_evaluator_service

logger = logging.getLogger(__name__)
from app.services.tool_executor import tool_executor, create_context
from app.services.conversation_store import conversation_store
from app.services.file_processor import file_processor
from app.tools.definitions import get_tools_for_model
from app.config import get_settings, THINKING_TOKEN_LIMIT_INITIAL, THINKING_TOKEN_LIMIT_FOLLOWUP
from app.models.schemas import ChatRequest
from app.middleware.auth import require_auth
from app.models.auth_schemas import UserResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for English"""
    return len(text) // 4 + 1


def parse_text_function_calls(content: str) -> List[Dict]:
    """
    Parse text-based function calls from model output.

    Some models output function calls as text in various formats:
    - {"function_call": {"name": "...", "arguments": {...}}}
    - {"name": "...", "arguments": {...}}
    - [TOOL CALL] function_name("arg") or [TOOL CALL] function_name(key=value)

    Returns list of tool_calls in Ollama format.
    """
    tool_calls = []

    # Try to find JSON objects that look like function calls
    # Pattern for {"function_call": ...} format (OpenAI style)
    function_call_pattern = r'\{"function_call"\s*:\s*\{[^}]+\}\s*\}'
    # Pattern for direct {"name": "...", "arguments": ...} format
    direct_pattern = r'\{"name"\s*:\s*"[^"]+"\s*,\s*"arguments"\s*:\s*\{[^}]*\}\s*\}'

    for pattern in [function_call_pattern, direct_pattern]:
        matches = re.findall(pattern, content, re.DOTALL)
        for match in matches:
            try:
                parsed = json.loads(match)

                # Handle {"function_call": {...}} format
                if "function_call" in parsed:
                    fc = parsed["function_call"]
                    tool_calls.append({
                        "function": {
                            "name": fc.get("name"),
                            "arguments": fc.get("arguments", {})
                        }
                    })
                # Handle direct {"name": "...", "arguments": {...}} format
                elif "name" in parsed and "arguments" in parsed:
                    tool_calls.append({
                        "function": {
                            "name": parsed["name"],
                            "arguments": parsed.get("arguments", {})
                        }
                    })
            except json.JSONDecodeError:
                continue

    # Pattern for [TOOL CALL] function_name("arg") or [TOOL CALL] function_name(key=value, ...)
    # This catches models that output tool calls as readable text
    tool_call_text_pattern = r'\[TOOL\s*CALL\]\s*(\w+)\s*\(([^)]*)\)'
    text_matches = re.findall(tool_call_text_pattern, content, re.IGNORECASE)
    for func_name, args_str in text_matches:
        # Parse the arguments
        arguments = {}
        if args_str.strip():
            # Try to parse as key=value pairs first
            kv_pattern = r'(\w+)\s*[=:]\s*["\']?([^"\',$]+)["\']?'
            kv_matches = re.findall(kv_pattern, args_str)
            if kv_matches:
                for key, value in kv_matches:
                    arguments[key.strip()] = value.strip()
            else:
                # Treat as a single query argument
                # Remove surrounding quotes if present
                query = args_str.strip().strip('"\'')
                if query:
                    arguments["query"] = query

        if func_name:
            tool_calls.append({
                "function": {
                    "name": func_name,
                    "arguments": arguments
                }
            })
            logger.debug(f"Parsed text-based tool call: {func_name}({arguments})")

    return tool_calls


def truncate_messages_for_context(messages: List[Dict], max_tokens: int, reserve_tokens: int = 1000) -> List[Dict]:
    """
    Truncate message history to fit within context window.
    Keeps system message, current tool results, and recent messages.
    reserve_tokens: space to reserve for model response
    """
    available_tokens = max_tokens - reserve_tokens

    if not messages:
        return messages

    # Calculate total tokens for each message
    message_tokens = []
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, dict):
            content = json.dumps(content)
        tokens = estimate_tokens(str(content))
        message_tokens.append(tokens)

    total_tokens = sum(message_tokens)

    # If within limit, return as-is
    if total_tokens <= available_tokens:
        return messages

    # Strategy: Keep last N messages (tool results + instruction), truncate older history
    # Find where current tool interaction starts (look for tool role from the end)
    critical_start = len(messages)
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].get("role") == "tool" or messages[i].get("role") == "assistant":
            critical_start = i
        elif messages[i].get("role") == "user" and i < len(messages) - 1:
            critical_start = i
            break

    # Always keep: system prompt (if any) + critical messages from current interaction
    result = []
    kept_tokens = 0

    # Add system message if present
    if messages and messages[0].get("role") == "system":
        result.append(messages[0])
        kept_tokens += message_tokens[0]

    # Calculate tokens for critical messages
    critical_tokens = sum(message_tokens[critical_start:])

    # If critical messages alone exceed limit, we need to truncate tool content
    if critical_tokens > available_tokens - kept_tokens:
        logger.warning(f"Tool results too large ({critical_tokens} tokens), truncating content")
        # Still add them but they'll be cut by the model
        for i in range(critical_start, len(messages)):
            result.append(messages[i])
        return result

    # Add truncation notice
    if critical_start > (1 if messages[0].get("role") == "system" else 0):
        result.append({
            "role": "system",
            "content": "[Earlier conversation history truncated to fit context window]"
        })

    # Add critical messages
    result.extend(messages[critical_start:])
    kept_tokens += critical_tokens

    logger.debug(f"Kept {len(result)} messages (est. {kept_tokens} tokens, dropped {critical_start} older messages)")
    return result


async def build_context_with_compaction(
    messages: List[Dict],
    conv_id: str,
    settings,
    event_callback=None,
    user_id: Optional[int] = None
) -> List[Dict]:
    """Build context with intelligent compaction.

    Args:
        messages: Current message list
        conv_id: Conversation ID for storing compaction state
        settings: AppSettings instance
        event_callback: Optional async callback for SSE events (for status updates)
        user_id: User ID for ownership verification during compaction

    Returns:
        Message list with compaction applied if needed
    """
    if not settings.compaction_enabled:
        return truncate_messages_for_context(messages, settings.num_ctx)

    # Get current summary state
    current_summary = conversation_store.get_summary(conv_id)
    summary_tokens = conversation_store.get_summary_token_count(conv_id)

    # Check if compaction is needed
    should_do, to_compact, indices = compaction_service.should_compact(
        messages, settings, summary_tokens
    )

    if should_do:
        logger.info(f"Triggering compaction for conversation {conv_id}")

        # Notify client that we're optimizing (optional)
        if event_callback:
            await event_callback({
                "event": "status",
                "data": json.dumps({"status": "optimizing", "message": "Optimizing context..."})
            })

        # Perform compaction (with user verification)
        record = await compaction_service.compact_conversation(
            conv_id=conv_id,
            messages=messages,
            indices_to_compact=indices,
            model=settings.model,
            existing_summary=current_summary,
            existing_summary_tokens=summary_tokens,
            user_id=user_id
        )

        if record:
            # Build message list with summary
            messages = compaction_service.build_compacted_messages(
                messages,
                record.summary,
                indices
            )
            logger.debug(f"Compaction complete, new message count: {len(messages)}")
        else:
            # Fallback to simple truncation
            logger.warning("Compaction failed, falling back to truncation")
            return truncate_messages_for_context(messages, settings.num_ctx)

    elif current_summary:
        # Not compacting now, but we have an existing summary
        # Rebuild messages with the summary included
        conv = conversation_store.get(conv_id)
        if conv:
            # Find which messages are compacted
            compacted_indices = []
            for i, msg in enumerate(conv.messages):
                if msg.compacted:
                    compacted_indices.append(i)

            if compacted_indices:
                messages = compaction_service.build_compacted_messages(
                    messages,
                    current_summary,
                    compacted_indices
                )

    # Final safety truncation (should rarely be needed)
    return truncate_messages_for_context(messages, settings.num_ctx)


class EditMessageRequest(BaseModel):
    content: str


class ForkMessageRequest(BaseModel):
    content: str


class RenameConversationRequest(BaseModel):
    title: str


async def extract_memory_search_terms(
    user_message: str,
    model: str,
    max_retries: int = 2
) -> List[str]:
    """Phase 1: Extract search terms from user message for memory query."""
    prompt_builder = get_prompt_builder()
    extraction_prompt = prompt_builder.build_extraction_prompt(user_message)

    # Build simple messages for extraction
    messages = [
        {"role": "system", "content": "You are a JSON-only response assistant."},
        {"role": "user", "content": extraction_prompt}
    ]

    for attempt in range(max_retries + 1):
        try:
            # Use existing chat_complete for non-streaming
            response = await ollama_service.chat_complete(
                messages=messages,
                model=model,
                options={"temperature": 0.1, "num_ctx": 1024}
            )

            response_text = response.get("message", {}).get("content", "").strip()

            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', response_text)
            if json_match:
                data = json.loads(json_match.group())
                terms = data.get("terms", [])
                if isinstance(terms, list):
                    return [str(t) for t in terms if t]

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Memory extraction attempt {attempt + 1} failed: {e}")
            if attempt < max_retries:
                messages[1]["content"] += '\n\nYour previous response was not valid JSON. Respond ONLY with: {"terms": ["term1"]}'
                continue

    return []


@router.post("")
async def chat(request: Request, user: UserResponse = Depends(require_auth)):
    """Send a chat message and receive SSE stream response"""
    body = await request.json()
    chat_request = ChatRequest(**body)
    conv_id = request.headers.get("X-Conversation-ID")

    # Create new conversation if none specified
    if not conv_id:
        settings = get_settings()
        conv = await conversation_store.create(model=settings.model, user_id=user.id)
        conv_id = conv.id

    # Create request-scoped context for tool execution (thread-safe)
    tool_ctx = create_context(user_id=user.id, conversation_id=conv_id)

    async def event_generator():
        nonlocal conv_id, tool_ctx
        settings = get_settings()
        conv = conversation_store.get(conv_id, user_id=user.id)

        # If conversation not found or not owned by user, create a new one
        if not conv:
            conv = await conversation_store.create(model=settings.model, user_id=user.id)
            conv_id = conv.id
            # Update context with new conversation ID
            tool_ctx.conversation_id = conv_id

        # Send conversation ID to client
        yield {
            "event": "conversation",
            "data": json.dumps({"id": conv_id})
        }

        # Update context with conversation ID (in case it changed)
        tool_ctx.conversation_id = conv_id

        # Check if current model supports vision and tools
        is_vision = await ollama_service.is_vision_model(settings.model)
        supports_tools = await ollama_service.supports_tools(settings.model)
        logger.info(f"Chat request: model={settings.model}, vision={is_vision}, tools={supports_tools}")
        logger.debug(f"Images received: {len(chat_request.images) if chat_request.images else 0}")

        # Get appropriate tools for this model (only if it supports tools)
        # Include MCP tools from connected servers
        mcp_manager = get_mcp_manager()
        mcp_tools = mcp_manager.get_tools_as_openai_format()
        tools = get_tools_for_model(supports_tools=supports_tools, supports_vision=is_vision, mcp_tools=mcp_tools)

        # Register images for tool use (only if vision model)
        if chat_request.images and is_vision:
            msg_index = len(conv.messages)
            for img in chat_request.images:
                tool_ctx.register_image(msg_index, img)
                logger.debug(f"Registered image for tool use, length: {len(img)}")

        # Get history in API format (with user verification)
        history = conversation_store.get_messages_for_api(conv_id, user_id=user.id)

        # Process attached files and build enhanced message
        user_message = chat_request.message
        if chat_request.files:
            logger.info(f"Processing {len(chat_request.files)} attached files")
            for f in chat_request.files:
                logger.debug(f"File: {f.name}, type: {f.type}, content_len: {len(f.content) if f.content else 0}")
            file_context = file_processor.format_files_for_context(
                [f.model_dump() for f in chat_request.files]
            )
            logger.debug(f"File context length: {len(file_context) if file_context else 0}")
            if file_context:
                user_message = f"{chat_request.message}\n\n{file_context}"
                logger.debug(f"Enhanced user_message length: {len(user_message)}")

        # If images were uploaded but model doesn't support vision, inform the model
        if chat_request.images and not is_vision:
            # Get model capabilities to provide helpful context
            capabilities = await ollama_service.get_model_capabilities(settings.model)
            caps_list = capabilities.get("capabilities", [])
            caps_str = ", ".join(caps_list) if caps_list else "text processing"

            image_notice = f"\n\n[SYSTEM NOTE: The user has attached {len(chat_request.images)} image(s), but you are a text-only model without vision capabilities. You cannot see or analyze these images. Please politely inform the user that you cannot view images and suggest they use a vision-capable model (like llava, moondream, or llama3.2-vision) for image analysis. You can help with: {caps_str}.]"
            user_message = user_message + image_notice
            logger.debug("Added image notice for non-vision model")

        # === Load User Profile ===
        profile_service = get_user_profile_service()
        profile_context = None
        full_unlock_active = False  # Track if adult sections are unlocked for unanswered questions
        try:
            # Base sections always loaded
            sections_to_load = ["identity", "communication", "persona_preferences", "pet_peeves",
                                "boundaries", "relationship_metrics", "interaction"]

            # Get session ID from request headers for session-scoped unlock check
            session_id = request.headers.get("X-Session-ID")

            # Check if session has adult content unlocked
            # CRITICAL: This checks session-scoped unlock, NOT database status
            # New sessions start LOCKED by default (child safety requirement)
            adult_status = await profile_service.get_adult_mode_status(user.id)
            session_unlock_status = await profile_service.get_session_unlock_status(user.id, session_id) if session_id else {"enabled": False}

            # Both Tier 1 (adult_mode) AND session unlock required for adult sections
            full_unlock_active = adult_status.get("enabled") and session_unlock_status.get("enabled")
            if full_unlock_active:
                sections_to_load.extend(["sexual_romantic", "dark_content", "private_self", "substances_health"])
                logger.debug("Session unlock enabled - including sensitive sections in prompt")

            profile_sections = await profile_service.read_sections(
                user.id,
                sections_to_load,
                include_disabled=False
            )
            if profile_sections:
                profile_context = profile_sections
                logger.debug(f"Loaded profile context with {len(profile_sections)} sections")
        except Exception as e:
            logger.warning(f"Profile loading failed: {e}")

        # === Two-Phase Memory Retrieval ===
        memory_service = get_memory_service()
        prompt_builder = get_prompt_builder()
        memory_context = []
        user_name = None

        # Phase 1: Extract search terms (skip for very short messages)
        if len(chat_request.message) > 10:
            try:
                search_terms = await extract_memory_search_terms(
                    chat_request.message,
                    settings.model
                )
                logger.info(f"Memory search terms: {search_terms}")

                # Query memories with extracted terms
                if search_terms:
                    query = " ".join(search_terms)
                    memory_context = await memory_service.query_memories(
                        user_id=user.id,
                        query=query,
                        top_k=5
                    )
                    logger.info(f"Retrieved {len(memory_context)} memories")

                    # Check for user's name in memories
                    for mem in memory_context:
                        if mem.get("category") == "personal" and "name" in mem.get("content", "").lower():
                            content = mem.get("content", "")
                            if "name is" in content.lower():
                                # Extract and validate name
                                extracted = content.split("name is")[-1].strip().split()[0]
                                # Validate: names should be simple alphanumeric, no special chars
                                # that could be used for injection
                                if extracted and len(extracted) <= 50 and re.match(r'^[\w\-]+$', extracted):
                                    user_name = extracted
            except Exception as e:
                logger.warning(f"Memory retrieval failed: {e}")
                # Continue without memory context

        # Phase 2: Build enhanced system prompt with profile
        system_prompt = prompt_builder.build_prompt(
            persona=settings.persona,
            memory_context=memory_context,
            profile_context=profile_context,
            user_name=user_name,
            has_tools=supports_tools,
            has_vision=is_vision,
            full_unlock_enabled=full_unlock_active
        )

        # Log system prompt stats for debugging
        prompt_lines = system_prompt.count('\n')
        prompt_chars = len(system_prompt)
        logger.info(f"[SystemPrompt] {prompt_chars} chars, {prompt_lines} lines, tools={supports_tools}, vision={is_vision}, full_unlock={full_unlock_active}")
        if profile_context:
            populated_sections = [k for k, v in profile_context.items() if v and isinstance(v, dict) and any(v.values())]
            logger.debug(f"[Profile] Populated sections: {populated_sections}")

        # Build messages with memory-enhanced system prompt
        messages = ollama_service.build_messages_with_system(
            system_prompt=system_prompt,
            user_message=user_message,
            history=history,
            images=chat_request.images if is_vision else None,
            is_vision_model=is_vision,
            supports_tools=supports_tools
        )

        # Add user message to conversation
        user_msg = await conversation_store.add_message(
            conv_id,
            role="user",
            content=chat_request.message,
            images=chat_request.images if chat_request.images and is_vision else None
        )

        if user_msg:
            yield {
                "event": "message",
                "data": json.dumps({
                    "id": user_msg.id,
                    "role": "user"
                })
            }

        # Prepare Ollama options
        options = {
            "temperature": settings.temperature,
            "top_p": settings.top_p,
            "top_k": settings.top_k,
            "num_ctx": settings.num_ctx,
            "repeat_penalty": settings.repeat_penalty
        }

        collected_content = ""
        collected_thinking = ""  # Track thinking content for storage
        tool_calls = []

        # Store context metadata for the response
        context_metadata = {
            "memories_used": memory_context if memory_context else None,
            "tools_available": [t.get("function", {}).get("name") for t in tools] if tools else None
        }
        logger.info(f"[Context] Prepared metadata: memories={len(memory_context) if memory_context else 0}, tools={len(context_metadata['tools_available']) if context_metadata['tools_available'] else 0}")

        # Track active streams for cleanup on disconnect
        active_stream = None

        try:
            # Apply context window management with compaction
            async def send_status(event):
                yield event

            messages = await build_context_with_compaction(
                messages, conv_id, settings, user_id=user.id
            )

            # Track if we're in thinking mode
            is_thinking = False
            thinking_token_count = 0
            logger.debug(f"Starting stream with think={chat_request.think}")

            # Stream from Ollama - track for cleanup
            active_stream = ollama_service.chat_stream(
                messages=messages,
                model=settings.model,
                tools=tools,
                options=options,
                think=chat_request.think
            )
            async for chunk in active_stream:
                # Debug: log chunks that have thinking content
                if chunk.get("message", {}).get("thinking"):
                    logger.debug(f"Received thinking token: {len(chunk['message']['thinking'])} chars")
                if "message" in chunk:
                    msg = chunk["message"]

                    # Stream thinking tokens if present
                    if msg.get("thinking"):
                        is_thinking = True
                        thinking_token_count += 1
                        collected_thinking += msg["thinking"]  # Collect for storage
                        yield {
                            "event": "token",
                            "data": json.dumps({"thinking": msg["thinking"]})
                        }
                        # Safety: if thinking goes on too long without content, break
                        if thinking_token_count > THINKING_TOKEN_LIMIT_INITIAL:
                            logger.warning(f"Thinking limit reached ({thinking_token_count} tokens) without content, breaking")
                            break

                    # Stream content tokens
                    if msg.get("content"):
                        # If we were thinking and now have content, signal thinking is done
                        if is_thinking:
                            is_thinking = False
                            yield {
                                "event": "token",
                                "data": json.dumps({"thinking_done": True})
                            }
                        collected_content += msg["content"]
                        yield {
                            "event": "token",
                            "data": json.dumps({"content": msg["content"]})
                        }

                    # Collect tool calls
                    if msg.get("tool_calls"):
                        tool_calls = msg["tool_calls"]

                if chunk.get("done"):
                    # Signal thinking done if we were still thinking
                    if is_thinking:
                        yield {
                            "event": "token",
                            "data": json.dumps({"thinking_done": True})
                        }
                    break

            # Safety: If we had thinking but no content and no tool calls, send a fallback
            if collected_thinking and not collected_content and not tool_calls:
                logger.warning("Model produced thinking but no content - sending fallback response")
                fallback_msg = "I apologize, but I wasn't able to formulate a response. Could you please rephrase your question?"
                collected_content = fallback_msg
                yield {
                    "event": "token",
                    "data": json.dumps({"content": fallback_msg})
                }

            # If no native tool_calls, try parsing text-based function calls
            if not tool_calls and collected_content:
                parsed_calls = parse_text_function_calls(collected_content)
                if parsed_calls:
                    logger.info(f"Parsed {len(parsed_calls)} text-based function call(s)")
                    tool_calls = parsed_calls

            # Handle tool calls if any
            if tool_calls:
                # Store results to avoid executing tools twice
                tool_results = []

                for tc in tool_calls:
                    func = tc.get("function", {})
                    yield {
                        "event": "tool_call",
                        "data": json.dumps({
                            "name": func.get("name"),
                            "arguments": func.get("arguments")
                        })
                    }

                    # Execute the tool with explicit context
                    result = await tool_executor.execute(tc, user_id=user.id, conversation_id=conv_id)
                    tool_results.append(result)

                    yield {
                        "event": "tool_result",
                        "data": json.dumps({
                            "name": func.get("name"),
                            "result": result
                        })
                    }

                # Add assistant message with tool calls to conversation
                logger.info(f"[Context] Saving assistant message with thinking={len(collected_thinking) if collected_thinking else 0} chars")
                assistant_msg = await conversation_store.add_message(
                    conv_id,
                    role="assistant",
                    content=collected_content,
                    tool_calls=tool_calls,
                    thinking_content=collected_thinking if collected_thinking else None,
                    memories_used=context_metadata.get("memories_used"),
                    tools_available=context_metadata.get("tools_available")
                )

                # Build context with full history plus current tool results
                messages_with_tool = messages.copy()

                # Add assistant's tool call
                messages_with_tool.append({
                    "role": "assistant",
                    "content": collected_content,
                    "tool_calls": tool_calls
                })

                # Add tool results with clear marker for the model
                for tc, result in zip(tool_calls, tool_results):
                    func_name = tc.get("function", {}).get("name", "unknown")
                    # Wrap result with clear context marker
                    tool_content = {
                        "_current_request": True,
                        "tool": func_name,
                        "result": result
                    }
                    messages_with_tool.append({
                        "role": "tool",
                        "tool_name": func_name,
                        "content": json.dumps(tool_content)
                    })

                # Add instruction to respond to current results
                messages_with_tool.append({
                    "role": "user",
                    "content": "Based on the tool results above, please answer my question."
                })

                # Apply context window management for follow-up (use simple truncation for tool responses)
                messages_with_tool = truncate_messages_for_context(messages_with_tool, settings.num_ctx)

                # Get follow-up response (disable thinking mode to prevent infinite loops)
                followup_content = ""
                logger.debug(f"Starting follow-up stream with {len(messages_with_tool)} messages")
                thinking_count = 0
                # Track follow-up stream for cleanup
                followup_stream = ollama_service.chat_stream(
                    messages=messages_with_tool,
                    model=settings.model,
                    options=options,
                    think=False
                )
                try:
                    async for chunk in followup_stream:
                        msg = chunk.get("message", {})

                        # Track thinking tokens to detect runaway loops
                        if msg.get("thinking"):
                            thinking_count += 1
                            if thinking_count > THINKING_TOKEN_LIMIT_FOLLOWUP:
                                logger.warning(f"Thinking limit reached ({thinking_count} tokens), breaking")
                                break
                            continue  # Skip thinking tokens

                        if msg.get("content"):
                            content = msg["content"]
                            followup_content += content
                            yield {
                                "event": "token",
                                "data": json.dumps({"content": content})
                            }
                        if chunk.get("done"):
                            logger.debug(f"Follow-up done, content: {len(followup_content)} chars, thinking tokens: {thinking_count}")
                            break
                finally:
                    # Ensure follow-up stream is closed
                    try:
                        await followup_stream.aclose()
                    except Exception:
                        pass

                # Safety: If no content after tool call, send a fallback
                if not followup_content:
                    logger.warning("No content in follow-up response after tool call - sending fallback")
                    followup_content = "I retrieved the information, but couldn't formulate a response. Please try rephrasing your question."
                    yield {
                        "event": "token",
                        "data": json.dumps({"content": followup_content})
                    }

                # Add follow-up to conversation
                if followup_content:
                    followup_msg = await conversation_store.add_message(
                        conv_id,
                        role="assistant",
                        content=followup_content,
                        memories_used=context_metadata.get("memories_used"),
                        tools_available=context_metadata.get("tools_available")
                    )
                    if followup_msg:
                        yield {
                            "event": "message",
                            "data": json.dumps({
                                "id": followup_msg.id,
                                "role": "assistant"
                            })
                        }
            else:
                # No tool calls - add regular assistant message
                if collected_content:
                    logger.info(f"[Context] Saving assistant message with thinking={len(collected_thinking) if collected_thinking else 0} chars, memories={len(context_metadata.get('memories_used') or [])} items")
                    assistant_msg = await conversation_store.add_message(
                        conv_id,
                        role="assistant",
                        content=collected_content,
                        thinking_content=collected_thinking if collected_thinking else None,
                        memories_used=context_metadata.get("memories_used"),
                        tools_available=context_metadata.get("tools_available")
                    )
                    if assistant_msg:
                        yield {
                            "event": "message",
                            "data": json.dumps({
                                "id": assistant_msg.id,
                                "role": "assistant"
                            })
                        }

                    # For non-tool models, extract profile updates from the response
                    if not supports_tools and collected_content:
                        try:
                            from app.services.profile_extractor import extract_profile_updates
                            profile_updates = extract_profile_updates(collected_content, chat_request.message)
                            if profile_updates:
                                logger.info(f"Extracted {len(profile_updates)} profile updates from non-tool model response")
                                await profile_service.update_profile(
                                    user.id,
                                    profile_updates,
                                    reason="Extracted from conversation (non-tool model)"
                                )
                        except Exception as e:
                            logger.warning(f"Profile extraction failed: {e}")

            # === Trigger Evaluation if Needed ===
            try:
                evaluator = get_evaluator_service()
                evaluator.increment_interaction(user.id)
                if await evaluator.should_evaluate(user.id):
                    eval_result = await evaluator.evaluate(user.id)
                    logger.debug(f"Evaluation result: {eval_result.get('session_polarity', 'unknown')}")
            except Exception as e:
                logger.warning(f"Evaluation failed: {e}")

            yield {
                "event": "done",
                "data": json.dumps({"finish_reason": "stop"})
            }

        except (BrokenPipeError, ConnectionError, ConnectionResetError):
            # Client disconnected - exit gracefully without trying to yield
            logger.debug("Client disconnected during SSE stream")
            return
        except asyncio.CancelledError:
            # Request was cancelled - exit gracefully
            logger.debug("SSE stream cancelled")
            return
        except Exception as e:
            logger.error(f"Stream error: {e}")
            try:
                yield {
                    "event": "error",
                    "data": json.dumps({"message": str(e)})
                }
            except (BrokenPipeError, ConnectionError, ConnectionResetError):
                # Even the error yield failed - client is gone
                pass
        finally:
            # Clean up any active Ollama streams
            if active_stream is not None:
                try:
                    await active_stream.aclose()
                except Exception:
                    pass  # Stream may already be closed
            # Clean up context-scoped image registry
            tool_ctx.clear_images()

    return EventSourceResponse(event_generator())


@router.get("/conversations")
async def list_conversations(user: UserResponse = Depends(require_auth)):
    """List conversations for the authenticated user"""
    return {"conversations": conversation_store.list_for_user(user.id)}


@router.post("/conversations")
async def create_conversation(user: UserResponse = Depends(require_auth)):
    """Create a new conversation for the authenticated user"""
    settings = get_settings()
    conv = await conversation_store.create(model=settings.model, user_id=user.id)
    return {"id": conv.id, "title": conv.title}


@router.get("/conversations/{conv_id}")
async def get_conversation(conv_id: str, user: UserResponse = Depends(require_auth)):
    """Get a specific conversation with all messages (owned by user)"""
    conv = conversation_store.get(conv_id, user_id=user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv.to_dict()


@router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: str, user: UserResponse = Depends(require_auth)):
    """Delete a conversation (must be owned by user)"""
    # Verify ownership first
    conv = conversation_store.get(conv_id, user_id=user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if await conversation_store.delete(conv_id):
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Conversation not found")


@router.patch("/conversations/{conv_id}")
async def rename_conversation(
    conv_id: str,
    request: RenameConversationRequest,
    user: UserResponse = Depends(require_auth)
):
    """Rename a conversation (must be owned by user)"""
    # Verify ownership first
    conv = conversation_store.get(conv_id, user_id=user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if await conversation_store.rename(conv_id, request.title):
        return {"status": "renamed", "title": request.title}
    raise HTTPException(status_code=404, detail="Conversation not found")


@router.delete("/conversations/{conv_id}/messages")
async def clear_conversation(conv_id: str, user: UserResponse = Depends(require_auth)):
    """Clear all messages from a conversation (must be owned by user)"""
    # Verify ownership first
    conv = conversation_store.get(conv_id, user_id=user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if await conversation_store.clear_messages(conv_id):
        return {"status": "cleared"}
    raise HTTPException(status_code=404, detail="Conversation not found")


@router.patch("/conversations/{conv_id}/messages/{msg_id}")
async def edit_message(
    conv_id: str,
    msg_id: str,
    request: EditMessageRequest,
    user: UserResponse = Depends(require_auth)
):
    """Edit a message (in-place, for simple edits)"""
    # Verify ownership first
    conv = conversation_store.get(conv_id, user_id=user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    msg = await conversation_store.update_message(conv_id, msg_id, request.content)
    if msg:
        return {"status": "updated", "id": msg.id}
    raise HTTPException(status_code=404, detail="Message not found")


@router.post("/conversations/{conv_id}/messages/{msg_id}/fork")
async def fork_conversation(
    conv_id: str,
    msg_id: str,
    request: ForkMessageRequest,
    user: UserResponse = Depends(require_auth)
):
    """Fork conversation at a message with new content"""
    # Verify ownership first
    conv = conversation_store.get(conv_id, user_id=user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    new_conv = await conversation_store.fork_at_message(conv_id, msg_id, request.content)
    if new_conv:
        return {
            "status": "forked",
            "id": new_conv.id,
            "title": new_conv.title
        }
    raise HTTPException(status_code=404, detail="Conversation or message not found")


@router.post("/conversations/{conv_id}/regenerate/{msg_id}")
async def regenerate_response(
    conv_id: str,
    msg_id: str,
    request: Request,
    user: UserResponse = Depends(require_auth)
):
    """Regenerate an assistant response by removing it and generating a new one"""
    # Create request-scoped context for tool execution (thread-safe)
    tool_ctx = create_context(user_id=user.id, conversation_id=conv_id)

    conv = conversation_store.get(conv_id, user_id=user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Find the message index
    msg_index = None
    for i, msg in enumerate(conv.messages):
        if msg.id == msg_id:
            msg_index = i
            break

    if msg_index is None:
        raise HTTPException(status_code=404, detail="Message not found")

    # The message should be an assistant message
    if conv.messages[msg_index].role != "assistant":
        raise HTTPException(status_code=400, detail="Can only regenerate assistant messages")

    # Find the preceding user message
    user_msg_index = None
    for i in range(msg_index - 1, -1, -1):
        if conv.messages[i].role == "user":
            user_msg_index = i
            break

    if user_msg_index is None:
        raise HTTPException(status_code=400, detail="No preceding user message found")

    user_message = conv.messages[user_msg_index].content
    user_images = conv.messages[user_msg_index].images

    # Remove messages from the assistant message onward
    await conversation_store.truncate_messages(conv_id, msg_index)

    async def event_generator():
        settings = get_settings()

        # Check model capabilities
        is_vision = await ollama_service.is_vision_model(settings.model)
        supports_tools = await ollama_service.supports_tools(settings.model)

        # Get appropriate tools (including MCP tools from connected servers)
        mcp_manager = get_mcp_manager()
        mcp_tools = mcp_manager.get_tools_as_openai_format()
        tools = get_tools_for_model(supports_tools=supports_tools, supports_vision=is_vision, mcp_tools=mcp_tools)

        # Get updated history (without the removed messages, with user verification)
        history = conversation_store.get_messages_for_api(conv_id, user_id=user.id)

        # === Load User Profile ===
        profile_service = get_user_profile_service()
        profile_context = None
        full_unlock_active = False  # Track if adult sections are unlocked
        try:
            # Base sections always loaded
            sections_to_load = ["identity", "communication", "persona_preferences", "pet_peeves",
                                "boundaries", "relationship_metrics", "interaction"]

            # Get session ID from request headers for session-scoped unlock check
            session_id = request.headers.get("X-Session-ID")

            # Check if session has adult content unlocked
            # CRITICAL: This checks session-scoped unlock, NOT database status
            adult_status = await profile_service.get_adult_mode_status(user.id)
            session_unlock_status = await profile_service.get_session_unlock_status(user.id, session_id) if session_id else {"enabled": False}

            # Both Tier 1 (adult_mode) AND session unlock required for adult sections
            full_unlock_active = adult_status.get("enabled") and session_unlock_status.get("enabled")
            if full_unlock_active:
                sections_to_load.extend(["sexual_romantic", "dark_content", "private_self", "substances_health"])
                logger.debug("Regenerate: Session unlock enabled - including sensitive sections")

            profile_sections = await profile_service.read_sections(
                user.id,
                sections_to_load,
                include_disabled=False
            )
            if profile_sections:
                profile_context = profile_sections
        except Exception as e:
            logger.warning(f"Regenerate profile loading failed: {e}")

        # === Two-Phase Memory Retrieval ===
        memory_service = get_memory_service()
        prompt_builder = get_prompt_builder()
        memory_context = []
        user_name = None

        # Phase 1: Extract search terms (skip for very short messages)
        if len(user_message) > 10:
            try:
                search_terms = await extract_memory_search_terms(
                    user_message,
                    settings.model
                )
                logger.info(f"Regenerate memory search terms: {search_terms}")

                # Query memories with extracted terms
                if search_terms:
                    query = " ".join(search_terms)
                    memory_context = await memory_service.query_memories(
                        user_id=user.id,
                        query=query,
                        top_k=5
                    )
                    logger.info(f"Regenerate retrieved {len(memory_context)} memories")

                    # Check for user's name in memories
                    for mem in memory_context:
                        if mem.get("category") == "personal" and "name" in mem.get("content", "").lower():
                            content = mem.get("content", "")
                            if "name is" in content.lower():
                                # Extract and validate name
                                extracted = content.split("name is")[-1].strip().split()[0]
                                # Validate: names should be simple alphanumeric, no special chars
                                # that could be used for injection
                                if extracted and len(extracted) <= 50 and re.match(r'^[\w\-]+$', extracted):
                                    user_name = extracted
            except Exception as e:
                logger.warning(f"Regenerate memory retrieval failed: {e}")
                # Continue without memory context

        # Phase 2: Build enhanced system prompt with profile
        system_prompt = prompt_builder.build_prompt(
            persona=settings.persona,
            memory_context=memory_context,
            profile_context=profile_context,
            user_name=user_name,
            has_tools=supports_tools,
            has_vision=is_vision,
            full_unlock_enabled=full_unlock_active
        )

        # Build messages with memory-enhanced system prompt
        messages = ollama_service.build_messages_with_system(
            system_prompt=system_prompt,
            user_message=user_message,
            history=history[:-1] if history else [],  # Exclude the last user message as we'll add it fresh
            images=user_images if is_vision else None,
            is_vision_model=is_vision,
            supports_tools=supports_tools
        )

        # Prepare options
        options = {
            "temperature": settings.temperature,
            "top_p": settings.top_p,
            "top_k": settings.top_k,
            "num_ctx": settings.num_ctx,
            "repeat_penalty": settings.repeat_penalty
        }

        collected_content = ""
        tool_calls = []

        try:
            # Apply context window management with compaction (with user verification)
            messages = await build_context_with_compaction(
                messages, conv_id, settings, user_id=user.id
            )

            async for chunk in ollama_service.chat_stream(
                messages=messages,
                model=settings.model,
                tools=tools,
                options=options
            ):
                if "message" in chunk:
                    msg = chunk["message"]
                    if msg.get("content"):
                        collected_content += msg["content"]
                        yield {
                            "event": "token",
                            "data": json.dumps({"content": msg["content"]})
                        }
                    if msg.get("tool_calls"):
                        tool_calls = msg["tool_calls"]
                if chunk.get("done"):
                    break

            # If no native tool_calls, try parsing text-based function calls
            if not tool_calls and collected_content:
                parsed_calls = parse_text_function_calls(collected_content)
                if parsed_calls:
                    logger.info(f"Regenerate: Parsed {len(parsed_calls)} text-based function call(s)")
                    tool_calls = parsed_calls

            # Handle tool calls if any (simplified version)
            if tool_calls:
                for tc in tool_calls:
                    func = tc.get("function", {})
                    yield {
                        "event": "tool_call",
                        "data": json.dumps({
                            "name": func.get("name"),
                            "arguments": func.get("arguments")
                        })
                    }
                    result = await tool_executor.execute(tc, user_id=user.id, conversation_id=conv_id)
                    yield {
                        "event": "tool_result",
                        "data": json.dumps({
                            "name": func.get("name"),
                            "result": result
                        })
                    }

            # Save the new assistant message
            if collected_content:
                assistant_msg = await conversation_store.add_message(
                    conv_id,
                    role="assistant",
                    content=collected_content,
                    tool_calls=tool_calls if tool_calls else None
                )
                if assistant_msg:
                    yield {
                        "event": "message",
                        "data": json.dumps({
                            "id": assistant_msg.id,
                            "role": "assistant"
                        })
                    }

            yield {
                "event": "done",
                "data": json.dumps({"finish_reason": "stop"})
            }

        except (BrokenPipeError, ConnectionError, ConnectionResetError):
            logger.debug("Client disconnected during regenerate stream")
            return
        except asyncio.CancelledError:
            logger.debug("Regenerate stream cancelled")
            return
        except Exception as e:
            logger.error(f"Regenerate stream error: {e}")
            try:
                yield {
                    "event": "error",
                    "data": json.dumps({"message": str(e)})
                }
            except (BrokenPipeError, ConnectionError, ConnectionResetError):
                pass
        finally:
            # Clean up context-scoped resources
            tool_ctx.clear_images()

    return EventSourceResponse(event_generator())


# Legacy endpoints for backward compatibility
@router.get("/history")
async def get_chat_history(request: Request, user: UserResponse = Depends(require_auth)):
    """Get chat history for current session (legacy)"""
    conv_id = request.headers.get("X-Conversation-ID", "default")
    conv = conversation_store.get(conv_id, user_id=user.id)
    if not conv:
        return {"history": []}
    return {"history": conversation_store.get_messages_for_api(conv_id, user_id=user.id)}


@router.delete("/history")
async def clear_chat_history(request: Request, user: UserResponse = Depends(require_auth)):
    """Clear chat history for current session (legacy)"""
    conv_id = request.headers.get("X-Conversation-ID")
    if conv_id:
        # Verify ownership before clearing
        conv = conversation_store.get(conv_id, user_id=user.id)
        if conv:
            await conversation_store.clear_messages(conv_id)
    # Clear images from context if available, otherwise from executor
    from app.services.tool_executor import get_current_context
    ctx = get_current_context()
    if ctx:
        ctx.clear_images()
    else:
        tool_executor.clear_images()
    return {"status": "cleared"}

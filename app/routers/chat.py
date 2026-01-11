from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.ollama import ollama_service
from app.services.tool_executor import tool_executor
from app.services.conversation_store import conversation_store
from app.services.file_processor import file_processor
from app.tools.definitions import get_tools_for_model
from app.config import get_settings
from app.models.schemas import ChatRequest

router = APIRouter(prefix="/api/chat", tags=["chat"])


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for English"""
    return len(text) // 4 + 1


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
        print(f"[CONTEXT] Warning: Tool results too large ({critical_tokens} tokens), truncating content")
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

    print(f"[CONTEXT] Kept {len(result)} messages (est. {kept_tokens} tokens, dropped {critical_start} older messages)")
    return result


class EditMessageRequest(BaseModel):
    content: str


class ForkMessageRequest(BaseModel):
    content: str


class RenameConversationRequest(BaseModel):
    title: str


@router.post("")
async def chat(request: Request):
    """Send a chat message and receive SSE stream response"""
    body = await request.json()
    chat_request = ChatRequest(**body)
    conv_id = request.headers.get("X-Conversation-ID")

    # Create new conversation if none specified
    if not conv_id:
        settings = get_settings()
        conv = conversation_store.create(model=settings.model)
        conv_id = conv.id

    async def event_generator():
        nonlocal conv_id
        settings = get_settings()
        conv = conversation_store.get(conv_id)

        # If conversation not found, create a new one
        if not conv:
            conv = conversation_store.create(model=settings.model)
            conv_id = conv.id

        # Send conversation ID to client
        yield {
            "event": "conversation",
            "data": json.dumps({"id": conv_id})
        }

        # Set current conversation in tool executor for context-aware tools
        tool_executor.set_current_conversation(conv_id)

        # Check if current model supports vision and tools
        is_vision = await ollama_service.is_vision_model(settings.model)
        supports_tools = await ollama_service.supports_tools(settings.model)
        print(f"[CHAT] Model: {settings.model}, is_vision: {is_vision}, supports_tools: {supports_tools}")
        print(f"[CHAT] Images received: {len(chat_request.images) if chat_request.images else 0}")

        # Get appropriate tools for this model (only if it supports tools)
        tools = get_tools_for_model(is_vision) if supports_tools else None

        # Register images for tool use (only if vision model)
        if chat_request.images and is_vision:
            msg_index = len(conv.messages)
            for img in chat_request.images:
                tool_executor.register_image(msg_index, img)
                print(f"[CHAT] Registered image for tool use, length: {len(img)}")

        # Get history in API format
        history = conversation_store.get_messages_for_api(conv_id)

        # Process attached files and build enhanced message
        user_message = chat_request.message
        if chat_request.files:
            print(f"[CHAT] Processing {len(chat_request.files)} attached files")
            for f in chat_request.files:
                print(f"[CHAT] File: {f.name}, type: {f.type}, content_len: {len(f.content) if f.content else 0}, is_base64: {f.is_base64}")
            file_context = file_processor.format_files_for_context(
                [f.model_dump() for f in chat_request.files]
            )
            print(f"[CHAT] file_context length: {len(file_context) if file_context else 0}")
            if file_context:
                user_message = f"{chat_request.message}\n\n{file_context}"
                print(f"[CHAT] Enhanced user_message length: {len(user_message)}")
                print(f"[CHAT] First 1000 chars of user_message: {user_message[:1000]}")

        # If images were uploaded but model doesn't support vision, inform the model
        if chat_request.images and not is_vision:
            # Get model capabilities to provide helpful context
            capabilities = await ollama_service.get_model_capabilities(settings.model)
            caps_list = capabilities.get("capabilities", [])
            caps_str = ", ".join(caps_list) if caps_list else "text processing"

            image_notice = f"\n\n[SYSTEM NOTE: The user has attached {len(chat_request.images)} image(s), but you are a text-only model without vision capabilities. You cannot see or analyze these images. Please politely inform the user that you cannot view images and suggest they use a vision-capable model (like llava, moondream, or llama3.2-vision) for image analysis. You can help with: {caps_str}.]"
            user_message = user_message + image_notice
            print(f"[CHAT] Added image notice for non-vision model")

        # Build messages with persona (handle images based on vision capability)
        messages = ollama_service.build_messages(
            user_message=user_message,
            history=history,
            persona=settings.persona,
            images=chat_request.images if is_vision else None,
            is_vision_model=is_vision,
            has_tools=supports_tools
        )

        # Add user message to conversation
        user_msg = conversation_store.add_message(
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
        tool_calls = []

        try:
            # Apply context window truncation
            messages = truncate_messages_for_context(messages, settings.num_ctx)

            # Track if we're in thinking mode
            is_thinking = False
            print(f"[CHAT] Starting stream with think={chat_request.think}")

            # Stream from Ollama
            async for chunk in ollama_service.chat_stream(
                messages=messages,
                model=settings.model,
                tools=tools,
                options=options,
                think=chat_request.think
            ):
                # Debug: log chunks that have thinking content
                if chunk.get("message", {}).get("thinking"):
                    print(f"[CHAT] Received thinking token: {len(chunk['message']['thinking'])} chars")
                if "message" in chunk:
                    msg = chunk["message"]

                    # Stream thinking tokens if present
                    if msg.get("thinking"):
                        is_thinking = True
                        yield {
                            "event": "token",
                            "data": json.dumps({"thinking": msg["thinking"]})
                        }

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

                    # Execute the tool
                    result = await tool_executor.execute(tc)
                    tool_results.append(result)

                    yield {
                        "event": "tool_result",
                        "data": json.dumps({
                            "name": func.get("name"),
                            "result": result
                        })
                    }

                    # If video generation started
                    if result.get("video_id"):
                        yield {
                            "event": "video_started",
                            "data": json.dumps({
                                "video_id": result["video_id"]
                            })
                        }

                # Add assistant message with tool calls to conversation
                assistant_msg = conversation_store.add_message(
                    conv_id,
                    role="assistant",
                    content=collected_content,
                    tool_calls=tool_calls
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

                # Apply context window truncation for follow-up
                messages_with_tool = truncate_messages_for_context(messages_with_tool, settings.num_ctx)

                # Get follow-up response (disable thinking mode to prevent infinite loops)
                followup_content = ""
                print(f"[DEBUG] Starting follow-up stream with {len(messages_with_tool)} messages")
                thinking_count = 0
                async for chunk in ollama_service.chat_stream(
                    messages=messages_with_tool,
                    model=settings.model,
                    options=options,
                    think=False
                ):
                    msg = chunk.get("message", {})

                    # Track thinking tokens to detect runaway loops
                    if msg.get("thinking"):
                        thinking_count += 1
                        if thinking_count > 2000:  # Allow more thinking for complex queries
                            print(f"[DEBUG] Thinking limit reached ({thinking_count} tokens), breaking")
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
                        print(f"[DEBUG] Follow-up done, total content: {len(followup_content)} chars, thinking tokens: {thinking_count}")
                        break

                # Add follow-up to conversation
                if followup_content:
                    followup_msg = conversation_store.add_message(
                        conv_id,
                        role="assistant",
                        content=followup_content
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
                    assistant_msg = conversation_store.add_message(
                        conv_id,
                        role="assistant",
                        content=collected_content
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

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)})
            }

    return EventSourceResponse(event_generator())


@router.get("/conversations")
async def list_conversations():
    """List all conversations"""
    return {"conversations": conversation_store.list_all()}


@router.post("/conversations")
async def create_conversation():
    """Create a new conversation"""
    settings = get_settings()
    conv = conversation_store.create(model=settings.model)
    return {"id": conv.id, "title": conv.title}


@router.get("/conversations/{conv_id}")
async def get_conversation(conv_id: str):
    """Get a specific conversation with all messages"""
    conv = conversation_store.get(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv.to_dict()


@router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: str):
    """Delete a conversation"""
    if conversation_store.delete(conv_id):
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Conversation not found")


@router.patch("/conversations/{conv_id}")
async def rename_conversation(conv_id: str, request: RenameConversationRequest):
    """Rename a conversation"""
    if conversation_store.rename(conv_id, request.title):
        return {"status": "renamed", "title": request.title}
    raise HTTPException(status_code=404, detail="Conversation not found")


@router.delete("/conversations/{conv_id}/messages")
async def clear_conversation(conv_id: str):
    """Clear all messages from a conversation"""
    if conversation_store.clear_messages(conv_id):
        return {"status": "cleared"}
    raise HTTPException(status_code=404, detail="Conversation not found")


@router.patch("/conversations/{conv_id}/messages/{msg_id}")
async def edit_message(conv_id: str, msg_id: str, request: EditMessageRequest):
    """Edit a message (in-place, for simple edits)"""
    msg = conversation_store.update_message(conv_id, msg_id, request.content)
    if msg:
        return {"status": "updated", "id": msg.id}
    raise HTTPException(status_code=404, detail="Message not found")


@router.post("/conversations/{conv_id}/messages/{msg_id}/fork")
async def fork_conversation(conv_id: str, msg_id: str, request: ForkMessageRequest):
    """Fork conversation at a message with new content"""
    new_conv = conversation_store.fork_at_message(conv_id, msg_id, request.content)
    if new_conv:
        return {
            "status": "forked",
            "id": new_conv.id,
            "title": new_conv.title
        }
    raise HTTPException(status_code=404, detail="Conversation or message not found")


@router.post("/conversations/{conv_id}/regenerate/{msg_id}")
async def regenerate_response(conv_id: str, msg_id: str):
    """Regenerate an assistant response by removing it and generating a new one"""
    conv = conversation_store.get(conv_id)
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
    with conversation_store._lock:
        conv.messages = conv.messages[:msg_index]
        conversation_store._save(conv)

    async def event_generator():
        settings = get_settings()

        # Check model capabilities
        is_vision = await ollama_service.is_vision_model(settings.model)
        supports_tools = await ollama_service.supports_tools(settings.model)

        # Get appropriate tools
        tools = get_tools_for_model(is_vision) if supports_tools else None

        # Get updated history (without the removed messages)
        history = conversation_store.get_messages_for_api(conv_id)

        # Build messages
        messages = ollama_service.build_messages(
            user_message=user_message,
            history=history[:-1] if history else [],  # Exclude the last user message as we'll add it fresh
            persona=settings.persona,
            images=user_images if is_vision else None,
            is_vision_model=is_vision,
            has_tools=supports_tools
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
            messages = truncate_messages_for_context(messages, settings.num_ctx)

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
                    result = await tool_executor.execute(tc)
                    yield {
                        "event": "tool_result",
                        "data": json.dumps({
                            "name": func.get("name"),
                            "result": result
                        })
                    }

            # Save the new assistant message
            if collected_content:
                assistant_msg = conversation_store.add_message(
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

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)})
            }

    return EventSourceResponse(event_generator())


# Legacy endpoints for backward compatibility
@router.get("/history")
async def get_chat_history(request: Request):
    """Get chat history for current session (legacy)"""
    conv_id = request.headers.get("X-Conversation-ID", "default")
    conv = conversation_store.get(conv_id)
    if not conv:
        return {"history": []}
    return {"history": conversation_store.get_messages_for_api(conv_id)}


@router.delete("/history")
async def clear_chat_history(request: Request):
    """Clear chat history for current session (legacy)"""
    conv_id = request.headers.get("X-Conversation-ID")
    if conv_id:
        conversation_store.clear_messages(conv_id)
    tool_executor.clear_images()
    return {"status": "cleared"}

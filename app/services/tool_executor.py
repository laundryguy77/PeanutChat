from typing import Dict, Any, Optional, List
import httpx
import json
import logging
import socket
import ipaddress
import time
from urllib.parse import urlparse
from app.services.conversation_store import conversation_store
from app.config import BRAVE_SEARCH_API_KEY, HF_TOKEN, VIDEO_GENERATION_SPACE
from app.services.knowledge_base import get_knowledge_base
from app.services.memory_service import get_memory_service
from app.services.mcp_client import get_mcp_manager
from app.services.user_profile_service import get_user_profile_service
from app.services.image_backends import UnifiedImageGenerator
from app.services.video_backends import VideoGenerator

logger = logging.getLogger(__name__)

# URL cache: {url: {"content": ..., "timestamp": ..., "status": ...}}
_url_cache: Dict[str, Dict[str, Any]] = {}
URL_CACHE_TTL = 300  # 5 minutes


class ToolExecutor:
    def __init__(self):
        self.image_registry: Dict[str, str] = {}  # Track shared images
        self.current_conversation_id: Optional[str] = None  # Current conversation for search
        self.current_user_id: Optional[int] = None  # Current user for knowledge base

    def set_current_conversation(self, conv_id: str):
        """Set the current conversation ID for context-aware tools"""
        self.current_conversation_id = conv_id

    def set_current_user(self, user_id: int):
        """Set the current user ID for user-scoped tools"""
        self.current_user_id = user_id

    def register_image(self, message_index: int, image_base64: str):
        """Register an image from a message for later tool use"""
        self.image_registry[f"image_{message_index}"] = image_base64
        self.image_registry["last_shared_image"] = image_base64

    def clear_images(self):
        """Clear the image registry"""
        self.image_registry.clear()

    def get_image(self, reference: str) -> Optional[str]:
        """Get image by reference"""
        return self.image_registry.get(reference)

    async def execute(
        self,
        tool_call: Dict[str, Any],
        user_id: Optional[int] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a tool call and return the result.

        Args:
            tool_call: The tool call to execute
            user_id: User ID for user-scoped tools (overrides current_user_id)
            conversation_id: Conversation ID for conversation-scoped tools (overrides current_conversation_id)
        """
        # Use explicit parameters if provided, otherwise fall back to instance state
        effective_user_id = user_id if user_id is not None else self.current_user_id
        effective_conv_id = conversation_id if conversation_id is not None else self.current_conversation_id

        function = tool_call.get("function", {})
        name = function.get("name")
        arguments = function.get("arguments", {})

        # Parse arguments if they're a string
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                return {"error": f"Invalid arguments format: {arguments}"}

        # Map tool names (some models like gpt-oss use different names)
        tool_name_map = {
            "browser.search": "web_search",
            "browser.open": "browse_website",
        }
        name = tool_name_map.get(name, name)

        if name == "web_search":
            return await self._execute_web_search(arguments)
        elif name == "browse_website":
            return await self._execute_browse_website(arguments)
        elif name == "search_conversations":
            return await self._execute_conversation_search(arguments, effective_conv_id, effective_user_id)
        elif name == "search_knowledge_base":
            return await self._execute_knowledge_search(arguments, effective_user_id)
        elif name == "add_memory":
            return await self._execute_add_memory(arguments, effective_user_id)
        elif name == "query_memory":
            return await self._execute_query_memory(arguments, effective_user_id)
        elif name == "set_conversation_title":
            return await self._execute_set_conversation_title(arguments, effective_conv_id)
        elif name == "generate_video":
            return await self._execute_generate_video(arguments, effective_user_id)
        elif name == "text_to_image":
            return await self._execute_text_to_image(arguments, effective_user_id)
        elif name == "image_to_image":
            return await self._execute_image_to_image(arguments)
        elif name == "inpaint_image":
            return await self._execute_inpaint_image(arguments)
        elif name == "upscale_image":
            return await self._execute_upscale_image(arguments)
        elif name == "text_to_video":
            return await self._execute_text_to_video(arguments)
        elif name == "image_to_video":
            return await self._execute_image_to_video(arguments)
        elif name == "user_profile_read":
            return await self._execute_user_profile_read(arguments, effective_user_id)
        elif name == "user_profile_update":
            return await self._execute_user_profile_update(arguments, effective_user_id)
        elif name == "user_profile_log_event":
            return await self._execute_user_profile_log_event(arguments, effective_user_id)
        elif name == "user_profile_enable_section":
            return await self._execute_user_profile_enable_section(arguments, effective_user_id)
        elif name == "user_profile_add_nested":
            return await self._execute_user_profile_add_nested(arguments, effective_user_id)
        elif name == "user_profile_query":
            return await self._execute_user_profile_query(arguments, effective_user_id)
        elif name == "user_profile_export":
            return await self._execute_user_profile_export(arguments, effective_user_id)
        elif name == "user_profile_reset":
            return await self._execute_user_profile_reset(arguments, effective_user_id)
        elif name.startswith("mcp_"):
            # Route to MCP manager for MCP tools
            return await self._execute_mcp_tool(name, arguments)

        # For unknown tools, return a helpful message instead of breaking
        logger.warning(f"Unknown tool requested: {name}")
        return {"error": f"Tool '{name}' is not available. Available tools: web_search, browse_website, search_conversations, search_knowledge_base, add_memory, query_memory"}

    async def _execute_web_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web search and fetch top results for comprehensive answers"""
        query = args.get("query", "")

        if not query:
            return {
                "error": "Search query is required.",
                "success": False
            }

        try:
            # Step 1: Search Brave for 6 URLs
            search_results = await self._brave_search(query, 6)

            if not search_results or search_results[0].get("title") == "No results found":
                return {
                    "success": False,
                    "query": query,
                    "error": "No search results found"
                }

            # Step 2: Fetch content from first 3 results
            fetched_content = []
            pages_fetched = 0

            for i, result in enumerate(search_results[:3]):
                url = result.get("url", "")
                if not url:
                    continue

                logger.info(f"Web search fetching result {i+1}/3: {url}")
                fetch_result = await self._fetch_url_content(url)

                if fetch_result.get("success"):
                    fetched_content.append({
                        "title": result.get("title", ""),
                        "url": url,
                        "content": fetch_result.get("content", "")[:2500]  # ~625 tokens per page
                    })
                    pages_fetched += 1
                else:
                    # Fall back to snippet if fetch fails
                    fetched_content.append({
                        "title": result.get("title", ""),
                        "url": url,
                        "content": f"[Snippet] {result.get('snippet', '')}"
                    })

            # Step 3: If we got less than 2 successful fetches, try next 3
            if pages_fetched < 2 and len(search_results) > 3:
                logger.info(f"Only {pages_fetched} pages fetched, trying next batch...")
                for i, result in enumerate(search_results[3:6]):
                    url = result.get("url", "")
                    if not url:
                        continue

                    logger.info(f"Web search fetching result {i+4}/6: {url}")
                    fetch_result = await self._fetch_url_content(url)

                    if fetch_result.get("success"):
                        fetched_content.append({
                            "title": result.get("title", ""),
                            "url": url,
                            "content": fetch_result.get("content", "")[:2500]  # ~625 tokens per page
                        })
                        pages_fetched += 1

            logger.info(f"Web search completed: {pages_fetched} pages fetched, {len(fetched_content)} total results")

            return {
                "success": True,
                "query": query,
                "results": fetched_content,
                "pages_fetched": pages_fetched,
                "num_results": len(fetched_content)
            }

        except Exception as e:
            return {
                "error": f"Search failed: {str(e)}",
                "success": False
            }

    def _is_private_ip(self, hostname: str) -> bool:
        """Check if a hostname resolves to a private/reserved IP address"""
        try:
            # Resolve hostname to IP
            ip_str = socket.gethostbyname(hostname)
            ip = ipaddress.ip_address(ip_str)

            # Check if IP is private, loopback, link-local, or reserved
            return (
                ip.is_private or
                ip.is_loopback or
                ip.is_link_local or
                ip.is_reserved or
                ip.is_multicast
            )
        except (socket.gaierror, ValueError):
            # If we can't resolve, be safe and block
            return True

    def _get_cached_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Get cached URL content if still valid"""
        global _url_cache
        if url in _url_cache:
            cached = _url_cache[url]
            if time.time() - cached["timestamp"] < URL_CACHE_TTL:
                logger.debug(f"Cache hit for: {url}")
                return cached
            else:
                # Expired, remove from cache
                del _url_cache[url]
        return None

    def _cache_url(self, url: str, result: Dict[str, Any]):
        """Cache URL content"""
        global _url_cache
        _url_cache[url] = {
            **result,
            "timestamp": time.time()
        }
        # Clean old entries if cache gets too large
        if len(_url_cache) > 100:
            oldest_url = min(_url_cache, key=lambda u: _url_cache[u]["timestamp"])
            del _url_cache[oldest_url]

    async def _execute_browse_website(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Browse a website and return its content"""
        # Support both 'url' (our format) and 'id' (gpt-oss browser.open format)
        url = args.get("url") or args.get("id", "")
        if isinstance(url, str):
            url = url.strip()

        # Validate URL format
        if not url:
            return {
                "success": False,
                "error": "URL is required."
            }

        if not url.startswith(('http://', 'https://')):
            return {
                "success": False,
                "error": "URL must start with http:// or https://"
            }

        # Parse URL to get hostname
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            if not hostname:
                return {
                    "success": False,
                    "error": "Invalid URL: could not extract hostname"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Invalid URL format: {str(e)}"
            }

        # Security check: block private/internal IPs
        if self._is_private_ip(hostname):
            return {
                "success": False,
                "error": "Access to private/internal network addresses is blocked for security reasons."
            }

        # Check cache first
        cached = self._get_cached_url(url)
        if cached:
            return {
                "success": True,
                "url": url,
                "status": cached.get("status", 200),
                "content": cached.get("content", ""),
                "length": cached.get("length", 0),
                "cached": True
            }

        logger.info(f"Browsing URL: {url}")

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, max_redirects=5) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                }
                response = await client.get(url, headers=headers)

                status = response.status_code

                if status >= 400:
                    return {
                        "success": False,
                        "url": url,
                        "status": status,
                        "error": f"HTTP error {status}: {response.reason_phrase}"
                    }

                content_type = response.headers.get("content-type", "")

                # Handle different content types
                if "application/json" in content_type:
                    try:
                        json_data = response.json()
                        content = json.dumps(json_data, indent=2)[:10000]
                    except:
                        content = response.text[:10000]
                elif "text/html" in content_type or "text/plain" in content_type or "text/xml" in content_type:
                    html = response.text
                    content = self._extract_text_from_html(html)
                    # Truncate to reasonable size
                    if len(content) > 10000:
                        content = content[:10000] + "\n\n[Content truncated...]"
                else:
                    return {
                        "success": False,
                        "url": url,
                        "status": status,
                        "error": f"Unsupported content type: {content_type}. This tool only supports HTML, plain text, and JSON."
                    }

                result = {
                    "success": True,
                    "url": str(response.url),  # Final URL after redirects
                    "status": status,
                    "content": content,
                    "length": len(content)
                }

                # Cache the result
                self._cache_url(url, result)

                logger.debug(f"Browse success: {len(content)} characters extracted")

                return result

        except httpx.TimeoutException:
            return {
                "success": False,
                "url": url,
                "error": "Request timed out after 10 seconds"
            }
        except httpx.TooManyRedirects:
            return {
                "success": False,
                "url": url,
                "error": "Too many redirects (maximum 5)"
            }
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": f"Failed to fetch URL: {str(e)}"
            }

    async def _brave_search(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """Perform Brave Search and return results"""
        logger.info(f"Brave search: {query}")
        results = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": BRAVE_SEARCH_API_KEY
            }
            params = {
                "q": query,
                "count": num_results
            }

            try:
                response = await client.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()

                    # Extract web results
                    web_results = data.get("web", {}).get("results", [])
                    for result in web_results[:num_results]:
                        results.append({
                            "title": result.get("title", ""),
                            "url": result.get("url", ""),
                            "snippet": result.get("description", ""),
                            "source": "Brave Search"
                        })
                    logger.info(f"Brave search found {len(results)} results")
                else:
                    logger.error(f"Brave API error: {response.status_code} - {response.text}")
            except Exception as e:
                logger.error(f"Brave Search API error: {e}")

        # If no results, return a message
        if not results:
            results.append({
                "title": "No results found",
                "url": "",
                "snippet": f"No search results found for: {query}",
                "source": "Brave Search"
            })

        return results[:num_results]

    async def _fetch_url_content(self, url: str) -> Dict[str, Any]:
        """Fetch and extract text content from a URL (internal helper)"""

        if not url:
            return {
                "error": "URL is required.",
                "success": False
            }

        # Validate URL scheme
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            return {
                "error": "URL must start with http:// or https://",
                "success": False
            }

        # Parse URL to get hostname
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            if not hostname:
                return {
                    "error": "Invalid URL: could not extract hostname",
                    "success": False
                }
        except Exception as e:
            return {
                "error": f"Invalid URL format: {str(e)}",
                "success": False
            }

        # Security check: block private/internal IPs
        if self._is_private_ip(hostname):
            return {
                "error": "Access to private/internal network addresses is blocked for security reasons.",
                "success": False
            }

        logger.debug(f"Fetching URL: {url}")

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, max_redirects=5) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                }
                response = await client.get(url, headers=headers)

                if response.status_code != 200:
                    logger.debug(f"Fetch URL HTTP {response.status_code} for {url}")
                    return {
                        "error": f"Failed to fetch URL: HTTP {response.status_code}",
                        "success": False
                    }

                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type and "text/plain" not in content_type:
                    return {
                        "error": f"Unsupported content type: {content_type}",
                        "success": False
                    }

                html = response.text

                # Extract text content from HTML
                text = self._extract_text_from_html(html)

                # Truncate if too long (keep first ~8000 chars for context limit)
                if len(text) > 8000:
                    text = text[:8000] + "\n\n[Content truncated...]"

                logger.debug(f"Extracted {len(text)} characters from URL")

                return {
                    "success": True,
                    "url": url,
                    "content": text,
                    "length": len(text)
                }

        except httpx.TimeoutException:
            logger.debug(f"Timeout fetching {url}")
            return {"error": "Request timed out", "success": False}
        except Exception as e:
            logger.debug(f"Error fetching {url}: {e}")
            return {"error": f"Failed to fetch URL: {str(e)}", "success": False}

    def _extract_text_from_html(self, html: str) -> str:
        """Extract readable text from HTML"""
        import re

        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<noscript[^>]*>.*?</noscript>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML comments
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)

        # Replace block elements with newlines
        html = re.sub(r'<(p|div|br|h[1-6]|li|tr)[^>]*>', '\n', html, flags=re.IGNORECASE)

        # Remove all remaining HTML tags
        html = re.sub(r'<[^>]+>', ' ', html)

        # Decode common HTML entities
        html = html.replace('&nbsp;', ' ')
        html = html.replace('&amp;', '&')
        html = html.replace('&lt;', '<')
        html = html.replace('&gt;', '>')
        html = html.replace('&quot;', '"')
        html = html.replace('&#39;', "'")
        html = html.replace('&#x27;', "'")

        # Clean up whitespace
        lines = []
        for line in html.split('\n'):
            line = ' '.join(line.split())  # Normalize whitespace
            if line:
                lines.append(line)

        return '\n'.join(lines)

    async def _execute_conversation_search(
        self, args: Dict[str, Any], conversation_id: Optional[str] = None, user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Search through previous conversations for context"""
        query = args.get("query", "")

        if not query:
            return {
                "error": "Search query is required.",
                "success": False
            }

        try:
            logger.info(f"Conversation search: {query}")
            results = conversation_store.search_conversations(
                query=query,
                exclude_conv_id=conversation_id,
                max_results=10,
                user_id=user_id
            )

            if not results:
                return {
                    "success": True,
                    "query": query,
                    "message": "No matching content found in previous conversations.",
                    "results": [],
                    "num_results": 0
                }

            logger.info(f"Conversation search found {len(results)} results")

            # Format results for the model
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "conversation": r["conversation_title"],
                    "speaker": r["message_role"],
                    "content": r["snippet"],
                    "relevance": round(r["score"] * 100)
                })

            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "num_results": len(formatted_results),
                "message": f"Found {len(formatted_results)} relevant excerpts from past conversations."
            }

        except Exception as e:
            logger.error(f"Conversation search error: {e}")
            return {
                "error": f"Search failed: {str(e)}",
                "success": False
            }

    async def _execute_knowledge_search(
        self, args: Dict[str, Any], user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Search the user's knowledge base for relevant documents"""
        query = args.get("query", "")

        if not query:
            return {
                "error": "Search query is required.",
                "success": False
            }

        if not user_id:
            return {
                "success": True,
                "query": query,
                "message": "Knowledge base search requires authentication.",
                "results": [],
                "num_results": 0
            }

        try:
            logger.info(f"Knowledge base search: {query}")
            kb = get_knowledge_base()
            results = await kb.search(
                user_id=user_id,
                query=query,
                top_k=5,
                threshold=0.3
            )

            if not results:
                return {
                    "success": True,
                    "query": query,
                    "message": "No matching content found in your knowledge base. You may need to upload relevant documents first.",
                    "results": [],
                    "num_results": 0
                }

            logger.info(f"Knowledge base search found {len(results)} results")

            # Format results for the model
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "filename": r["filename"],
                    "content": r["content"][:1000],  # Limit content length
                    "similarity": r["similarity"],
                    "chunk_index": r["chunk_index"]
                })

            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "num_results": len(formatted_results),
                "message": f"Found {len(formatted_results)} relevant excerpts from your uploaded documents."
            }

        except Exception as e:
            logger.error(f"Knowledge base search error: {e}")
            return {
                "error": f"Search failed: {str(e)}",
                "success": False
            }

    async def _execute_add_memory(
        self, args: Dict[str, Any], user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Add information to user's memory."""
        if not user_id:
            return {"success": False, "error": "User not authenticated"}

        memory_service = get_memory_service()
        result = await memory_service.add_memory(
            user_id=user_id,
            content=args.get("content", ""),
            category=args.get("category", "general"),
            importance=args.get("importance", 5),
            source="inferred"
        )
        return result

    async def _execute_query_memory(
        self, args: Dict[str, Any], user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Query user's memory."""
        if not user_id:
            return {"success": False, "error": "User not authenticated"}

        memory_service = get_memory_service()
        results = await memory_service.query_memories(
            user_id=user_id,
            query=args.get("query", ""),
            top_k=5
        )
        return {
            "success": True,
            "query": args.get("query", ""),
            "results": results,
            "count": len(results)
        }

    async def _execute_set_conversation_title(
        self, args: Dict[str, Any], conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Set the title of the current conversation."""
        title = args.get("title", "").strip()

        if not title:
            return {"success": False, "error": "Title is required"}

        if not conversation_id:
            return {"success": False, "error": "No active conversation"}

        # Limit title length
        if len(title) > 100:
            title = title[:100]

        try:
            success = await conversation_store.rename(conversation_id, title)
            if success:
                logger.info(f"Conversation title set to: {title}")
                return {
                    "success": True,
                    "title": title,
                    "message": f"Conversation title updated to: {title}"
                }
            else:
                return {"success": False, "error": "Failed to update conversation title"}
        except Exception as e:
            logger.error(f"Error setting conversation title: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_generate_video(
        self, args: Dict[str, Any], user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a video using Hugging Face Spaces."""
        import asyncio

        prompt = args.get("prompt", "").strip()
        duration = args.get("duration", 4)

        if not prompt:
            return {"success": False, "error": "Prompt is required"}

        # Inject avatar style from profile for consistent character
        if user_id:
            try:
                profile_service = get_user_profile_service()
                profile_data = await profile_service.get_profile(user_id)
                if profile_data:
                    profile = profile_data.get("profile", {})
                    persona = profile.get("persona_preferences", {})
                    avatar_style = persona.get("avatar_style_tags")
                    if avatar_style:
                        prompt = f"{avatar_style}. {prompt}"
                        logger.debug(f"Injected avatar style into video prompt: {avatar_style}")
            except Exception as e:
                logger.warning(f"Failed to get avatar style for video generation: {e}")

        # Validate duration
        duration = max(2, min(10, duration))

        if not VIDEO_GENERATION_SPACE:
            return {"success": False, "error": "Video generation is not configured. Set VIDEO_GENERATION_SPACE in environment."}

        logger.info(f"Generating video with prompt: {prompt[:100]}...")

        try:
            # Import gradio_client dynamically to avoid startup dependency
            from gradio_client import Client

            # Run the synchronous gradio client in a thread pool
            loop = asyncio.get_event_loop()

            def generate_sync():
                try:
                    # Create client with optional auth token
                    if HF_TOKEN:
                        client = Client(VIDEO_GENERATION_SPACE, hf_token=HF_TOKEN)
                    else:
                        client = Client(VIDEO_GENERATION_SPACE)

                    # Call the predict method with the prompt
                    # Note: API may vary by space, this handles common patterns
                    result = client.predict(
                        prompt,
                        api_name="/predict"
                    )
                    return result
                except Exception as e:
                    # Try alternative API endpoint
                    try:
                        if HF_TOKEN:
                            client = Client(VIDEO_GENERATION_SPACE, hf_token=HF_TOKEN)
                        else:
                            client = Client(VIDEO_GENERATION_SPACE)
                        result = client.predict(
                            prompt,
                            api_name="/generate"
                        )
                        return result
                    except:
                        raise e

            # Execute with 120 second timeout for video generation
            result = await asyncio.wait_for(
                loop.run_in_executor(None, generate_sync),
                timeout=120.0
            )

            # Handle various result formats
            video_url = None
            if isinstance(result, str):
                video_url = result
            elif isinstance(result, dict):
                video_url = result.get("video") or result.get("url") or result.get("output")
            elif isinstance(result, (list, tuple)) and len(result) > 0:
                video_url = result[0] if isinstance(result[0], str) else result[0].get("url", result[0])

            if video_url:
                logger.info(f"Video generated successfully: {video_url[:100]}...")
                return {
                    "success": True,
                    "video_url": video_url,
                    "prompt": prompt,
                    "duration": duration,
                    "message": f"Video generated successfully. URL: {video_url}"
                }
            else:
                return {
                    "success": False,
                    "error": "Video generation completed but no URL was returned",
                    "raw_result": str(result)[:500]
                }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Video generation timed out after 120 seconds. The service may be busy, please try again later."
            }
        except ImportError:
            return {
                "success": False,
                "error": "gradio-client is not installed. Run: pip install gradio-client"
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Video generation error: {error_msg}")

            # Provide helpful error messages
            if "429" in error_msg or "rate" in error_msg.lower():
                return {"success": False, "error": "Rate limit exceeded. Please wait and try again later."}
            elif "401" in error_msg or "403" in error_msg:
                return {"success": False, "error": "Authentication failed. Check HF_TOKEN in environment."}
            elif "queue" in error_msg.lower():
                return {"success": False, "error": "The video generation service is currently busy. Please try again later."}
            else:
                return {"success": False, "error": f"Video generation failed: {error_msg[:200]}"}

    async def _get_avatar_style_prefix(self, user_id: Optional[int] = None) -> str:
        """Get avatar style from user profile for consistent character generation."""
        if not user_id:
            return ""
        try:
            profile_service = get_user_profile_service()
            profile_data = await profile_service.get_profile(user_id)
            if profile_data:
                profile = profile_data.get("profile", {})
                persona = profile.get("persona_preferences", {})
                avatar_style = persona.get("avatar_style_tags")
                if avatar_style:
                    return avatar_style
        except Exception as e:
            logger.warning(f"Failed to get avatar style: {e}")
        return ""

    async def _execute_text_to_image(
        self, args: Dict[str, Any], user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate an image from text using HuggingFace Spaces (FLUX.1/SD)."""
        import tempfile

        prompt = args.get("prompt", "").strip()
        if not prompt:
            return {"success": False, "error": "Prompt is required"}

        # Inject avatar style from profile for consistent character
        avatar_style = await self._get_avatar_style_prefix(user_id)
        if avatar_style:
            prompt = f"{avatar_style}. {prompt}"
            logger.debug(f"Injected avatar style into image prompt: {avatar_style}")

        logger.info(f"Text-to-image generation with prompt: {prompt[:100]}...")

        try:
            async with UnifiedImageGenerator(headless=True) as gen:
                result = await gen.text_to_image(
                    prompt=prompt,
                    negative_prompt=args.get("negative_prompt", ""),
                    width=args.get("width", 1024),
                    height=args.get("height", 1024),
                    return_base64=True
                )

            if result.get("success"):
                return {
                    "success": True,
                    "base64": result["base64"],
                    "mime_type": result.get("mime_type", "image/png"),
                    "message": "Image generated successfully"
                }
            return result
        except Exception as e:
            logger.error(f"Text-to-image generation error: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_image_to_image(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Transform an image based on a text prompt."""
        import tempfile
        import base64
        import os

        image_base64 = args.get("image_base64", "")
        prompt = args.get("prompt", "").strip()

        if not image_base64:
            return {"success": False, "error": "image_base64 is required"}
        if not prompt:
            return {"success": False, "error": "prompt is required"}

        # Inject avatar style from profile
        avatar_style = await self._get_avatar_style_prefix()
        if avatar_style:
            prompt = f"{avatar_style}. {prompt}"

        logger.info(f"Image-to-image transformation with prompt: {prompt[:100]}...")

        try:
            # Save base64 image to temp file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                f.write(base64.b64decode(image_base64))
                temp_image_path = f.name

            try:
                async with UnifiedImageGenerator(headless=True) as gen:
                    result = await gen.image_to_image(
                        image_path=temp_image_path,
                        prompt=prompt,
                        negative_prompt=args.get("negative_prompt", ""),
                        strength=args.get("strength", 0.7),
                        return_base64=True
                    )
            finally:
                os.unlink(temp_image_path)

            if result.get("success"):
                return {
                    "success": True,
                    "base64": result["base64"],
                    "mime_type": result.get("mime_type", "image/png"),
                    "message": "Image transformed successfully"
                }
            return result
        except Exception as e:
            logger.error(f"Image-to-image error: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_inpaint_image(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Inpaint regions of an image based on a mask."""
        import tempfile
        import base64
        import os

        image_base64 = args.get("image_base64", "")
        mask_base64 = args.get("mask_base64", "")
        prompt = args.get("prompt", "").strip()

        if not image_base64:
            return {"success": False, "error": "image_base64 is required"}
        if not mask_base64:
            return {"success": False, "error": "mask_base64 is required"}
        if not prompt:
            return {"success": False, "error": "prompt is required"}

        # Inject avatar style from profile
        avatar_style = await self._get_avatar_style_prefix()
        if avatar_style:
            prompt = f"{avatar_style}. {prompt}"

        logger.info(f"Inpainting with prompt: {prompt[:100]}...")

        try:
            # Save base64 images to temp files
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                f.write(base64.b64decode(image_base64))
                temp_image_path = f.name

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                f.write(base64.b64decode(mask_base64))
                temp_mask_path = f.name

            try:
                async with UnifiedImageGenerator(headless=True) as gen:
                    result = await gen.inpaint(
                        image_path=temp_image_path,
                        mask_path=temp_mask_path,
                        prompt=prompt,
                        negative_prompt=args.get("negative_prompt", ""),
                        return_base64=True
                    )
            finally:
                os.unlink(temp_image_path)
                os.unlink(temp_mask_path)

            if result.get("success"):
                return {
                    "success": True,
                    "base64": result["base64"],
                    "mime_type": result.get("mime_type", "image/png"),
                    "message": "Image inpainted successfully"
                }
            return result
        except Exception as e:
            logger.error(f"Inpaint error: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_upscale_image(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Upscale an image using AI enhancement."""
        import tempfile
        import base64
        import os

        image_base64 = args.get("image_base64", "")
        if not image_base64:
            return {"success": False, "error": "image_base64 is required"}

        scale = args.get("scale", 2.0)
        logger.info(f"Upscaling image with scale factor: {scale}")

        try:
            # Save base64 image to temp file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                f.write(base64.b64decode(image_base64))
                temp_image_path = f.name

            try:
                async with UnifiedImageGenerator(headless=True) as gen:
                    result = await gen.upscale(
                        image_path=temp_image_path,
                        scale=scale,
                        return_base64=True
                    )
            finally:
                os.unlink(temp_image_path)

            if result.get("success"):
                return {
                    "success": True,
                    "base64": result["base64"],
                    "mime_type": result.get("mime_type", "image/png"),
                    "message": f"Image upscaled successfully ({scale}x)"
                }
            return result
        except Exception as e:
            logger.error(f"Upscale error: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_text_to_video(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video from text using HuggingFace Spaces via Playwright."""
        prompt = args.get("prompt", "").strip()
        if not prompt:
            return {"success": False, "error": "Prompt is required"}

        negative_prompt = args.get("negative_prompt", "")
        duration = args.get("duration", 3.0)

        logger.info(f"Text-to-video generation: {prompt[:100]}...")

        try:
            async with VideoGenerator(headless=True, timeout=300000) as gen:
                result = await gen.text_to_video(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    duration=duration,
                    return_base64=True
                )

            if result.get("success"):
                return {
                    "success": True,
                    "base64": result.get("base64"),
                    "mime_type": "video/mp4",
                    "size_bytes": result.get("size_bytes"),
                    "message": "Video generated successfully"
                }
            return result
        except Exception as e:
            logger.error(f"Text-to-video error: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_image_to_video(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Animate an image into video using HuggingFace Spaces via Playwright."""
        import os
        import tempfile
        import base64

        image_base64 = args.get("image_base64", "").strip()
        if not image_base64:
            return {"success": False, "error": "image_base64 is required"}

        prompt = args.get("prompt", "")
        negative_prompt = args.get("negative_prompt", "")

        logger.info("Image-to-video generation from base64 input")

        try:
            # Save base64 image to temp file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                f.write(base64.b64decode(image_base64))
                temp_image_path = f.name

            try:
                async with VideoGenerator(headless=True, timeout=300000) as gen:
                    result = await gen.image_to_video(
                        image_path=temp_image_path,
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        return_base64=True
                    )
            finally:
                os.unlink(temp_image_path)

            if result.get("success"):
                return {
                    "success": True,
                    "base64": result.get("base64"),
                    "mime_type": "video/mp4",
                    "size_bytes": result.get("size_bytes"),
                    "message": "Video generated successfully from image"
                }
            return result
        except Exception as e:
            logger.error(f"Image-to-video error: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_mcp_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool via the MCP manager."""
        logger.info(f"Executing MCP tool: {tool_name}")
        mcp_manager = get_mcp_manager()
        result = await mcp_manager.call_tool(tool_name, args)
        logger.info(f"MCP tool result: {result}")
        return result

    # User Profile Tool Executors

    async def _execute_user_profile_read(
        self, args: Dict[str, Any], user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Read user profile sections."""
        if not user_id:
            return {"success": False, "error": "User not authenticated"}

        profile_service = get_user_profile_service()
        sections = args.get("sections", ["all"])
        include_disabled = args.get("include_disabled", False)

        result = await profile_service.read_sections(
            user_id=user_id,
            sections=sections,
            include_disabled=include_disabled
        )
        return {"success": True, "profile": result}

    async def _execute_user_profile_update(
        self, args: Dict[str, Any], user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update user profile fields."""
        if not user_id:
            return {"success": False, "error": "User not authenticated"}

        profile_service = get_user_profile_service()
        updates = args.get("updates", [])
        reason = args.get("reason", "AI-initiated update")

        result = await profile_service.update_profile(
            user_id=user_id,
            updates=updates,
            reason=reason
        )
        return {"success": True, "updated": True}

    async def _execute_user_profile_log_event(
        self, args: Dict[str, Any], user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Log an interaction event."""
        if not user_id:
            return {"success": False, "error": "User not authenticated"}

        profile_service = get_user_profile_service()
        result = await profile_service.log_event(
            user_id=user_id,
            event_type=args.get("event_type"),
            context=args.get("context"),
            severity=args.get("severity", "moderate")
        )
        return result

    async def _execute_user_profile_enable_section(
        self, args: Dict[str, Any], user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Enable or disable a sensitive section."""
        if not user_id:
            return {"success": False, "error": "User not authenticated"}

        profile_service = get_user_profile_service()
        result = await profile_service.enable_section(
            user_id=user_id,
            section=args.get("section"),
            user_confirmed=args.get("user_confirmed", False),
            enabled=args.get("enabled", True)
        )
        return result

    async def _execute_user_profile_add_nested(
        self, args: Dict[str, Any], user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Add to a nested section."""
        if not user_id:
            return {"success": False, "error": "User not authenticated"}

        profile_service = get_user_profile_service()
        result = await profile_service.add_nested(
            user_id=user_id,
            section=args.get("section"),
            domain=args.get("domain"),
            key=args.get("key"),
            value=args.get("value")
        )
        return result

    async def _execute_user_profile_query(
        self, args: Dict[str, Any], user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Query the user profile."""
        if not user_id:
            return {"success": False, "error": "User not authenticated"}

        profile_service = get_user_profile_service()
        result = await profile_service.query_profile(
            user_id=user_id,
            query=args.get("query", "")
        )
        return result

    async def _execute_user_profile_export(
        self, args: Dict[str, Any], user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Export user profile."""
        if not user_id:
            return {"success": False, "error": "User not authenticated"}

        profile_service = get_user_profile_service()
        result = await profile_service.export_profile(
            user_id=user_id,
            format=args.get("format", "json"),
            tier=args.get("tier", "exportable"),
            user_confirmed=args.get("user_confirmed", False)
        )
        return {"success": True, "export": result}

    async def _execute_user_profile_reset(
        self, args: Dict[str, Any], user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Reset user profile sections."""
        if not user_id:
            return {"success": False, "error": "User not authenticated"}

        if not args.get("user_confirmed"):
            return {"success": False, "error": "User confirmation required for reset"}

        profile_service = get_user_profile_service()
        result = await profile_service.reset_profile(
            user_id=user_id,
            sections=args.get("sections", []),
            preserve_identity=args.get("preserve_identity", True)
        )
        return {"success": True, "reset": True}


# Global executor instance
tool_executor = ToolExecutor()

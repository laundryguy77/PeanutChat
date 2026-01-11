from typing import Dict, Any, Optional, List
import httpx
import json
import socket
import ipaddress
import time
from urllib.parse import urlparse
from app.services.image_generator import image_generator
from app.services.conversation_store import conversation_store
from app.config import BRAVE_SEARCH_API_KEY

# URL cache: {url: {"content": ..., "timestamp": ..., "status": ...}}
_url_cache: Dict[str, Dict[str, Any]] = {}
URL_CACHE_TTL = 300  # 5 minutes


class ToolExecutor:
    def __init__(self):
        self.image_registry: Dict[str, str] = {}  # Track shared images
        self.current_conversation_id: Optional[str] = None  # Current conversation for search

    def set_current_conversation(self, conv_id: str):
        """Set the current conversation ID for context-aware tools"""
        self.current_conversation_id = conv_id

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

    async def execute(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call and return the result"""
        function = tool_call.get("function", {})
        name = function.get("name")
        arguments = function.get("arguments", {})

        # Parse arguments if they're a string
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                return {"error": f"Invalid arguments format: {arguments}"}

        if name == "web_search":
            return await self._execute_web_search(arguments)
        elif name == "browse_website":
            return await self._execute_browse_website(arguments)
        elif name == "generate_image":
            return await self._execute_generate_image(arguments)
        elif name == "search_conversations":
            return await self._execute_conversation_search(arguments)

        return {"error": f"Unknown tool: {name}"}

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

                print(f"[WEB SEARCH] Fetching result {i+1}/3: {url}")
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
                print(f"[WEB SEARCH] Only {pages_fetched} pages fetched, trying next batch...")
                for i, result in enumerate(search_results[3:6]):
                    url = result.get("url", "")
                    if not url:
                        continue

                    print(f"[WEB SEARCH] Fetching result {i+4}/6: {url}")
                    fetch_result = await self._fetch_url_content(url)

                    if fetch_result.get("success"):
                        fetched_content.append({
                            "title": result.get("title", ""),
                            "url": url,
                            "content": fetch_result.get("content", "")[:2500]  # ~625 tokens per page
                        })
                        pages_fetched += 1

            print(f"[WEB SEARCH] Completed with {pages_fetched} pages fetched, {len(fetched_content)} total results")

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
                print(f"[BROWSE] Cache hit for: {url}")
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
        url = args.get("url", "").strip()

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

        print(f"[BROWSE] Fetching: {url}")

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

                print(f"[BROWSE] Success: {len(content)} characters extracted")

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
        print(f"[BRAVE SEARCH] Executing search for: {query}")
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
                    print(f"[BRAVE SEARCH] Found {len(results)} results")
                else:
                    print(f"[BRAVE SEARCH] API error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Brave Search API error: {e}")

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

        print(f"[FETCH URL] Fetching: {url}")

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
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
                    print(f"[FETCH URL] HTTP {response.status_code} for {url}")
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

                print(f"[FETCH URL] Extracted {len(text)} characters")

                return {
                    "success": True,
                    "url": url,
                    "content": text,
                    "length": len(text)
                }

        except httpx.TimeoutException:
            print(f"[FETCH URL] Timeout for {url}")
            return {"error": "Request timed out", "success": False}
        except Exception as e:
            print(f"[FETCH URL] Error for {url}: {e}")
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

    async def _execute_conversation_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search through previous conversations for context"""
        query = args.get("query", "")

        if not query:
            return {
                "error": "Search query is required.",
                "success": False
            }

        try:
            print(f"[CONV SEARCH] Searching for: {query}")
            results = conversation_store.search_conversations(
                query=query,
                exclude_conv_id=self.current_conversation_id,
                max_results=10
            )

            if not results:
                return {
                    "success": True,
                    "query": query,
                    "message": "No matching content found in previous conversations.",
                    "results": [],
                    "num_results": 0
                }

            print(f"[CONV SEARCH] Found {len(results)} results")

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
            print(f"[CONV SEARCH] Error: {e}")
            return {
                "error": f"Search failed: {str(e)}",
                "success": False
            }

    async def _execute_generate_image(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute image generation tool"""
        prompt = args.get("prompt", "")
        if not prompt:
            return {
                "error": "A prompt describing the image is required.",
                "success": False
            }

        # Style modifiers
        style_modifiers = {
            "photorealistic": ", photorealistic, highly detailed, 8k, professional photography",
            "artistic": ", artistic, creative, expressive brushwork, fine art",
            "anime": ", anime style, manga art, vibrant colors, detailed",
            "digital_art": ", digital art, concept art, detailed illustration",
            "oil_painting": ", oil painting, classical art style, rich colors, textured",
            "watercolor": ", watercolor painting, soft edges, flowing colors",
            "sketch": ", pencil sketch, hand-drawn, detailed linework"
        }

        # Apply style modifier if specified
        style = args.get("style")
        if style and style in style_modifiers:
            prompt += style_modifiers[style]

        # Get dimensions (ensure divisible by 8)
        width = args.get("width", 1024)
        height = args.get("height", 1024)
        width = max(512, min(1536, (width // 8) * 8))
        height = max(512, min(1536, (height // 8) * 8))

        negative_prompt = args.get("negative_prompt")

        try:
            result = await image_generator.generate(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height
            )

            if result.get("success"):
                return {
                    "success": True,
                    "image_url": result["url"],
                    "image_id": result["image_id"],
                    "message": f"Image generated successfully! You can view it at {result['url']}",
                    "prompt": prompt,
                    "seed": result.get("seed")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Image generation failed")
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Image generation error: {str(e)}"
            }


# Global executor instance
tool_executor = ToolExecutor()

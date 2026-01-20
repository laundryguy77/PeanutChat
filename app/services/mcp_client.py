"""MCP (Model Context Protocol) client for connecting to external tool servers."""

import asyncio
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class MCPServer:
    """Configuration for an MCP server."""
    id: str
    user_id: int
    name: str
    transport: str  # 'stdio' or 'sse'
    command: Optional[str] = None
    args: List[str] = field(default_factory=list)
    url: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    created_at: Optional[str] = None


class MCPClient:
    """Client for communicating with a single MCP server via JSON-RPC over stdio."""

    def __init__(self, server: MCPServer):
        self.server = server
        self.process: Optional[asyncio.subprocess.Process] = None
        self._request_id = 0
        self._pending_requests: Dict[int, asyncio.Future] = {}
        self._reader_task: Optional[asyncio.Task] = None
        self._tools: List[Dict[str, Any]] = []
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected and self.process is not None

    async def connect(self) -> bool:
        """Connect to the MCP server by spawning the process."""
        if self.server.transport != 'stdio':
            logger.error(f"Unsupported transport: {self.server.transport}")
            return False

        if not self.server.command:
            logger.error("No command specified for stdio transport")
            return False

        try:
            # Build environment with any custom env vars
            env = os.environ.copy()
            env.update(self.server.env)

            # Spawn the process
            cmd = self.server.command
            args = self.server.args if self.server.args else []

            logger.info(f"Starting MCP server: {cmd} {' '.join(args)}")

            self.process = await asyncio.create_subprocess_exec(
                cmd,
                *args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )

            # Start reading responses
            self._reader_task = asyncio.create_task(self._read_responses())

            # Initialize the connection
            init_result = await self._send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True}
                },
                "clientInfo": {
                    "name": "PeanutChat",
                    "version": "1.0.0"
                }
            })

            if init_result is None:
                logger.error("Failed to initialize MCP connection")
                await self.disconnect()
                return False

            # Send initialized notification
            await self._send_notification("notifications/initialized", {})

            # Get available tools
            tools_result = await self._send_request("tools/list", {})
            if tools_result and "tools" in tools_result:
                self._tools = tools_result["tools"]
                logger.info(f"MCP server '{self.server.name}' provides {len(self._tools)} tools")

            self._connected = True
            return True

        except FileNotFoundError:
            logger.error(f"MCP server command not found: {self.server.command}")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            await self.disconnect()
            return False

    async def disconnect(self):
        """Disconnect from the MCP server."""
        self._connected = False

        if self._reader_task:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
            self._reader_task = None

        if self.process:
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.process.kill()
            except Exception as e:
                logger.warning(f"Error terminating MCP process: {e}")
            self.process = None

        self._tools = []
        self._pending_requests.clear()

    async def _read_responses(self):
        """Read JSON-RPC responses from stdout."""
        if not self.process or not self.process.stdout:
            return

        buffer = ""
        while True:
            try:
                data = await self.process.stdout.read(4096)
                if not data:
                    logger.warning("MCP server closed stdout")
                    break

                buffer += data.decode('utf-8')

                # Process complete lines
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        message = json.loads(line)
                        await self._handle_message(message)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON from MCP server: {e}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error reading MCP responses: {e}")
                break

    async def _handle_message(self, message: Dict[str, Any]):
        """Handle incoming JSON-RPC message."""
        if "id" in message:
            # This is a response
            req_id = message["id"]
            if req_id in self._pending_requests:
                future = self._pending_requests.pop(req_id)
                if "error" in message:
                    future.set_exception(Exception(message["error"].get("message", "Unknown error")))
                else:
                    future.set_result(message.get("result"))

    async def _send_request(self, method: str, params: Dict[str, Any]) -> Optional[Any]:
        """Send a JSON-RPC request and wait for response."""
        if not self.process or not self.process.stdin:
            return None

        self._request_id += 1
        req_id = self._request_id

        request = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params
        }

        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending_requests[req_id] = future

        try:
            data = json.dumps(request) + "\n"
            self.process.stdin.write(data.encode('utf-8'))
            await self.process.stdin.drain()

            # Wait for response with timeout
            result = await asyncio.wait_for(future, timeout=30.0)
            return result
        except asyncio.TimeoutError:
            self._pending_requests.pop(req_id, None)
            logger.error(f"Request {method} timed out")
            return None
        except Exception as e:
            self._pending_requests.pop(req_id, None)
            logger.error(f"Request {method} failed: {e}")
            return None

    async def _send_notification(self, method: str, params: Dict[str, Any]):
        """Send a JSON-RPC notification (no response expected)."""
        if not self.process or not self.process.stdin:
            return

        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }

        try:
            data = json.dumps(notification) + "\n"
            self.process.stdin.write(data.encode('utf-8'))
            await self.process.stdin.drain()
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get the list of tools from this server."""
        return self._tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server."""
        if not self.connected:
            return {"error": "MCP server not connected"}

        try:
            result = await self._send_request("tools/call", {
                "name": tool_name,
                "arguments": arguments
            })

            if result is None:
                return {"error": "Tool call failed or timed out"}

            # Extract content from MCP response
            if "content" in result:
                contents = result["content"]
                # Combine text content
                text_parts = []
                for item in contents:
                    if item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                return {"success": True, "result": "\n".join(text_parts)}

            return {"success": True, "result": result}

        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return {"error": str(e)}


class MCPManager:
    """Manager for multiple MCP server connections."""

    def __init__(self):
        # Keyed by server_id
        self._clients: Dict[str, MCPClient] = {}

    def get_client(self, server_id: str) -> Optional[MCPClient]:
        """Get a client by server ID."""
        return self._clients.get(server_id)

    async def connect_server(self, server: MCPServer) -> bool:
        """Connect to an MCP server."""
        # Disconnect existing connection if any
        if server.id in self._clients:
            await self.disconnect_server(server.id)

        client = MCPClient(server)
        success = await client.connect()

        if success:
            self._clients[server.id] = client
            logger.info(f"Connected to MCP server: {server.name}")
        else:
            logger.error(f"Failed to connect to MCP server: {server.name}")

        return success

    async def disconnect_server(self, server_id: str) -> bool:
        """Disconnect from an MCP server."""
        client = self._clients.pop(server_id, None)
        if client:
            await client.disconnect()
            logger.info(f"Disconnected from MCP server: {server_id}")
            return True
        return False

    def is_connected(self, server_id: str) -> bool:
        """Check if a server is connected."""
        client = self._clients.get(server_id)
        return client.connected if client else False

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all tools from all connected servers."""
        tools = []
        for server_id, client in self._clients.items():
            if client.connected:
                for tool in client.get_tools():
                    # Prefix tool name with server ID for uniqueness
                    prefixed_tool = {
                        "name": f"mcp_{server_id}_{tool['name']}",
                        "original_name": tool['name'],
                        "server_id": server_id,
                        "description": tool.get("description", ""),
                        "inputSchema": tool.get("inputSchema", {})
                    }
                    tools.append(prefixed_tool)
        return tools

    def get_tools_as_openai_format(self) -> List[Dict[str, Any]]:
        """Get all MCP tools in OpenAI function calling format."""
        openai_tools = []
        for tool in self.get_all_tools():
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {"type": "object", "properties": {}})
                }
            }
            openai_tools.append(openai_tool)
        return openai_tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool by its prefixed name."""
        # Parse the prefixed name: mcp_{server_id}_{original_name}
        if not tool_name.startswith("mcp_"):
            return {"error": f"Not an MCP tool: {tool_name}"}

        parts = tool_name[4:].split("_", 1)
        if len(parts) != 2:
            return {"error": f"Invalid MCP tool name format: {tool_name}"}

        server_id, original_name = parts

        client = self._clients.get(server_id)
        if not client:
            return {"error": f"MCP server not connected: {server_id}"}

        return await client.call_tool(original_name, arguments)

    async def disconnect_all(self):
        """Disconnect from all servers."""
        for server_id in list(self._clients.keys()):
            await self.disconnect_server(server_id)


# Global MCP manager instance
_mcp_manager: Optional[MCPManager] = None


def get_mcp_manager() -> MCPManager:
    """Get the global MCP manager instance."""
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = MCPManager()
    return _mcp_manager

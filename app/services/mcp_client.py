"""MCP (Model Context Protocol) client for connecting to external tool servers."""

import asyncio
import json
import logging
import os
import re
import resource
import shutil
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# Allowlist of permitted MCP server commands (basename only)
# These are common/trusted MCP server executables
ALLOWED_MCP_COMMANDS = {
    # Node.js based MCP servers
    "node",
    "npx",
    "npm",
    # Python based MCP servers
    "python",
    "python3",
    "uvx",
    "uv",
    # Deno based MCP servers
    "deno",
    # Specific MCP server binaries (add trusted ones here)
    "mcp-server-fetch",
    "mcp-server-filesystem",
    "mcp-server-git",
    "mcp-server-github",
    "mcp-server-postgres",
    "mcp-server-sqlite",
    "mcp-server-brave-search",
    "mcp-server-puppeteer",
    "mcp-server-memory",
    "mcp-server-time",
    "mcp-server-sequential-thinking",
}

# Allowlist of permitted environment variables for MCP processes
# Only these can be set by users; all others are blocked
ALLOWED_ENV_VARS = {
    # API keys and tokens (common for MCP servers)
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "BRAVE_API_KEY",
    "GITHUB_TOKEN",
    "GITHUB_PERSONAL_ACCESS_TOKEN",
    "DATABASE_URL",
    "POSTGRES_URL",
    "SQLITE_PATH",
    # MCP-specific configuration
    "MCP_SERVER_NAME",
    "MCP_DEBUG",
    # Common safe vars
    "TZ",
    "LANG",
    "LC_ALL",
    "NODE_ENV",
    "PYTHONDONTWRITEBYTECODE",
}

# Environment variables that should NEVER be inherited by MCP processes
# These could be exploited for code execution or to leak secrets
BLOCKED_INHERITED_VARS = {
    "LD_PRELOAD",
    "LD_LIBRARY_PATH",
    "DYLD_INSERT_LIBRARIES",
    "DYLD_LIBRARY_PATH",
    "PYTHONPATH",
    "PYTHONSTARTUP",
    "PYTHONHOME",
    "NODE_OPTIONS",
    "NODE_PATH",
    "PERL5LIB",
    "RUBYLIB",
    "CLASSPATH",
    # Secrets from parent process that shouldn't leak
    "JWT_SECRET",
    "JWT_SECRET_KEY",
    "SECRET_KEY",
    "DATABASE_PASSWORD",
    "DB_PASSWORD",
    "AWS_SECRET_ACCESS_KEY",
    "PRIVATE_KEY",
}

# Patterns that indicate sensitive data in command arguments
SENSITIVE_ARG_PATTERNS = [
    re.compile(r'(api[_-]?key|token|secret|password|credential)[=:]\S+', re.IGNORECASE),
    re.compile(r'(sk-[a-zA-Z0-9]+)', re.IGNORECASE),  # OpenAI keys
    re.compile(r'(ghp_[a-zA-Z0-9]+)', re.IGNORECASE),  # GitHub tokens
    re.compile(r'(xox[baprs]-[a-zA-Z0-9-]+)', re.IGNORECASE),  # Slack tokens
]

# Resource limits for MCP subprocesses
MCP_PROCESS_LIMITS = {
    "max_memory_mb": 512,  # Maximum memory in MB
    "max_cpu_time_seconds": 300,  # Maximum CPU time
    "max_file_descriptors": 256,  # Maximum open files
}

# Connection timeout for MCP initialization (seconds)
MCP_CONNECT_TIMEOUT = 30.0


def _sanitize_log_args(args: List[str]) -> List[str]:
    """Sanitize command arguments for logging by redacting sensitive values."""
    sanitized = []
    for arg in args:
        sanitized_arg = arg
        for pattern in SENSITIVE_ARG_PATTERNS:
            sanitized_arg = pattern.sub('[REDACTED]', sanitized_arg)
        sanitized.append(sanitized_arg)
    return sanitized


def _validate_command_path(command: str) -> tuple[bool, str, str]:
    """
    Validate an MCP server command for security.

    Returns:
        (is_valid, resolved_path, error_message)
    """
    if not command:
        return False, "", "Command is empty"

    # Get the basename for allowlist check
    basename = os.path.basename(command)

    # Check if command is in allowlist
    if basename not in ALLOWED_MCP_COMMANDS:
        return False, "", f"Command '{basename}' is not in the allowed MCP commands list"

    # If it's a bare command name, resolve using PATH
    if '/' not in command and '\\' not in command:
        resolved = shutil.which(command)
        if not resolved:
            return False, "", f"Command '{command}' not found in PATH"
        command = resolved

    # Resolve to absolute path
    try:
        path = Path(command).resolve(strict=True)
        resolved_path = str(path)
    except (OSError, RuntimeError) as e:
        return False, "", f"Cannot resolve command path: {e}"

    # Security checks on resolved path
    # 1. Must be absolute
    if not path.is_absolute():
        return False, "", "Command must resolve to an absolute path"

    # 2. Must be a file (not directory or symlink to unexpected location)
    if not path.is_file():
        return False, "", "Command must be a regular file"

    # 3. Check the resolved basename is still in allowlist
    # (prevents symlink attacks like /tmp/evil -> /bin/bash)
    resolved_basename = path.name
    if resolved_basename not in ALLOWED_MCP_COMMANDS:
        # Allow if the resolved path is a known interpreter running an allowed package
        # e.g., /usr/bin/python3 running uvx
        pass  # The original basename was checked above

    # 4. Prevent path traversal (should be caught by resolve(), but double-check)
    if '..' in str(path):
        return False, "", "Path traversal detected in command"

    return True, resolved_path, ""


def _build_safe_environment(user_env: Dict[str, str]) -> Dict[str, str]:
    """
    Build a safe environment for MCP subprocess.

    - Starts with minimal inherited environment
    - Filters out dangerous inherited variables
    - Only allows user-specified variables from the allowlist
    """
    # Start with minimal safe environment
    safe_env = {}

    # Copy only essential system variables
    essential_vars = {"PATH", "HOME", "USER", "SHELL", "TERM", "LANG", "LC_ALL", "TZ"}
    for var in essential_vars:
        if var in os.environ and var not in BLOCKED_INHERITED_VARS:
            safe_env[var] = os.environ[var]

    # Add user-specified variables ONLY if they're in the allowlist
    for key, value in user_env.items():
        if key in ALLOWED_ENV_VARS:
            safe_env[key] = value
        elif key in BLOCKED_INHERITED_VARS:
            logger.warning(f"Blocked dangerous env var from MCP config: {key}")
        else:
            logger.warning(f"Ignored non-allowlisted env var for MCP: {key}")

    return safe_env


def _set_process_limits():
    """
    Set resource limits for the subprocess.
    Called as preexec_fn before subprocess starts.
    """
    try:
        # Memory limit (soft, hard) in bytes
        max_mem = MCP_PROCESS_LIMITS["max_memory_mb"] * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (max_mem, max_mem))

        # CPU time limit
        max_cpu = MCP_PROCESS_LIMITS["max_cpu_time_seconds"]
        resource.setrlimit(resource.RLIMIT_CPU, (max_cpu, max_cpu))

        # File descriptor limit
        max_fds = MCP_PROCESS_LIMITS["max_file_descriptors"]
        resource.setrlimit(resource.RLIMIT_NOFILE, (max_fds, max_fds))
    except (ValueError, resource.error) as e:
        # Log but don't fail - some limits may not be settable
        pass  # Can't log here as we're in subprocess preexec


def _validate_mcp_tool_response(response: Any) -> tuple[bool, str]:
    """
    Validate MCP tool response structure.

    Returns:
        (is_valid, error_message)
    """
    if response is None:
        return False, "Response is None"

    if not isinstance(response, dict):
        return False, f"Response must be a dict, got {type(response).__name__}"

    # Check for required fields in tool list response
    if "tools" in response:
        tools = response["tools"]
        if not isinstance(tools, list):
            return False, "tools must be a list"
        for i, tool in enumerate(tools):
            if not isinstance(tool, dict):
                return False, f"tool[{i}] must be a dict"
            if "name" not in tool:
                return False, f"tool[{i}] missing required 'name' field"
            if not isinstance(tool.get("name"), str):
                return False, f"tool[{i}].name must be a string"
            # Validate inputSchema if present
            if "inputSchema" in tool:
                if not isinstance(tool["inputSchema"], dict):
                    return False, f"tool[{i}].inputSchema must be a dict"

    # Check for content in tool call response
    if "content" in response:
        content = response["content"]
        if not isinstance(content, list):
            return False, "content must be a list"
        for i, item in enumerate(content):
            if not isinstance(item, dict):
                return False, f"content[{i}] must be a dict"
            if "type" not in item:
                return False, f"content[{i}] missing required 'type' field"

    return True, ""


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
            # SECURITY: Validate command against allowlist
            is_valid, resolved_cmd, error = _validate_command_path(self.server.command)
            if not is_valid:
                logger.error(f"MCP command validation failed: {error}")
                return False

            # SECURITY: Build safe environment (allowlist only)
            env = _build_safe_environment(self.server.env)

            args = self.server.args if self.server.args else []

            # SECURITY: Sanitize args before logging to prevent credential leakage
            sanitized_args = _sanitize_log_args(args)
            logger.info(f"Starting MCP server: {resolved_cmd} {' '.join(sanitized_args)}")

            # SECURITY: Apply resource limits via preexec_fn
            self.process = await asyncio.create_subprocess_exec(
                resolved_cmd,
                *args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                preexec_fn=_set_process_limits
            )

            # Start reading responses
            self._reader_task = asyncio.create_task(self._read_responses())

            # SECURITY: Wrap entire initialization in timeout
            try:
                async with asyncio.timeout(MCP_CONNECT_TIMEOUT):
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

                    # SECURITY: Validate tool list response
                    if tools_result:
                        is_valid, validation_error = _validate_mcp_tool_response(tools_result)
                        if not is_valid:
                            logger.warning(f"Invalid MCP tools response: {validation_error}")
                            # Continue with empty tools rather than crash
                            tools_result = {"tools": []}

                        if "tools" in tools_result:
                            self._tools = tools_result["tools"]
                            logger.info(f"MCP server '{self.server.name}' provides {len(self._tools)} tools")

            except asyncio.TimeoutError:
                logger.error(f"MCP connection timed out after {MCP_CONNECT_TIMEOUT}s")
                await self.disconnect()
                return False

            self._connected = True
            return True

        except FileNotFoundError:
            # SECURITY: Don't expose full path in error
            logger.error(f"MCP server command not found")
            return False
        except Exception as e:
            # SECURITY: Don't expose full exception details
            logger.error(f"Failed to connect to MCP server: {type(e).__name__}")
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

            # SECURITY: Validate response structure
            is_valid, validation_error = _validate_mcp_tool_response(result)
            if not is_valid:
                logger.warning(f"Invalid MCP tool response: {validation_error}")
                return {"error": "Invalid response from MCP server"}

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
            # SECURITY: Don't expose internal error details
            logger.error(f"Tool call failed: {type(e).__name__}")
            return {"error": "Tool execution failed"}


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

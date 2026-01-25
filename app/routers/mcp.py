"""MCP Server management API endpoints."""
import json
import logging
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.middleware.auth import require_auth
from app.models.auth_schemas import UserResponse
from app.services.database import get_database
from app.services.mcp_client import (
    MCPServer,
    get_mcp_manager,
    _validate_command_path,
    _validate_args,
    ALLOWED_MCP_COMMANDS,
    ALLOWED_ENV_VARS
)

router = APIRouter(prefix="/api/mcp", tags=["mcp"])
logger = logging.getLogger(__name__)


class MCPServerCreate(BaseModel):
    """Request body for creating an MCP server."""
    name: str
    transport: str = "stdio"
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    env: Optional[dict] = None


class MCPServerResponse(BaseModel):
    """Response model for an MCP server."""
    id: str
    name: str
    transport: str
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    env: Optional[dict] = None
    enabled: bool
    connected: bool
    created_at: Optional[str] = None


def _row_to_server(row) -> MCPServer:
    """Convert a database row to an MCPServer object."""
    return MCPServer(
        id=row["id"],
        user_id=row["user_id"],
        name=row["name"],
        transport=row["transport"],
        command=row["command"],
        args=json.loads(row["args"]) if row["args"] else [],
        url=row["url"],
        env=json.loads(row["env"]) if row["env"] else {},
        enabled=bool(row["enabled"]),
        created_at=row["created_at"]
    )


def _server_to_response(server: MCPServer) -> MCPServerResponse:
    """Convert an MCPServer to a response model."""
    manager = get_mcp_manager()
    return MCPServerResponse(
        id=server.id,
        name=server.name,
        transport=server.transport,
        command=server.command,
        args=server.args,
        url=server.url,
        env=server.env,
        enabled=server.enabled,
        connected=manager.is_connected(server.id),
        created_at=server.created_at
    )


@router.get("/servers", response_model=List[MCPServerResponse])
async def list_servers(user: UserResponse = Depends(require_auth)):
    """List all configured MCP servers for the user."""
    db = get_database()
    rows = db.fetchall(
        "SELECT * FROM mcp_servers WHERE user_id = ? ORDER BY created_at DESC",
        (user.id,)
    )
    servers = [_row_to_server(row) for row in rows]
    return [_server_to_response(s) for s in servers]


@router.post("/servers", response_model=MCPServerResponse)
async def add_server(
    request: MCPServerCreate,
    user: UserResponse = Depends(require_auth)
):
    """Add a new MCP server configuration."""
    db = get_database()

    # SECURITY: Validate command and args BEFORE storing
    if request.transport == "stdio" and request.command:
        # Validate command is in allowlist
        is_valid, resolved_path, error = _validate_command_path(request.command)
        if not is_valid:
            logger.warning(
                f"User {user.id} attempted to add MCP server with invalid command: "
                f"{request.command} - {error}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Invalid command: {error}. Allowed commands: {', '.join(sorted(ALLOWED_MCP_COMMANDS))}"
            )

        # Validate args don't contain dangerous patterns
        if request.args:
            args_valid, args_error = _validate_args(request.args)
            if not args_valid:
                logger.warning(
                    f"User {user.id} attempted to add MCP server with invalid args: {args_error}"
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid arguments: {args_error}"
                )

    # Validate env vars are in allowlist
    if request.env:
        invalid_vars = [k for k in request.env.keys() if k not in ALLOWED_ENV_VARS]
        if invalid_vars:
            logger.warning(
                f"User {user.id} attempted to add MCP server with non-allowlisted env vars: {invalid_vars}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Non-allowlisted environment variables: {', '.join(invalid_vars)}. "
                       f"Allowed: {', '.join(sorted(ALLOWED_ENV_VARS))}"
            )

    logger.info(f"User {user.id} adding MCP server: {request.name} ({request.command})")

    # SECURITY: Use full UUID to prevent collisions
    server_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()

    db.execute(
        """
        INSERT INTO mcp_servers (id, user_id, name, transport, command, args, url, env, enabled, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            server_id,
            user.id,
            request.name,
            request.transport,
            request.command,
            json.dumps(request.args) if request.args else None,
            request.url,
            json.dumps(request.env) if request.env else None,
            1,
            created_at
        )
    )

    server = MCPServer(
        id=server_id,
        user_id=user.id,
        name=request.name,
        transport=request.transport,
        command=request.command,
        args=request.args or [],
        url=request.url,
        env=request.env or {},
        enabled=True,
        created_at=created_at
    )

    return _server_to_response(server)


@router.delete("/servers/{server_id}")
async def delete_server(
    server_id: str,
    user: UserResponse = Depends(require_auth)
):
    """Remove an MCP server configuration."""
    db = get_database()

    # Verify ownership
    row = db.fetchone(
        "SELECT * FROM mcp_servers WHERE id = ? AND user_id = ?",
        (server_id, user.id)
    )
    if not row:
        raise HTTPException(status_code=404, detail="Server not found")

    # Disconnect if connected
    manager = get_mcp_manager()
    if manager.is_connected(server_id):
        await manager.disconnect_server(server_id)

    # Delete from database
    db.execute(
        "DELETE FROM mcp_servers WHERE id = ? AND user_id = ?",
        (server_id, user.id)
    )

    return {"success": True}


@router.post("/servers/{server_id}/connect")
async def connect_server(
    server_id: str,
    user: UserResponse = Depends(require_auth)
):
    """Connect to an MCP server."""
    db = get_database()

    row = db.fetchone(
        "SELECT * FROM mcp_servers WHERE id = ? AND user_id = ?",
        (server_id, user.id)
    )
    if not row:
        raise HTTPException(status_code=404, detail="Server not found")

    server = _row_to_server(row)
    manager = get_mcp_manager()

    # SECURITY: Log connection attempts for audit
    logger.info(
        f"User {user.id} connecting to MCP server: {server.name} "
        f"(id={server_id}, command={server.command})"
    )

    success = await manager.connect_server(server)
    if not success:
        logger.warning(f"User {user.id} failed to connect to MCP server {server_id}")
        raise HTTPException(status_code=500, detail="Failed to connect to MCP server")

    # Get tools from the connected server
    client = manager.get_client(server_id)
    tools = client.get_tools() if client else []

    logger.info(f"User {user.id} connected to MCP server {server_id}, tools: {[t.get('name') for t in tools]}")

    return {
        "success": True,
        "connected": True,
        "tools": tools
    }


@router.post("/servers/{server_id}/disconnect")
async def disconnect_server(
    server_id: str,
    user: UserResponse = Depends(require_auth)
):
    """Disconnect from an MCP server."""
    db = get_database()

    # Verify ownership
    row = db.fetchone(
        "SELECT * FROM mcp_servers WHERE id = ? AND user_id = ?",
        (server_id, user.id)
    )
    if not row:
        raise HTTPException(status_code=404, detail="Server not found")

    manager = get_mcp_manager()
    await manager.disconnect_server(server_id)

    return {"success": True, "connected": False}


@router.get("/tools")
async def list_tools(user: UserResponse = Depends(require_auth)):
    """List all available tools from connected MCP servers."""
    manager = get_mcp_manager()
    tools = manager.get_all_tools()
    return {"tools": tools}

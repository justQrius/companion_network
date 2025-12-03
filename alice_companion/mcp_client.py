"""MCP Client for Alice's Companion to call tools on Bob's Companion MCP server.

This module implements an MCP client that connects to Bob's Companion's MCP endpoint
over HTTP using JSON-RPC 2.0 protocol. The endpoint is hardcoded per ADR-003 for MVP.

Architecture Decision Record (ADR-003):
- Hardcoded endpoints for local demo: Alice (localhost:8001), Bob (localhost:8002)
- JSON-RPC 2.0 protocol over HTTP transport
- Simplified discovery (no Agent Cards for MVP)
"""

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

# Hardcoded endpoint per ADR-003 (Architecture Decision Record)
BOB_ENDPOINT = "http://localhost:8002/run"


class MCPClient:
    """MCP Client for calling tools on remote MCP server over HTTP/JSON-RPC 2.0.
    
    This client implements the MCP protocol over HTTP using JSON-RPC 2.0.
    It connects to Bob's Companion endpoint and can call tools on his MCP server.
    
    Attributes:
        endpoint: The HTTP endpoint URL for the remote MCP server
        client: HTTP client for making requests
        _initialized: Whether the client has been initialized/connected
    """
    
    def __init__(self, endpoint: str = BOB_ENDPOINT):
        """Initialize MCP client with target endpoint.
        
        Args:
            endpoint: HTTP endpoint URL for remote MCP server (default: Bob's endpoint)
        """
        self.endpoint = endpoint
        self.client: Optional[httpx.AsyncClient] = None
        self._initialized = False
        
    async def _ensure_connection(self):
        """Ensure HTTP client is initialized and connection is established.
        
        Creates HTTP client if not already created. This handles connection
        establishment logic as required by AC3.
        """
        if self.client is None:
            # Create async HTTP client with reasonable timeout
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=10.0),
                follow_redirects=True
            )
            self._initialized = True
            logger.info(f"MCP client initialized for endpoint: {self.endpoint}")
    
    async def call_tool(self, tool_name: str, **params: Any) -> Dict[str, Any]:
        """Call a tool on the remote MCP server.
        
        Sends a JSON-RPC 2.0 request to the remote endpoint to execute the specified tool.
        Handles connection establishment, error handling, and retry logic per architecture
        error handling pattern.
        
        Args:
            tool_name: Name of the tool to call on remote MCP server
            **params: Keyword arguments to pass as tool parameters
            
        Returns:
            Dictionary containing tool execution result
            
        Raises:
            ConnectionError: If connection cannot be established after retry
            ValueError: If tool call fails with invalid parameters
            Exception: For other unexpected errors (with retry logic)
        """
        await self._ensure_connection()
        
        # Construct JSON-RPC 2.0 request
        # MCP protocol uses JSON-RPC 2.0 format for tool calls
        request_id = f"mcp_call_{id(self)}_{asyncio.get_event_loop().time()}"
        jsonrpc_request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        # Retry logic per architecture error handling pattern
        # MCP call failures: retry once, then report to user
        max_retries = 1
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                logger.debug(
                    f"Calling tool '{tool_name}' on {self.endpoint} "
                    f"(attempt {attempt + 1}/{max_retries + 1})"
                )
                
                # Send HTTP POST request with JSON-RPC 2.0 payload
                response = await self.client.post(
                    self.endpoint,
                    json=jsonrpc_request,
                    headers={"Content-Type": "application/json"}
                )
                
                # Check HTTP status
                response.raise_for_status()
                
                # Parse JSON-RPC 2.0 response
                result = response.json()
                
                # Validate JSON-RPC 2.0 response structure
                if "error" in result:
                    error = result["error"]
                    logger.warning(
                        f"Tool call error: {error.get('message', 'Unknown error')} "
                        f"(code: {error.get('code', 'unknown')})"
                    )
                    raise ValueError(
                        f"Tool call failed: {error.get('message', 'Unknown error')}"
                    )
                
                if "result" not in result:
                    raise ValueError("Invalid JSON-RPC response: missing 'result' field")
                
                # Extract tool result from JSON-RPC response
                tool_result = result["result"]
                logger.info(f"Tool '{tool_name}' called successfully")
                return tool_result
                
            except httpx.ConnectError as e:
                last_error = e
                logger.warning(
                    f"Connection error (attempt {attempt + 1}): {e}. "
                    f"{'Retrying...' if attempt < max_retries else 'Giving up.'}"
                )
                if attempt < max_retries:
                    # Wait briefly before retry
                    await asyncio.sleep(0.5)
                    continue
                else:
                    # After retry, report to user (graceful degradation)
                    error_msg = (
                        f"Agent temporarily unavailable: "
                        f"Cannot connect to {self.endpoint}. "
                        f"Please ensure the remote Companion is running."
                    )
                    logger.error(error_msg)
                    raise ConnectionError(error_msg) from e
                    
            except httpx.HTTPStatusError as e:
                last_error = e
                logger.warning(
                    f"HTTP error {e.response.status_code} (attempt {attempt + 1}): {e}"
                )
                if attempt < max_retries:
                    await asyncio.sleep(0.5)
                    continue
                else:
                    error_msg = (
                        f"HTTP error calling tool: {e.response.status_code}. "
                        f"Response: {e.response.text[:200]}"
                    )
                    raise ConnectionError(error_msg) from e
                    
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error calling tool (attempt {attempt + 1}): {e}")
                if attempt < max_retries:
                    await asyncio.sleep(0.5)
                    continue
                else:
                    raise
        
        # Should not reach here, but handle edge case
        raise ConnectionError(
            f"Tool call failed after {max_retries + 1} attempts: {last_error}"
        )
    
    async def close(self):
        """Close the HTTP client connection.
        
        Cleans up resources and closes the HTTP client. Should be called
        when the client is no longer needed.
        """
        if self.client is not None:
            await self.client.aclose()
            self.client = None
            self._initialized = False
            logger.info("MCP client connection closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_connection()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


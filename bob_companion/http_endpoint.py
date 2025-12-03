"""HTTP endpoint for Bob's MCP server tools.

This module provides an HTTP endpoint at /run that handles JSON-RPC 2.0 requests
and routes them to MCP tools. This enables A2A Protocol communication.

Architecture:
- Endpoint: http://localhost:8002/run
- Protocol: JSON-RPC 2.0 over HTTP POST
- Routes tool calls to functions in mcp_server.py
"""

import asyncio
import json
import logging
from typing import Any, Dict

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from bob_companion.mcp_server import check_availability, propose_event

logger = logging.getLogger(__name__)

app = FastAPI(title="Bob's Companion MCP Server")


@app.post("/run")
async def handle_jsonrpc(request: Request) -> JSONResponse:
    """Handle JSON-RPC 2.0 requests and route to MCP tools.
    
    This endpoint receives JSON-RPC 2.0 requests from MCP clients and routes
    them to the appropriate MCP tool function.
    
    Expected JSON-RPC 2.0 format:
    {
        "jsonrpc": "2.0",
        "id": "request_id",
        "method": "tools/call",
        "params": {
            "name": "tool_name",
            "arguments": {...}
        }
    }
    
    Returns JSON-RPC 2.0 response:
    {
        "jsonrpc": "2.0",
        "id": "request_id",
        "result": {...} or "error": {...}
    }
    """
    try:
        body = await request.json()
        
        # Validate JSON-RPC 2.0 structure
        if body.get("jsonrpc") != "2.0":
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request: jsonrpc must be '2.0'"
                    }
                }
            )
        
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        # Handle tools/call method
        if method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            # Route to appropriate tool
            if tool_name == "check_availability":
                result = await check_availability(
                    timeframe=tool_args.get("timeframe"),
                    event_type=tool_args.get("event_type"),
                    duration_minutes=tool_args.get("duration_minutes"),
                    requester=tool_args.get("requester")
                )
            elif tool_name == "propose_event":
                result = await propose_event(
                    event_name=tool_args.get("event_name"),
                    datetime=tool_args.get("datetime"),
                    location=tool_args.get("location"),
                    participants=tool_args.get("participants"),
                    requester=tool_args.get("requester")
                )
            else:
                return JSONResponse(
                    status_code=200,
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {tool_name}"
                        }
                    }
                )
            
            # Return successful result
            return JSONResponse(
                status_code=200,
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            )
        else:
            # Unknown method
            return JSONResponse(
                status_code=200,
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            )
            
    except Exception as e:
        logger.error(f"Error handling JSON-RPC request: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": body.get("id") if 'body' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
        )


def run_server(host: str = "localhost", port: int = 8002):
    """Run the HTTP server for Bob's MCP tools.
    
    Args:
        host: Host to bind to (default: localhost)
        port: Port to bind to (default: 8002)
    """
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()


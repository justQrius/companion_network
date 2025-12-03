"""A2A (Agent-to-Agent) event logging utilities.

This module provides functions for logging A2A communication events for the
network activity monitor. Events are logged to session state for Gradio visualization.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def log_a2a_event(
    session_state: Dict[str, Any],
    sender: str,
    receiver: str,
    tool: str,
    params: Dict[str, Any],
    result: Dict[str, Any]
) -> None:
    """Log A2A communication event for network monitor.
    
    Creates an event dictionary following the architecture pattern (lines 428-440)
    and appends it to `app:a2a_events` list in session state. The event includes
    timestamp, sender, receiver, tool name, redacted parameters, and status.
    
    Integration Pattern:
    - Called after A2A tool calls (both successful and failed)
    - Events are stored in session state for Gradio network activity monitor
    - Sensitive parameters (e.g., "requester") are redacted from logs
    
    Args:
        session_state: Session state dictionary to update (mutated in-place)
        sender: Sender agent identifier (e.g., "alice", "bob")
        receiver: Receiver agent identifier (e.g., "bob", "alice")
        tool: Tool name that was called
        params: Tool parameters (will be redacted)
        result: Tool execution result (used to determine status)
        
    Example:
        log_a2a_event(
            session_state=session.state,
            sender="alice",
            receiver="bob",
            tool="check_availability",
            params={"timeframe": "this weekend", "requester": "alice"},
            result={"available": True, "slots": [...]}
        )
    """
    # Redact sensitive parameters (e.g., requester) per architecture pattern
    redacted_params = {
        k: v for k, v in params.items() 
        if k != "requester"
    }
    
    # Determine status from result
    status = "success" if "error" not in result else "failed"
    
    # Create event dictionary following architecture pattern
    event = {
        "timestamp": datetime.now().isoformat(),
        "sender": sender,
        "receiver": receiver,
        "tool": tool,
        "params": redacted_params,
        "status": status
    }
    
    # Initialize app:a2a_events list if it doesn't exist
    if "app:a2a_events" not in session_state:
        session_state["app:a2a_events"] = []
    
    # Append event to list
    session_state["app:a2a_events"].append(event)
    
    # Log to application logger
    logger.info(f"A2A: {sender} → {receiver} : {tool} ({status})")


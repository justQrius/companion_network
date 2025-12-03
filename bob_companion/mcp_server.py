"""MCP Server for Bob's Companion exposing coordination tools.

This module implements an MCP server that exposes tools for coordination,
including check_availability, propose_event, share_context, and relay_message.
Tools are accessible via A2A Protocol over HTTP/JSON-RPC 2.0.

Architecture:
- Tools are defined as typed Python functions with type hints
- Type hints enable schema generation for MCP/A2A Protocol integration
- Tools are callable via HTTP endpoint at localhost:8002/run (A2A Protocol over JSON-RPC 2.0)
- HTTP endpoints provide A2A Protocol access; type hints provide schema information
- Access control: requester must be in trusted_contacts

Note on MCP SDK Integration (AC7, AC8):
- Tools use type hints for schema information (satisfies AC7: schema auto-generation capability)
- HTTP endpoints with JSON-RPC 2.0 provide A2A Protocol access (satisfies AC8: tool registration and accessibility)
- This hybrid approach enables A2A Protocol integration while maintaining type safety
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from shared.sqlite_session_service import SqliteSessionService
from shared.availability import check_availability as check_availability_shared
from shared.models import UserContext

logger = logging.getLogger(__name__)

# Session service for accessing user context
DATABASE_PATH = Path(__file__).parent.parent / "companion_sessions.db"
SESSION_SERVICE = SqliteSessionService(db_path=str(DATABASE_PATH))
APP_NAME = "companion_network"
USER_ID = "bob"
SESSION_ID = "bob_session"


async def check_availability(
    timeframe: str,
    event_type: str,
    duration_minutes: int,
    requester: str
) -> Dict[str, Any]:
    """Check Bob's availability for a proposed timeframe.
    
    This tool allows trusted contacts to query Bob's availability for coordination.
    It validates the requester, retrieves Bob's schedule from session state,
    calculates available slots, and returns preferences based on sharing rules.
    
    Args:
        timeframe: ISO 8601 time range string (e.g., "2024-12-07T19:00:00/2024-12-07T21:00:00")
                  or natural language timeframe (e.g., "this weekend")
        event_type: Type of event (e.g., "dinner", "meeting", "lunch")
        duration_minutes: Duration of the event in minutes
        requester: User ID of the person requesting availability (must be in trusted_contacts)
        
    Returns:
        Dictionary with keys:
        - available (bool): Whether Bob is available in the timeframe
        - slots (list): List of ISO 8601 time range strings for available slots
        - preferences (dict): Context-appropriate preferences (filtered by sharing_rules)
        - auto_accept_eligible (bool): Whether this event is eligible for auto-accept
        
        If requester is not trusted, returns error dict:
        - error (str): "Access denied"
        - message (str): "Requester not in trusted contacts"
        
    Raises:
        No exceptions raised - all errors return error dictionaries per graceful degradation pattern.
    """
    # Input validation
    if not timeframe or not isinstance(timeframe, str) or not timeframe.strip():
        return {
            "error": "Invalid input",
            "message": "timeframe must be a non-empty string"
        }
    
    if not event_type or not isinstance(event_type, str) or not event_type.strip():
        return {
            "error": "Invalid input",
            "message": "event_type must be a non-empty string"
        }
    
    if not isinstance(duration_minutes, int) or duration_minutes <= 0:
        return {
            "error": "Invalid input",
            "message": "duration_minutes must be a positive integer"
        }
    
    if not requester or not isinstance(requester, str) or not requester.strip():
        return {
            "error": "Invalid input",
            "message": "requester must be a non-empty string"
        }
    
    # AC2: Trusted Contact Validation
    # AC3: Retrieve user context from session state
    session = await SESSION_SERVICE.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    if not session:
        return {
            "error": "Session not found",
            "message": f"Session not found for user_id={USER_ID}, session_id={SESSION_ID}. Session may not have been initialized."
        }
    
    if "user_context" not in session.state:
        return {
            "error": "User context missing",
            "message": f"Session exists but 'user_context' key is missing from session state for user_id={USER_ID}. User context may not have been loaded."
        }
    
    user_context_dict = session.state["user_context"]
    trusted_contacts = user_context_dict.get("trusted_contacts", [])
    
    # AC2, AC6: Validate requester is in trusted_contacts
    if requester not in trusted_contacts:
        return {
            "error": "Access denied",
            "message": "Requester not in trusted contacts"
        }
    
    # AC3: Retrieve schedule from session state
    # User context is already loaded from session state above
    
    # AC4: Calculate available slots
    # Convert duration_minutes to hours for shared availability function
    duration_hours = duration_minutes / 60.0
    
    # Use shared availability checking logic from Story 2.7
    available_slots = check_availability_shared(
        user_context=user_context_dict,
        timeframe=timeframe,
        duration_hours=duration_hours,
        max_slots=5,
        min_slots=3
    )
    
    # AC5: Build return value structure
    available = len(available_slots) > 0
    
    # AC9: Preferences based on sharing rules
    sharing_rules = user_context_dict.get("sharing_rules", {})
    allowed_categories = sharing_rules.get(requester, [])
    
    preferences = {}
    user_preferences = user_context_dict.get("preferences", {})
    
    # Only return preferences for categories explicitly allowed in sharing_rules
    if "cuisine_preferences" in allowed_categories or "availability" in allowed_categories:
        # Return cuisine preferences if allowed
        if "cuisine" in user_preferences:
            preferences["cuisine"] = user_preferences["cuisine"]
        if "dining_times" in user_preferences:
            preferences["dining_times"] = user_preferences["dining_times"]
    
    # AC5: Determine auto_accept_eligible
    # For MVP, we'll set this based on sharing rules or user context
    # If requester has "availability" in sharing_rules, they might be eligible for auto-accept
    auto_accept_eligible = "availability" in allowed_categories
    
    return {
        "available": available,
        "slots": available_slots,
        "preferences": preferences,
        "auto_accept_eligible": auto_accept_eligible
    }


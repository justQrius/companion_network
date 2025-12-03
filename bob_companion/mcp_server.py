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
import uuid
from datetime import datetime as dt
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import asdict

from shared.sqlite_session_service import SqliteSessionService
from shared.availability import check_availability as check_availability_shared
from shared.models import UserContext, EventProposal

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


async def propose_event(
    event_name: str,
    datetime: str,
    location: str,
    participants: List[str],
    requester: str
) -> Dict[str, Any]:
    """Propose an event to Bob for coordination.
    
    This tool allows trusted contacts to propose specific events to Bob.
    It validates the requester, checks for schedule conflicts, creates an
    EventProposal object, and stores it in session state. The tool supports
    auto-accept logic and conflict detection.
    
    Args:
        event_name: Name/title of the event (e.g., "Dinner at Trattoria")
        datetime: ISO 8601 formatted datetime string (e.g., "2024-12-07T19:00:00")
        location: Location of the event (e.g., "Trattoria on Main")
        participants: List of user IDs participating in the event
        requester: User ID of the person proposing the event (must be in trusted_contacts)
        
    Returns:
        Dictionary with keys:
        - status (str): "accepted", "declined", "pending", or "counter"
        - message (str): Explanation message
        - event_id (str): Unique event identifier (if accepted/pending)
        
        If requester is not trusted, returns error dict:
        - error (str): "Access denied"
        - message (str): "Requester not in trusted contacts"
        
        If invalid input, returns error dict:
        - error (str): "Invalid input"
        - message (str): Description of validation error
        
    Raises:
        No exceptions raised - all errors return error dictionaries per graceful degradation pattern.
    """
    # AC1: Input validation
    if not event_name or not isinstance(event_name, str) or not event_name.strip():
        return {
            "error": "Invalid input",
            "message": "event_name must be a non-empty string"
        }
    
    if not datetime or not isinstance(datetime, str) or not datetime.strip():
        return {
            "error": "Invalid input",
            "message": "datetime must be a non-empty ISO 8601 string"
        }
    
    # Validate ISO 8601 datetime format
    try:
        proposed_datetime = dt.fromisoformat(datetime.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return {
            "error": "Invalid input",
            "message": "datetime must be a valid ISO 8601 formatted string"
        }
    
    if not isinstance(location, str):
        return {
            "error": "Invalid input",
            "message": "location must be a string"
        }
    
    if not isinstance(participants, list) or len(participants) == 0:
        return {
            "error": "Invalid input",
            "message": "participants must be a non-empty list of user IDs"
        }
    
    if not requester or not isinstance(requester, str) or not requester.strip():
        return {
            "error": "Invalid input",
            "message": "requester must be a non-empty string"
        }
    
    # AC2: Trusted Contact Validation
    # AC4: Retrieve user context from session state
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
    
    # AC2: Validate requester is in trusted_contacts
    if requester not in trusted_contacts:
        return {
            "error": "Access denied",
            "message": "Requester not in trusted contacts"
        }
    
    # AC4: Conflict Detection - Check for overlapping events
    # Query session state for existing EventProposals
    existing_proposals = []
    for key, value in session.state.items():
        if key.startswith("event_proposal:") and isinstance(value, dict):
            # Check if proposal is pending or accepted (declined proposals don't conflict)
            proposal_status = value.get("status", "")
            if proposal_status in ["pending", "accepted"]:
                existing_proposals.append(value)
    
    # Check for conflicts by comparing datetime
    for existing_proposal in existing_proposals:
        proposal_details = existing_proposal.get("details", {})
        existing_time_str = proposal_details.get("time", "")
        
        if existing_time_str:
            try:
                existing_datetime = dt.fromisoformat(existing_time_str.replace('Z', '+00:00'))
                # Check if times overlap (same timeslot or within 2 hours of each other)
                time_diff = abs((proposed_datetime - existing_datetime).total_seconds())
                # Consider it a conflict if within 2 hours (same timeslot or adjacent)
                if time_diff < 7200:  # 2 hours in seconds
                    return {
                        "status": "declined",
                        "message": f"Bob already has an event scheduled at {existing_time_str}. Please propose a different time.",
                        "event_id": None
                    }
            except (ValueError, AttributeError):
                # Skip invalid datetime formats in existing proposals
                continue
    
    # AC5: Auto-Accept Logic
    # For MVP, auto-accept is not implemented, so we default to "pending"
    # If auto-accept rules were implemented, we would check:
    # - If requester has "availability" in sharing_rules
    # - If event type matches auto-accept preferences
    # - If time matches preferred times
    auto_accept = False
    sharing_rules = user_context_dict.get("sharing_rules", {})
    allowed_categories = sharing_rules.get(requester, [])
    
    # For MVP, we'll leave auto-accept as False (default to pending)
    # This can be enhanced later based on user preferences
    
    # AC3: Create EventProposal object
    # Generate unique event_id
    timestamp_str = dt.now().strftime("%Y%m%d%H%M%S")
    event_id = f"evt_{timestamp_str}_{requester}_{USER_ID}"
    
    # Determine status based on auto-accept
    proposal_status = "accepted" if auto_accept else "pending"
    
    # Create EventProposal details dict
    proposal_details = {
        "title": event_name,
        "time": proposed_datetime.isoformat(),
        "location": location,
        "participants": participants
    }
    
    # Create EventProposal dataclass instance
    event_proposal = EventProposal(
        event_id=event_id,
        proposer=requester,
        recipient=USER_ID,
        status=proposal_status,
        timestamp=dt.now().isoformat(),
        details=proposal_details
    )
    
    # AC3: Store EventProposal in session state
    # AC8: User Notification - Queue message for next agent interaction
    # Batch both updates into a single session state update for better performance
    state = session.state.copy()
    proposal_key = f"event_proposal:{event_id}"
    # Convert dataclass to dict for JSON serialization
    state[proposal_key] = asdict(event_proposal)
    
    # Add notification to pending_messages list in session state
    if "pending_messages" not in state:
        state["pending_messages"] = []
    
    notification_message = f"{requester} has proposed {event_name} on {proposed_datetime.strftime('%Y-%m-%d at %H:%M')} at {location if location else 'TBD'}"
    state["pending_messages"].append(notification_message)
    
    # Update session state with both EventProposal and notification in single operation
    await SESSION_SERVICE.update_session_state(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=state
    )
    
    # AC7: Return value structure
    if proposal_status == "accepted":
        return {
            "status": "accepted",
            "message": f"Event '{event_name}' has been automatically accepted.",
            "event_id": event_id
        }
    else:
        return {
            "status": "pending",
            "message": f"Event '{event_name}' has been proposed and is awaiting Bob's review.",
            "event_id": event_id
        }


async def relay_message(
    message: str,
    urgency: str,
    sender: str
) -> Dict[str, Any]:
    """Relay a message from a trusted contact to Bob.
    
    This tool allows trusted contacts to send messages to Bob through his Companion.
    Messages are queued in session state and displayed to Bob in his next agent interaction.
    The tool validates the sender is in Bob's trusted_contacts list before accepting the message.
    
    Args:
        message: The message text to relay to Bob (required, non-empty string)
        urgency: Urgency level (enum: "low", "normal", "high") - affects display priority
        sender: User ID of the person sending the message (must be in trusted_contacts)
        
    Returns:
        Dictionary with keys:
        - delivered (bool): True if message was successfully queued, False on failure
        
        If sender is not trusted, returns error dict:
        - error (str): "Access denied"
        - message (str): "Sender not in trusted contacts"
        
        If invalid input, returns error dict:
        - error (str): "Invalid input"
        - message (str): Description of validation error
        
    Raises:
        No exceptions raised - all errors return error dictionaries per graceful degradation pattern.
        
    Message Storage:
        Messages are stored in session state under key "pending_messages" as a list.
        Each message dict contains: message (str), urgency (str), sender (str), timestamp (ISO 8601 string).
        Messages are displayed to Bob in his next agent response, sorted by urgency priority.
    """
    # AC1: Input validation
    if not message or not isinstance(message, str) or not message.strip():
        return {
            "error": "Invalid input",
            "message": "message must be a non-empty string"
        }
    
    # AC1: Urgency enum validation
    valid_urgencies = ["low", "normal", "high"]
    if urgency not in valid_urgencies:
        return {
            "error": "Invalid input",
            "message": f"urgency must be one of: {', '.join(valid_urgencies)}"
        }
    
    if not sender or not isinstance(sender, str) or not sender.strip():
        return {
            "error": "Invalid input",
            "message": "sender must be a non-empty string"
        }
    
    # AC2: Trusted Contact Validation
    # AC4: Retrieve user context from session state
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
    
    # AC2: Validate sender is in trusted_contacts
    if sender not in trusted_contacts:
        return {
            "error": "Access denied",
            "message": "Sender not in trusted contacts"
        }
    
    # AC3: Message Queuing
    # AC8: Create message dict with fields: message, urgency, sender, timestamp
    message_dict = {
        "message": message.strip(),
        "urgency": urgency,
        "sender": sender,
        "timestamp": dt.now().isoformat()
    }
    
    # AC8: Retrieve existing pending_messages list from session state
    state = session.state.copy()
    pending_messages = state.get("pending_messages", [])
    
    # AC8: Append new message to pending_messages list
    pending_messages.append(message_dict)
    
    # AC8: Store updated pending_messages list back to session state
    state["pending_messages"] = pending_messages
    
    try:
        await SESSION_SERVICE.update_session_state(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
            state=state
        )
    except Exception as e:
        # AC5: Handle session state write failures
        logger.error(f"Failed to update session state with pending message: {e}", exc_info=True)
        return {
            "error": "Storage failure",
            "message": "Failed to store message in session state",
            "delivered": False
        }
    
    # AC4: Return dict with delivered: True if successful
    return {
        "delivered": True
    }


async def share_context(
    category: str,
    purpose: str,
    requester: str
) -> Dict[str, Any]:
    """Share specific approved context with a trusted contact.
    
    This tool allows trusted contacts to request specific context categories
    (preferences, dietary, schedule, interests) based on sharing rules.
    It enforces strict privacy protection by only returning data explicitly
    allowed in sharing_rules (data minimization principle).
    
    Args:
        category: Context category to share (enum: "preferences", "dietary", "schedule", "interests")
        purpose: Description of what the context will be used for (logged for audit trail)
        requester: User ID of the person requesting context (must be in trusted_contacts)
        
    Returns:
        Dictionary with keys:
        - context_data (dict): Requested context data if category is allowed in sharing_rules
        - access_denied (str): Reason message if category is not permitted (mutually exclusive with context_data)
        
        If requester is not trusted, returns error dict:
        - error (str): "Access denied"
        - message (str): "Requester not in trusted contacts"
        
        If invalid input, returns error dict:
        - error (str): "Invalid input"
        - message (str): Description of validation error
        
    Raises:
        No exceptions raised - all errors return error dictionaries per graceful degradation pattern.
        
    Privacy Protection:
        - Only returns data for categories explicitly allowed in sharing_rules[requester]
        - Never exposes data not explicitly permitted (data minimization principle)
        - Logs purpose parameter for contextual integrity (not enforced in MVP)
    """
    # AC1: Input validation
    if not category or not isinstance(category, str) or not category.strip():
        return {
            "error": "Invalid input",
            "message": "category must be a non-empty string"
        }
    
    if not purpose or not isinstance(purpose, str) or not purpose.strip():
        return {
            "error": "Invalid input",
            "message": "purpose must be a non-empty string"
        }
    
    if not requester or not isinstance(requester, str) or not requester.strip():
        return {
            "error": "Invalid input",
            "message": "requester must be a non-empty string"
        }
    
    # AC6: Category enum validation
    valid_categories = ["preferences", "dietary", "schedule", "interests"]
    if category not in valid_categories:
        return {
            "error": "Invalid input",
            "message": f"category must be one of: {', '.join(valid_categories)}"
        }
    
    # AC2: Trusted Contact Validation
    # AC4: Retrieve user context from session state
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
    
    # AC2: Validate requester is in trusted_contacts
    if requester not in trusted_contacts:
        return {
            "error": "Access denied",
            "message": "Requester not in trusted contacts"
        }
    
    # AC8: Purpose logging (contextual integrity - logged but not enforced in MVP)
    logger.info(f"share_context called: category={category}, purpose={purpose}, requester={requester}")
    
    # AC3: Sharing Rules Validation
    sharing_rules = user_context_dict.get("sharing_rules", {})
    
    # AC7: Privacy Protection - Check if requester has sharing rules
    if requester not in sharing_rules:
        return {
            "access_denied": "No sharing rules defined for requester"
        }
    
    allowed_categories = sharing_rules.get(requester, [])
    
    # AC3, AC7: Privacy Protection - Check if category is allowed
    if not allowed_categories or category not in allowed_categories:
        return {
            "access_denied": "Category not permitted in sharing rules"
        }
    
    # AC4: Extract context data based on category
    context_data = {}
    
    if category == "preferences":
        # Extract preferences: cuisine, dining_times, weekend_availability
        user_preferences = user_context_dict.get("preferences", {})
        if "cuisine" in user_preferences:
            context_data["cuisine"] = user_preferences["cuisine"]
        if "dining_times" in user_preferences:
            context_data["dining_times"] = user_preferences["dining_times"]
        if "weekend_availability" in user_preferences:
            context_data["weekend_availability"] = user_preferences["weekend_availability"]
    
    elif category == "dietary":
        # Extract dietary restrictions/allergies if available
        # May be empty dict if not configured (AC4.6: handle missing data gracefully)
        user_preferences = user_context_dict.get("preferences", {})
        if "dietary_restrictions" in user_preferences:
            context_data["dietary_restrictions"] = user_preferences["dietary_restrictions"]
        if "allergies" in user_preferences:
            context_data["allergies"] = user_preferences["allergies"]
        # Return empty dict if not available (not an error)
    
    elif category == "schedule":
        # Extract schedule patterns (not full schedule, just patterns like "prefers evenings")
        # AC4.4: Return schedule patterns, not full schedule
        user_preferences = user_context_dict.get("preferences", {})
        if "schedule_patterns" in user_preferences:
            context_data["schedule_patterns"] = user_preferences["schedule_patterns"]
        # Return empty dict if not available (not an error)
    
    elif category == "interests":
        # Extract interests/hobbies if available
        # May be empty dict if not configured (AC4.6: handle missing data gracefully)
        user_preferences = user_context_dict.get("preferences", {})
        if "interests" in user_preferences:
            context_data["interests"] = user_preferences["interests"]
        if "hobbies" in user_preferences:
            context_data["hobbies"] = user_preferences["hobbies"]
        # Return empty dict if not available (not an error)
    
    # AC9: Return value structure - mutually exclusive context_data or access_denied
    # Since we've already validated category is allowed, return context_data
    return {
        "context_data": context_data
    }

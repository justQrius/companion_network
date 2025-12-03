"""Alice's Companion Agent using Google ADK.

This module initializes Alice's Companion agent with persistent session storage
and in-memory long-term memory, configured for coordination tasks.
"""

from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from google.adk import Agent, Runner
from alice_companion.sqlite_session_service import SqliteSessionService
from google.adk.memory import InMemoryMemoryService
from alice_companion.user_context import get_alice_context
from alice_companion.mcp_client import MCPClient
from shared.availability import check_availability
from shared.a2a_logging import log_a2a_event
from shared.coordination import (
    find_overlapping_slots,
    prioritize_slots_by_preferences,
    synthesize_recommendation,
    handle_no_overlaps
)
from shared.models import EventProposal
from datetime import datetime

# Configuration constants
AGENT_NAME = "alices_companion"  # Valid identifier (spaces/special chars not allowed)
AGENT_DISPLAY_NAME = "Alice's Companion"  # Display name for user-facing contexts
MODEL = "gemini-2.5-pro"
SESSION_ID = "alice_session"
DATABASE_PATH = Path(__file__).parent.parent / "companion_sessions.db"

# System instruction emphasizing coordination, privacy, and natural conversation
# Enhanced with natural language coordination request parsing (Story 2.5)
# Enhanced with availability checking capability (Story 2.7)
# Enhanced with A2A communication capability (Story 2.8)
# Enhanced with coordination logic capability (Story 2.9)
SYSTEM_INSTRUCTION = """You are Alice's personal Companion agent. You coordinate plans on Alice's behalf, 
maintaining her privacy while facilitating natural conversations with other companions. 
You help schedule events, share availability, and propose activities while respecting 
Alice's preferences and trusted contact list.

## Natural Language Coordination Understanding

You understand coordination requests in natural language - no rigid command syntax is required. 
When Alice makes a coordination request, you should:

1. **Identify Coordination Intent**: Recognize when Alice wants to coordinate with someone
   - Examples: "Find a time for dinner with Bob this weekend"
   - Examples: "Schedule lunch with Sarah next week"
   - Examples: "Plan a meeting with Mike tomorrow"

2. **Extract Key Information**: From natural language, extract:
   - **Activity type**: What kind of event (dinner, lunch, meeting, etc.)
   - **Participants**: Who is involved (extract names and match to trusted contacts)
   - **Time constraints**: When (timeframe, specific dates, relative times like "this weekend", "next week")

3. **Verify Trusted Contacts**: Before coordinating, check that the other party is in Alice's trusted contact list.
   Access this via session.state["user_context"]["trusted_contacts"]. Only proceed with coordination
   if the person is trusted.

4. **Check Availability**: After parsing the coordination request, check Alice's availability for the requested timeframe.
   Use the check_availability() helper function to retrieve Alice's schedule from session state and identify
   free time slots that align with her dining preferences. This helps you know when Alice is available before
   coordinating with other companions.

5. **A2A Communication**: When you need to coordinate with another Companion agent (e.g., Bob's Companion),
   use the call_other_companion_tool() helper function to call tools on their MCP server. This function:
   - Handles JSON-RPC 2.0 protocol communication automatically
   - Includes retry logic for reliability
   - Returns error dictionaries instead of raising exceptions (always provides feedback)
   - Logs all communication events for network monitoring
   - Example: result = await call_other_companion_tool("check_availability", timeframe="this weekend", requester="alice")
   - Always check for "error" key in result before processing: if "error" in result, inform Alice gracefully

6. **Coordinate Mutual Availability**: When you need to find a time that works for both Alice and another user,
   use the coordinate_mutual_availability() helper function. This function:
   - Checks Alice's availability for the requested timeframe
   - Calls the other Companion's check_availability tool via A2A
   - Finds overlapping time slots where both users are available
   - Prioritizes slots based on dining time and cuisine preferences
   - Synthesizes a natural language recommendation
   - Example: result = await coordinate_mutual_availability("this weekend", "bob")
   - If result["success"] is True, present result["recommendation"] to Alice
   - If no overlaps exist, present result["alternatives"]["suggestion"] and ask for flexibility
   - Always handle errors gracefully and provide clear feedback

7. **Event Proposal to User**: After coordinating mutual availability and getting a recommendation,
   you should propose the event to Alice for confirmation using the propose_event_to_user() helper function.
   This function:
   - Creates an EventProposal from the coordination recommendation
   - Formats a natural language message with time, duration, participant, and context
   - Stores the proposal in session state as "pending" awaiting Alice's confirmation
   - Presents the proposal message to Alice with a call to action
   - Example: After coordinate_mutual_availability() succeeds, call propose_event_to_user(recommendation, "bob")
   - The proposal waits for Alice's next message ("yes", "confirm", "sounds good") to proceed

7. **Acknowledge Naturally**: Respond with natural language acknowledgment that shows understanding:
   - Example: "I'll check your availability for this weekend and coordinate with Bob's Companion to find a time for dinner..."
   - Use conversational tone, not JSON or structured formats

8. **Identify Contact Need**: Determine which Companion agent you need to contact for coordination
   (e.g., if Alice mentions "Bob", you'll need to contact Bob's Companion).

8. **User Confirmation Handling**: When you present an event proposal to Alice, wait for her confirmation
   in her next message. Use the handle_user_confirmation() helper function to check if Alice's response
   indicates approval. Confirmation keywords include: "yes", "confirm", "sounds good", "go ahead", "proceed".
   If Alice confirms, you can proceed with calling Bob's Companion via A2A to finalize the event.

Remember: Use natural language understanding - Alice doesn't need to use specific commands or syntax.
You interpret her intent from conversational messages. Always handle coordination errors gracefully and provide
clear feedback to Alice if coordination fails."""

# Initialize session service with SQLite persistence
session_service = SqliteSessionService(db_path=str(DATABASE_PATH))

# Initialize memory service (non-persistent, in-memory)
memory_service = InMemoryMemoryService()

# Create agent instance
agent = Agent(
    name=AGENT_NAME,
    model=MODEL,
    instruction=SYSTEM_INSTRUCTION,
    description=f"{AGENT_DISPLAY_NAME} - Coordinates plans on Alice's behalf"
)

# Create runner with session and memory services
runner = Runner(
    app_name="companion_network",
    agent=agent,
    session_service=session_service,
    memory_service=memory_service
)


async def _initialize_user_context():
    """Initialize Alice's user context in session state.
    
    Loads Alice's pre-configured context into session state during agent
    initialization. This happens once, not on every message.
    """
    from dataclasses import asdict
    
    # Get or create session
    existing_session = await session_service.get_session(
        app_name="companion_network",
        user_id="alice",
        session_id=SESSION_ID
    )
    
    # Get Alice's context and convert to dict for JSON serialization
    alice_context = get_alice_context()
    context_dict = asdict(alice_context)
    
    # Prepare session state with user context
    if existing_session:
        # Update existing session state
        state = existing_session.state.copy()
        state["user_context"] = context_dict
        await session_service.update_session_state(
            app_name="companion_network",
            user_id="alice",
            session_id=SESSION_ID,
            state=state
        )
    else:
        # Create new session with context
        await session_service.create_session(
            app_name="companion_network",
            user_id="alice",
            session_id=SESSION_ID,
            state={"user_context": context_dict}
        )


# Initialize user context on module import
# Use safer initialization pattern that handles existing event loops
import asyncio

def _safe_initialize_context():
    """Safely initialize user context, handling both sync and async contexts."""
    try:
        # Check if there's already a running event loop
        loop = asyncio.get_running_loop()
        # If we're in an async context, schedule the task
        # Note: This won't block, but context will be initialized before first agent use
        loop.create_task(_initialize_user_context())
    except RuntimeError:
        # No running event loop, safe to use asyncio.run()
        asyncio.run(_initialize_user_context())

_safe_initialize_context()

def run(message: str) -> str:
    """Run the agent with a message and return the response.
    
    This function provides the agent.run() interface required by AC3.
    It wraps runner.run_async() to process messages through the agent.
    Also checks for pending_messages in session state and displays them before the main response.
    
    Args:
        message: User message to send to the agent
        
    Returns:
        Agent response as string (includes pending messages if any, followed by main response)
    """
    import asyncio
    from google.genai import types
    
    async def _run_async():
        # AC5, AC6, AC7: Check for pending_messages in session state before generating response
        session = await session_service.get_session(
            app_name="companion_network",
            user_id="alice",
            session_id=SESSION_ID
        )
        
        pending_messages_text = ""
        if session and "pending_messages" in session.state:
            pending_messages = session.state.get("pending_messages", [])
            
            if pending_messages:
                # AC6: Sort pending_messages by urgency (high → normal → low) for display priority
                urgency_order = {"high": 0, "normal": 1, "low": 2}
                sorted_messages = sorted(
                    pending_messages,
                    key=lambda m: urgency_order.get(m.get("urgency", "normal"), 1)
                )
                
                # AC7: Format each message with sender attribution: "Message from {sender}: {message}"
                formatted_messages = []
                for msg in sorted_messages:
                    sender = msg.get("sender", "Unknown")
                    msg_text = msg.get("message", "")
                    formatted_messages.append(f"Message from {sender.capitalize()}: {msg_text}")
                
                if formatted_messages:
                    pending_messages_text = "\n\n".join(formatted_messages) + "\n\n"
                
                # AC5: Clear pending_messages list from session state after displaying
                state = session.state.copy()
                state["pending_messages"] = []
                await session_service.update_session_state(
                    app_name="companion_network",
                    user_id="alice",
                    session_id=SESSION_ID,
                    state=state
                )
        
        # Generate main agent response
        content = types.Content(role='user', parts=[types.Part(text=message)])
        response_parts = []
        async for event in runner.run_async(
            user_id="alice",
            session_id=SESSION_ID,
            new_message=content
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_parts.append(part.text)
        
        main_response = "".join(response_parts)
        
        # AC5: Append formatted messages to agent response (before main response content)
        if pending_messages_text:
            return pending_messages_text + main_response
        return main_response
    
    return asyncio.run(_run_async())

# MCP Client integration for calling tools on Bob's Companion
# The MCP client is initialized on-demand when coordination is needed
_mcp_client: MCPClient | None = None


def get_mcp_client() -> MCPClient:
    """Get or create MCP client for calling tools on Bob's Companion.
    
    Returns a singleton MCP client instance that connects to Bob's Companion
    endpoint (http://localhost:8002/run) per ADR-003.
    
    Integration Pattern:
    - MCP client is created on-demand (lazy initialization)
    - Client handles connection establishment and error handling
    - Use call_bob_tool() helper for easier tool calling
    
    Returns:
        MCPClient instance configured for Bob's endpoint
    """
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client


async def call_other_companion_tool(tool_name: str, **params) -> dict:
    """Call a tool on another Companion's MCP server with error handling and logging.
    
    This function implements A2A (Agent-to-Agent) communication following the architecture
    error handling pattern. It calls tools on Bob's Companion MCP server using JSON-RPC 2.0
    protocol, handles errors gracefully, and logs events for the network activity monitor.
    
    Integration Pattern (Story 2.8):
    1. Agent identifies coordination need (e.g., "Find time with Bob")
    2. Agent verifies Bob is in trusted_contacts (from Story 2.5)
    3. Agent calls this function: call_other_companion_tool("check_availability", timeframe="...")
    4. MCP client handles HTTP/JSON-RPC 2.0 communication with retry logic
    5. Event is logged to session state for Gradio visualization
    6. Result (or error dict) is returned to agent for processing
    
    Error Handling (AC: 6, 7):
    - Retry logic: MCP client retries once on failure (handled by MCPClient)
    - Graceful degradation: Returns error dict instead of raising exceptions
    - User-friendly messages: Error dicts contain clear messages for Alice
    
    A2A Event Logging (AC: 4, 8):
    - All calls (successful and failed) are logged to session state
    - Events include timestamp, sender, receiver, tool, params (redacted), status
    - Logged to `app:a2a_events` list in Alice's session state
    
    Args:
        tool_name: Name of the tool to call on Bob's MCP server
        **params: Tool parameters as keyword arguments
        
    Returns:
        Dictionary containing tool execution result on success, or error dict on failure.
        Error dict format: {"error": "user-friendly message", "details": "technical details"}
        
    Example:
        result = await call_other_companion_tool(
            "check_availability",
            timeframe="this weekend",
            requester="alice"
        )
        if "error" in result:
            # Handle error gracefully
            print(f"Coordination failed: {result['error']}")
        else:
            # Process successful result
            slots = result.get("slots", [])
    """
    # Get current session for logging
    session = await session_service.get_session(
        app_name="companion_network",
        user_id="alice",
        session_id=SESSION_ID
    )
    
    if not session:
        # If session not available, still try the call but skip logging
        error_result = {
            "error": "Session not available for logging",
            "details": "Cannot log A2A event without session"
        }
        return error_result
    
    # Get MCP client and attempt tool call
    client = get_mcp_client()
    
    try:
        # Call tool on Bob's MCP server (includes retry logic per architecture pattern)
        result = await client.call_tool(tool_name, **params)
        
        # Log successful A2A event
        log_a2a_event(
            session_state=session.state,
            sender="alice",
            receiver="bob",
            tool=tool_name,
            params=params,
            result=result
        )
        
        # Update session state to persist the event log
        await session_service.update_session_state(
            app_name="companion_network",
            user_id="alice",
            session_id=SESSION_ID,
            state=session.state
        )
        
        return result
        
    except ConnectionError as e:
        # Connection error after retry - return graceful error message
        error_result = {
            "error": "Agent temporarily unavailable: Cannot connect to Bob's Companion. Please ensure Bob's Companion is running.",
            "details": str(e)
        }
        
        # Log failed A2A event
        log_a2a_event(
            session_state=session.state,
            sender="alice",
            receiver="bob",
            tool=tool_name,
            params=params,
            result=error_result
        )
        
        # Update session state
        await session_service.update_session_state(
            app_name="companion_network",
            user_id="alice",
            session_id=SESSION_ID,
            state=session.state
        )
        
        return error_result
        
    except ValueError as e:
        # Tool call error (invalid parameters, tool not found, etc.)
        error_result = {
            "error": f"Coordination request failed: {str(e)}",
            "details": str(e)
        }
        
        # Log failed A2A event
        log_a2a_event(
            session_state=session.state,
            sender="alice",
            receiver="bob",
            tool=tool_name,
            params=params,
            result=error_result
        )
        
        # Update session state
        await session_service.update_session_state(
            app_name="companion_network",
            user_id="alice",
            session_id=SESSION_ID,
            state=session.state
        )
        
        return error_result
        
    except Exception as e:
        # Unexpected error - still return graceful message (demo must never crash)
        error_result = {
            "error": "An unexpected error occurred during coordination. Please try again.",
            "details": str(e)
        }
        
        # Log failed A2A event
        log_a2a_event(
            session_state=session.state,
            sender="alice",
            receiver="bob",
            tool=tool_name,
            params=params,
            result=error_result
        )
        
        # Update session state
        await session_service.update_session_state(
            app_name="companion_network",
            user_id="alice",
            session_id=SESSION_ID,
            state=session.state
        )
        
        return error_result


async def call_bob_tool(tool_name: str, **params) -> dict:
    """Helper method to call a tool on Bob's Companion MCP server.
    
    This is a convenience wrapper around call_other_companion_tool() for backward
    compatibility. New code should use call_other_companion_tool() directly.
    
    Args:
        tool_name: Name of the tool to call on Bob's MCP server
        **params: Tool parameters as keyword arguments
        
    Returns:
        Dictionary containing tool execution result or error dict
    """
    return await call_other_companion_tool(tool_name, **params)


async def check_alice_availability(timeframe: str, duration_hours: int = 2) -> list[str]:
    """Check Alice's availability for a given timeframe.
    
    This helper function retrieves Alice's user context from session state and
    uses the shared availability checking logic to identify free time slots.
    
    Integration Pattern:
    1. Agent parses coordination request and extracts timeframe (from Story 2.5)
    2. Agent calls this helper to check Alice's availability
    3. Function retrieves user_context from session state
    4. Function calls shared check_availability() with Alice's context
    5. Returns list of ISO 8601 time range strings for available slots
    
    Args:
        timeframe: Natural language timeframe (e.g., "this weekend") or ISO 8601 range
        duration_hours: Duration of event in hours (default: 2 for dinner)
        
    Returns:
        List of ISO 8601 time range strings (e.g., ["2024-12-07T19:00:00/2024-12-07T21:00:00"])
        Returns empty list if all times are busy
        
    Raises:
        ValueError: If session state is not accessible or user_context is missing
    """
    # Get current session to access user_context
    session = await session_service.get_session(
        app_name="companion_network",
        user_id="alice",
        session_id=SESSION_ID
    )
    
    if not session or "user_context" not in session.state:
        raise ValueError("Alice's user context not found in session state")
    
    user_context = session.state["user_context"]
    
    # Use shared availability checking function
    return check_availability(
        user_context=user_context,
        timeframe=timeframe,
        duration_hours=duration_hours,
        max_slots=5,
        min_slots=3
    )


async def coordinate_mutual_availability(
    timeframe: str,
    other_user_id: str = "bob",
    duration_hours: int = 2
) -> dict:
    """Coordinate mutual availability with another user's Companion.
    
    This function implements the coordination logic flow:
    1. Check Alice's availability for the timeframe
    2. Call Bob's Companion via A2A to check Bob's availability
    3. Find overlapping slots
    4. Prioritize slots by preferences
    5. Synthesize natural language recommendation
    
    Integration Pattern (Story 2.9):
    - Uses Story 2.7: check_alice_availability() for Alice's slots
    - Uses Story 2.8: call_other_companion_tool() to get Bob's availability
    - Uses shared coordination functions for slot intersection and prioritization
    - Returns structured result with recommendation or alternatives
    
    Error Handling:
    - If A2A call fails, returns error dict with graceful message
    - If no overlaps exist, returns alternatives via handle_no_overlaps()
    - All errors are handled gracefully (demo must never crash)
    
    Args:
        timeframe: Natural language timeframe (e.g., "this weekend") or ISO 8601 range
        other_user_id: User ID of the other user (default: "bob")
        duration_hours: Duration of event in hours (default: 2 for dinner)
        
    Returns:
        Dictionary with keys:
        - "success": bool indicating if coordination succeeded
        - "recommendation": Natural language recommendation (if overlaps found)
        - "slots": List of prioritized overlapping slots (ISO 8601 format)
        - "alternatives": Dict with alternatives (if no overlaps)
        - "error": Error message (if coordination failed)
        
    Example:
        result = await coordinate_mutual_availability("this weekend", "bob")
        if result.get("success"):
            print(result["recommendation"])  # "Saturday 7pm, Bob prefers Italian"
        elif "error" in result:
            print(result["error"])  # Graceful error message
        else:
            print(result["alternatives"]["suggestion"])  # Flexibility request
    """
    # Get current session to access user context
    session = await session_service.get_session(
        app_name="companion_network",
        user_id="alice",
        session_id=SESSION_ID
    )
    
    if not session or "user_context" not in session.state:
        return {
            "success": False,
            "error": "Alice's user context not found in session state"
        }
    
    alice_context = session.state["user_context"]
    alice_preferences = alice_context.get("preferences", {})
    
    # Step 1: Check Alice's availability (Story 2.7)
    try:
        alice_slots = await check_alice_availability(timeframe, duration_hours)
    except ValueError as e:
        return {
            "success": False,
            "error": f"Unable to check Alice's availability: {str(e)}"
        }
    
    # Step 2: Call Bob's Companion via A2A to check Bob's availability (Story 2.8)
    bob_result = await call_other_companion_tool(
        "check_availability",
        timeframe=timeframe,
        event_type="dinner",
        duration_minutes=duration_hours * 60,
        requester="alice"
    )
    
    # Handle A2A call errors gracefully
    if "error" in bob_result:
        return {
            "success": False,
            "error": bob_result["error"],
            "alice_slots": alice_slots  # Still provide Alice's availability
        }
    
    # Extract Bob's slots and preferences from A2A response
    bob_slots = bob_result.get("slots", [])
    bob_preferences = bob_result.get("preferences", {})
    
    # Step 3: Find overlapping slots (AC: 1, 7)
    overlapping_slots = find_overlapping_slots(alice_slots, bob_slots)
    
    # Step 4: Handle no overlaps case (AC: 6)
    if not overlapping_slots:
        no_overlap_result = handle_no_overlaps(
            alice_slots,
            bob_slots,
            alice_name="Alice",
            bob_name="Bob"
        )
        return {
            "success": False,
            "has_overlaps": False,
            "alternatives": no_overlap_result,
            "message": no_overlap_result["message"],
            "suggestion": no_overlap_result["suggestion"]
        }
    
    # Step 5: Prioritize slots by preferences (AC: 2, 3, 5)
    prioritized_slots = prioritize_slots_by_preferences(
        overlapping_slots,
        alice_preferences,
        bob_preferences
    )
    
    # Step 6: Synthesize natural language recommendation (AC: 4)
    recommendation = synthesize_recommendation(
        prioritized_slots,
        alice_preferences,
        bob_preferences,
        bob_name="Bob"
    )
    
    return {
        "success": True,
        "recommendation": recommendation,
        "slots": prioritized_slots,
        "alice_preferences": alice_preferences,
        "bob_preferences": bob_preferences
    }


async def create_event_proposal(
    recommendation: dict,
    recipient_user_id: str = "bob",
    proposer_user_id: str = "alice"
) -> dict:
    """Create an EventProposal object from a coordination recommendation and store it in session state.
    
    This function implements event proposal creation following Story 2.10 requirements.
    It extracts proposal details from the recommendation returned by coordinate_mutual_availability(),
    creates an EventProposal dataclass instance, and stores it in session state using
    DatabaseSessionService.
    
    Integration Pattern (Story 2.10):
    - Uses recommendation dict from coordinate_mutual_availability() (Story 2.9)
    - Creates EventProposal using dataclass from shared/models.py (Story 2.1)
    - Stores proposal in session state under key "event_proposal:{event_id}"
    - Sets proposal status to "pending" awaiting user confirmation
    
    Args:
        recommendation: Dictionary from coordinate_mutual_availability() containing:
            - "success": bool
            - "recommendation": Natural language recommendation string
            - "slots": List of prioritized ISO 8601 time range strings
            - "alice_preferences": Alice's preferences dict
            - "bob_preferences": Bob's preferences dict
        recipient_user_id: User ID of the person receiving the proposal (default: "bob")
        proposer_user_id: User ID of the person proposing (default: "alice")
        
    Returns:
        Dictionary with keys:
        - "success": bool indicating if proposal was created successfully
        - "event_proposal": EventProposal dataclass instance (if successful)
        - "event_id": Unique event identifier (if successful)
        - "error": Error message (if creation failed)
        
    Example:
        recommendation = await coordinate_mutual_availability("this weekend", "bob")
        if recommendation.get("success"):
            result = await create_event_proposal(recommendation, "bob", "alice")
            if result.get("success"):
                event_id = result["event_id"]
                proposal = result["event_proposal"]
    """
    # Get current session to access user context and store proposal
    session = await session_service.get_session(
        app_name="companion_network",
        user_id=proposer_user_id,
        session_id=SESSION_ID
    )
    
    if not session or "user_context" not in session.state:
        return {
            "success": False,
            "error": f"{proposer_user_id.capitalize()}'s user context not found in session state"
        }
    
    # Validate trusted contact (AC8): Check if recipient is in proposer's trusted_contacts
    user_context = session.state["user_context"]
    trusted_contacts = user_context.get("trusted_contacts", [])
    
    if recipient_user_id not in trusted_contacts:
        return {
            "success": False,
            "error": f"I can only coordinate with trusted contacts. {recipient_user_id.capitalize()} is not in your trusted contacts list."
        }
    
    # Validate recommendation structure
    if not recommendation.get("success") or not recommendation.get("slots"):
        return {
            "success": False,
            "error": "Invalid recommendation: missing success flag or slots"
        }
    
    # Extract proposal details from recommendation
    slots = recommendation.get("slots", [])
    if not slots:
        return {
            "success": False,
            "error": "No available time slots in recommendation"
        }
    
    # Use the first (best) slot for the proposal
    best_slot = slots[0]
    
    # Parse slot to extract datetime
    if '/' not in best_slot:
        return {
            "success": False,
            "error": f"Invalid slot format: {best_slot}"
        }
    
    try:
        parts = best_slot.split('/')
        if len(parts) != 2:
            return {
                "success": False,
                "error": f"Invalid slot format: {best_slot}"
            }
        
        start_datetime = datetime.fromisoformat(parts[0])
        end_datetime = datetime.fromisoformat(parts[1])
        
        # Calculate duration in hours
        duration_hours = (end_datetime - start_datetime).total_seconds() / 3600
        
        # Extract preferences for context
        alice_preferences = recommendation.get("alice_preferences", {})
        bob_preferences = recommendation.get("bob_preferences", {})
        
        # Generate unique event_id: evt_{timestamp}_{proposer}_{recipient}
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        event_id = f"evt_{timestamp_str}_{proposer_user_id}_{recipient_user_id}"
        
        # Create EventProposal details dict
        proposal_details = {
            "title": "Dinner",
            "time": start_datetime.isoformat(),
            "end_time": end_datetime.isoformat(),
            "duration_hours": duration_hours,
            "location": "",  # Can be filled later if needed
            "participants": [proposer_user_id, recipient_user_id],
            "recommendation_text": recommendation.get("recommendation", ""),
            "alice_preferences": alice_preferences,
            "bob_preferences": bob_preferences
        }
        
        # Create EventProposal dataclass instance
        event_proposal = EventProposal(
            event_id=event_id,
            proposer=proposer_user_id,
            recipient=recipient_user_id,
            status="pending",
            timestamp=datetime.now().isoformat(),
            details=proposal_details
        )
        
        # Store proposal in session state under key "event_proposal:{event_id}"
        state = session.state.copy()
        proposal_key = f"event_proposal:{event_id}"
        # Convert dataclass to dict for JSON serialization
        from dataclasses import asdict
        state[proposal_key] = asdict(event_proposal)
        
        # Update session state
        await session_service.update_session_state(
            app_name="companion_network",
            user_id=proposer_user_id,
            session_id=SESSION_ID,
            state=state
        )
        
        return {
            "success": True,
            "event_proposal": event_proposal,
            "event_id": event_id
        }
        
    except (ValueError, AttributeError) as e:
        return {
            "success": False,
            "error": f"Error parsing slot or creating proposal: {str(e)}"
        }


def format_proposal_message(event_proposal: EventProposal) -> str:
    """Format an EventProposal as a natural language message for the user.
    
    This function creates a conversational, natural language message from an
    EventProposal dataclass. The message includes all required elements per
    Story 2.10 AC1: proposed time, duration, participant, additional context,
    and call to action.
    
    Integration Pattern (Story 2.10):
    - Takes EventProposal dataclass from create_event_proposal()
    - Formats details into human-readable natural language
    - Returns message that can be presented to user via agent response
    - Message is conversational, not JSON dump (AC4)
    
    Args:
        event_proposal: EventProposal dataclass instance with proposal details
        
    Returns:
        Natural language message string formatted for user presentation.
        Includes: time, duration, participant, context, call to action.
        
    Example:
        proposal = EventProposal(...)
        message = format_proposal_message(proposal)
        # Returns: "I found a great time for dinner with Bob: Saturday, December 7th at 7:00pm 
        #           for 2 hours. Bob is in the mood for Italian cuisine. Should I confirm this with Bob?"
    """
    details = event_proposal.details
    
    # Extract time information
    time_str = details.get("time", "")
    if time_str:
        try:
            start_datetime = datetime.fromisoformat(time_str)
            # Format as "Saturday, December 7th at 7:00pm"
            day_name = start_datetime.strftime("%A")  # e.g., "Saturday"
            month_name = start_datetime.strftime("%B")  # e.g., "December"
            day = start_datetime.day
            # Add ordinal suffix (1st, 2nd, 3rd, etc.)
            if 10 <= day % 100 <= 20:
                suffix = "th"
            else:
                suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
            day_str = f"{day}{suffix}"
            
            hour = start_datetime.hour
            minute = start_datetime.minute
            # Format as 12-hour time with am/pm
            if hour == 0:
                time_display = f"12:{minute:02d}am"
            elif hour < 12:
                time_display = f"{hour}:{minute:02d}am"
            elif hour == 12:
                time_display = f"12:{minute:02d}pm"
            else:
                time_display = f"{hour - 12}:{minute:02d}pm"
            
            formatted_time = f"{day_name}, {month_name} {day_str} at {time_display}"
        except (ValueError, AttributeError):
            formatted_time = time_str
    else:
        formatted_time = "a time to be determined"
    
    # Extract duration
    duration_hours = details.get("duration_hours", 2)
    if duration_hours == 1:
        duration_str = "1 hour"
    else:
        duration_str = f"{int(duration_hours)} hours"
    
    # Extract participant name
    participants = details.get("participants", [])
    recipient_id = event_proposal.recipient
    # Capitalize first letter for display
    participant_name = recipient_id.capitalize()
    
    # Extract additional context from preferences
    context_parts = []
    bob_preferences = details.get("bob_preferences", {})
    cuisine_prefs = bob_preferences.get("cuisine", [])
    if cuisine_prefs:
        cuisine_str = ", ".join(cuisine_prefs[:2])  # Limit to 2 cuisines
        context_parts.append(f"{participant_name} is in the mood for {cuisine_str}")
    
    # Build natural language message
    message_parts = [
        f"I found a great time for dinner with {participant_name}: {formatted_time} for {duration_str}."
    ]
    
    # Add context if available
    if context_parts:
        message_parts.append(" ".join(context_parts) + ".")
    
    # Add call to action
    message_parts.append(f"Should I confirm this with {participant_name}?")
    
    return " ".join(message_parts)


async def propose_event_to_user(
    recommendation: dict,
    recipient_user_id: str = "bob",
    proposer_user_id: str = "alice"
) -> dict:
    """Propose an event to the user by creating a proposal and formatting a natural language message.
    
    This helper function integrates event proposal creation with the agent flow. It:
    1. Creates an EventProposal from the coordination recommendation
    2. Formats a natural language message for the user
    3. Returns both the proposal and message for the agent to present
    
    Integration Pattern (Story 2.10):
    - Called after coordinate_mutual_availability() returns a successful recommendation
    - Creates proposal using create_event_proposal()
    - Formats message using format_proposal_message()
    - Agent presents message to user and waits for confirmation
    - Proposal is stored in session state as "pending"
    
    Args:
        recommendation: Dictionary from coordinate_mutual_availability() with recommendation
        recipient_user_id: User ID of the person receiving the proposal (default: "bob")
        proposer_user_id: User ID of the person proposing (default: "alice")
        
    Returns:
        Dictionary with keys:
        - "success": bool indicating if proposal was created successfully
        - "message": Natural language proposal message for user (if successful)
        - "event_proposal": EventProposal instance (if successful)
        - "event_id": Unique event identifier (if successful)
        - "error": Error message (if creation failed)
        
    Example:
        recommendation = await coordinate_mutual_availability("this weekend", "bob")
        if recommendation.get("success"):
            result = await propose_event_to_user(recommendation, "bob", "alice")
            if result.get("success"):
                # Present result["message"] to user
                # Wait for user confirmation
    """
    # Create event proposal
    proposal_result = await create_event_proposal(
        recommendation,
        recipient_user_id,
        proposer_user_id
    )
    
    if not proposal_result.get("success"):
        return proposal_result
    
    # Format natural language message
    event_proposal = proposal_result["event_proposal"]
    message = format_proposal_message(event_proposal)
    
    return {
        "success": True,
        "message": message,
        "event_proposal": event_proposal,
        "event_id": proposal_result["event_id"]
    }


async def handle_user_confirmation(
    user_message: str,
    proposer_user_id: str = "alice"
) -> dict:
    """Check if user's message indicates confirmation of a pending event proposal.
    
    This function parses the user's message for confirmation keywords and retrieves
    the pending EventProposal from session state. If confirmed, it updates the
    proposal status and prepares for A2A communication with the other Companion.
    
    Integration Pattern (Story 2.10):
    - Called after propose_event_to_user() presents proposal to user
    - Checks user's next message for confirmation keywords
    - Retrieves pending EventProposal from session state
    - Updates proposal status based on user response
    - If confirmed, prepares for A2A communication (Story 2.8 pattern)
    
    Confirmation Keywords (AC7):
    - "yes", "confirm", "sounds good", "go ahead", "proceed"
    - Case-insensitive matching
    
    Args:
        user_message: User's message text to check for confirmation
        proposer_user_id: User ID of the person who proposed (default: "alice")
        
    Returns:
        Dictionary with keys:
        - "confirmed": bool indicating if user confirmed
        - "event_proposal": EventProposal instance if found and confirmed
        - "event_id": Event ID if found
        - "message": Status message
        - "error": Error message if proposal not found or other error
        
    Example:
        result = await handle_user_confirmation("yes, that sounds good", "alice")
        if result.get("confirmed"):
            # Proceed with A2A communication to finalize event
    """
    # Confirmation keywords (case-insensitive)
    confirmation_keywords = [
        "yes", "confirm", "sounds good", "go ahead", "proceed",
        "sure", "ok", "okay", "yep", "yeah", "that works", "let's do it"
    ]
    
    # Check if message contains confirmation keyword
    user_message_lower = user_message.lower().strip()
    is_confirmed = any(keyword in user_message_lower for keyword in confirmation_keywords)
    
    # Get current session to retrieve pending proposal
    session = await session_service.get_session(
        app_name="companion_network",
        user_id=proposer_user_id,
        session_id=SESSION_ID
    )
    
    if not session:
        return {
            "confirmed": False,
            "error": "Session not found"
        }
    
    # Find pending EventProposal in session state
    state = session.state
    pending_proposal = None
    pending_event_id = None
    
    # Search for event_proposal keys in session state
    for key, value in state.items():
        if key.startswith("event_proposal:"):
            # Check if this is a pending proposal
            if isinstance(value, dict) and value.get("status") == "pending":
                # Check if this proposal belongs to the current user
                if value.get("proposer") == proposer_user_id:
                    pending_proposal = value
                    pending_event_id = value.get("event_id")
                    break
    
    if not pending_proposal:
        return {
            "confirmed": False,
            "message": "No pending event proposal found. Please coordinate an event first."
        }
    
    # If user confirmed, update proposal status
    if is_confirmed:
        # Update proposal status to "confirmed" (or "accepted" if that's the convention)
        # Note: We'll keep it as "pending" until A2A communication succeeds
        # But we can mark it as "user_confirmed" in a separate field
        updated_proposal = pending_proposal.copy()
        updated_proposal["status"] = "user_confirmed"  # Intermediate status
        
        # Update session state
        proposal_key = f"event_proposal:{pending_event_id}"
        state[proposal_key] = updated_proposal
        
        await session_service.update_session_state(
            app_name="companion_network",
            user_id=proposer_user_id,
            session_id=SESSION_ID,
            state=state
        )
        
        # Reconstruct EventProposal dataclass for return
        from dataclasses import asdict
        event_proposal = EventProposal(**updated_proposal)
        
        return {
            "confirmed": True,
            "event_proposal": event_proposal,
            "event_id": pending_event_id,
            "message": "Event proposal confirmed. Ready to finalize with the other party."
        }
    else:
        return {
            "confirmed": False,
            "message": "Event proposal not confirmed. Please respond with 'yes', 'confirm', or similar to proceed."
        }


async def finalize_event_with_other_companion(
    event_proposal: EventProposal,
    proposer_user_id: str = "alice"
) -> dict:
    """Finalize event by calling the other Companion's propose_event MCP tool via A2A.
    
    After the user confirms an event proposal, this function calls the other Companion's
    propose_event MCP tool to finalize the event. This implements Story 2.10 AC9: A2A
    communication initiation after user confirmation.
    
    Integration Pattern (Story 2.10):
    - Called after handle_user_confirmation() returns confirmed=True
    - Uses call_other_companion_tool() from Story 2.8 to call Bob's propose_event tool
    - Passes event details (event_name, datetime, location, participants, requester)
    - Handles A2A call response (accepted, declined, pending)
    - Updates EventProposal status based on Bob's response
    - Logs A2A call using shared/a2a_logging.py from Story 2.8
    
    Args:
        event_proposal: EventProposal dataclass instance that was confirmed by user
        proposer_user_id: User ID of the person who proposed (default: "alice")
        
    Returns:
        Dictionary with keys:
        - "success": bool indicating if A2A call succeeded
        - "status": Event status from other Companion ("accepted", "declined", "pending")
        - "message": Response message from other Companion
        - "event_id": Event ID if accepted/pending
        - "error": Error message if A2A call failed
        
    Example:
        confirmation = await handle_user_confirmation("yes", "alice")
        if confirmation.get("confirmed"):
            result = await finalize_event_with_other_companion(confirmation["event_proposal"], "alice")
            if result.get("success"):
                # Event finalized, inform user of result
    """
    details = event_proposal.details
    recipient_user_id = event_proposal.recipient
    
    # Extract event details for MCP tool call
    event_name = details.get("title", "Dinner")
    datetime_str = details.get("time", "")
    location = details.get("location", "")
    participants = details.get("participants", [])
    
    # Call Bob's propose_event MCP tool via A2A
    a2a_result = await call_other_companion_tool(
        "propose_event",
        event_name=event_name,
        datetime=datetime_str,
        location=location,
        participants=participants,
        requester=proposer_user_id
    )
    
    # Handle A2A call errors
    if "error" in a2a_result:
        return {
            "success": False,
            "error": a2a_result["error"]
        }
    
    # Extract response from Bob's Companion
    event_status = a2a_result.get("status", "pending")
    response_message = a2a_result.get("message", "")
    response_event_id = a2a_result.get("event_id", event_proposal.event_id)
    
    # Update EventProposal status based on Bob's response
    session = await session_service.get_session(
        app_name="companion_network",
        user_id=proposer_user_id,
        session_id=SESSION_ID
    )
    
    if session:
        state = session.state.copy()
        proposal_key = f"event_proposal:{event_proposal.event_id}"
        
        if proposal_key in state:
            # Update proposal status
            updated_proposal = state[proposal_key].copy()
            updated_proposal["status"] = event_status
            state[proposal_key] = updated_proposal
            
            # Update session state
            await session_service.update_session_state(
                app_name="companion_network",
                user_id=proposer_user_id,
                session_id=SESSION_ID,
                state=state
            )
    
    return {
        "success": True,
        "status": event_status,
        "message": response_message,
        "event_id": response_event_id
    }


# For AC3: "agent.run() method is available" - use run() function
# Note: Agent is a Pydantic model, so we use a module-level function
# Usage: from alice_companion.agent import agent, run; response = run("Hello")


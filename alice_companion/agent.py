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

7. **Acknowledge Naturally**: Respond with natural language acknowledgment that shows understanding:
   - Example: "I'll check your availability for this weekend and coordinate with Bob's Companion to find a time for dinner..."
   - Use conversational tone, not JSON or structured formats

8. **Identify Contact Need**: Determine which Companion agent you need to contact for coordination
   (e.g., if Alice mentions "Bob", you'll need to contact Bob's Companion).

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
    
    Args:
        message: User message to send to the agent
        
    Returns:
        Agent response as string
    """
    import asyncio
    from google.genai import types
    
    async def _run_async():
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
        return "".join(response_parts)
    
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


# For AC3: "agent.run() method is available" - use run() function
# Note: Agent is a Pydantic model, so we use a module-level function
# Usage: from alice_companion.agent import agent, run; response = run("Hello")


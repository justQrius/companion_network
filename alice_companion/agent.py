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

# Configuration constants
AGENT_NAME = "alices_companion"  # Valid identifier (spaces/special chars not allowed)
AGENT_DISPLAY_NAME = "Alice's Companion"  # Display name for user-facing contexts
MODEL = "gemini-2.5-pro"
SESSION_ID = "alice_session"
DATABASE_PATH = Path(__file__).parent.parent / "companion_sessions.db"

# System instruction emphasizing coordination, privacy, and natural conversation
# Enhanced with natural language coordination request parsing (Story 2.5)
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

4. **Acknowledge Naturally**: Respond with natural language acknowledgment that shows understanding:
   - Example: "I'll coordinate with Bob's Companion to find a time for dinner this weekend..."
   - Use conversational tone, not JSON or structured formats

5. **Identify Contact Need**: Determine which Companion agent you need to contact for coordination
   (e.g., if Alice mentions "Bob", you'll need to contact Bob's Companion).

Remember: Use natural language understanding - Alice doesn't need to use specific commands or syntax.
You interpret her intent from conversational messages."""

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


async def call_bob_tool(tool_name: str, **params) -> dict:
    """Helper method to call a tool on Bob's Companion MCP server.
    
    This is the primary interface for Alice's agent to interact with Bob's Companion.
    The agent can use this when it identifies coordination intent (from Story 2.5)
    and needs to call tools on Bob's MCP server.
    
    Integration Pattern:
    1. Agent identifies coordination need (e.g., "Find time with Bob")
    2. Agent verifies Bob is in trusted_contacts (from Story 2.5)
    3. Agent calls this helper: call_bob_tool("check_availability", timeframe="...")
    4. MCP client handles HTTP/JSON-RPC 2.0 communication
    5. Result is returned to agent for processing
    
    Args:
        tool_name: Name of the tool to call on Bob's MCP server
        **params: Tool parameters as keyword arguments
        
    Returns:
        Dictionary containing tool execution result
        
    Raises:
        ConnectionError: If Bob's Companion is unreachable
        ValueError: If tool call fails
    """
    client = get_mcp_client()
    return await client.call_tool(tool_name, **params)


# For AC3: "agent.run() method is available" - use run() function
# Note: Agent is a Pydantic model, so we use a module-level function
# Usage: from alice_companion.agent import agent, run; response = run("Hello")


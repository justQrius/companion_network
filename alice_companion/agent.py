"""Alice's Companion Agent using Google ADK.

This module initializes Alice's Companion agent with persistent session storage
and in-memory long-term memory, configured for coordination tasks.
"""

from pathlib import Path
from google.adk import Agent, Runner
from alice_companion.sqlite_session_service import SqliteSessionService
from google.adk.memory import InMemoryMemoryService

# Configuration constants
AGENT_NAME = "alices_companion"  # Valid identifier (spaces/special chars not allowed)
AGENT_DISPLAY_NAME = "Alice's Companion"  # Display name for user-facing contexts
MODEL = "gemini-2.5-pro"
SESSION_ID = "alice_session"
DATABASE_PATH = Path(__file__).parent.parent / "companion_sessions.db"

# System instruction emphasizing coordination, privacy, and natural conversation
SYSTEM_INSTRUCTION = """You are Alice's personal Companion agent. You coordinate plans on Alice's behalf, 
maintaining her privacy while facilitating natural conversations with other companions. 
You help schedule events, share availability, and propose activities while respecting 
Alice's preferences and trusted contact list."""

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

# For AC3: "agent.run() method is available" - use run() function
# Note: Agent is a Pydantic model, so we use a module-level function
# Usage: from alice_companion.agent import agent, run; response = run("Hello")


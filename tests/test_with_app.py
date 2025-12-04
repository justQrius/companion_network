"""Test using App pattern instead of direct Agent."""
import asyncio
import sys
import io
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.adk import Agent, Runner
from google.adk.apps import App
from google.adk.sessions import InMemorySessionService
from google.genai import types

def get_weather(city: str) -> str:
    """Get weather."""
    return f"Weather in {city}: Sunny, 72F"

# Create agent
test_agent = Agent(
    name="weather_bot",
    model="gemini-2.5-pro",
    instruction="Use get_weather tool when asked about weather.",
    tools=[get_weather]
)

# Wrap in App (this might fix the path issue)
app = App(
    name="test_weather_app",
    root_agent=test_agent
)

# Create runner with App
session_service = InMemorySessionService()
runner = Runner(
    app=app,  # Use app instead of agent
    session_service=session_service
)

async def test():
    print("\nTesting with App pattern...\n")

    # Create session first
    session = await session_service.create_session(
        app_name="test_weather_app",
        user_id="user1",
        session_id="session1"
    )
    print(f"Session created: {session.id}")

    message = "What's the weather in Tokyo?"
    print(f"User: {message}\n")

    content = types.Content(role='user', parts=[types.Part(text=message)])

    tool_called = False
    response_text = ""

    async for event in runner.run_async(
        user_id="user1",
        session_id=session.id,
        new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text
                if hasattr(part, 'function_call') and part.function_call:
                    print(f"TOOL CALLED: {part.function_call.name}")
                    tool_called = True

    print(f"\nAgent: {response_text}\n")

    if tool_called:
        print("SUCCESS: Tools working!")
    else:
        print("FAIL: No tools called")

try:
    asyncio.run(test())
except Exception as e:
    print(f"ERROR: {e}")

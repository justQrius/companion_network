"""
Companion Network - Gradio UI Orchestrator

Main application entry point for the Companion Network demo.
Implements split-screen layout with Alice and Bob's chat interfaces
and Network Activity Monitor.

This module serves as the Gradio Orchestrator, providing:
- Split-screen UI layout (Alice panel, Bob panel, Network monitor)
- Event routing for user interactions
- Agent initialization and chat interface handlers (Story 4.2)
"""

import gradio as gr
from typing import List, Tuple, Dict, Any
import logging
import json
from datetime import datetime
import threading
import time
import httpx
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import agent modules
from alice_companion import agent as alice_agent_module
from bob_companion import agent as bob_agent_module
from alice_companion.user_context import get_alice_context
from bob_companion.user_context import get_bob_context
from alice_companion.http_endpoint import run_server as start_alice_mcp_server
from bob_companion.http_endpoint import run_server as start_bob_mcp_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Module-level agent references (loaded in load_agent_references())
alice_agent = None
bob_agent = None

# Access to async runners for proper async/await pattern
alice_runner = None
bob_runner = None

# MCP server threads (for background execution)
alice_mcp_thread = None
bob_mcp_thread = None

# Module-level chat history (persists during session)
alice_chat_history: List[Tuple[str, str]] = []
bob_chat_history: List[Tuple[str, str]] = []

# Custom CSS for clean minimal styling
CUSTOM_CSS = """
/* Remove default container borders */
.gradio-container {
    border: none !important;
}

/* Enhance typography for readability */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    font-size: 14px;
    line-height: 1.6;
}

/* Clean minimal chat interface */
.chat-container {
    border-radius: 8px;
    padding: 1rem;
}

/* Panel labels styling */
.panel-label {
    font-weight: 600;
    font-size: 16px;
    margin-bottom: 0.5rem;
    color: #111827;
}
"""


def initialize_agents() -> Tuple[Any, Any]:
    """
    Initialize both Alice and Bob's Companion agents with proper configuration.
    
    This function ensures agents are initialized with:
    - Session IDs (alice_session, bob_session)
    - User contexts loaded from user_context.py files
    - Model: Gemini 2.5 Pro
    - SessionService: DatabaseSessionService with SQLite
    - MemoryService: InMemoryMemoryService
    
    Agents are already initialized on module import, but this function verifies
    they are ready and returns references for use by event handlers.
    
    Returns:
        Tuple of (alice_agent, bob_agent) module references
        
    Raises:
        Exception: If agent initialization fails
    """
    global alice_agent, bob_agent, alice_runner, bob_runner
    
    try:
        # Load user contexts (for validation, though agents already load them on import)
        alice_context = get_alice_context()
        bob_context = get_bob_context()
        
        # Store agent module references
        # Note: Agent initialization (with session IDs and user contexts) happens
        # in agent modules on import via _safe_initialize_context()
        alice_agent = alice_agent_module
        bob_agent = bob_agent_module
        
        # Access runners for proper async/await pattern (avoid nested event loops)
        alice_runner = alice_agent_module.runner
        bob_runner = bob_agent_module.runner
        
        # Verify agents are properly configured
        if not alice_runner or not bob_runner:
            raise ValueError("Agent runners not initialized")
        
        logger.info("✅ Alice agent initialized (session ID: alice_session, model: gemini-2.5-pro)")
        logger.info("✅ Bob agent initialized (session ID: bob_session, model: gemini-2.5-pro)")
        logger.info("✅ Both agents initialized successfully")
        
        return alice_agent, bob_agent
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize agents: {e}", exc_info=True)
        raise


def load_agent_references() -> None:
    """
    Load references to Alice and Bob Companion agent modules.
    
    This is a compatibility wrapper around initialize_agents() for backward
    compatibility with existing code.
    """
    initialize_agents()


async def _run_alice_agent_async(message: str) -> str:
    """
    Run Alice's agent asynchronously using runner.run_async().
    
    This function properly awaits async operations without creating nested event loops.
    It replicates the logic from agent.run() but uses await instead of asyncio.run().
    
    Args:
        message: User message to send to the agent
        
    Returns:
        Agent response as string
    """
    from google.genai import types
    
    # Check for pending_messages in session state
    session = await alice_runner.session_service.get_session(
        app_name="companion_network",
        user_id="alice",
        session_id="alice_session"
    )
    
    pending_messages_text = ""
    if session and "pending_messages" in session.state:
        pending_messages = session.state.get("pending_messages", [])
        
        if pending_messages:
            # Sort by urgency (high → normal → low)
            urgency_order = {"high": 0, "normal": 1, "low": 2}
            sorted_messages = sorted(
                pending_messages,
                key=lambda m: urgency_order.get(m.get("urgency", "normal"), 1)
            )
            
            # Format with sender attribution
            formatted_messages = []
            for msg in sorted_messages:
                sender = msg.get("sender", "Unknown")
                msg_text = msg.get("message", "")
                formatted_messages.append(f"Message from {sender.capitalize()}: {msg_text}")
            
            if formatted_messages:
                pending_messages_text = "\n\n".join(formatted_messages) + "\n\n"
            
            # Clear pending_messages from session state
            state = session.state.copy()
            state["pending_messages"] = []
            await alice_runner.session_service.update_session_state(
                app_name="companion_network",
                user_id="alice",
                session_id="alice_session",
                state=state
            )
    
    # Generate main agent response
    content = types.Content(role='user', parts=[types.Part(text=message)])
    response_parts = []
    async for event in alice_runner.run_async(
        user_id="alice",
        session_id="alice_session",
        new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_parts.append(part.text)
    
    main_response = "".join(response_parts)
    
    # Append formatted messages to agent response (before main response content)
    if pending_messages_text:
        return pending_messages_text + main_response
    return main_response


async def _run_bob_agent_async(message: str) -> str:
    """
    Run Bob's agent asynchronously using runner.run_async().
    
    This function properly awaits async operations without creating nested event loops.
    It replicates the logic from agent.run() but uses await instead of asyncio.run().
    
    Args:
        message: User message to send to the agent
        
    Returns:
        Agent response as string
    """
    from google.genai import types
    
    # Check for pending_messages in session state
    session = await bob_runner.session_service.get_session(
        app_name="companion_network",
        user_id="bob",
        session_id="bob_session"
    )
    
    pending_messages_text = ""
    if session and "pending_messages" in session.state:
        pending_messages = session.state.get("pending_messages", [])
        
        if pending_messages:
            # Sort by urgency (high → normal → low)
            urgency_order = {"high": 0, "normal": 1, "low": 2}
            sorted_messages = sorted(
                pending_messages,
                key=lambda m: urgency_order.get(m.get("urgency", "normal"), 1)
            )
            
            # Format with sender attribution
            formatted_messages = []
            for msg in sorted_messages:
                sender = msg.get("sender", "Unknown")
                msg_text = msg.get("message", "")
                formatted_messages.append(f"Message from {sender.capitalize()}: {msg_text}")
            
            if formatted_messages:
                pending_messages_text = "\n\n".join(formatted_messages) + "\n\n"
            
            # Clear pending_messages from session state
            state = session.state.copy()
            state["pending_messages"] = []
            await bob_runner.session_service.update_session_state(
                app_name="companion_network",
                user_id="bob",
                session_id="bob_session",
                state=state
            )
    
    # Generate main agent response
    content = types.Content(role='user', parts=[types.Part(text=message)])
    response_parts = []
    async for event in bob_runner.run_async(
        user_id="bob",
        session_id="bob_session",
        new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_parts.append(part.text)
    
    main_response = "".join(response_parts)
    
    # Append formatted messages to agent response (before main response content)
    if pending_messages_text:
        return pending_messages_text + main_response
    return main_response


async def handle_alice_input(message: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
    """
    Async event handler for Alice's chat input.
    
    Immediately appends user message to chat history for instant UI feedback,
    shows "thinking..." indicator, then calls agent asynchronously to get response.
    Appends agent response to history and returns updated history with cleared input.
    
    Args:
        message: User message string from input textbox
        history: Current chat history (List[Tuple[str, str]] format)
        
    Returns:
        Tuple of (updated_history, empty_string):
        - updated_history: Chat history with user message and agent response
        - empty_string: Clears input textbox
    """
    global alice_chat_history
    
    # AC1: Immediately append user message to chat history (instant UI feedback)
    if message.strip():
        # Update both local history and module-level history
        alice_chat_history = history.copy() if history else []
        
        # AC2: Show explicit "thinking..." indicator
        alice_chat_history.append((message, "thinking..."))
        
        try:
            # AC3, AC4: Call agent asynchronously and wait for response
            # Use proper async/await pattern (no nested event loops)
            agent_response = await _run_alice_agent_async(message)
            
            # AC3: Append agent response to chat history
            # Update the last entry (replace "thinking..." with actual response)
            alice_chat_history[-1] = (message, agent_response)
            
            # AC7: Chat history persists (stored in module-level variable)
            # AC6: Async handler prevents UI blocking
            
            # AC4: Return updated history (Gradio automatically updates UI)
            return alice_chat_history, ""
            
        except Exception as e:
            # Error handling: Display user-friendly error message in chat
            error_message = "I encountered an error processing your message. Please try again."
            logger.error(f"Error in handle_alice_input: {e}", exc_info=True)
            
            # Update history with error message (replace "thinking..." with error)
            alice_chat_history[-1] = (message, error_message)
            return alice_chat_history, ""
    
    # Empty message, return unchanged
    return history, ""


async def handle_bob_input(message: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
    """
    Async event handler for Bob's chat input.
    
    Immediately appends user message to chat history for instant UI feedback,
    shows "thinking..." indicator, then calls agent asynchronously to get response.
    Appends agent response to history and returns updated history with cleared input.
    
    Args:
        message: User message string from input textbox
        history: Current chat history (List[Tuple[str, str]] format)
        
    Returns:
        Tuple of (updated_history, empty_string):
        - updated_history: Chat history with user message and agent response
        - empty_string: Clears input textbox
    """
    global bob_chat_history
    
    # AC1: Immediately append user message to chat history (instant UI feedback)
    if message.strip():
        # Update both local history and module-level history
        bob_chat_history = history.copy() if history else []
        
        # AC2: Show explicit "thinking..." indicator
        bob_chat_history.append((message, "thinking..."))
        
        try:
            # AC3, AC4: Call agent asynchronously and wait for response
            # Use proper async/await pattern (no nested event loops)
            agent_response = await _run_bob_agent_async(message)
            
            # AC3: Append agent response to chat history
            # Update the last entry (replace "thinking..." with actual response)
            bob_chat_history[-1] = (message, agent_response)
            
            # AC7: Chat history persists (stored in module-level variable)
            # AC6: Async handler prevents UI blocking
            
            # AC4: Return updated history (Gradio automatically updates UI)
            return bob_chat_history, ""
            
        except Exception as e:
            # Error handling: Display user-friendly error message in chat
            error_message = "I encountered an error processing your message. Please try again."
            logger.error(f"Error in handle_bob_input: {e}", exc_info=True)
            
            # Update history with error message (replace "thinking..." with error)
            bob_chat_history[-1] = (message, error_message)
            return bob_chat_history, ""
    
    # Empty message, return unchanged
    return history, ""


async def update_network_monitor() -> Dict[str, Any]:
    """
    Update the Network Activity Monitor with A2A events from both agents.
    
    Reads A2A events from both Alice's and Bob's session states, merges them
    chronologically, and formats them for display in the Gradio JSON component.
    
    Integration Pattern (Story 4.3):
    - Reads from `app:a2a_events` list in both Alice's and Bob's session states
    - Events are logged by Story 2.8's A2A communication layer
    - Formats events chronologically (oldest to newest)
    - Returns formatted JSON for Gradio display
    
    Returns:
        Dictionary containing formatted events for JSON display, or empty state message.
        Format: {"events": [...], "count": N, "last_updated": "timestamp"}
    """
    try:
        # Get both sessions to read A2A events
        alice_session = await alice_runner.session_service.get_session(
            app_name="companion_network",
            user_id="alice",
            session_id="alice_session"
        )
        
        bob_session = await bob_runner.session_service.get_session(
            app_name="companion_network",
            user_id="bob",
            session_id="bob_session"
        )
        
        # Collect events from both sessions
        all_events = []
        
        if alice_session and "app:a2a_events" in alice_session.state:
            alice_events = alice_session.state.get("app:a2a_events", [])
            all_events.extend(alice_events)
        
        if bob_session and "app:a2a_events" in bob_session.state:
            bob_events = bob_session.state.get("app:a2a_events", [])
            all_events.extend(bob_events)
        
        # Handle empty events list
        if not all_events:
            return {
                "message": "No A2A events yet",
                "events": [],
                "count": 0,
                "last_updated": datetime.now().isoformat()
            }
        
        # Sort events chronologically (oldest to newest) by timestamp
        sorted_events = sorted(
            all_events,
            key=lambda e: e.get("timestamp", ""),
            reverse=False  # Oldest first
        )
        
        # Format events for display (ensure all required fields are present)
        # Format sender/receiver names to match story requirements: "Alice's Companion", "Bob's Companion"
        def format_agent_name(name: str) -> str:
            """Format agent identifier to display name."""
            if name.lower() == "alice":
                return "Alice's Companion"
            elif name.lower() == "bob":
                return "Bob's Companion"
            else:
                return name  # Fallback for unknown names
        
        def format_timestamp(iso_timestamp: str) -> str:
            """Format ISO 8601 timestamp to human-readable format."""
            try:
                # Handle ISO format with or without timezone
                timestamp_str = iso_timestamp.replace('Z', '+00:00') if 'Z' in iso_timestamp else iso_timestamp
                dt = datetime.fromisoformat(timestamp_str)
                # Remove timezone info for formatting if present
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, AttributeError, TypeError):
                return iso_timestamp  # Return original if parsing fails
        
        def format_status(status: str) -> Dict[str, Any]:
            """Format status with visual distinction indicators."""
            status_lower = status.lower() if status else "unknown"
            if status_lower == "success":
                return {
                    "status": "success",
                    "icon": "✅",
                    "color": "green"
                }
            elif status_lower == "failed":
                return {
                    "status": "failed",
                    "icon": "❌",
                    "color": "red"
                }
            else:
                return {
                    "status": status,
                    "icon": "⚠️",
                    "color": "orange"
                }
        
        formatted_events = []
        for event in sorted_events:
            # Validate event structure (handle malformed events gracefully)
            if not isinstance(event, dict):
                logger.warning(f"Skipping malformed event (not a dict): {event}")
                continue
            
            sender = event.get("sender", "unknown")
            receiver = event.get("receiver", "unknown")
            timestamp = event.get("timestamp", "")
            tool = event.get("tool", "unknown")
            params = event.get("params", {})
            status = event.get("status", "unknown")
            
            # Validate required fields
            if not timestamp or not tool:
                logger.warning(f"Skipping event with missing required fields: {event}")
                continue
            
            formatted_event = {
                "timestamp": format_timestamp(timestamp),
                "timestamp_iso": timestamp,  # Keep ISO format for sorting
                "sender": format_agent_name(sender),
                "receiver": format_agent_name(receiver),
                "tool": tool,
                "params": params if isinstance(params, dict) else {},
                "status_info": format_status(status)
            }
            formatted_events.append(formatted_event)
        
        # Handle very long event lists: limit to most recent 100 events for performance
        # JSON component will handle scrolling automatically
        max_events = 100
        if len(formatted_events) > max_events:
            formatted_events = formatted_events[-max_events:]  # Keep most recent events
            logger.info(f"Network monitor: Limited display to {max_events} most recent events (total: {len(sorted_events)})")
        
        # Visual activity indicator: Check if there are recent events (within last 2 seconds)
        # This provides visual feedback that A2A communication is active
        now = datetime.now()
        recent_events = []
        for event in sorted_events:
            try:
                timestamp_str = event.get("timestamp", "")
                if not timestamp_str:
                    continue
                # Handle ISO format with or without timezone
                timestamp_str = timestamp_str.replace('Z', '+00:00') if 'Z' in timestamp_str else timestamp_str
                event_time = datetime.fromisoformat(timestamp_str)
                # Remove timezone info for comparison
                if event_time.tzinfo is not None:
                    event_time = event_time.replace(tzinfo=None)
                time_diff = (now - event_time).total_seconds()
                if 0 <= time_diff <= 2.0:  # Events within last 2 seconds
                    recent_events.append(event)
            except (ValueError, AttributeError, TypeError):
                continue
        
        activity_status = "🟢 Active" if recent_events else "⚪ Idle"
        
        # Return formatted data for JSON component
        return {
            "events": formatted_events,
            "count": len(formatted_events),
            "total_count": len(sorted_events),  # Total events (may be more than displayed)
            "last_updated": datetime.now().isoformat(),
            "activity_status": activity_status,
            "recent_activity": len(recent_events) > 0,
            "message": f"Showing {len(formatted_events)} of {len(sorted_events)} events" if len(formatted_events) < len(sorted_events) else f"{len(formatted_events)} events"
        }
        
    except Exception as e:
        logger.error(f"Error updating network monitor: {e}", exc_info=True)
        return {
            "error": "Failed to load network events",
            "details": str(e),
            "events": [],
            "count": 0,
            "last_updated": datetime.now().isoformat()
        }


def create_layout():
    """
    Create the split-screen Gradio layout structure.
    
    Layout:
    - Top Row: Two columns (Alice left, Bob right)
    - Bottom Row: Network Activity Monitor
    
    Returns:
        gr.Blocks: Configured Gradio Blocks interface
    """
    with gr.Blocks() as app:
        # Inject custom CSS using gr.HTML (works in all Gradio versions)
        gr.HTML(f"<style>{CUSTOM_CSS}</style>", visible=False)
        
        # App title
        gr.Markdown("# 🤝 Companion Network - A2A Coordination Demo")
        gr.Markdown("*Watch Alice and Bob's Companions coordinate autonomously*")
        
        # Top Row: Split-screen chat interfaces
        # Using min_width for desktop-first responsive design (~1200px minimum per AC5)
        with gr.Row():
            # Left Column: Alice's Companion
            with gr.Column(scale=1, min_width=500):
                gr.Markdown("### 👩 Alice's Companion", elem_classes=["panel-label"])
                
                # Chat history display (conversational format)
                alice_chatbot = gr.Chatbot(
                    label="Chat History",
                    height=400,
                    show_label=False
                )
                
                # Input and submit
                with gr.Row():
                    alice_input = gr.Textbox(
                        placeholder="Type your message to Alice's Companion...",
                        label="Message",
                        show_label=False,
                        scale=4
                    )
                    alice_submit = gr.Button("Send", variant="primary", scale=1)
                
                # AC1, AC4, AC6: Connect event handlers to Gradio components
                # Button click handler
                alice_submit.click(
                    handle_alice_input,
                    inputs=[alice_input, alice_chatbot],
                    outputs=[alice_chatbot, alice_input]
                )
                # Enter key handler (submit on Enter)
                alice_input.submit(
                    handle_alice_input,
                    inputs=[alice_input, alice_chatbot],
                    outputs=[alice_chatbot, alice_input]
                )
            
            # Right Column: Bob's Companion
            with gr.Column(scale=1, min_width=500):
                gr.Markdown("### 👨 Bob's Companion", elem_classes=["panel-label"])
                
                # Chat history display (conversational format)
                bob_chatbot = gr.Chatbot(
                    label="Chat History",
                    height=400,
                    show_label=False
                )
                
                # Input and submit
                with gr.Row():
                    bob_input = gr.Textbox(
                        placeholder="Type your message to Bob's Companion...",
                        label="Message",
                        show_label=False,
                        scale=4
                    )
                    bob_submit = gr.Button("Send", variant="primary", scale=1)
                
                # AC1, AC4, AC6: Connect event handlers to Gradio components
                # Button click handler
                bob_submit.click(
                    handle_bob_input,
                    inputs=[bob_input, bob_chatbot],
                    outputs=[bob_chatbot, bob_input]
                )
                # Enter key handler (submit on Enter)
                bob_input.submit(
                    handle_bob_input,
                    inputs=[bob_input, bob_chatbot],
                    outputs=[bob_chatbot, bob_input]
                )
        
        # Bottom Row: Network Activity Monitor
        with gr.Row():
            with gr.Column(min_width=1200):
                gr.Markdown("### 🔗 Network Activity Monitor", elem_classes=["panel-label"])
                network_monitor = gr.JSON(
                    label="A2A Communication Log",
                    value={"message": "No A2A events yet", "events": [], "count": 0},
                    show_label=False
                )
                # Real-time updates: poll every 500ms (per NFR: updates within 500ms of A2A call completion)
                app.load(
                    fn=update_network_monitor,
                    outputs=network_monitor,
                    every=0.5  # 500ms polling interval
                )
    
    return app


def start_mcp_servers() -> None:
    """
    Start both Alice and Bob's MCP servers in background threads.
    
    Starts MCP servers on:
    - localhost:8001 (Alice)
    - localhost:8002 (Bob)
    
    Servers run in background threads so they don't block Gradio UI launch.
    All 4 coordination tools are registered: check_availability, propose_event,
    share_context, relay_message.
    
    Raises:
        Exception: If MCP server startup fails
    """
    global alice_mcp_thread, bob_mcp_thread
    import uvicorn
    from alice_companion.http_endpoint import app as alice_app
    from bob_companion.http_endpoint import app as bob_app
    
    def run_alice_server():
        """Run Alice's MCP server in background thread."""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            config = uvicorn.Config(
                alice_app,
                host="localhost",
                port=8001,
                log_level="info"
            )
            server = uvicorn.Server(config)
            loop.run_until_complete(server.serve())
        except Exception as e:
            logger.error(f"❌ Alice MCP server failed: {e}", exc_info=True)
    
    def run_bob_server():
        """Run Bob's MCP server in background thread."""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            config = uvicorn.Config(
                bob_app,
                host="localhost",
                port=8002,
                log_level="info"
            )
            server = uvicorn.Server(config)
            loop.run_until_complete(server.serve())
        except Exception as e:
            logger.error(f"❌ Bob MCP server failed: {e}", exc_info=True)
    
    try:
        # Start Alice's MCP server in background thread
        alice_mcp_thread = threading.Thread(
            target=run_alice_server,
            daemon=True,
            name="AliceMCPServer"
        )
        alice_mcp_thread.start()
        
        # Start Bob's MCP server in background thread
        bob_mcp_thread = threading.Thread(
            target=run_bob_server,
            daemon=True,
            name="BobMCPServer"
        )
        bob_mcp_thread.start()
        
        # Give servers a moment to start
        time.sleep(2)
        
        logger.info("✅ Alice MCP server started on localhost:8001")
        logger.info("✅ Bob MCP server started on localhost:8002")
        logger.info("✅ Both MCP servers started successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to start MCP servers: {e}", exc_info=True)
        raise


def verify_a2a_endpoints() -> None:
    """
    Verify A2A endpoints are accessible before launching Gradio UI.
    
    Checks that both endpoints respond to HTTP requests:
    - http://localhost:8001/run (Alice)
    - http://localhost:8002/run (Bob)
    
    Note: These are POST-only endpoints, so we expect 405 Method Not Allowed
    for GET requests, which confirms the server is running.
    
    Raises:
        Exception: If endpoints are not accessible
    """
    endpoints = [
        ("Alice", "http://localhost:8001/run"),
        ("Bob", "http://localhost:8002/run")
    ]
    
    for name, url in endpoints:
        max_retries = 5
        retry_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                # Try a GET request to verify endpoint is accessible
                # POST-only endpoints will return 405, which confirms server is running
                response = httpx.get(url, timeout=2.0)
                # Any response (including 405) means server is running
                if response.status_code == 405:
                    logger.info(f"✅ {name} A2A endpoint accessible at {url} (POST-only endpoint)")
                    break
                else:
                    logger.info(f"✅ {name} A2A endpoint accessible at {url} (status: {response.status_code})")
                    break
            except httpx.ConnectError:
                # Server not ready yet, wait and retry
                if attempt < max_retries - 1:
                    logger.debug(f"⏳ {name} endpoint not ready (attempt {attempt + 1}/{max_retries}), waiting...")
                    time.sleep(retry_delay)
                else:
                    raise Exception(f"❌ {name} A2A endpoint not accessible at {url} after {max_retries} attempts")
            except Exception as e:
                # For POST-only endpoints, 405 is expected
                if "405" in str(e) or "Method Not Allowed" in str(e) or hasattr(e, 'response') and e.response.status_code == 405:
                    logger.info(f"✅ {name} A2A endpoint accessible at {url} (POST-only endpoint)")
                    break
                else:
                    if attempt < max_retries - 1:
                        logger.debug(f"⏳ {name} endpoint error (attempt {attempt + 1}/{max_retries}): {e}, retrying...")
                        time.sleep(retry_delay)
                    else:
                        raise Exception(f"❌ {name} A2A endpoint verification failed: {e}")


def startup_sequence() -> None:
    """
    Orchestrate complete startup sequence for Companion Network demo.
    
    Executes initialization steps in correct order:
    1. Load environment variables (.env file)
    2. Initialize Alice agent (with user context, session ID)
    3. Initialize Bob agent (with user context, session ID)
    4. Start Alice MCP server (localhost:8001)
    5. Start Bob MCP server (localhost:8002)
    6. Verify A2A endpoints are accessible
    7. Log completion status
    
    Raises:
        Exception: If any initialization step fails
    """
    logger.info("=" * 60)
    logger.info("🚀 Starting Companion Network Demo")
    logger.info("=" * 60)
    
    try:
        # Step 1: Environment variables are loaded via dotenv at module import
        
        # Step 2 & 3: Initialize agents
        logger.info("📋 Step 1/6: Initializing agents...")
        initialize_agents()
        
        # Step 4 & 5: Start MCP servers
        logger.info("📋 Step 2/6: Starting MCP servers...")
        start_mcp_servers()
        
        # Step 6: Verify A2A endpoints
        logger.info("📋 Step 3/6: Verifying A2A endpoints...")
        verify_a2a_endpoints()
        
        logger.info("=" * 60)
        logger.info("✅ Startup sequence completed successfully!")
        logger.info("=" * 60)
        logger.info("📊 Components ready:")
        logger.info("   - Alice agent: initialized (session: alice_session)")
        logger.info("   - Bob agent: initialized (session: bob_session)")
        logger.info("   - Alice MCP server: running on localhost:8001")
        logger.info("   - Bob MCP server: running on localhost:8002")
        logger.info("   - A2A endpoints: verified accessible")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ Startup sequence failed: {e}")
        logger.error("=" * 60)
        logger.error("Please check the error above and ensure:")
        logger.error("  - .env file exists with GOOGLE_API_KEY")
        logger.error("  - Ports 8001 and 8002 are not in use")
        logger.error("  - All dependencies are installed")
        logger.error("=" * 60)
        raise


def main():
    """
    Main entry point for the Gradio application.
    
    Executes startup sequence (agent initialization, MCP server startup, A2A endpoint
    verification), creates layout, and launches the Companion Network demo interface
    on localhost:7860.
    """
    try:
        # Execute startup sequence
        startup_sequence()
        
        # Create Gradio layout
        logger.info("📋 Step 4/6: Creating Gradio layout...")
        app = create_layout()
        
        # Launch Gradio app
        logger.info("📋 Step 5/6: Launching Gradio UI on localhost:7860...")
        logger.info("=" * 60)
        logger.info("🌐 Companion Network Demo is ready!")
        logger.info("   Open your browser to: http://localhost:7860")
        logger.info("=" * 60)
        
        # Note: title parameter may not be supported in older Gradio versions
        # CSS is injected via gr.HTML() in create_layout() instead of css parameter
        app.launch(
            server_name="localhost",
            server_port=7860,
            share=False
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}", exc_info=True)
        logger.error("Application startup aborted. Please fix errors and try again.")
        raise


if __name__ == "__main__":
    main()

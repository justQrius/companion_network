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
from typing import List, Tuple
import logging

# Import agent modules
from alice_companion import agent as alice_agent_module
from bob_companion import agent as bob_agent_module
from alice_companion.user_context import get_alice_context
from bob_companion.user_context import get_bob_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Module-level agent references (loaded in load_agent_references())
alice_agent = None
bob_agent = None

# Access to async runners for proper async/await pattern
alice_runner = None
bob_runner = None

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


def load_agent_references() -> None:
    """
    Load references to Alice and Bob Companion agent modules.
    
    Agents are initialized in their respective modules on import (with user contexts
    and session IDs configured). This function stores module references and runner
    instances for use by event handlers.
    
    This function is called once during app startup (Task 2).
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
        
        logger.info("Alice agent reference loaded (session ID: alice_session)")
        logger.info("Bob agent reference loaded (session ID: bob_session)")
        logger.info("Both agent references loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load agent references: {e}")
        raise


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


def create_layout():
    """
    Create the split-screen Gradio layout structure.
    
    Layout:
    - Top Row: Two columns (Alice left, Bob right)
    - Bottom Row: Network Activity Monitor
    
    Returns:
        gr.Blocks: Configured Gradio Blocks interface
    """
    with gr.Blocks(
        theme=gr.themes.Base(),  # Gradio Base theme
        css=CUSTOM_CSS,
        title="Companion Network - A2A Coordination Demo"
    ) as app:
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
                network_monitor = gr.Textbox(
                    label="A2A Communication Log",
                    value="A2A events will appear here",
                    lines=6,
                    interactive=False,
                    show_label=False
                )
                # Placeholder for network monitor updates (to be implemented in Story 4.3)
                # app.load(update_network_monitor, outputs=network_monitor, every=1)
    
    return app


def main():
    """
    Main entry point for the Gradio application.
    
    Initializes agents, creates layout, and launches the Companion Network
    demo interface on localhost:7860.
    """
    # Load agent references before creating layout
    load_agent_references()
    
    # Create Gradio layout
    app = create_layout()
    
    # Launch Gradio app
    app.launch(
        server_name="localhost",
        server_port=7860,
        share=False
    )


if __name__ == "__main__":
    main()

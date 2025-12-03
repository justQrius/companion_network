"""
Companion Network - Gradio UI Orchestrator

Main application entry point for the Companion Network demo.
Implements split-screen layout with Alice and Bob's chat interfaces
and Network Activity Monitor.

This module serves as the Gradio Orchestrator, providing:
- Split-screen UI layout (Alice panel, Bob panel, Network monitor)
- Event routing for user interactions
- Integration point for Companion agents (to be added in Story 4.2)
"""

import gradio as gr

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
                
                # Placeholder for event handlers (to be implemented in Story 4.2)
                # alice_submit.click(handle_alice_input, [alice_input, alice_chatbot], [alice_chatbot, alice_input])
                # alice_input.submit(handle_alice_input, [alice_input, alice_chatbot], [alice_chatbot, alice_input])
            
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
                
                # Placeholder for event handlers (to be implemented in Story 4.2)
                # bob_submit.click(handle_bob_input, [bob_input, bob_chatbot], [bob_chatbot, bob_input])
                # bob_input.submit(handle_bob_input, [bob_input, bob_chatbot], [bob_chatbot, bob_input])
        
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
    
    Launches the Companion Network demo interface on localhost:7860.
    Agent initialization and MCP server startup will be added in Story 4.4.
    """
    app = create_layout()
    
    # Launch Gradio app
    app.launch(
        server_name="localhost",
        server_port=7860,
        share=False
    )


if __name__ == "__main__":
    main()

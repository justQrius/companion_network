# Companion Network - Agent-to-Agent Coordination Demo

> **Eliminating the coordination tax.** AI assistants that coordinate with each other on behalf of their humans.

[![Status](https://img.shields.io/badge/status-early%20development-orange)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Description

Companion Network demonstrates a fundamental shift in how AI assistants work: from single-user helpers to a coordinated network of agents that communicate on behalf of their humans. This project showcases **agent-to-agent (A2A) coordination** as the solution to the invisible "coordination tax" that drains hours from our lives.

Every multi-person activity—dinner plans, meetings, group activities—requires coordination overhead: back-and-forth messages asking "when are you free?", mental tracking of who knows what, and one person becoming the switchboard for everyone else. Current solutions (shared calendars, group chats, AI assistants) fail because they only help one person at a time. **They can't coordinate across people.**

Companion Network eliminates this coordination tax. Two personal AI Companions communicate with each other—via **Google's A2A Protocol** and **MCP**—to negotiate availability, share preferences (with privacy controls), and coordinate plans. Instead of 5-8 messages to schedule dinner, it's one request to your Companion. The coordination happens automatically, intelligently, privately—between AIs who know their humans' preferences, schedules, and boundaries.

**Example:** Alice says *"Find a time for dinner with Bob this weekend"* → Her Companion talks to Bob's Companion → They negotiate and propose: *"Saturday 7pm, Bob prefers Italian"* → Done. No group chat noise. No back-and-forth texting. Just results.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** - Required by Google ADK
- **uv** - Ultra-fast Python package manager (10-100x faster than pip)
  - Installation instructions below
- **Google API key** - Get your API key from [Google AI Studio](https://aistudio.google.com/apikey)

## Setup Instructions

Follow these steps to set up and run the Companion Network demo:

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/google_adk_mcp.git
cd google_adk_mcp
```

### 2. Install uv (if not already installed)

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Create and Activate Virtual Environment

```bash
# Create virtual environment with uv
uv venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
# Install all project dependencies (10-100x faster than pip)
uv pip install -e .
```

This will install:
- `google-adk>=1.19.0` - Agent framework
- `mcp[cli]>=1.22.0` - MCP Python SDK
- `gradio` - Web UI framework
- `python-dotenv` - Environment variable management

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Windows (PowerShell):
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# macOS/Linux:
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

Replace `your_api_key_here` with your actual Google API key from Google AI Studio.

**Important:** Never commit the `.env` file to version control. The `.gitignore` file is configured to exclude it.

### 6. Verify Installation

```bash
# Check that dependencies are installed
uv pip list | grep google-adk
uv pip list | grep mcp
uv pip list | grep gradio
```

## Running the Demo

Launch the Gradio application:

```bash
python app.py
```

### Expected Output

After running `python app.py`, you should see:

1. **Gradio UI launches** at `http://localhost:7860`
2. **Split-screen interface** showing:
   - **Left side:** Alice's Companion chat interface
   - **Right side:** Bob's Companion chat interface
   - **Bottom:** Network Activity Monitor displaying real-time A2A communication logs

3. **Demo Scenario:** 
   - Type a message in Alice's chat: *"Find a time for dinner with Bob this weekend"*
   - Alice's Companion will automatically contact Bob's Companion via A2A Protocol
   - Watch the Network Activity Monitor to see the Companion-to-Companion communication
   - The Companions will negotiate availability and preferences
   - A proposal will appear: *"Saturday 7pm, Bob prefers Italian"*
   - Alice can confirm or modify the proposal

The split-screen UI allows you to see both Companions coordinating in real-time, demonstrating true agent-to-agent communication.

## Demo Scenario

When you run `python app.py`, the application starts a Gradio web server that displays a split-screen interface:

- **Left Panel:** Alice's Companion - Chat interface where you can interact with Alice's AI Companion
- **Right Panel:** Bob's Companion - Chat interface where you can interact with Bob's AI Companion  
- **Network Monitor:** Real-time log showing all A2A (Agent-to-Agent) communication between the Companions

### Complete Demo Flow

**Step 1: Initial Request**
1. In Alice's chat interface (left panel), type: *"Find a time for dinner with Bob this weekend"*
2. Press Enter or click Send
3. **Expected:** Message appears immediately in Alice's chat
4. **Expected:** "thinking..." indicator appears while Alice's Companion processes

**Step 2: A2A Coordination (5-10 seconds)**
1. Watch the Network Activity Monitor (bottom panel) as A2A events appear in real-time
2. **Expected:** Events show `check_availability` calls between Alice and Bob
3. **Expected:** Events show `propose_event` calls
4. **Expected:** Each event includes timestamp, sender, receiver, tool name, and status

**Step 3: View Coordination Results**
1. **Alice's View:** Alice's Companion responds with coordination messages showing the negotiation process
2. **Bob's View:** Bob sees incoming event proposal in his chat interface
3. **Network Monitor:** All A2A calls displayed with correct details

**Step 4: Confirm Event**
1. In Alice's chat, type: *"Sounds good, confirm it"*
2. Press Enter or click Send
3. **Expected:** Event is confirmed in both Companions' session states
4. **Expected:** Event status is consistent across both agents

### Performance Targets

- **Complete Flow:** Should complete within 10 seconds (from initial request to confirmation)
- **A2A Latency:** Companion-to-Companion communication should complete within 3-5 seconds
- **UI Responsiveness:** Chat interface should feel "instant" (sub-100ms response time)

### What to Observe

- **Network Monitor:** Shows all A2A calls (check_availability, propose_event, share_context, relay_message) with timestamps, sender, receiver, tool names, and status
- **Chat Interfaces:** Natural language responses showing coordination process
- **State Consistency:** Event confirmed in both agents' session states with consistent status
- **Error Handling:** Graceful error messages (no crashes) if something goes wrong

### Troubleshooting

If the demo doesn't work as expected:

1. **Check system startup:** Verify all components initialized (agents, MCP servers, A2A endpoints)
2. **Check Network Monitor:** Should show A2A events if coordination is happening
3. **Check browser console:** Look for JavaScript errors
4. **Check logs:** Review terminal output for error messages
5. **See detailed guide:** Refer to `docs/sprint-artifacts/4-5-manual-testing-guide.md` for comprehensive troubleshooting

This demonstrates the core value proposition: **one request from Alice results in autonomous coordination between the two AI agents**, eliminating the need for back-and-forth messaging.

## Architecture

The project follows a **hybrid architecture**:
- **Companion Framework (Developer Tool):** Each Companion is an MCP Server exposing coordination tools
- **Demo Application (Web App):** Gradio split-screen interface showcasing A2A coordination

Key components:
- **Google ADK** - Agent framework with native A2A Protocol support
- **MCP (Python SDK)** - Tool exposure and calling between agents
- **Gradio** - Web-based UI with split-screen layout
- **SQLite** - Session persistence (survives demo restarts)

## What Makes This Special

- **🎯 Eliminates the coordination tax** - Instead of 5-8 messages to schedule dinner, it's one request to your Companion
- **🤖 True A2A coordination** - Meaningfully uses Google's A2A Protocol for agent-to-agent communication
- **🔧 Comprehensive ADK usage** - Uses multiple ADK capabilities (agents, MCP server, MCP client, memory, sessions, A2A)
- **🔒 Privacy-first** - User-controlled sharing rules ensure information is only shared with trusted contacts
- **👀 Transparent** - Real-time network activity monitor shows all Companion-to-Companion interactions

## MCP Tools

Each Companion exposes these MCP tools to other Companions:

1. **`check_availability`** - Query availability for a proposed timeframe
2. **`propose_event`** - Propose a specific event with details
3. **`share_context`** - Request approved contextual information
4. **`relay_message`** - Send a message to be relayed to the human

## Tech Stack

- **Google ADK** - Agent framework
- **Gemini 2.5 Pro** - LLM powering the Companions
- **A2A Protocol** - Companion-to-Companion communication
- **MCP (Python SDK)** - Tool exposure and calling
- **Gradio** - Web UI
- **SQLite** - Session persistence
- **uv** - Fast dependency management (10-100x faster than pip)

## Project Status

🚧 **Early Development** - This project is in its initial phase. The MVP is currently under active development.

### Planned MVP Features

- ✅ Two Companion agents (Alice and Bob) with pre-configured contexts
- ✅ Basic availability checking via simulated calendar data
- ✅ Event proposal and acceptance/decline flow
- ✅ A2A communication using Google's A2A Protocol and MCP
- ✅ Split-screen Gradio interface showing both Companions
- ✅ Network activity monitor displaying real-time A2A communication logs

### Out of Scope for MVP

- Real calendar integration (Google Calendar, Outlook, etc.)
- More than 2 users
- Cloud database or production-grade storage
- Mobile interface
- Authentication/user accounts
- Proactive suggestions from Companions

## Contributing

This project is currently in active development. Contributions and feedback are welcome!

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Author

**justQrius**

---

_Companion Network - A novel demonstration of agent-to-agent coordination that eliminates the "coordination tax" for users._

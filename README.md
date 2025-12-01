# Companion Network

> **Eliminating the coordination tax.** AI assistants that coordinate with each other on behalf of their humans.

[![Status](https://img.shields.io/badge/status-early%20development-orange)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

Companion Network demonstrates a fundamental shift in how AI assistants work: from single-user helpers to a coordinated network of agents that communicate on behalf of their humans. Built for the **MCP Hackathon**, **Kaggle AI Agents Intensive**, and **Google Gemini Award**, this project showcases **agent-to-agent (A2A) coordination** as the solution to the invisible "coordination tax" that drains hours from our lives.

### The Problem

Every multi-person activity—dinner plans, meetings, group activities—requires coordination overhead:
- Back-and-forth messages asking "when are you free?"
- Mental tracking of who knows what
- One person becoming the switchboard for everyone else

Current solutions (shared calendars, group chats, AI assistants) fail because they only help one person at a time. **They can't coordinate across people.**

### The Solution

Two personal AI Companions communicate with each other—via **Google's A2A Protocol** and **MCP**—to negotiate availability, share preferences (with privacy controls), and coordinate plans.

**Example:** Alice says *"Find a time for dinner with Bob this weekend"* → Her Companion talks to Bob's Companion → They negotiate and propose: *"Saturday 7pm, Bob prefers Italian"* → Done. No group chat noise. No back-and-forth texting. Just results.

## What Makes This Special

- **🎯 Eliminates the coordination tax** - Instead of 5-8 messages to schedule dinner, it's one request to your Companion
- **🤖 True A2A coordination** - The only hackathon project meaningfully using Google's A2A Protocol
- **🔧 Comprehensive ADK usage** - Uses more ADK capabilities (agents, MCP server, MCP client, memory, sessions, A2A) than any other concept
- **🔒 Privacy-first** - User-controlled sharing rules ensure information is only shared with trusted contacts
- **👀 Transparent** - Real-time network activity monitor shows all Companion-to-Companion interactions

## Architecture

Companion Network follows a **hybrid architecture** combining a **Web App** (Gradio demo) and a **Developer Tool** (Companion Framework):

### Component 1: Companion Agent (Backend)
- **Agent Framework:** Google ADK (Agent Development Kit)
- **Model:** Gemini 2.5 Pro
- **Communication:** A2A Protocol for inter-agent messaging
- **Interface:** MCP Server exposing coordination tools
- **State Management:** In-memory session handling (SQLite for persistence)

### Component 2: Demo Interface (Frontend)
- **Framework:** Gradio (Python-based UI)
- **Layout:** Split-screen (Alice View | Bob View)
- **Visualization:** Network Activity Monitor (Log of A2A calls)
- **Interaction:** Chat-based input for human-to-agent communication

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

🚧 **Early Development** - This project is in its initial phase. The MVP is being developed for hackathon demonstrations.

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

## Getting Started

> **Note:** This project is in early development. Setup instructions will be added as the codebase matures.

### Prerequisites

- Python 3.10+
- Google ADK access
- Gemini API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/google_adk_mcp.git
cd google_adk_mcp

# Install dependencies (using uv for faster installs)
uv pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Running the Demo

```bash
# Start the Gradio application
python -m src.demo.app
```

## Author

**justQrius**

---

_Companion Network - A novel demonstration of agent-to-agent coordination that eliminates the "coordination tax" for users._


# Companion Network - Architecture Document

## Project Context

**Project:** Companion Network - Agent-to-Agent Coordination Demo  
**Type:** Hybrid (Web App + Developer Tool)  
**Domain:** Consumer / General (Low Complexity)  
**Date:** 2025-11-30  

### Understanding

I've reviewed the project documentation for **Companion Network** and found:

- **31 Functional Requirements** organized into:
  - Agent Core & Identity (FR1-FR4)
  - Coordination Logic (FR5-FR9)
  - MCP Server - Inbound (FR10-FR14)
  - MCP Client - Outbound (FR15-FR18)
  - User Interface - Gradio Demo (FR19-FR25)
  - Data & State (FR26-FR31)

- **Key Aspects Identified:**
  - **Core Functionality:** Two Companion agents (Alice/Bob) communicate via A2A Protocol and MCP to coordinate dinner plans
  - **Critical NFRs:** Privacy (data minimization, contextual integrity), Performance (demo quality with 3-5s A2A latency), Reliability (graceful degradation)
  - **Unique Challenges:** Hybrid Python/Gradio architecture, In-memory state for MVP, Novel A2A protocol integration
  
- **UX Design Extracted:**
  - **Platform:** Gradio web-based split-screen interface
  - **Design Style:** Clean & Minimal (ChatGPT/Claude-like)
  - **Framework:** Gradio Base Theme + Custom CSS
  - **Desired Feeling:** Relief and Empowerment
  - **Core Experience:** User delegates coordination task → AIs negotiate autonomously → User approves result

## Project Initialization

**Approach:** Manual Setup with Modern Tooling

**Rationale:** The Companion Network architecture is novel—combining Google ADK agents, MCP server/client dual-role, A2A Protocol, and Gradio UI. No existing starter template covers this combination. Manual setup with cutting-edge tools provides maximum flexibility and performance.

**Initialization Commands:**

```bash
# 1. Install uv (ultra-fast Python package manager)
# Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create project with uv (auto-creates venv + installs deps)
uv venv
source .venv/bin/act  # Windows: .venv\Scripts\activate

# 3. Install core dependencies with uv (10-100x faster than pip)
uv pip install google-adk mcp gradio python-dotenv

# 4. Create ADK agent structure
adk create alice_companion
adk create bob_companion
mkdir shared

# 5. Initialize Git repository
git init
# (See Version Control Strategy section for .gitignore setup)
```

**Technology Decisions:**

| Decision | Choice | Rationale | Updated Date |
|----------|--------|-----------|--------------|
| **Python Runtime** | Python 3.10+ | Required by Google ADK | 2025-11-30 |
| **Dependency Manager** | `uv` (Astral) | 10-100x faster than pip, unified tool (replaces pip+venv+pip-tools), Rust-based performance, growing industry adoption as of Nov 2025 | 2025-11-30 |
| **Environment Isolation** | `uv venv` | Auto-managed by uv, 3x faster than venv | 2025-11-30 |
| **Agent Structure** | ADK standard | `agent.py`, `__init__.py`, `.env` per ADK conventions | 2025-11-30 |
| **Configuration** | `.env` + `pyproject.toml` | `.env` for secrets, `pyproject.toml` for project metadata and dependencies | 2025-11-30 |

**First Implementation Story:**  
Story 1 should execute the initialization commands above to establish the base project structure.

## Version Control Strategy

**Repository Structure:**

```bash
companion_network/
├── .git/                         # Git repository
├── .gitignore                    # Ignored files (see below)
├── .gitattributes                # Git LFS configuration (if needed)
├── README.md                     # Project documentation
├── pyproject.toml                # Project metadata and dependencies
├── uv.lock                       # Locked dependencies (commit this!)
├── .env.example                  # Template for environment variables
├── .env                          # Actual secrets (DO NOT

 COMMIT)
├── companion_sessions.db         # SQLite (gitignored, local only)
├── alice_companion/
├── bob_companion/
├── shared/
└── app.py
```

**Git Workflow:**

1. **Initial Repository Setup:**
   ```bash
   git init
   git add .gitignore README.md pyproject.toml
   git commit -m "Initial project structure"
   ```

2. **Branch Strategy (Simplified for Hackathon):**
   - `main` - Stable demo-ready code
   - `dev` - Active development
   - Feature branches: `feature/alice-agent`, `feature/gradio-ui`, etc.
   - Experiment branches: `experiment/tool-schema-v2`, etc.

3. **Commit Conventions:**
   - Use clear, present-tense messages: "Add check_availability tool" not "Added..."
   - Prefix with component: `[Alice] Add check_availability tool`
   - Atomic commits: One logical change per commit

4. **Dependency Locking:**
   - **ALWAYS commit `uv.lock`** to ensure reproducible builds
   - Run `uv pip compile pyproject.toml -o uv.lock` after dependency changes

### `.gitignore` for Python AI/Agent Projects

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual Environments
.venv/
venv/
env/
ENV/

# uv
.uv/

# IDE
.vscode/
.idea/
*.swp
*~

# Environment Variables (CRITICAL - DO NOT COMMIT SECRETS)
.env

# Databases (local dev only)
*.db
*.sqlite
*.sqlite3
companion_sessions.db

# Logs
*.log
logs/
mlruns/
runs/

# Model files (use DVC if needed in future)
models/*.pth
models/*.h5
models/*.pkl
models/*.joblib

# Data files (if large datasets added)
data/raw/
data/processed/
*.csv
*.parquet
*.npy

# Jupyter
.ipynb_checkpoints/

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Build/Distribution
build/
dist/
*.egg-info/
```

**Why These Choices:**

| Practice | Rationale |
|----------|-----------|
| Commit `uv.lock` | Ensures exact dependency versions for all developers and CI/CD. Critical for reproducibility. |
| `.env.example` in repo | Provides template for required env vars without exposing secrets. |
| Ignore `.db` files | SQLite databases are local dev artifacts, not source code. Each dev creates their own. |
| Exclude model files | Model weights can be regenerated. For production, use DVC or model registry. |
| OS-specific ignores | Prevents committing macOS/Windows filesystem metadata. |

**For Future Production Evolution:**
- Add DVC (Data Version Control) for model/data versioning
- Implement pre-commit hooks for linting (ruff) and type checking (mypy)
- Add GitHub Actions for CI/CD (test on every push)

## Executive Summary

The Companion Network architecture is a **Python-based multi-agent system** demonstrating Agent-to-Agent (A2A) coordination via Google's ADK and MCP protocols. Built for a hackathon demo, this architecture prioritizes **stability, simplicity, and showcase value** over production scalability.

**Core Architecture:**  
Two Companion agents (Alice and Bob) run locally, each acting as both an MCP server (exposing 4 coordination tools) and MCP client (calling other Companions' tools). A2A communication happens over HTTP (localhost:8001, localhost:8002) using JSON-RPC 2.0. The split-screen Gradio UI provides real-time visualization of both users and their A2A network activity.

**Key Technical Decisions:**  
Gemini 2.5 Pro for proven stability, SQLite for session persistence (survives demo restarts), official MCP Python SDK for flexibility, and native ADK A2A support for seamless agent-to-agent communication. State management uses ADK's `DatabaseSessionService` with session/user/app scopes.

**Implementation Philosophy:**  
"Boring technology that works." Every decision prioritizes demo reliability and clarity for hackathon judges. Manual Python setup (no complex starters), hardcoded endpoints (no discovery complexity), and graceful error handling (never crash during judging).

## Decision Summary

| Category | Decision | Version | Rationale | Verification Date |
| -------- | -------- | ------- | --------- | ----------------- |
| AI Model | Gemini 2.5 Pro | gemini-2.5-pro | Stable production model (released June 2025) with proven agentic capabilities, native tool use, and strong reasoning for A2A coordination. Preferred over Gemini 3 Pro preview for hackathon stability. | 2025-11-30 |
| MCP Implementation | Official MCP Python SDK | v1.22.0 (2025-11-20) | Full protocol support with dual server/client capability. Provides flexibility needed for novel A2A pattern. Well-documented and actively maintained. | 2025-11-30 |
| A2A Protocol | Google ADK Native Support | ADK v1.19.0+ (2025-11-19) | ADK provides built-in A2A implementation with `to_a2a()` and `/run` endpoints. Agent Cards for discovery, JSON-RPC 2.0 over HTTP for communication. For local demo, hardcoded endpoint URLs. | 2025-11-30 |
| Memory - Session | DatabaseSessionService (SQLite) | SQLite 3 | Persistent session storage in local SQLite file. Survives demo restarts, no server setup needed. Perfect for local hackathon demonstration. | 2025-11-30 |
| Memory - Long-term | InMemoryMemoryService | N/A | Simple in-memory storage for MVP. PRD doesn't require cross-session learning for demo. Keeps complexity minimal. | 2025-11-30 |
| UI Framework | Gradio | Latest stable | Gradio Blocks with Row/Column layout for split-screen interface. Handles concurrency automatically. JSON component for network activity log. | 2025-11-30 |
| Error Handling | Try-Catch with Graceful Degradation | Python built-in | MCP call failures: retry once, then report to user. Agent unreachable: clear error message, no crash. Demo-quality reliability. | 2025-11-30 |
| Logging | Python logging + Structured A2A logs | Python stdlib | Standard logging for debugging. Structured JSON array for A2A events displayed in Gradio network monitor. | 2025-11-30 |
| Tool Schemas | Python Type Hints + MCP Auto-generation | MCP SDK feature | Define tools as typed Python functions. MCP SDK auto-generates JSON schemas from function signatures and docstrings. | 2025-11-30 |
| Concurrency | Gradio Built-in Event Handling | Gradio async | Gradio manages concurrent user interactions via async tasks. No manual threading needed. Prevents deadlock automatically. | 2025-11-30 |
| Data Models | Python dataclasses | Python 3.10+ stdlib | Type-safe data structures for UserContext, EventProposal, SharingRules. Clean, Pythonic, IDE-friendly. | 2025-11-30 |

## Project Structure

```
companion_network/
├── .env                          # API keys (GOOGLE_API_KEY, etc.)
├── requirements.txt              # Dependencies
├── companion_sessions.db         # SQLite session storage (created at runtime)
├── alice_companion/              # Alice's Companion agent
│   ├── __init__.py              # Package marker
│   ├── agent.py                 # ADK agent definition
│   ├── mcp_server.py            # MCP server exposing 4 tools
│   ├── mcp_client.py            # MCP client for calling Bob
│   ├── user_context.py          # Alice's context data models
│   └── a2a_config.json          # Agent Card for discovery
├── bob_companion/                # Bob's Companion agent
│   ├── __init__.py
│   ├── agent.py
│   ├── mcp_server.py
│   ├── mcp_client.py
│   ├── user_context.py
│   └── a2a_config.json
├── shared/                       # Shared utilities
│   ├── __init__.py
│   ├── models.py                # Shared data models (EventProposal, etc.)
│   ├── schemas.py               # MCP tool schemas
│   └── logger.py                # Logging configuration
└── app.py                        # Gradio UI orchestrating both Companions
```

### Architectural Boundaries

**FR Mapping to Components:**

| Functional Requirement | Component | Location |
|------------------------|-----------|----------|
| FR1-FR4: Agent Core & Identity | ADK Agent | `{alice,bob}_companion/agent.py` |
| FR5-FR9: Coordination Logic | Agent Tools | `{alice,bob}_companion/agent.py` |
| FR10-FR14: MCP Server (Inbound) | MCP Server | `{alice,bob}_companion/mcp_server.py` |
| FR15-FR18: MCP Client (Outbound) | MCP Client | `{alice,bob}_companion/mcp_client.py` |
| FR19-FR25: Gradio UI | Gradio Interface | `app.py` |
| FR26-FR31: Data & State | Session Service + Models | `shared/models.py` + SQLite |

### Integration Points

**1. Gradio ↔ Companion Agents**
- **Protocol:** Python function calls
- **Flow:** User input → Gradio event handler → `agent.run()` → Response to UI

**2. Alice's Companion ↔ Bob's Companion**
- **Protocol:** A2A over HTTP (JSON-RPC 2.0)
- **Flow:** Alice agent → MCP Client → HTTP POST to `http://localhost:8002/run` → Bob's A2A endpoint → MCP Server → Tool execution → Response

**3. Companion ↔ MCP Tools**
- **Protocol:** MCP tool calling (internal)
- **Flow:** Agent reasoning → Tool decision → MCP Server routes to tool function → Execute → Return result

**4. Agent ↔ Session Storage**
- **Protocol:** ADK SessionService API
- **Flow:** Agent state update → `DatabaseSessionService` → SQLite write → Persistence

## Technology Stack Details

### Core Technologies

**Runtime:**
- Python 3.10+ (Required by ADK)
- Virtual environment (venv) for dependency isolation

**AI & Agent Framework:**
- Google ADK v1.19.0+ (Agent framework)
- Gemini 2.5 Pro (`gemini-2.5-pro`) - LLM
- A2A Protocol (Native in ADK) - Agent-to-agent communication

**Communication & Tools:**
- MCP Python SDK v1.22.0 - Tool exposure and calling
- HTTP/JSON-RPC 2.0 - A2A transport

**UI:**
- Gradio (latest stable) - Web interface
- Gradio Blocks API - Split-screen layout

**Data & Persistence:**
- SQLite 3 - Session storage (DatabaseSessionService)
- Python dataclasses - Data models
- JSON - Event state serialization

**Development:**
- Python logging - Debugging and A2A activity logs
- python-dotenv - Environment variable management
- uv - Ultra-fast package manager and dependency resolver (10-100x faster than pip)

### Dependencies (pyproject.toml)

```toml
[project]
name = "companion-network"
version = "0.1.0"
description = "Agent-to-Agent coordination demo using Google ADK, MCP, and A2A Protocol"
requires-python = ">=3.10"
dependencies = [
    "google-adk>=1.19.0",
    "mcp[cli]>=1.22.0",
    "gradio",
    "python-dotenv",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Installation with uv:**
```bash
uv pip install -e .  # Installs project in editable mode
```


## Implementation Patterns

These patterns ensure consistent implementation across all components:

### Naming Conventions

**Python Modules & Files:**
- Modules: `snake_case` (e.g., `mcp_server.py`, `user_context.py`)
- Classes: `PascalCase` (e.g., `UserContext`, `EventProposal`)
- Functions: `snake_case` (e.g., `check_availability`, `propose_event`)

**MCP Tools:**
- Tool names: `snake_case` (e.g., `check_availability`, `propose_event`, `share_context`, `relay_message`)
- Parameter names: `snake_case` (e.g., `timeframe`, `event_type`, `requester`)

**State Keys:**
- Session state: Plain keys (e.g., `"user_context"`, `"events"`)
- User state: `user:` prefix (e.g., `"user:preferences"`)
- App state: `app:` prefix (e.g., `"app:config"`)

**Database:**
- SQLite file: `companion_sessions.db`
- Table names: `snake_case` (ADK manages schema)

### Code Organization

**Tool Definition Pattern:**
```python
def check_availability(
    timeframe: str,
    event_type: str,
    duration_minutes: int,
    requester: str
) -> dict:
    """Query availability for a proposed timeframe.
    
    Args:
        timeframe: ISO 8601 time range (e.g., "2025-12-07T19:00:00/2025-12-07T21:00:00")
        event_type: Type of event ('dinner', 'meeting', etc.)
        duration_minutes: Duration in minutes
        requester: User ID of requester
        
    Returns:
        dict with keys: available (bool), slots (list), preferences (dict)
    """
    # 1. Validate requester is in trusted_contacts
    # 2. Check sharing_rules for this requester
    # 3. Query schedule from session state
    # 4. Return availability data
```

**Error Handling Pattern:**
```python
async def call_other_companion_tool(tool_name: str, **params):
    """Call tool on another Companion's MCP server."""
    try:
        response = await mcp_client.call_tool(tool_name, **params)
        return response
    except MCPError as e:
        logger.warning(f"MCP call failed: {e}, retrying once...")
        try:
            response = await mcp_client.call_tool(tool_name, **params)
            return response
        except MCPError as retry_error:
            logger.error(f"MCP call failed after retry: {retry_error}")
            return {"error": "Agent temporarily unavailable", "details": str(retry_error)}
```

**A2A Event Logging Pattern:**
```python
def log_a2a_event(sender: str, receiver: str, tool: str, params: dict, result: dict):
    """Log A2A communication event for network monitor."""
    event = {
        "timestamp": datetime.now().isoformat(),
        "sender": sender,
        "receiver": receiver,
        "tool": tool,
        "params": {k: v for k, v in params.items() if k != "requester"},  # Redact sensitive
        "status": "success" if "error" not in result else "failed"
    }
    # Append to app state for Gradio network log
    state["app:a2a_events"].append(event)
    logger.info(f"A2A: {sender} → {receiver} : {tool}")
```

## Consistency Rules

### Error Handling Strategy

**Principle:** Demo must never crash. Always provide feedback.

**MCP Call Failures:**
1. Retry once (network might be flaky)
2. If still fails, return structured error to agent
3. Agent should inform user gracefully

**Agent Unreachable:**
- Display: "Could not reach [User]'s Companion. They may be offline."
- Log error for debugging
- Allow user to retry or cancel

**Invalid Input:**
- Validate at tool boundary
- Return clear error message (not stack traces)

**State Inconsistency:**
- Log warning
- Attempt to auto-correct if possible
- Otherwise, ask user for clarification

### Logging Strategy

**Log Levels:**
- `DEBUG`: Detailed agent reasoning steps, state changes
- `INFO`: A2A events, user actions, tool calls
- `WARNING`: Retry attempts, validation failures
- `ERROR`: Unrecoverable errors, exceptions

**Log Format:**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**A2A Network Log (for Gradio UI):**
- Stored in `app:a2a_events` (list of dicts)
- Each event: `{"timestamp", "sender", "receiver", "tool", "params", "status"}`
- Updated in real-time
- Displayed as JSON in Gradio component

### Date/Time Handling

**Standard:** ISO 8601 format
- Datetime strings: `"2025-12-07T19:00:00"` (no timezone for demo simplicity)
- Time ranges: `"2025-12-07T19:00:00/2025-12-07T21:00:00"`
- Python: Use `datetime.fromisoformat()` for parsing

### Data Models

**UserContext:**
```python
from dataclasses import dataclass, field

@dataclass
class UserContext:
    user_id: str
    name: str
    preferences: dict = field(default_factory=dict)  # {"cuisine": [...], "dining_times": [...]}
    schedule: dict = field(default_factory=dict)     # {"busy_slots": [...]}
    trusted_contacts: list = field(default_factory=list)
    sharing_rules: dict = field(default_factory=dict)  # {contact_id: [allowed_categories]}
```

**EventProposal:**
```python
@dataclass
class EventProposal:
    event_id: str
    proposer: str
    recipient: str
    status: str  # "pending", "accepted", "declined", "counter"
    details: dict  # {"title", "time", "location"}
    timestamp: str
```

**SharingRules:**
```python
@dataclass
class SharingRule:
    contact_id: str
    allowed_categories: list  # ["availability", "cuisine_preferences", "dietary", "schedule"]
```

## API Contracts (MCP Tools)

### Tool 1: check_availability

**Purpose:** Query availability for a proposed timeframe

**Input Schema:**
```json
{
  "timeframe": "string (ISO 8601 range)",
  "event_type": "string (enum: dinner, meeting, etc.)",
  "duration_minutes": "integer",
  "requester": "string (user_id)"
}
```

**Output Schema:**
```json
{
  "available": "boolean",
  "slots": ["list of available ISO 8601 ranges"],
  "preferences": {"context-appropriate preferences dict"},
  "auto_accept_eligible": "boolean"
}
```

**Access Control:** Requester must be in `trusted_contacts`

### Tool 2: propose_event

**Purpose:** Propose a specific event to this user

**Input Schema:**
```json
{
  "event_name": "string",
  "datetime": "string (ISO 8601)",
  "location": "string",
  "participants": ["list of user_ids"],
  "requester": "string (user_id)"
}
```

**Output Schema:**
```json
{
  "status": "string (enum: accepted, declined, pending, counter)",
  "message": "string (explanation)",
  "event_id": "string (if accepted/pending)"
}
```

**Access Control:** Requester must be in `trusted_contacts`

### Tool 3: share_context

**Purpose:** Request specific approved context

**Input Schema:**
```json
{
  "category": "string (enum: preferences, dietary, schedule, interests)",
  "purpose": "string (what the context will be used for)",
  "requester": "string (user_id)"
}
```

**Output Schema:**
```json
{
  "context_data": "dict (if approved)",
  "access_denied": "string (reason, if denied)"
}
```

**Access Control:** Check `sharing_rules[requester]` for `category`

### Tool 4: relay_message

**Purpose:** Send a message to be relayed to the human

**Input Schema:**
```json
{
  "message": "string",
  "urgency": "string (enum: low, normal, high)",
  "sender": "string (user_id)"
}
```

**Output Schema:**
```json
{
  "delivered": "boolean"
}
```

**Access Control:** Requester must be in `trusted_contacts`

## Security Architecture

### Privacy (Critical NFR)

**Data Minimization:**
- Tools MUST check `sharing_rules` before returning any data
- Never expose data categories not explicitly allowed
- Log all data sharing requests for audit

**Contextual Integrity:**
- Information shared for "dinner planning" should not be retained for other purposes
- Each A2A interaction is scoped to a specific task
- No cross-purpose data retention in this MVP

**Local-First Design:**
- User context stored locally in SQLite (not cloud for demo)
- No external API calls except to other local Companions
- API keys in `.env`, never committed to version control

**Consent:**
- Hardcoded `sharing_rules` for demo
- In production, would require explicit user permission UI

### Authentication & Authorization

**For MVP (Hardcoded Demo):**
- No real authentication (Alice and Bob identities are hardcoded)
- `trusted_contacts` list pre-configured in user context
- MCP tool validation: Check `requester` against `trusted_contacts`

**A2A Endpoint Security:**
- Localhost only (`http://localhost:8001`, `http://localhost:8002`)
- No HTTPS needed for local demo
- Production would require: API keys, OAuth, or mutual TLS

## Performance Considerations

### A2A Latency (NFR: 3-5 seconds)

**Target:** Complete coordination within 3-5 seconds

**Optimization Strategies:**
- Use async/await for all network calls
- Parallel MCP calls where possible
- Minimal agent reasoning steps (focused prompts)
- Local endpoints (no network latency)

**Monitoring:**
- Log timestamps for each A2A call
- Display total coordination time in UI

### UI Responsiveness (NFR: Sub-100ms)

**Strategy:**
- Gradio uses async event handlers (non-blocking)
- Show "thinking..." indicator during agent processing
- Update UI incrementally (streaming if possible)

**Implementation:**
```python
async def handle_user_input(message: str, agent_name: str):
    # Immediately show user message
    chat_history.append({"role": "user", "content": message})
    yield chat_history  # Update UI
    
    # Process in background
    response = await agent.run(message)
    chat_history.append({"role": "assistant", "content": response})
    yield chat_history  # Update UI again
```

### Concurrency (NFR: Simultaneous Alice/Bob)

**Approach:** Gradio handles automatically
- Each user's input triggers separate async task
- No manual threading needed
- Gradio's event loop prevents deadlock

**State Isolation:**
- Each agent has separate session in `DatabaseSessionService`
- Session IDs: `"alice_session"`, `"bob_session"`
- No shared state except `app:` prefix (network log)

## Deployment Architecture

### Local Development

**Setup:**
1. Clone repository
2. Create virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Create `.env` with `GOOGLE_API_KEY=<your-key>`
5. Run: `python app.py`

**Architecture:**
```
┌─────────────────────┐
│   Browser           │
│   localhost:7860    │
└──────────┬──────────┘
           │ HTTP
┌──────────▼──────────────────────────────┐
│  Gradio App (app.py)                    │
│  ┌────────────────┐  ┌───────────────┐  │
│  │ Alice Companion│  │ Bob Companion │  │
│  │ :8001 (A2A)    │  │ :8002 (A2A)   │  │
│  └────────┬───────┘  └───────┬───────┘  │
│           │ A2A HTTP         │          │
│           └──────────────────┘          │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  SQLite: companion_sessions.db  │  │
│  └──────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

### Demo/Hackathon Deployment

**Option 1: Local (Recommended for MCP Hackathon)**
- Run on laptop during presentation
- Judges interact with localhost
- Most reliable (no network dependencies)

**Option 2: Cloud (Optional)**
- Deploy to Google Cloud Run or similar
- Requires: Persistent disk for SQLite, or migrate to Cloud SQL
- Network lag may impact demo responsiveness

## Development Environment

### Prerequisites

- Python 3.10 or later
- pip (Python package manager)
- Git (for version control)
- Google AI Studio API key (for Gemini 2.5 Pro)
- Code editor (VS Code recommended)

### Setup Commands

```bash
# 1. Install uv (one-time setup)
# Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create and activate virtual environment with uv
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies (10-100x faster than pip)
uv pip install google-adk mcp[cli] gradio python-dotenv

# 4. Create .env file
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# 5. Initialize project structure
adk create alice_companion
adk create bob_companion
mkdir shared

# 6. Initialize Git repository
git init
# Copy .gitignore from architecture doc
# Create .env.example (template without secrets)
cp .env .env.example
# Edit .env.example to remove actual API key value

# 7. First commit
git add .
git commit -m "Initial project setup with ADK, MCP, and Gradio"

# 8. Run the demo
python app.py
```

### Development Workflow

1. **Implement Agents:** Start with `alice_companion/agent.py` and `bob_companion/agent.py`
2. **Define MCP Tools:** Implement 4 tools in each `mcp_server.py`
3. **Create Gradio UI:** Build split-screen interface in `app.py`
4. **Enable A2A:** Use `agent.to_a2a()` to expose A2A endpoints
5. **Test:** Simulate "Find a time for dinner" scenario
6. **Iterate:** Refine agent prompts and tool logic
7. **Commit Frequently:** Atomic commits with clear messages
8. **Lock Dependencies:** Run `uv pip compile` after adding new packages

## Architecture Decision Records (ADRs)

### ADR-001: Use Gemini 2.5 Pro instead of Gemini 3 Pro Preview

**Status:** Accepted

**Context:** Gemini 3 Pro was released in preview on Nov 18, 2025, offering state-of-the-art capabilities. However, for a hackathon demo, stability is critical.

**Decision:** Use Gemini 2.5 Pro (stable, released June 2025)

**Consequences:**
- ✅ Proven stability for demo environment
- ✅ Well-documented, fewer edge cases
- ❌ Miss cutting-edge Gemini 3 features (adaptive thinking, thought signatures)

**Rationale:** Demo reliability outweighs marginal capability gains. Judges care about working demo, not latest model.

---

### ADR-002: SQLite for Session Persistence

**Status:** Accepted

**Context:** ADK offers multiple SessionService options: InMemory, Database, VertexAI

**Decision:** Use DatabaseSessionService with SQLite

**Consequences:**
- ✅ Sessions persist across demo restarts
- ✅ No server setup required
- ✅ Easy to inspect data during development
- ❌ Not scalable for production (but irrelevant for MVP)

**Rationale:** Balance between persistence (demo can restart) and simplicity (no database server).

---

### ADR-003: Hardcoded A2A Endpoints for Local Demo

**Status:** Accepted

**Context:** A2A Protocol supports discovery via Agent Cards. For production, dynamic discovery is essential.

**Decision:** Hardcode Alice (`localhost:8001`) and Bob (`localhost:8002`) endpoints

**Consequences:**
- ✅ Simpler implementation
- ✅ No network discovery needed
- ❌ Not extensible to 3+ agents

**Rationale:** MVP is 2-agent demo. Hardcoding reduces complexity and potential failure points during judging.

---

### ADR-004: In-Memory Long-Term Memory (Not Persistent)

**Status:** Accepted

**Context:** ADK supports VertexAIMemoryBankService for persistent long-term memory with semantic search.

**Decision:** Use InMemoryMemoryService (non-persistent)

**Consequences:**
- ✅ Simpler implementation
- ✅ No cloud dependencies
- ❌ Agents don't "remember" across application restarts

**Rationale:** PRD doesn't require cross-session learning for MVP. Demo scenario is self-contained ("Plan dinner this weekend").

---

### ADR-005: Use uv Instead of pip/venv

**Status:** Accepted  
**Date:** 2025-11-30

**Context:** Traditional Python dependency management uses pip + venv (or Poetry). As of November 2025, uv (by Astral) has emerged as a significantly faster alternative (10-100x faster than pip), written in Rust [1][2].

**Decision:** Use `uv` for package management and virtual environments

**Consequences:**
- ✅ **Dramatic speed improvement:** 10-100x faster package installation and dependency resolution
- ✅ **Unified tooling:** Replaces pip, pip-tools, virtualenv, and aspects of Poetry/pyenv in one tool
- ✅ **Better caching:** Efficient dependency caching reduces redundant downloads
- ✅ **uv.lock for reproducibility:** Lock file ensures exact dependency versions across environments
- ✅ **Growing adoption:** Increasingly standard in Python community as of late 2025
- ⚠️ **Newer tool:** Less mature than pip (released 2024), but actively developed by Astral (creators of Ruff)
- ❌ **Team familiarity:** Team members may need to install uv and learn new commands

**Rationale:**  
For a hackathon demo where iteration speed matters, uv's performance advantage is significant. Installing dependencies during setup or after adding new packages is 10-100x faster, reducing friction. The tool is pip-compatible (`uv pip install`) for easy adoption. The Python community is rapidly adopting uv as the modern standard for 2025+.

**References:**
- [1] Real Python: https://realpython.com/python-packages-with-uv/
- [2] Analytics Vidhya: uv performance benchmarks

---

_Generated by BMAD Decision Architecture Workflow v1.0_  
_Date: 2025-11-30_  
_For: Ra_

# companion_network - Epic Breakdown

**Author:** Ra
**Date:** 2025-11-30
**Project Level:** Low Complexity
**Target Scale:** Hackathon Demo (MVP)

---

## Overview

This document provides the complete epic and story breakdown for companion_network, decomposing the requirements from the [PRD](./prd.md) into implementable stories.

**Living Document Notice:** This is the initial version incorporating PRD + UX Design + Architecture context.

## Functional Requirements Inventory

### Agent Core & Identity
- **FR1**: Agent maintains a persistent identity ("Companion") associated with a specific user
- **FR2**: Agent stores and retrieves user context (name, preferences, schedule) from memory
- **FR3**: Agent enforces a "Trusted Contact" list to control access to its MCP tools
- **FR4**: Agent can initiate A2A communication with other known Companions

### Coordination Logic
- **FR5**: Agent can parse natural language requests for coordination (e.g., "Dinner with Bob")
- **FR6**: Agent can determine availability by checking its user's schedule data
- **FR7**: Agent can identify overlapping free slots between its user and another Companion
- **FR8**: Agent can synthesize a recommendation based on mutual availability and preferences
- **FR9**: Agent can propose specific events to its user for confirmation

### MCP Server (Inbound)
- **FR10**: System exposes `check_availability` tool to trusted Companions
- **FR11**: System exposes `propose_event` tool to trusted Companions
- **FR12**: System exposes `share_context` tool to trusted Companions
- **FR13**: System exposes `relay_message` tool to trusted Companions
- **FR14**: System validates "requester" field against Trusted Contact list before executing tools

### MCP Client (Outbound)
- **FR15**: Agent can discover the MCP endpoint of a target user's Companion
- **FR16**: Agent can call tools on another Companion's MCP server
- **FR17**: Agent handles tool execution errors or timeouts gracefully
- **FR18**: Agent logs all outbound MCP calls for the network activity monitor

### User Interface (Gradio Demo)
- **FR19**: UI displays two distinct chat interfaces (Alice and Bob) side-by-side
- **FR20**: Users can send natural language messages to their respective Companions
- **FR21**: UI displays Companion responses in a conversational format
- **FR22**: UI updates in real-time without requiring page refreshes

### Network Visualization
- **FR23**: UI displays a log of all Companion-to-Companion (A2A) interactions
- **FR24**: Log entries include timestamp, sender, receiver, tool called, and key parameters
- **FR25**: UI provides visual indication when A2A communication is active

### Data & State
- **FR26**: System initializes with pre-configured data for the demo scenario (Alice/Bob)
- **FR27**: System stores user preferences (cuisine, time) in a structured format
- **FR28**: System stores user schedule (busy/free blocks) in a structured format
- **FR29**: System maintains sharing rules mapping contacts to allowed information categories
- **FR30**: System tracks the lifecycle state of an event proposal (proposed → pending → accepted/declined)
- **FR31**: System prevents conflicting event proposals for the same timeslot

---

## Epics Summary

This project is decomposed into **4 epics** that deliver incremental user value:

**Epic 1: Foundation & Project Setup** (FR26)  
Establish the development environment, project structure, and core dependencies. This greenfield foundation enables all subsequent development.

**Epic 2: Companion Agent Core** (FR1-FR9, FR15-FR18, FR27-FR29)  
Build Alice and Bob's intelligent Companion agents with A2A coordination capability. Users can delegate coordination tasks, and Companions communicate autonomously to negotiate plans.

**Epic 3: MCP Tool Integration** (FR10-FR14)  
Expose the 4 MCP tools (`check_availability`, `propose_event`, `share_context`, `relay_message`) that enable Companions to interact with each other. Implements privacy-aware information sharing.

**Epic 4: Gradio Demo Interface** (FR19-FR25, FR30-FR31)  
Create the split-screen Gradio UI showing both Companions coordinating in real-time, plus network activity visualization. Demonstrates the complete A2A coordination flow to hackathon judges.

---

## FR Coverage Map

| Epic | Functional Requirements | User Value Delivered |
|------|------------------------|----------------------|
| **Epic 1: Foundation** | FR26 | Development environment ready for agent implementation |
| **Epic 2: Companion Agent Core** | FR1-FR9, FR15-FR18, FR27-FR29 | Users can delegate coordination; Companions negotiate autonomously |
| **Epic 3: MCP Tool Integration** | FR10-FR14 | Companions can query each other's availability and share context securely |
| **Epic 4: Gradio Demo Interface** | FR19-FR25, FR30-FR31 | Complete visual demonstration of A2A coordination for hackathon judges |

**Verification:** All 31 FRs are mapped across 4 epics. ✓

---

## Epic 1: Foundation & Project Setup

**Goal:** Establish the development environment, project structure, and core dependencies to enable all subsequent agent development.

**FRs Covered:** FR26

**Value Delivered:** Development environment ready for agent implementation

---

### Story 1.1: Initialize Development Environment with Modern Tooling

As a developer,  
I want a properly configured Python development environment with modern dependency management,  
So that I can develop the Companion Network efficiently with fast package installation and reproducible builds.

**Acceptance Criteria:**

**Given** a clean development machine  
**When** I follow the setup commands  
**Then** the following are installed and verified:
- uv (ultra-fast Python package manager) v1.0+
- Python 3.10+ runtime
- Virtual environment created via `uv venv`
- Virtual environment activated successfully

**And** running `uv --version` shows installed version  
**And** running `python --version` shows Python 3.10 or later  
**And** the `.venv` directory exists in the project root

**Prerequisites:** None (first story)

**Technical Notes:**
- Use uv installation scripts from architecture doc (Windows: PowerShell, macOS/Linux: curl)
- uv provides 10-100x faster package installation vs pip (`from docs/architecture.md` ADR-005)
- Replaces pip, venv, and pip-tools with unified tooling
- Virtual environment isolates dependencies

---

### Story 1.2: Initialize Project Structure with ADK Foundation

As a developer,  
I want the complete project folder structure established,  
So that I have organized locations for Alice's agent, Bob's agent, shared utilities, and the Gradio UI.

**Acceptance Criteria: **

**Given** the development environment is ready (Story 1.1)  
**When** I initialize the project structure  
**Then** the following directories and files exist:
```
companion_network/
├── alice_companion/
│   ├── __init__.py
│   ├── agent.py
│   ├── mcp_server.py
│   ├── mcp_client.py
│   ├── user_context.py
│   └── a2a_config.json
├── bob_companion/
│   ├── __init__.py
│   ├── agent.py
│   ├── mcp_server.py
│   ├── mcp_client.py
│   ├── user_context.py
│   └── a2a_config.json
├── shared/
│   ├── __init__.py
│   ├── models.py
│   ├── schemas.py
│   └── logger.py
├── app.py
├── pyproject.toml
├── uv.lock
├── .env.example
└── .gitignore
```

**And** each Python package has proper `__init__.py` files  
**And** `.env.example` contains template environment variables (without secrets)  
**And** `.gitignore` follows Python AI project best practices (`from docs/architecture.md` Version Control section)

**Prerequisites:** Story 1.1 (environment ready)

**Technical Notes:**
- Use `adk create alice_companion` and `adk create bob_companion` for ADK agent scaffolding
- `pyproject.toml` defines project metadata per Architecture doc (`from docs/architecture.md` lines 334-350)
- `.gitignore` must exclude `.env`, `*.db`, `.venv`, `__pycache__` (critical for security)
- Each Companion subdirectory acts as a Python package

---

### Story 1.3: Install Core Dependencies

As a developer,  
I want all necessary Python packages installed,  
So that I can use Google ADK, MCP SDK, Gradio, and environment management.

**Acceptance Criteria:**

**Given** the project structure is initialized (Story 1.2)  
**When** I install dependencies using uv  
**Then** the following packages are installed in the virtual environment:
- `google-adk >= 1.19.0` (agent framework with A2A support)
- `mcp[cli] >= 1.22.0` (MCP Python SDK with server/client)
- `gradio` (latest stable - UI framework)
- `python-dotenv` (environment variable management)

**And** running `uv pip list` shows all 4 core packages  
**And** the `uv.lock` file is generated with exact dependency versions  
**And** `uv.lock` is committed to Git for reproducibility

**Prerequisites:** Story 1.2 (project structure exists)

**Technical Notes:**
- Installation command: `uv pip install google-adk mcp[cli] gradio python-dotenv`
- uv automatically resolves dependencies and creates lock file
- Lock file ensures exact same versions across all development environments
- **CRITICAL**: Always commit `uv.lock` to version control (`from docs/architecture.md` ADR-005)

---

### Story 1.4: Configure Environment Variables and Secrets

As a developer,  
I want secure API key management,  
So that I can authenticate with Gemini 2.5 Pro without exposing secrets in version control.

**Acceptance Criteria:**

**Given** dependencies are installed (Story 1.3)  
**When** I configure environment variables  
**Then** the following are set up:
- `.env` file created in project root (gitignored - not committed)
- `.env` contains `GOOGLE_API_KEY=<actual_api_key>`
- `.env.example` contains `GOOGLE_API_KEY=your_api_key_here` (template)
- `.gitignore` includes `.env` to prevent accidental commits

**And** running `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OK' if os.getenv('GOOGLE_API_KEY') else 'MISSING') "` prints `OK`  
**And** `.env` file is NOT tracked by Git (`git status` does not show `.env`)  
**And** `.env.example` IS tracked by Git (provides template for other developers)

**Prerequisites:** Story 1.3 (python-dotenv installed)

**Technical Notes:**
- Use `python-dotenv` to load environment variables from `.env` file
- **SECURITY**: `.env` must NEVER be committed (`from docs/architecture.md` lines 151-152)
- Gemini API key from Google AI Studio: https://aistudio.google.com/apikey
- `.env.example` serves as documentation for required variables

---

### Story 1.5: Initialize Git Repository with Best Practices

As a developer,  
I want proper version control from the start,  
So that I can track changes, collaborate effectively, and follow Python AI project conventions.

**Acceptance Criteria:**

**Given** project structure and dependencies are configured (Stories 1.2-1.4)  
**When** I initialize Git and make the first commit  
**Then** the following are completed:
- Git repository initialized (`git init`)
- `.gitignore` properly configured for Python AI projects
- `.gitattributes` configured (if using Git LFS for future model files)
- Initial commit includes: `README.md`, `pyproject.toml`, `uv.lock`, `.env.example`, `.gitignore`, project structure
- Initial commit message: `\"Initial project setup with ADK, MCP, and Gradio\"`

**And** `.env` file is NOT committed (verified via `git log --all --decorate -- .env` returns empty)  
**And** `uv.lock` IS committed (ensures reproducibility)  
**And** running `git status` shows clean working directory after initial commit  
**And** `.gitignore` excludes: `.env`, `*.db`, `.venv`, `__pycache__`, `*.pyc`

**Prerequisites:** Stories 1.2-1.4 (project fully configured)

**Technical Notes:**
- Use `.gitignore` template from `docs/architecture.md` Version Control section (lines 127-195)
- Commit `uv.lock` for reproducible builds across environments
- Atomic commit: all fundamental setup in one commit
- Branch strategy: `main` for stable, `dev` for active work (`from docs/architecture.md` lines 112-114)

---

### Story 1.6: Create Project README with Setup Instructions

As a developer or hackathon judge,  
I want clear documentation on what the project is and how to run it,  
So that anyone can understand and execute the demo without extensive explanation.

**Acceptance Criteria:**

**Given** the project is initialized and in Git (Story 1.5)  
**When** I create the `README.md` file  
**Then** it includes the following sections:
- **Project Title**: "Companion Network - Agent-to-Agent Coordination Demo"
- **Description**: Brief explanation of A2A coordination eliminating "coordination tax"
- **Prerequisites**: Python 3.10+, uv, Google API key
- **Setup Instructions**: Step-by-step commands to clone, install, configure, and run
- **Demo Scenario**: What to expect when running (`app.py` shows split-screen UI, Alice coordinates with Bob)
- **Architecture**: Link to `docs/architecture.md` for technical details
- **Hackathon Context**: MCP Hackathon, Kaggle AI Agents, Google Gemini Award

**And** following the setup instructions from scratch on a clean machine succeeds  
**And** README includes command: `python app.py` to launch the demo  
**And** README explains expected output: Gradio UI at `localhost:7860`

**Prerequisites:** Story 1.5 (Git initialized)

**Technical Notes:**
- README serves dual purpose: developer onboarding + judge evaluation
- Must be concise but complete (judges may review GitHub repo)
- Include links to PRD (`docs/prd.md`) and Architecture (`docs/architecture.md`)
- Provide example `.env` setup: `echo \"GOOGLE_API_KEY=your_key\" > .env`

---

## Epic 2: Companion Agent Core

**Goal:** Build Alice and Bob's intelligent Companion agents with A2A coordination capability. Users can delegate coordination tasks, and Companions communicate autonomously to negotiate plans.

**FRs Covered:** FR1-FR9, FR15-FR18, FR27-FR29

**Value Delivered:** Users can delegate coordination; Companions negotiate autonomously

---

### Story 2.1: Define User Context Data Models

As a developer,  
I want structured data models for user context information,  
So that each Companion can store and retrieve user preferences, schedules, and sharing rules in a type-safe manner.

**Acceptance Criteria:**

**Given** the foundation is established (Epic 1)  
**When** I create the data models  
**Then** the following Python dataclasses are defined in `shared/models.py`:
- `UserContext` with fields: user_id, name, preferences (dict), schedule (dict), trusted_contacts (list), sharing_rules (dict)
- `EventProposal` with fields: event_id, proposer, recipient, status, details (dict), timestamp
- `SharingRule` with fields: contact_id, allowed_categories (list)

**And** each dataclass uses Python 3.10+ type hints for IDE support  
**And** default factories prevent mutable default argument issues  
**And** models match the schemas from Architecture doc (`docs/architecture.md` lines 498-531)

**Prerequisites:** Story 1.6 (project structure complete)

**Technical Notes:**
- Use `dataclasses` module (Python stdlib)
- UserContext.preferences stores: cuisine types, dining_times, weekend_availability
- UserContext.schedule stores: busy_slots as ISO 8601 time ranges
- EventProposal.status: enum values "pending", "accepted", "declined", "counter"
- These models are shared across both Alice and Bob's agents

---

### Story 2.2: Initialize Alice's Companion Agent with ADK

As a developer,  
I want Alice's Companion agent initialized using Google ADK,  
So that Alice has an intelligent agent with persistent identity and memory.

**Acceptance Criteria:**

**Given** data models are defined (Story 2.1)  
**When** I implement `alice_companion/agent.py`  
**Then** the agent is configured with:
- Agent name: "Alice's Companion"
- Model: Gemini 2.5 Pro (`gemini-2.5-pro`)
- System instruction: "You are Alice's personal Companion agent. You coordinate plans on Alice's behalf..."
- SessionService: DatabaseSessionService with SQLite (`companion_sessions.db`)
- MemoryService: InMemoryMemoryService (non-persistent)
- Session ID: "alice_session"

**And** agent can be instantiated without errors  
**And** agent.run() method is available for processing messages  
**And** session state persists across agent restarts (SQLite database)

**Prerequisites:** Story 2.1 (data models exist)

**Technical Notes:**
- Follow Architecture doc ADR-001 (Gemini 2.5 Pro for stability, not 3 Pro preview)
- Follow Architecture doc ADR-002 (SQLite for session persistence)
- Follow Architecture doc ADR-004 (InMemory for long-term memory - MVP doesn't need persistence)
- System instruction should emphasize: coordination, privacy, natural conversation
- Agent initialization code pattern from ADK documentation
- FR1 satisfied: persistent identity

---

### Story 2.3: Initialize Bob's Companion Agent with ADK

As a developer,  
I want Bob's Companion agent initialized using Google ADK,  
So that Bob has an intelligent agent that mirrors Alice's capabilities.

**Acceptance Criteria:**

**Given** Alice's agent is implemented (Story 2.2)  
**When** I implement `bob_companion/agent.py`  
**Then** the agent is configured with:
- Agent name: "Bob's Companion"
- Model: Gemini 2.5 Pro (`gemini-2.5-pro`)  
- System instruction: "You are Bob's personal Companion agent. You coordinate plans on Bob's behalf..."
- SessionService: DatabaseSessionService with same SQLite file
- MemoryService: InMemoryMemoryService
- Session ID: "bob_session"

**And** both agents can run concurrently without session conflicts  
**And** Bob's agent has identical capabilities to Alice's  
**And** each agent uses separate session IDs to prevent state collision

**Prerequisites:** Story 2.2 (Alice's agent complete)

**Technical Notes:**
- Duplicate Alice's setup with Bob-specific configuration
- Both agents share same `companion_sessions.db` but different session IDs
- Shared SQLite file allows inspecting both agents' state during development
- Consider creating a shared agent factory function to reduce code duplication

---

### Story 2.4: Load Pre-configured User Context for Demo

As a developer,  
I want Alice and Bob's user contexts pre-configured with demo data,  
So that the hackathon demo scenario works without manual data entry.

**Acceptance Criteria:**

**Given** both agents are initialized (Stories 2.2-2.3)  
**When** I implement `{alice,bob}_companion/user_context.py`  
**Then** Alice's context includes:
- User ID: "alice", Name: "Alice"
- Preferences: cuisine = ["Italian", "Thai", "Sushi"], dining_times = ["19:00", "19:30", "20:00"]
- Schedule: busy_slots = (demo weekend with some conflicts)
- Trusted contacts: ["bob"]
- Sharing rules: {"bob": ["availability", "cuisine_preferences"]}

**And** Bob's context includes:
- User ID: "bob", Name: "Bob"
- Preferences: cuisine = ["Italian", "Mexican"], dining_times = ["18:30", "19:00"]
- Schedule: busy_slots = (complementary to Alice's schedule)
- Trusted contacts: ["alice"]
- Sharing rules: {"alice": ["availability", "cuisine_preferences"]}

**And** both contexts are loaded into agent session state on initialization  
**And** agents can retrieve context via session state access

**Prerequisites:** Stories 2.2-2.3 (agents initialized)

**Technical Notes:**
- Store context in agents' DatabaseSessionService under session scope
- Use UserContext dataclass from Story 2.1
- Demo data from PRD lines 329-346 (Alice) and symmetric Bob data
- Context loading happens in agent initialization, not every message
- FR2, FR26, FR27, FR28, FR29 satisfied

---

### Story 2.5: Implement Natural Language Coordination Request Parsing

As Alice,  
I want to tell my Companion "Find a time for dinner with Bob this weekend",  
So that my agent understands my coordination intent without rigid command syntax.

**Acceptance Criteria:**

**Given** Alice's agent has her user context loaded (Story 2.4)  
**When** Alice sends message: "Find a time for dinner with Bob this weekend"  
**Then** the agent reasoning extracts:
- **Coordination type**: "dinner"
- **Other party**: "Bob"
- **Timeframe**: "this weekend" (Saturday-Sunday)
- **Intent**: Initiate coordination

**And** agent responds with natural language acknowledgment: "I'll coordinate with Bob's Companion to find a time for dinner this weekend..."  
**And** agent identifies need to contact Bob's Companion  
**And** no rigid command parsing required (natural language understanding)

**Prerequisites:** Story 2.4 (context loaded)

**Technical Notes:**
- Leverage Gemini 2.5 Pro's natural language understanding
- System prompt should include examples of coordination requests
- Agent should extract: activity type, participants, time constraints
- FR5 satisfied: parse natural language coordination requests
- NFR Usability: Natural language, conversational tone

---

### Story 2.6: Implement A2A Endpoint Discovery and MCP Client Setup

As Alice's Companion,  
I want to discover Bob's Companion's MCP endpoint,  
So that I can call tools on his MCP server to coordinate.

**Acceptance Criteria:**

**Given** Bob's identity is extracted from coordination request (Story 2.5)  
**When** Alice's agent needs to contact Bob's Companion  
**Then** the MCP client is configured with:
- Bob's endpoint: `http://localhost:8002/run` (hardcoded for MVP)
- JSON-RPC 2.0 protocol
- HTTP transport

**And** Alice's agent can call tools on Bob's MCP server  
**And** MCP client handles connection establishment  
**And** endpoint discovery is simplified (hardcoded per ADR-003)

**Prerequisites:** Story 2.5 (coordination intent identified)

**Technical Notes:**
- Follow Architecture doc ADR-003 (hardcoded endpoints for 2-agent demo)
- Alice: `localhost:8001`, Bob: `localhost:8002`
- Use MCP Python SDK's client functionality
- For production, would use Agent Cards for dynamic discovery
- FR15 satisfied: discover MCP endpoint
- Implement in `alice_companion/mcp_client.py` and `bob_companion/mcp_client.py`

---

### Story 2.7: Implement Agent Availability Checking Logic

As Alice's Companion,  
I want to check Alice's availability for the requested timeframe,  
So that I can identify when she's free for the proposed dinner.

**Acceptance Criteria:**

**Given** coordination request specifies "this weekend" (Story 2.5)  
**When** the agent checks Alice's availability  
**Then** the agent logic:
- Retrieves Alice's schedule from session state (busy_slots)
- Parses "this weekend" into specific date range (Saturday-Sunday)
- Identifies free time slots by excluding busy_slots
- Considers Alice's dining_times preferences (19:00, 19:30, 20:00)
- Returns available slots as ISO 8601 time ranges

**And** agent can list 3-5 candidate time slots  
**And** slots align with Alice's preferences when possible  
**And** logic handles edge cases (all times busy, no preferences match)

**Prerequisites:** Story 2.4 (schedule data loaded)

**Technical Notes:**
- FR6 satisfied: determine availability by checking schedule data
- Use Python datetime/timedelta for time calculations
- Schedule.busy_slots format: ["2024-12-07T14:00:00/2024-12-07T16:00:00"]
- Preferences.dining_times are preferred start times, not constraints
- Consider duration: dinner typically 2 hours

---

### Story 2.8: Implement A2A Communication with Error Handling

As Alice's Companion,  
I want to call tools on Bob's Companion's MCP server,  
So that I can coordinate dinner plans across both users.

**Acceptance Criteria:**

**Given** MCP client is configured (Story 2.6)  
**When** Alice's agent calls a tool on Bob's server (e.g., `check_availability`)  
**Then** the call:
- Uses JSON-RPC 2.0 over HTTP POST
- Includes tool name and parameters
- Receives structured response from Bob's MCP server
- Logs the call for network activity monitor

**And** if the call succeeds, the agent processes the response  
**And** if the call fails, the agent retries once  
**And** if retry fails, the agent reports error to Alice gracefully  
**And** all calls are logged to `app:a2a_events` list for Gradio visualization

**Prerequisites:** Story 2.6 (MCP client setup)

**Technical Notes:**
- Follow error handling pattern from Architecture doc lines 410-424
- FR16 satisfied: call tools on another Companion's MCP server
- FR17 satisfied: handle errors/timeouts gracefully
- FR18 satisfied: log all outbound MCP calls
- Use async/await for non-blocking calls
- Log format from Architecture doc lines 428-440
- NFR: Demo must never crash - always provide user feedback

---

### Story 2.9: Implement Coordination Logic with Mutual Availability

As Alice's Companion,  
I want to synthesize Alice and Bob's availability into a recommendation,  
So that I can propose a time that works for both users.

**Acceptance Criteria:**

**Given** Alice's availability is known (Story 2.7)  
**And** Bob's availability is retrieved via A2A (Story 2.8 calling `check_availability`)  
**When** the agent identifies overlapping free slots  
**Then** the coordination logic:
- Finds time slots where both are available
- Considers both users' dining time preferences
- Considers cuisine preferences if Bob shared them
- Synthesizes recommendation: "Saturday 7pm, Bob prefers Italian"

**And** if multiple slots available, prioritizes based on preferences  
**And** if no overlaps, suggests alternatives or asks users for flexibility  
**And** recommendation is natural language, not just raw data

**Prerequisites:** Stories 2.7-2.8 (availability checking and A2A calls)

**Technical Notes:**
- FR7 satisfied: identify overlapping free slots
- FR8 satisfied: synthesize recommendation based on availability and preferences
- Algorithm: intersect Alice's free slots with Bob's free slots
- Preference matching: if both have "Italian" in cuisine lists, note it
- Use Gemini's reasoning to create natural recommendation text
- Consider timezone handling (simplified for MVP: assume same timezone)

---

### Story 2.10: Implement Event Proposal to User

As Alice's Companion,  
I want to propose the coordinated dinner to Alice for confirmation,  
So that she can approve before finalizing with Bob.

**Acceptance Criteria:**

**Given** a recommendation is synthesized (Story 2.9)  
**When** the agent presents the proposal to Alice  
**Then** the message includes:
- Proposed time: "Saturday, December 7th at 7:00pm"
- Duration: "2 hours"
- Participant: "Bob"
- Additional context: "Bob is in the mood for Italian"
- Call to action: "Should I confirm this with Bob?"

**And** the proposal is stored in session state as EventProposal object  
**And** proposal status is "pending" awaiting Alice's confirmation  
**And** message feels natural and conversational (not robotic)

**Prerequisites:** Story 2.9 (recommendation ready)

**Technical Notes:**
- FR9 satisfied: propose specific events to user for confirmation
- FR4 satisfied: agent can initiate A2A communication
- FR3 satisfied: enforces trusted contact list (Bob is in Alice's trusted_contacts)
- Use EventProposal dataclass from Story 2.1
- Store proposal in session state under unique event_id
- Proposal waits for Alice's next message ("yes", "confirm", "sounds good")
- NFR Usability: Natural language, not JSON dumps
- UX Design: conversational chat interface from Gradio spec

---
## Epic 3: MCP Tool Integration

**Goal:** Expose the 4 MCP tools (`check_availability`, `propose_event`, `share_context`, `relay_message`) that enable Companions to interact with each other. Implements privacy-aware information sharing.

**FRs Covered:** FR10-FR14

**Value Delivered:** Companions can query each other's availability and share context securely

---

### Story 3.1: Implement `check_availability` MCP Tool

As Bob's Companion,  
I want to expose a `check_availability` tool via MCP server,  
So that Alice's Companion can query Bob's availability for coordination.

**Acceptance Criteria:**

**Given** Bob's Companion has an MCP server running (Story 2.3)  
**When** Alice's Companion calls `check_availability` tool  
**Then** the tool:
- Accepts parameters: timeframe (ISO 8601 range), event_type (string), duration_minutes (int), requester (string)
- Validates requester is in Bob's trusted_contacts list
- Retrieves Bob's schedule from session state
- Calculates available slots within timeframe
- Returns: available (bool), slots (list), preferences (dict), auto_accept_eligible (bool)

**And** if requester not trusted, returns access denied error  
**And** tool schema is auto-generated from Python function signature  
**And** tool is registered with Bob's MCP server

**Prerequisites:** Story 2.3 (Bob's agent initialized)

**Technical Notes:**
- FR10 satisfied: expose `check_availability` to trusted Companions
- FR14 satisfied: validate requester against trusted contacts
- Implement in `bob_companion/mcp_server.py` (and mirrored in Alice's)
- Use Python type hints for automatic schema generation (MCP SDK feature)
- Access control: check `requester` in `user_context.trusted_contacts`
- Return preferences based on `sharing_rules` for this requester
- Architecture doc lines 535-559 for API contract

---

### Story 3.2: Implement `propose_event` MCP Tool

As Bob's Companion,  
I want to expose a `propose_event` tool via MCP server,  
So that Alice's Companion can propose dinner plans to Bob.

**Acceptance Criteria:**

**Given** Alice's Companion has coordinated a time (Epic 2)  
**When** Alice's Companion calls `propose_event` on Bob's server  
**Then** the tool:
- Accepts parameters: event_name, datetime, location, participants, requester
- Validates requester is in trusted_contacts
- Creates EventProposal object in Bob's session state
- Sets status to "pending"
- Notifies Bob through agent response
- Returns: status (enum), message (string), event_id (string)

**And** if Bob has conflicting events, returns "declined" with reason  
**And** if Bob's auto-accept rules match, returns "accepted"  
**And** otherwise returns "pending" for Bob's manual review

**Prerequisites:** Story 3.1 (MCP server setup)

**Technical Notes:**
- FR11 satisfied: expose `propose_event` to trusted Companions
- FR30 satisfied: track event lifecycle (proposed → pending → accepted/declined)
- FR31 satisfied: prevent conflicting events for same timeslot
- Use EventProposal dataclass from Story 2.1
- Check for schedule conflicts before accepting
- Architecture doc lines 561-585 for API contract

---

### Story 3.3: Implement `share_context` MCP Tool

As Bob's Companion,  
I want to expose a `share_context` tool via MCP server,  
So that Alice's Companion can request Bob's preferences for coordination.

**Acceptance Criteria:**

**Given** Alice's Companion needs Bob's cuisine preferences  
**When** Alice's Companion calls `share_context` tool  
**Then** the tool:
- Accepts parameters: category (enum), purpose (string), requester (string)
- Validates requester is in trusted_contacts
- Checks `sharing_rules[requester]` for allowed categories
- Returns context_data if category is allowed
- Returns access_denied if category not permitted

**And** category enum includes: preferences, dietary, schedule, interests  
**And** only data explicitly allowed by sharing rules is returned  
**And** privacy protection: never expose data not in sharing rules

**Prerequisites:** Story 3.2 (other tools established)

**Technical Notes:**
- FR12 satisfied: expose `share_context` to trusted Companions
- NFR Privacy: strict adherence to sharing rules (data minimization)
- NFR Contextual Integrity: purpose logged but not enforced in MVP
- Check `user_context.sharing_rules[requester]` contains category
- Example: if Alice is allowed "cuisine_preferences", return those; deny "schedule"
- Architecture doc lines 587-608 for API contract

---

### Story 3.4: Implement `relay_message` MCP Tool

As Bob's Companion,  
I want to expose a `relay_message` tool via MCP server,  
So that Alice's Companion can send messages to Bob through his Companion.

**Acceptance Criteria:**

**Given** Alice's Companion needs to notify Bob  
**When** Alice's Companion calls `relay_message` tool  
**Then** the tool:
- Accepts parameters: message (string), urgency (enum: low/normal/high), sender (string)
- Validates sender is in trusted_contacts
- Queues message for Bob's next interaction
- Returns: delivered (bool)

**And** message appears in Bob's Companion chat interface  
**And** urgency affects display priority  
**And** sender attribution is clear: "Message from Alice: ..."

**Prerequisites:** Story 3.3 (all other tools complete)

**Technical Notes:**
- FR13 satisfied: expose `relay_message` to trusted Companions
- Store messages in session state: `session:pending_messages` list
- Display in Gradio chat when Bob's Companion sends next response
- Use case: "Alice confirmed dinner for Saturday 7pm"
- Architecture doc lines 610-630 for API contract

---

## Epic 4: Gradio Demo Interface

**Goal:** Create the split-screen Gradio UI showing both Companions coordinating in real-time, plus network activity visualization. Demonstrates the complete A2A coordination flow to hackathon judges.

**FRs Covered:** FR19-FR25, FR30-FR31

**Value Delivered:** Complete visual demonstration of A2A coordination for hackathon judges

---

### Story 4.1: Create Gradio Split-Screen Layout

As a demo viewer,  
I want to see Alice and Bob's chat interfaces side-by-side,  
So that I can observe both Companions coordinating simultaneously.

**Acceptance Criteria:**

**Given** the Gradio app is launched (Story 1.6 setup)  
**When** I open the browser to `localhost:7860`  
**Then** the interface displays:
- Left panel: "Alice's Companion" with chat interface
- Right panel: "Bob's Companion" with chat interface
- Bottom panel: "Network Activity Monitor"
- Clean, minimal design (from UX Design spec)

**And** each chat panel has input textbox and submit button  
**And** chat history displays in conversational format  
**And** layout is responsive (desktop-first per UX spec)

**Prerequisites:** Epic 1 (project setup), Epic 2 (agents exist)

**Technical Notes:**
- FR19 satisfied: two distinct chat interfaces side-by-side
- Use Gradio Blocks with Row/Column layout
- UX Design: Gradio Base theme + custom CSS for clean minimal style
- Split-screen requires ~1200px width minimum (desktop-first)
- Architecture doc lines 813 (Gradio UI component)

---

### Story 4.2: Implement Chat Interface for Alice and Bob

As Alice or Bob,  
I want to send natural language messages to my Companion,  
So that I can request coordination without technical commands.

**Acceptance Criteria:**

**Given** the split-screen layout exists (Story 4.1)  
**When** Alice types "Find a time for dinner with Bob this weekend" and submits  
**Then** Alice's interface:
- Displays her message in chat history
- Shows "thinking..." indicator while agent processes
- Displays Companion's response when ready
- Updates in real-time without page refresh

**And** Bob's interface updates independently when his Companion receives A2A calls  
**And** both interfaces use async event handlers (non-blocking)  
**And** chat history persists during session

**Prerequisites:** Story 4.1 (layout ready)

**Technical Notes:**
- FR20 satisfied: users send natural language messages
- FR21 satisfied: Companion responses in conversational format
- FR22 satisfied: real-time updates without page refresh
- Use Gradio's async event handlers
- Call `agent.run(message)` for each user input
- NFR UI Responsiveness: sub-100ms feedback (immediate message display)
- Store chat history in Gradio State component

---

### Story 4.3: Implement Network Activity Monitor

As a hackathon judge,  
I want to see all A2A communications between Companions,  
So that I understand the agent-to-agent coordination happening behind the scenes.

**Acceptance Criteria:**

**Given** Companions are coordinating (Epic 2)  
**When** Alice's Companion calls `check_availability` on Bob's server  
**Then** the Network Activity Monitor displays:
- Timestamp of the call
- Sender: "Alice's Companion"
- Receiver: "Bob's Companion"
- Tool called: "check_availability"
- Key parameters: timeframe, event_type
- Status: "success" or "failed"

**And** each A2A call is logged in chronological order  
**And** logs display as formatted JSON or structured table  
**And** visual indicator shows when communication is active

**Prerequisites:** Story 4.2 (chat working), Story 2.8 (A2A logging implemented)

**Technical Notes:**
- FR23 satisfied: log of all A2A interactions
- FR24 satisfied: timestamp, sender, receiver, tool, parameters
- FR25 satisfied: visual indication when A2A active
- Read from `app:a2a_events` list (populated by Story 2.8)
- Use Gradio JSON component or DataFrame for display
- Update monitor in real-time as events occur
- Log format from Architecture doc lines 428-440

---

### Story 4.4: Integrate Agents with Gradio UI

As the system,  
I want Alice and Bob's agents orchestrated by the Gradio app,  
So that all components work together in the demo.

**Acceptance Criteria:**

**Given** all components are implemented (Epics 1-3)  
**When** the Gradio app starts (`python app.py`)  
**Then** the system:
- Initializes both Alice and Bob's Companion agents
- Loads their user contexts
- Starts MCP servers on localhost:8001 (Alice) and localhost:8002 (Bob)
- Exposes Gradio UI on localhost:7860
- Handles concurrent user interactions

**And** Alice's input triggers her agent which may call Bob's tools  
**And** Bob's input triggers his agent which may call Alice's tools  
**And** Network monitor updates for all A2A calls  
**And** No deadlocks or race conditions occur

**Prerequisites:** Stories 4.1-4.3 (UI complete)

**Technical Notes:**
- Implement in `app.py` (main orchestrator)
- Initialize agents with `to_a2a()` for A2A endpoints
- Gradio handles concurrency automatically (async event loop)
- NFR Concurrency: simultaneous Alice/Bob processing without deadlock
- NFR A2A Latency: complete coordination within 3-5 seconds
- Architecture doc lines 713-745 for deployment architecture

---

### Story 4.5: End-to-End Demo Scenario Validation

As a hackathon judge,  
I want to see the complete "Plan Dinner" scenario execute successfully,  
So that I can evaluate the A2A coordination demonstration.

**Acceptance Criteria:**

**Given** the complete system is running (Story 4.4)  
**When** I execute the demo scenario:
1. Alice types: "Find a time for dinner with Bob this weekend"
2. Alice's Companion contacts Bob's Companion
3. Companions negotiate availability
4. Alice's Companion proposes: "Saturday 7pm, Bob prefers Italian"
5. Alice types: "Sounds good, confirm it"

**Then** the demo flow completes successfully:
- Alice sees Companion coordinating with Bob
- Bob sees incoming event proposal in his chat
- Network monitor shows all A2A calls
- Event is confirmed in both Companions' session state
- No errors or crashes occur

**And** the entire flow completes within 10 seconds  
**And** all NFRs are satisfied (privacy, performance, reliability, usability)  
**And** Demo is ready for judges

**Prerequisites:** Story 4.4 (full system integrated)

**Technical Notes:**
- This is the acceptance test for the complete MVP
- Validates all 31 FRs are working together
- Test scenario from PRD lines 152-157
- NFR Transparency: users always know when agents are communicating
- NFR Control: users can intervene at any time
- NFR Graceful Degradation: if Bob offline, clear error message

---

## FR Coverage Matrix

| FR | Description | Epic | Stories |
|----|-------------|------|---------|
| FR1 | Persistent agent identity | 2 | 2.2, 2.3 |
| FR2 | Store/retrieve user context | 2 | 2.4 |
| FR3 | Enforce trusted contacts | 2 | 2.10 |
| FR4 | Initiate A2A communication | 2 | 2.10 |
| FR5 | Parse natural language requests | 2 | 2.5 |
| FR6 | Determine availability | 2 | 2.7 |
| FR7 | Identify overlapping slots | 2 | 2.9 |
| FR8 | Synthesize recommendations | 2 | 2.9 |
| FR9 | Propose events to user | 2 | 2.10 |
| FR10 | Expose check_availability tool | 3 | 3.1 |
| FR11 | Expose propose_event tool | 3 | 3.2 |
| FR12 | Expose share_context tool | 3 | 3.3 |
| FR13 | Expose relay_message tool | 3 | 3.4 |
| FR14 | Validate requester (trusted contacts) | 3 | 3.1, 3.2, 3.3, 3.4 |
| FR15 | Discover MCP endpoint | 2 | 2.6 |
| FR16 | Call tools on other Companion | 2 | 2.8 |
| FR17 | Handle errors gracefully | 2 | 2.8 |
| FR18 | Log outbound MCP calls | 2 | 2.8 |
| FR19 | Split-screen UI (Alice & Bob) | 4 | 4.1 |
| FR20 | Send natural language messages | 4 | 4.2 |
| FR21 | Display conversational responses | 4 | 4.2 |
| FR22 | Real-time UI updates | 4 | 4.2 |
| FR23 | Display A2A interaction log | 4 | 4.3 |
| FR24 | Log details (timestamp, sender, receiver, tool) | 4 | 4.3 |
| FR25 | Visual A2A activity indicator | 4 | 4.3 |
| FR26 | Pre-configured demo data | 1, 2 | 1.2, 2.4 |
| FR27 | Store preferences (structured) | 2 | 2.1, 2.4 |
| FR28 | Store schedule (structured) | 2 | 2.1, 2.4 |
| FR29 | Maintain sharing rules | 2 | 2.1, 2.4 |
| FR30 | Track event lifecycle | 3 | 3.2 |
| FR31 | Prevent conflicting events | 3 | 3.2 |

**Verification:** All 31 functional requirements mapped to specific stories across 4 epics. ✓

---

## Summary

This epic breakdown transforms the Companion Network PRD into **25 implementable stories** organized across **4 value-driven epics**:

- **Epic 1: Foundation** (6 stories) - Modern Python environment with uv, ADK structure, Git best practices
- **Epic 2: Companion Agent Core** (10 stories) - Intelligent agents with A2A coordination, the primary user value
- **Epic 3: MCP Tool Integration** (4 stories) - Privacy-aware tools enabling secure A2A communication
- **Epic 4: Gradio Demo Interface** (5 stories) - Visual demonstration for hackathon judges

**Each story includes:**
- BDD-style acceptance criteria (Given/When/Then/And)
- Clear prerequisites (dependency tracking)
- Technical implementation notes from Architecture doc
- FR traceability

**Context Incorporated:**
- ✅ PRD requirements (all 31 FRs)
- ✅ UX interaction patterns (clean minimal Gradio interface)
- ✅ Architecture technical decisions (Gemini 2.5 Pro, uv, SQLite, A2A Protocol)

**Status:** COMPLETE - Ready for Phase 4 Implementation!

---

_For implementation: Use the `dev-story` workflow to implement each story sequentially._

_This document will serve as the source of truth for epic/story breakdown during development._

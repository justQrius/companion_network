# companion_network - Product Requirements Document

**Author:** Ra
**Date:** 2025-11-30
**Version:** 1.0

---

## Executive Summary

Companion Network demonstrates a fundamental shift in how AI assistants work: from single-user helpers to a coordinated network of agents that communicate on behalf of their humans. Built for the MCP Hackathon, Kaggle AI Agents Intensive, and Google Gemini Award, this project showcases agent-to-agent (A2A) coordination as the solution to the invisible "coordination tax" that drains hours from our lives.

Every multi-person activity—dinner plans, meetings, group activities—requires coordination overhead: back-and-forth messages asking "when are you free?", mental tracking of who knows what, and one person becoming the switchboard for everyone else. Current solutions (shared calendars, group chats, AI assistants) fail because they only help one person at a time. They can't coordinate across people.

Companion Network changes this. Two personal AI Companions communicate with each other—via Google's A2A Protocol and MCP—to negotiate availability, share preferences (with privacy controls), and coordinate plans. Alice says "Find a time for dinner with Bob this weekend," and her Companion talks to Bob's Companion to make it happen. No group chat noise. No back-and-forth texting. Just results.

The hackathon MVP demonstrates this with a split-screen Gradio interface showing both Companions coordinating in real-time, plus a network activity monitor visualizing the A2A communication. This is the only hackathon project that meaningfully uses A2A Protocol, and it uses more ADK capabilities (agents, MCP server, MCP client, memory, sessions, A2A) than any other concept.

### What Makes This Special

**Eliminating the coordination tax.** 

Companion Network gives back the hours we lose to logistics. Instead of eight messages to schedule dinner, it's one request to your Companion. The coordination happens automatically, intelligently, privately—between AIs who know their humans' preferences, schedules, and boundaries. You focus on living. Your Companion handles the coordination.

---

## Project Classification

**Technical Type:** Hybrid (Web App + Developer Tool)
**Domain:** Consumer / General
**Complexity:** Low

**Hybrid Architecture Rationale:**

This project has dual deliverables that are equally critical:

1. **Web App (Gradio Demo)** - The immediate hackathon deliverable is a functioning Gradio application that demonstrates agent-to-agent coordination through a split-screen interface. This is what judges will see and interact with.

2. **Developer Tool (Companion Framework)** - The underlying architecture is designed as a reusable framework: each Companion is an MCP Server that exposes coordination tools, making the pattern extensible beyond the demo. The framework itself is valuable for developers building multi-agent coordination systems.

The Web App showcases the concept; the Developer Tool makes it transferable. Both are first-class deliverables.

**Domain Classification:**

Consumer coordination falls in the "general" domain (low complexity). This is not healthcare, fintech, or regulated industry software. There are no compliance requirements, safety certifications, or domain-specific regulatory frameworks. The complexity comes from the technical implementation (A2A protocol, MCP servers, multi-agent orchestration), not from domain constraints.

**Referenced Documents:**
- Product Brief: `docs/companion_network.md` (comprehensive technical architecture and demo scenario)
- Research Documents: None (general domain, no specialized research needed)
- Domain Brief: None (not applicable for general consumer domain)

---

## Success Criteria

### Hackathon Success (Immediate)

Success for the hackathon demo means judges experience three distinct reactions:

1. **"I've never seen that before"** - The A2A coordination moment is genuinely novel. When Alice's Companion reaches out to Bob's Companion and they negotiate in real-time, judges recognize this as a new paradigm in AI assistants.

2. **"This solves a real problem"** - Every judge has experienced the coordination tax. They immediately relate to the pain of 5-8 messages just to schedule dinner and see how this eliminates it.

3. **"This uses ADK better than anything else"** - The technical showcase is obvious: A2A Protocol, MCP server/client dual role, multi-agent orchestration, memory, sessions—all working together in a cohesive demo.

**Competition-Specific Success Metrics:**

- **MCP Hackathon Track 1 (Building MCP → Consumer):**
  - ✅ Each Companion is a functioning MCP Server exposing 4+ coordination tools
  - ✅ Tools are well-documented with clear schemas
  - ✅ Demonstrates novel "social" MCP server pattern (agents calling other agents' servers)

- **MCP Hackathon Track 2 (MCP in Action → Consumer):**
  - ✅ Gradio application with split-screen interface showing both Companions
  - ✅ Autonomous A2A coordination visible in real-time
  - ✅ Network activity monitor showing MCP tool calls between Companions
  - ✅ Context engineering: user preferences, relationship trust levels, sharing rules

- **Kaggle AI Agents Intensive Capstone:**
  - ✅ Multi-agent system with clear orchestration (Coordinator + Scheduler agents per Companion)
  - ✅ Tool usage across agent boundaries (MCP client/server)
  - ✅ Demonstrates advanced agent patterns: delegation, negotiation, context sharing

- **Google Gemini Award:**
  - ✅ Powered by Gemini 2.5 Pro for both Companions
  - ✅ Only project meaningfully using A2A Protocol (the core differentiator)
  - ✅ Showcases ADK capabilities more comprehensively than other submissions
  - ✅ Novel concept with real-world value

### Product Success (Beyond Hackathon)

Success means users experience **effortless coordination** that feels like magic:

**The Key Success Moment:**
User says "Find a time for dinner with my friend" → 30 seconds later → "Saturday 7pm works for both of you, they're in the mood for Italian" → User thinks "that's magic."

**Measurable Outcomes:**

- **Time Saved:** Coordination tasks that typically require 5-8 messages complete in 1 user request
- **Mental Load Reduced:** Users don't track "who knows what" or "what's confirmed" - their Companion handles state
- **Privacy Maintained:** Users control what information their Companion shares, with whom, and in what context
- **Trust Established:** Coordination feels natural and helpful, not robotic or intrusive
- **Adoption Indicator:** Users proactively use their Companion for coordination instead of defaulting to manual texting

**Success is NOT:**
- High user counts (this is a proof of concept)
- Complex feature sets (MVP focuses on core coordination)
- Perfect accuracy (some coordination will need human confirmation)
- Replacing all communication (augmenting, not replacing human interaction)

---

## Product Scope

### MVP - Minimum Viable Product (Hackathon Deliverable)

The MVP is scoped specifically for the hackathon timeline and demonstrates the core A2A coordination capability:

**Core Coordination Flow:**
- Two Companion agents (Alice and Bob) with pre-configured user contexts
- Basic availability checking via simulated calendar data
- Event proposal and acceptance/decline flow
- A2A communication using Google's A2A Protocol and MCP

**User Interface:**
- Split-screen Gradio application showing both Companions simultaneously
- Chat interface for each user to interact with their Companion
- Network activity monitor displaying real-time A2A communication logs
- Visual indicators showing when Companions are communicating with each other

**User Context (Pre-configured for Demo):**
- Basic preferences: cuisine types (Italian, Thai, etc.), preferred times (evening, weekend)
- Simple schedule: busy/free blocks for the demo weekend
- Trust level: Alice and Bob are marked as trusted contacts for each other
- Sharing rules: Basic approval for sharing availability and food preferences

**MCP Server Tools (Per Companion):**
- `check_availability` - Query availability for a timeframe
- `propose_event` - Propose a specific event with details
- `share_context` - Request approved contextual information
- `relay_message` - Send a message to be relayed to the human

**Technical Stack:**
- Google ADK for agent framework
- Gemini 2.5 Pro as the LLM
- A2A Protocol for Companion-to-Companion communication
- MCP (Python SDK) for tool exposure and calling
- Gradio for UI
- SQLite for session persistence (survives demo restarts)
- uv for dependency management (10-100x faster than pip)

**Demo Scenario:**
- Alice requests: "Find a time for dinner with Bob this weekend"
- Alice's Companion contacts Bob's Companion via A2A
- Bob's Companion checks availability and preferences
- Companions negotiate and propose: "Saturday 7pm, Bob prefers Italian"
- Alice confirms, event is coordinated

**Out of Scope for MVP:**
- Real calendar integration (Google Calendar, Outlook, etc.)
- More than 2 users
- Cloud database or production-grade storage (using local SQLite for demo)
- Mobile interface
- Authentication/user accounts
- Proactive suggestions from Companions
- Complex trust hierarchies or granular sharing controls

### Growth Features (Post-MVP)

**After proving the concept, expand capabilities:**

**Multi-User Coordination:**
- Support 3+ people in a single coordination request
- Group event planning with multiple Companions negotiating
- Handling conflicting preferences across larger groups

**Real Calendar Integration:**
- Connect to Google Calendar, Outlook, Apple Calendar via MCP
- Actual availability checking from live calendars
- Automatic event creation and updates

**Enhanced Context & Learning:**
- Companions learn user preferences over time
- Pattern recognition: "You usually prefer Thai on weekdays"
- Relationship context: "You always meet Sarah at that coffee shop"
- Location awareness and suggestions

**Advanced Sharing Controls:**
- Granular privacy settings per contact
- Context-specific sharing rules: "Share dietary restrictions with close friends only"
- Temporary trust elevation: "For this event, share my exact schedule"

**Proactive Coordination:**
- Companion suggests coordination: "You haven't seen Mike in 3 weeks, want me to check his availability?"
- Automatic rescheduling when conflicts arise
- Follow-up coordination: "Dinner is in 2 hours, should I confirm with Bob?"

**Additional Event Types:**
- Meetings (professional context)
- Group activities (movies, sports, etc.)
- Recurring events (weekly lunch, monthly book club)
- Multi-day coordination (weekend trips, conferences)

### Vision (Future)

**The full Companion Network vision extends beyond coordination:**

**Ecosystem Integration:**
- Companions coordinate with business AI assistants (schedule meetings across companies)
- Integration with smart home, transportation, and reservation systems
- Cross-platform: mobile app, web, voice assistants, wearables

**Advanced AI Capabilities:**
- Predictive coordination: "Based on patterns, scheduling your monthly dinner with Alex"
- Conflict resolution: Companions negotiate when preferences clash
- Context synthesis: "Bob mentioned he's training for a marathon, suggesting earlier dinner times"

**Social Coordination Layer:**
- Gift coordination: Companions help organize group gifts
- Event planning: Birthday parties, weddings, group trips
- Information relay: "Tell everyone about the venue change"

**Developer Platform:**
- Companion SDK for building custom coordination agents
- MCP server templates for different coordination patterns
- Marketplace for Companion extensions and integrations

**Privacy & Trust Infrastructure:**
- Decentralized identity and data ownership
- Cryptographic proof of consent for information sharing
- Audit logs of all A2A communications
- User control over data retention and deletion

**Business Model Exploration:**
- Freemium: Basic coordination free, advanced features paid
- Enterprise: Team coordination for organizations
- API access: Developers building on Companion Network
- Privacy-first monetization: Never selling user data

---

{{#if domain_considerations}}

## Domain-Specific Requirements

{{domain_considerations}}

This section shapes all functional and non-functional requirements below.
{{/if}}

---

{{#if innovation_patterns}}

## Innovation & Novel Patterns

{{innovation_patterns}}

### Validation Approach

{{validation_approach}}
{{/if}}

---

## Hybrid Project Requirements (Web App + Developer Tool)

### Core Architecture

The system follows a hybrid architecture where the **Companion Framework** (Developer Tool) powers the **Demo Application** (Web App).

**Component 1: Companion Agent (The "Backend")**
- **Agent Framework:** Google ADK (Agent Development Kit)
- **Model:** Gemini 2.5 Pro
- **Communication:** A2A Protocol for inter-agent messaging
- **Interface:** MCP Server exposing coordination tools
- **State Management:** In-memory session handling for demo

**Component 2: Demo Interface (The "Frontend")**
- **Framework:** Gradio (Python-based UI)
- **Layout:** Split-screen (Alice View | Bob View)
- **Visualization:** Network Activity Monitor (Log of A2A calls)
- **Interaction:** Chat-based input for human-to-agent communication

### API Specification (MCP Tools)

Each Companion exposes these MCP tools to other Companions:

**1. `check_availability`**
- **Purpose:** Query availability for a proposed timeframe
- **Inputs:** `timeframe` (string), `event_type` (enum), `duration_minutes` (int), `requester` (string)
- **Outputs:** `available` (bool), `slots` (list), `preferences` (dict), `auto_accept_eligible` (bool)

**2. `propose_event`**
- **Purpose:** Propose a specific event to this user
- **Inputs:** `event_name` (string), `datetime` (iso8601), `location` (string), `participants` (list), `requester` (string)
- **Outputs:** `status` (enum: accepted/declined/pending/counter), `message` (string)

**3. `share_context`**
- **Purpose:** Request specific approved context
- **Inputs:** `category` (enum: preferences/dietary/schedule/interests), `purpose` (string), `requester` (string)
- **Outputs:** `context_data` (dict) or `access_denied`

**4. `relay_message`**
- **Purpose:** Send a message to be relayed to the human
- **Inputs:** `message` (string), `urgency` (enum), `sender` (string)
- **Outputs:** `delivered` (bool)

### Authentication & Authorization

**For Hackathon MVP:**
- **Simulated Auth:** Hardcoded identities ("Alice", "Bob") for the demo
- **Trust Model:** "Trusted Contact" list configured in agent initialization
- **Access Control:**
  - `check_availability`: Only allowed if requester is in Trusted Contacts
  - `propose_event`: Only allowed if requester is in Trusted Contacts
  - `share_context`: Checks specific permission flags per category

### Platform Support

**Primary Target:** Web Browser (via Gradio)
- **Responsive:** Desktop-first (split screen requires width), functional on tablet
- **Runtime:** Python 3.10+ environment (local or cloud host)
- **Dependencies:** `google-adk`, `mcp`, `gradio`, `python-dotenv`

### Data Models

**User Context (In-Memory):**
```json
{
  "user_id": "alice",
  "name": "Alice",
  "preferences": {
    "cuisine": ["Italian", "Thai", "Sushi"],
    "dining_times": ["19:00", "19:30", "20:00"],
    "weekend_availability": "high"
  },
  "schedule": {
    "busy_slots": ["2024-12-07T14:00:00/2024-12-07T16:00:00"]
  },
  "trusted_contacts": ["bob"],
  "sharing_rules": {
    "bob": ["availability", "cuisine_preferences"]
  }
}
```

**Event Proposal:**
```json
{
  "event_id": "evt_123",
  "proposer": "alice",
  "recipient": "bob",
  "status": "pending",
  "details": {
    "title": "Dinner at Trattoria",
    "time": "2024-12-07T19:00:00",
    "location": "Trattoria on Main"
  }
}
```

---

## Functional Requirements

### Companion Agent Capabilities

**Agent Core & Identity**
- FR1: Agent maintains a persistent identity ("Companion") associated with a specific user
- FR2: Agent stores and retrieves user context (name, preferences, schedule) from memory
- FR3: Agent enforces a "Trusted Contact" list to control access to its MCP tools
- FR4: Agent can initiate A2A communication with other known Companions

**Coordination Logic**
- FR5: Agent can parse natural language requests for coordination (e.g., "Dinner with Bob")
- FR6: Agent can determine availability by checking its user's schedule data
- FR7: Agent can identify overlapping free slots between its user and another Companion
- FR8: Agent can synthesize a recommendation based on mutual availability and preferences
- FR9: Agent can propose specific events to its user for confirmation

**MCP Server (Inbound)**
- FR10: System exposes `check_availability` tool to trusted Companions
- FR11: System exposes `propose_event` tool to trusted Companions
- FR12: System exposes `share_context` tool to trusted Companions
- FR13: System exposes `relay_message` tool to trusted Companions
- FR14: System validates "requester" field against Trusted Contact list before executing tools

**MCP Client (Outbound)**
- FR15: Agent can discover the MCP endpoint of a target user's Companion
- FR16: Agent can call tools on another Companion's MCP server
- FR17: Agent handles tool execution errors or timeouts gracefully
- FR18: Agent logs all outbound MCP calls for the network activity monitor

### User Interface (Gradio Demo)

**Dual-User View**
- FR19: UI displays two distinct chat interfaces (Alice and Bob) side-by-side
- FR20: Users can send natural language messages to their respective Companions
- FR21: UI displays Companion responses in a conversational format
- FR22: UI updates in real-time without requiring page refreshes

**Network Visualization**
- FR23: UI displays a log of all Companion-to-Companion (A2A) interactions
- FR24: Log entries include timestamp, sender, receiver, tool called, and key parameters
- FR25: UI provides visual indication when A2A communication is active

### Data & State

**User Context Management**
- FR26: System initializes with pre-configured data for the demo scenario (Alice/Bob)
- FR27: System stores user preferences (cuisine, time) in a structured format
- FR28: System stores user schedule (busy/free blocks) in a structured format
- FR29: System maintains sharing rules mapping contacts to allowed information categories

**Event State**
- FR30: System tracks the lifecycle state of an event proposal (proposed → pending → accepted/declined)
- FR31: System prevents conflicting event proposals for the same timeslot

---

## Non-Functional Requirements

### Privacy & Security (Critical)
- **Data Minimization:** Companions must strictly adhere to sharing rules, never exposing data not explicitly allowed for a contact.
- **Contextual Integrity:** Information shared for one purpose (dinner planning) must not be retained or used for unrelated purposes.
- **Local-First Design:** For the demo, user context resides in-memory within the agent instance, not in a central database.
- **Consent:** High-sensitivity actions (booking, sharing location) must require explicit human confirmation.

### Performance (Demo Quality)
- **A2A Latency:** Companion-to-Companion communication should complete within 3-5 seconds to maintain demo flow.
- **UI Responsiveness:** Chat interface must feel "instant" (sub-100ms) even while agents are processing.
- **Concurrency:** System must handle simultaneous processing of Alice and Bob's agents without deadlock.

### Reliability
- **Graceful Degradation:** If one Companion is unreachable, the other should report this clearly to the user rather than crashing.
- **Error Recovery:** Agents should be able to retry failed A2A calls (e.g., timeout) at least once.
- **State Consistency:** Both Companions must agree on the final state of an event (accepted/declined).

### Usability
- **Natural Language:** Agents must communicate in natural, conversational tone, not JSON dumps (except in the network log).

This section shapes all functional and non-functional requirements below.
{{/if}}

---

{{#if innovation_patterns}}

## Innovation & Novel Patterns

{{innovation_patterns}}

### Validation Approach

{{validation_approach}}
{{/if}}

---

## Hybrid Project Requirements (Web App + Developer Tool)

### Core Architecture

The system follows a hybrid architecture where the **Companion Framework** (Developer Tool) powers the **Demo Application** (Web App).

**Component 1: Companion Agent (The "Backend")**
- **Agent Framework:** Google ADK (Agent Development Kit)
- **Model:** Gemini 2.5 Pro
- **Communication:** A2A Protocol for inter-agent messaging
- **Interface:** MCP Server exposing coordination tools
- **State Management:** In-memory session handling for demo

**Component 2: Demo Interface (The "Frontend")**
- **Framework:** Gradio (Python-based UI)
- **Layout:** Split-screen (Alice View | Bob View)
- **Visualization:** Network Activity Monitor (Log of A2A calls)
- **Interaction:** Chat-based input for human-to-agent communication

### API Specification (MCP Tools)

Each Companion exposes these MCP tools to other Companions:

**1. `check_availability`**
- **Purpose:** Query availability for a proposed timeframe
- **Inputs:** `timeframe` (string), `event_type` (enum), `duration_minutes` (int), `requester` (string)
- **Outputs:** `available` (bool), `slots` (list), `preferences` (dict), `auto_accept_eligible` (bool)

**2. `propose_event`**
- **Purpose:** Propose a specific event to this user
- **Inputs:** `event_name` (string), `datetime` (iso8601), `location` (string), `participants` (list), `requester` (string)
- **Outputs:** `status` (enum: accepted/declined/pending/counter), `message` (string)

**3. `share_context`**
- **Purpose:** Request specific approved context
- **Inputs:** `category` (enum: preferences/dietary/schedule/interests), `purpose` (string), `requester` (string)
- **Outputs:** `context_data` (dict) or `access_denied`

**4. `relay_message`**
- **Purpose:** Send a message to be relayed to the human
- **Inputs:** `message` (string), `urgency` (enum), `sender` (string)
- **Outputs:** `delivered` (bool)

### Authentication & Authorization

**For Hackathon MVP:**
- **Simulated Auth:** Hardcoded identities ("Alice", "Bob") for the demo
- **Trust Model:** "Trusted Contact" list configured in agent initialization
- **Access Control:**
  - `check_availability`: Only allowed if requester is in Trusted Contacts
  - `propose_event`: Only allowed if requester is in Trusted Contacts
  - `share_context`: Checks specific permission flags per category

### Platform Support

**Primary Target:** Web Browser (via Gradio)
- **Responsive:** Desktop-first (split screen requires width), functional on tablet
- **Runtime:** Python 3.10+ environment (local or cloud host)
- **Dependencies:** `google-adk`, `mcp`, `gradio`, `python-dotenv`

### Data Models

**User Context (In-Memory):**
```json
{
  "user_id": "alice",
  "name": "Alice",
  "preferences": {
    "cuisine": ["Italian", "Thai", "Sushi"],
    "dining_times": ["19:00", "19:30", "20:00"],
    "weekend_availability": "high"
  },
  "schedule": {
    "busy_slots": ["2024-12-07T14:00:00/2024-12-07T16:00:00"]
  },
  "trusted_contacts": ["bob"],
  "sharing_rules": {
    "bob": ["availability", "cuisine_preferences"]
  }
}
```

**Event Proposal:**
```json
{
  "event_id": "evt_123",
  "proposer": "alice",
  "recipient": "bob",
  "status": "pending",
  "details": {
    "title": "Dinner at Trattoria",
    "time": "2024-12-07T19:00:00",
    "location": "Trattoria on Main"
  }
}
```

---

## Functional Requirements

### Companion Agent Capabilities

**Agent Core & Identity**
- FR1: Agent maintains a persistent identity ("Companion") associated with a specific user
- FR2: Agent stores and retrieves user context (name, preferences, schedule) from memory
- FR3: Agent enforces a "Trusted Contact" list to control access to its MCP tools
- FR4: Agent can initiate A2A communication with other known Companions

**Coordination Logic**
- FR5: Agent can parse natural language requests for coordination (e.g., "Dinner with Bob")
- FR6: Agent can determine availability by checking its user's schedule data
- FR7: Agent can identify overlapping free slots between its user and another Companion
- FR8: Agent can synthesize a recommendation based on mutual availability and preferences
- FR9: Agent can propose specific events to its user for confirmation

**MCP Server (Inbound)**
- FR10: System exposes `check_availability` tool to trusted Companions
- FR11: System exposes `propose_event` tool to trusted Companions
- FR12: System exposes `share_context` tool to trusted Companions
- FR13: System exposes `relay_message` tool to trusted Companions
- FR14: System validates "requester" field against Trusted Contact list before executing tools

**MCP Client (Outbound)**
- FR15: Agent can discover the MCP endpoint of a target user's Companion
- FR16: Agent can call tools on another Companion's MCP server
- FR17: Agent handles tool execution errors or timeouts gracefully
- FR18: Agent logs all outbound MCP calls for the network activity monitor

### User Interface (Gradio Demo)

**Dual-User View**
- FR19: UI displays two distinct chat interfaces (Alice and Bob) side-by-side
- FR20: Users can send natural language messages to their respective Companions
- FR21: UI displays Companion responses in a conversational format
- FR22: UI updates in real-time without requiring page refreshes

**Network Visualization**
- FR23: UI displays a log of all Companion-to-Companion (A2A) interactions
- FR24: Log entries include timestamp, sender, receiver, tool called, and key parameters
- FR25: UI provides visual indication when A2A communication is active

### Data & State

**User Context Management**
- FR26: System initializes with pre-configured data for the demo scenario (Alice/Bob)
- FR27: System stores user preferences (cuisine, time) in a structured format
- FR28: System stores user schedule (busy/free blocks) in a structured format
- FR29: System maintains sharing rules mapping contacts to allowed information categories

**Event State**
- FR30: System tracks the lifecycle state of an event proposal (proposed → pending → accepted/declined)
- FR31: System prevents conflicting event proposals for the same timeslot

---

## Non-Functional Requirements

### Privacy & Security (Critical)
- **Data Minimization:** Companions must strictly adhere to sharing rules, never exposing data not explicitly allowed for a contact.
- **Contextual Integrity:** Information shared for one purpose (dinner planning) must not be retained or used for unrelated purposes.
- **Local-First Design:** For the demo, user context resides in-memory within the agent instance, not in a central database.
- **Consent:** High-sensitivity actions (booking, sharing location) must require explicit human confirmation.

### Performance (Demo Quality)
- **A2A Latency:** Companion-to-Companion communication should complete within 3-5 seconds to maintain demo flow.
- **UI Responsiveness:** Chat interface must feel "instant" (sub-100ms) even while agents are processing.
- **Concurrency:** System must handle simultaneous processing of Alice and Bob's agents without deadlock.

### Reliability
- **Graceful Degradation:** If one Companion is unreachable, the other should report this clearly to the user rather than crashing.
- **Error Recovery:** Agents should be able to retry failed A2A calls (e.g., timeout) at least once.
- **State Consistency:** Both Companions must agree on the final state of an event (accepted/declined).

### Usability
- **Natural Language:** Agents must communicate in natural, conversational tone, not JSON dumps (except in the network log).
- **Transparency:** Users must always know when their agent is communicating with another agent.
- **Control:** Users must be able to intervene or cancel a coordination attempt at any time.

---

_This PRD captures the essence of Companion Network - a novel demonstration of agent-to-agent coordination that eliminates the "coordination tax" for users._
 
_Created through collaborative discovery between Ra and AI facilitator._

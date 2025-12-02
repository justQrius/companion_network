# Project Brief: Companion Network - Agent-to-Agent Personal Coordination

## Executive Summary

**Project Name:** Companion Network
**Tagline:** "Your AI Talks to Their AI, So You Don't Have To"
**Target Tracks:**
- MCP Hackathon Track 1: Building MCP → Consumer (each Companion is an MCP Server)
- MCP Hackathon Track 2: MCP in Action → Consumer (the coordination demo)
- Kaggle AI Agents Intensive Capstone
- Google Gemini Award

---

## The Vision (Scoped for Hackathon)

The full Companion vision is a multi-year product. For the hackathon, we're building a **proof of concept** that demonstrates the most novel and impressive aspect:

> **Two AI Companions that can communicate with each other to coordinate on behalf of their humans.**

This is the "Companion Network" - the agent-to-agent coordination layer that makes the full vision possible.

---

## Why This Wins

### The Unique Angle

| What Others Build | What We Build |
|-------------------|---------------|
| AI that talks to humans | AI that talks to other AIs |
| Single-user assistants | Multi-user coordination |
| MCP tools for one agent | MCP servers that agents use to talk to each other |
| Chat interfaces | Agent-to-agent protocols |

**Nobody in the hackathon will demo two AIs negotiating a dinner time.**

### The Technical Showcase

| ADK Capability | How We Use It |
|----------------|---------------|
| **A2A Protocol** | Companion-to-Companion communication |
| **MCP (Server)** | Each Companion exposes tools to others |
| **MCP (Client)** | Companions use external tools (calendar, etc.) |
| **Multi-Agent** | Internal orchestration within each Companion |
| **Memory** | User preferences, past interactions |
| **Sessions** | Conversation continuity |

**This project uses MORE ADK capabilities than any other idea.**

---

## Problem Statement

### The Coordination Tax

Every multi-person activity requires coordination overhead:
- "When are you free?" → 5 back-and-forth messages
- "Did you tell Sarah about the change?" → Mental tracking burden
- "Can you check with everyone?" → One person becomes the switchboard

This "coordination tax" is invisible but real:
- **Time:** Hours spent on logistics instead of living
- **Mental load:** Tracking who knows what, what's confirmed
- **Friction:** Small barriers that prevent plans from happening

### Why Current Solutions Fail

| Solution | Problem |
|----------|---------|
| Shared calendars | Requires everyone to use same system |
| Group chats | Noisy, information gets lost |
| AI assistants | Only help one person, can't coordinate |
| Scheduling tools | Only solve meetings, not life |

**The missing piece:** AI assistants that can talk to *each other*.

---

## Solution: Companion Network

A demonstration of **agent-to-agent coordination** where:
1. Each person has their own Companion (an ADK agent)
2. Each Companion exposes an MCP Server (for other Companions to call)
3. Companions negotiate and coordinate on behalf of their humans
4. Humans just say what they want - the AIs figure out the logistics

### The Demo Scenario

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Alice: "Find a time for dinner with Bob this weekend"         │
│                                                                 │
│         ┌─────────────────────────────────────────────┐         │
│         │                                             │         │
│         ▼                                             │         │
│  ┌─────────────┐                           ┌─────────────┐      │
│  │   ALICE'S   │   A2A / MCP Protocol      │    BOB'S    │      │
│  │  COMPANION  │◄─────────────────────────►│  COMPANION  │      │
│  │             │                           │             │      │
│  │ • Knows her │  "Check availability      │ • Knows his │      │
│  │   schedule  │   for Saturday dinner"    │   schedule  │      │
│  │ • Knows her │                           │ • Knows his │      │
│  │   preferences│  "Saturday 7pm works,    │   preferences│     │
│  │             │   he prefers Italian"     │             │      │
│  └─────────────┘                           └─────────────┘      │
│         │                                             │         │
│         ▼                                             ▼         │
│                                                                 │
│  Alice's Companion: "Saturday 7pm works for both of you.       │
│                      Bob mentioned he's in the mood for        │
│                      Italian. Should I suggest Trattoria?"     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### What Makes It Special

1. **Alice never texted Bob** - The AIs handled it
2. **Context traveled** - Bob's preference came through
3. **Privacy preserved** - Only approved info was shared
4. **Natural language** - No scheduling UI, just conversation

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        GRADIO UI                                │
│                                                                 │
│  ┌───────────────────────┐     ┌───────────────────────┐        │
│  │     ALICE'S VIEW      │     │      BOB'S VIEW       │        │
│  │                       │     │                       │        │
│  │  Chat with Companion  │     │  Chat with Companion  │        │
│  │  ─────────────────    │     │  ─────────────────    │        │
│  │  [Conversation]       │     │  [Conversation]       │        │
│  │                       │     │                       │        │
│  │  ┌─────────────────┐  │     │  ┌─────────────────┐  │        │
│  │  │ Agent Activity  │  │     │  │ Agent Activity  │  │        │
│  │  │ ─────────────── │  │     │  │ ─────────────── │  │        │
│  │  │ Contacting Bob's│  │     │  │ Request from    │  │        │
│  │  │ Companion...    │  │     │  │ Alice's Agent   │  │        │
│  │  └─────────────────┘  │     │  └─────────────────┘  │        │
│  └───────────────────────┘     └───────────────────────┘        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              NETWORK ACTIVITY MONITOR                   │    │
│  │  ────────────────────────────────────────────────────   │    │
│  │  [12:01] Alice→Bob: check_availability(Saturday dinner) │    │
│  │  [12:02] Bob→Alice: available(7pm, prefers Italian)     │    │
│  │  [12:02] Alice: Proposing Trattoria to user             │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Each Companion: Dual Role

```
┌─────────────────────────────────────────────────────────────────┐
│                     COMPANION AGENT                             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    MCP SERVER                           │    │
│  │          (Exposed to other Companions)                  │    │
│  │                                                         │    │
│  │  Tools exposed:                                         │    │
│  │  • check_availability(timeframe) → Available slots      │    │
│  │  • propose_event(details) → Accept/Decline/Counter      │    │
│  │  • share_info(category) → Approved information          │    │
│  │  • send_message(content) → Relay to human               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   ADK AGENT CORE                        │    │
│  │                                                         │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │    │
│  │  │ Coordinator │  │  Scheduler  │  │   Memory    │      │    │
│  │  │    Agent    │  │    Agent    │  │   Manager   │      │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │    │
│  │                                                         │    │
│  │  User Context:                                          │    │
│  │  • Preferences (cuisine, times, locations)              │    │
│  │  • Relationships (who's who, trust levels)              │    │
│  │  • Schedule (busy times, flexible times)                │    │
│  │  • Sharing rules (what can be shared with whom)         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   MCP CLIENT                            │    │
│  │           (Calls other Companions + Tools)              │    │
│  │                                                         │    │
│  │  External tools:                                        │    │
│  │  • Other Companions' MCP servers                        │    │
│  │  • Calendar MCP (if integrated)                         │    │
│  │  • Search MCP (for restaurant lookup, etc.)             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### A2A Communication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    COORDINATION FLOW                            │
│                                                                 │
│  1. USER REQUEST                                                │
│     Alice: "Find a time for dinner with Bob this weekend"       │
│                              │                                  │
│                              ▼                                  │
│  2. INTENT PARSING (Alice's Companion)                          │
│     • Action: Schedule event                                    │
│     • Participants: Bob                                         │
│     • Timeframe: This weekend                                   │
│     • Type: Dinner                                              │
│                              │                                  │
│                              ▼                                  │
│  3. A2A OUTREACH                                                │
│     Alice's Companion → Bob's Companion MCP Server              │
│     Tool: check_availability                                    │
│     Params: {                                                   │
│       timeframe: "Saturday OR Sunday, evening",                 │
│       event_type: "dinner",                                     │
│       requester: "Alice"                                        │
│     }                                                           │
│                              │                                  │
│                              ▼                                  │
│  4. AVAILABILITY CHECK (Bob's Companion)                        │
│     • Check Bob's schedule                                      │
│     • Check Bob's preferences                                   │
│     • Check sharing permissions for Alice                       │
│     • Prepare response                                          │
│                              │                                  │
│                              ▼                                  │
│  5. A2A RESPONSE                                                │
│     Bob's Companion → Alice's Companion                         │
│     Response: {                                                 │
│       available_slots: ["Sat 7pm", "Sun 6pm"],                  │
│       preferences: "Italian or Thai",                           │
│       notes: "Prefers not too late on Sunday"                   │
│     }                                                           │
│                              │                                  │
│                              ▼                                  │
│  6. SYNTHESIS (Alice's Companion)                               │
│     • Match Alice's preferences with Bob's                      │
│     • Find optimal slot                                         │
│     • Prepare recommendation                                    │
│                              │                                  │
│                              ▼                                  │
│  7. USER RESPONSE                                               │
│     "Saturday 7pm works for both of you. Bob's in the mood      │
│      for Italian. Should I look up Trattoria on Main?"          │
│                              │                                  │
│                              ▼                                  │
│  8. CONFIRMATION FLOW (if user approves)                        │
│     Alice's Companion → Bob's Companion                         │
│     Tool: propose_event                                         │
│     Params: { event: "Dinner at Trattoria", time: "Sat 7pm" }   │
│                                                                 │
│     Bob's Companion notifies Bob (or auto-accepts based on      │
│     trust level and event type)                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Exposed MCP Tools (Per Companion)

Each Companion exposes these tools for other Companions to call:

### Tool 1: `check_availability`

```json
{
  "name": "check_availability",
  "description": "Check this person's availability for a proposed timeframe. Returns available slots and relevant preferences.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "timeframe": {
        "type": "string",
        "description": "Natural language timeframe (e.g., 'this weekend', 'next Tuesday evening')"
      },
      "event_type": {
        "type": "string",
        "enum": ["dinner", "lunch", "coffee", "meeting", "activity", "other"],
        "description": "Type of event being planned"
      },
      "duration_minutes": {
        "type": "integer",
        "default": 120,
        "description": "Expected duration"
      },
      "requester": {
        "type": "string",
        "description": "Who is asking (for permission checking)"
      }
    },
    "required": ["timeframe", "requester"]
  }
}
```

**Response:**
```json
{
  "available": true,
  "slots": [
    {"start": "2024-12-07T19:00", "flexibility": "high"},
    {"start": "2024-12-08T18:00", "flexibility": "medium"}
  ],
  "preferences": {
    "cuisine": ["Italian", "Thai"],
    "location_preference": "downtown",
    "notes": "Prefers not too late on Sunday"
  },
  "auto_accept_eligible": true
}
```

### Tool 2: `propose_event`

```json
{
  "name": "propose_event",
  "description": "Propose a specific event to this person. Returns acceptance, decline, or counter-proposal.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "event_name": {
        "type": "string",
        "description": "Name/description of the event"
      },
      "datetime": {
        "type": "string",
        "description": "ISO datetime of the event"
      },
      "location": {
        "type": "string",
        "description": "Location or venue"
      },
      "participants": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Who else is invited"
      },
      "requester": {
        "type": "string",
        "description": "Who is proposing"
      }
    },
    "required": ["event_name", "datetime", "requester"]
  }
}
```

**Response:**
```json
{
  "status": "accepted",  // or "declined", "pending_human", "counter_proposal"
  "message": "Sounds great! See you there.",
  "counter_proposal": null,  // or alternative details
  "added_to_calendar": true
}
```

### Tool 3: `share_context`

```json
{
  "name": "share_context",
  "description": "Request specific context about this person that they've approved for sharing.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "category": {
        "type": "string",
        "enum": ["preferences", "dietary", "schedule_patterns", "interests", "gift_ideas"],
        "description": "Category of information requested"
      },
      "purpose": {
        "type": "string",
        "description": "Why this information is needed"
      },
      "requester": {
        "type": "string"
      }
    },
    "required": ["category", "requester"]
  }
}
```

### Tool 4: `relay_message`

```json
{
  "name": "relay_message",
  "description": "Send a message to be relayed to this person through their Companion.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "message": {
        "type": "string",
        "description": "Message to relay"
      },
      "urgency": {
        "type": "string",
        "enum": ["low", "normal", "high"],
        "default": "normal"
      },
      "sender": {
        "type": "string"
      }
    },
    "required": ["message", "sender"]
  }
}
```

---

## Implementation

### Core Agent Structure

```python
from google.adk.agents import LlmAgent, Agent
from google.adk.tools import FunctionTool
from google.adk.memory import MemoryService
from google.adk.sessions import SessionService

class CompanionAgent:
    """A personal AI companion that can coordinate with other Companions."""

    def __init__(self, user_id: str, user_name: str):
        self.user_id = user_id
        self.user_name = user_name
        self.memory = MemoryService()
        self.sessions = SessionService()

        # User context (would be populated from profile/learning)
        self.user_context = {
            "name": user_name,
            "preferences": {},
            "schedule": {},
            "sharing_rules": {},
            "trusted_contacts": []
        }

        # Core agent
        self.agent = LlmAgent(
            name=f"{user_name}_companion",
            model="gemini-2.5-pro",
            instruction=self._build_instruction(),
            tools=self._build_tools()
        )

    def _build_instruction(self) -> str:
        return f"""You are {self.user_name}'s personal AI Companion.

Your role:
- Help {self.user_name} with daily life coordination
- Communicate with other people's Companions on their behalf
- Protect their privacy - only share what's approved
- Be proactive but not intrusive

You know:
- Their preferences and patterns
- Who they trust and at what level
- What information can be shared with whom

When coordinating with other Companions:
- Be collaborative and efficient
- Share only approved information
- Propose options, don't demand
- Handle conflicts gracefully

Current user context:
{self.user_context}
"""

    def _build_tools(self) -> list:
        return [
            # Tools for calling OTHER Companions
            FunctionTool(
                name="contact_companion",
                description="Contact another person's Companion",
                function=self.contact_companion
            ),
            # Tools for local actions
            FunctionTool(
                name="check_my_calendar",
                description="Check user's calendar",
                function=self.check_calendar
            ),
            FunctionTool(
                name="remember",
                description="Store information for later",
                function=self.remember
            )
        ]

    async def contact_companion(
        self,
        companion_id: str,
        tool_name: str,
        params: dict
    ) -> dict:
        """Call a tool on another Companion's MCP server."""
        # This would make an actual MCP call to the other Companion
        mcp_client = await self.get_mcp_client(companion_id)
        result = await mcp_client.call_tool(tool_name, params)
        return result


# === MCP SERVER TOOLS (exposed to other Companions) ===

async def check_availability(
    timeframe: str,
    event_type: str = "other",
    duration_minutes: int = 120,
    requester: str = ""
) -> dict:
    """MCP Tool: Check this user's availability."""

    companion = get_current_companion()

    # Check if requester is trusted
    if requester not in companion.user_context["trusted_contacts"]:
        return {
            "available": False,
            "reason": "Not in trusted contacts",
            "message": "Please have them add you as a contact first"
        }

    # Check calendar (simplified)
    available_slots = companion.check_calendar(timeframe)

    # Get shareable preferences
    preferences = companion.get_shareable_preferences(requester, event_type)

    return {
        "available": len(available_slots) > 0,
        "slots": available_slots,
        "preferences": preferences,
        "auto_accept_eligible": companion.can_auto_accept(requester, event_type)
    }


async def propose_event(
    event_name: str,
    datetime: str,
    location: str = "",
    participants: list = [],
    requester: str = ""
) -> dict:
    """MCP Tool: Propose an event to this user."""

    companion = get_current_companion()

    # Check if auto-accept is enabled for this requester/event type
    if companion.can_auto_accept(requester, event_name):
        # Auto-accept and add to calendar
        companion.add_to_calendar(event_name, datetime, location, participants)
        return {
            "status": "accepted",
            "message": f"{companion.user_name} is confirmed!",
            "added_to_calendar": True
        }
    else:
        # Queue for human approval
        companion.queue_for_approval(event_name, datetime, location, participants, requester)
        return {
            "status": "pending_human",
            "message": f"I'll check with {companion.user_name} and get back to you",
            "added_to_calendar": False
        }
```

### Gradio UI with MCP Server

```python
import gradio as gr
from companion import CompanionAgent

# Create two Companions for the demo
alice_companion = CompanionAgent("alice", "Alice")
bob_companion = CompanionAgent("bob", "Bob")

# Register them with each other
alice_companion.register_contact("bob", bob_companion.mcp_endpoint)
bob_companion.register_contact("alice", alice_companion.mcp_endpoint)

def alice_chat(message, history):
    """Handle Alice's chat with her Companion."""
    response = alice_companion.chat(message)
    return response

def bob_chat(message, history):
    """Handle Bob's chat with his Companion."""
    response = bob_companion.chat(message)
    return response

def get_network_log():
    """Get the A2A communication log."""
    return format_network_log(get_all_a2a_messages())

# Build the UI
with gr.Blocks(title="Companion Network Demo") as demo:
    gr.Markdown("# 🤝 Companion Network Demo")
    gr.Markdown("*Two AI Companions coordinating on behalf of their humans*")

    with gr.Row():
        # Alice's side
        with gr.Column():
            gr.Markdown("### 👩 Alice's Companion")
            alice_chatbot = gr.Chatbot(label="Chat with Alice's Companion")
            alice_input = gr.Textbox(placeholder="Alice: Ask your Companion...")
            alice_input.submit(alice_chat, [alice_input, alice_chatbot], alice_chatbot)

        # Bob's side
        with gr.Column():
            gr.Markdown("### 👨 Bob's Companion")
            bob_chatbot = gr.Chatbot(label="Chat with Bob's Companion")
            bob_input = gr.Textbox(placeholder="Bob: Ask your Companion...")
            bob_input.submit(bob_chat, [bob_input, bob_chatbot], bob_chatbot)

    # Network monitor
    gr.Markdown("### 🔗 Network Activity")
    network_log = gr.Textbox(
        label="Companion-to-Companion Communication",
        lines=6,
        interactive=False
    )

    # Auto-refresh network log
    demo.load(get_network_log, outputs=network_log, every=2)

# Enable MCP server mode
demo.launch(mcp_server=True)
```

---

## ADK Capabilities Demonstrated

| Day | Capability | Implementation |
|-----|------------|----------------|
| **Day 1** | Agent Architecture | Companion agent with coordinator, scheduler, memory |
| **Day 2** | Tools & MCP | Each Companion is MCP Server + Client |
| **Day 3** | Sessions & Memory | User context, preferences, conversation history |
| **Day 4** | Evaluation | Response quality, coordination success metrics |
| **Day 5** | A2A Protocol | Companion-to-Companion communication |

**This is the ONLY project that meaningfully uses A2A Protocol.**

---

## MCP Hackathon Fit

### Track 1: Building MCP → Consumer ⭐

Each Companion is an MCP Server exposing coordination tools.

| Requirement | How We Meet It |
|-------------|----------------|
| Functioning MCP Server | ✅ Each Companion exposes 4 tools |
| Demo with MCP Client | ✅ Companions call each other's MCP servers |
| Documentation | ✅ Full tool schemas |
| Innovation | ✅ First "social" MCP server |

### Track 2: MCP in Action → Consumer ⭐⭐

The full demo is a Gradio app showing autonomous coordination.

| Requirement | How We Meet It |
|-------------|----------------|
| Gradio App | ✅ Split-screen showing both Companions |
| Uses MCP Tools | ✅ Companions use each other as tools |
| Autonomous Behavior | ✅ Full coordination without human micro-management |
| Context Engineering | ✅ User preferences, relationship context |

**Submit to BOTH tracks for maximum chances.**

---

## Google Gemini Award Strategy

| Factor | How Companion Network Excels |
|--------|------------------------------|
| **Gemini Usage** | Both Companions powered by Gemini 2.5 Pro |
| **ADK Showcase** | Only project using A2A Protocol |
| **Novel Concept** | Agent-to-agent social coordination |
| **Real Value** | Solves universal coordination pain |
| **Demo Appeal** | Visually impressive split-screen coordination |

**Narrative:**
> "We built an AI that talks to other AIs. Using Google's A2A Protocol and ADK, Companion Network lets your AI coordinate with your friends' AIs. No more 'when are you free?' texts - just 'plan dinner with Bob' and watch the AIs figure it out."

---

## Demo Scenario Script

### Setup (shown before demo)
- Alice and Bob are friends
- Each has a Companion that knows their preferences
- They're connected in the Companion Network

### Demo Flow (2 minutes)

**[0:00-0:15] The Problem**
Show text message thread: 8 messages just to schedule dinner.
"This is how we coordinate today. There's a better way."

**[0:15-0:30] The Solution**
Alice types: "Find a time for dinner with Bob this weekend"

**[0:30-1:15] The Magic**
Split screen shows:
- Left: Alice's Companion thinking, then reaching out
- Right: Bob's Companion receiving request, checking calendar
- Bottom: Network log showing A2A communication
- Left: Alice's Companion synthesizes response

Alice's Companion: "Saturday 7pm works for both of you. Bob's in the mood for Italian - there's a new place called Trattoria he's been wanting to try. Should I propose that?"

**[1:15-1:30] Confirmation**
Alice: "Yes, book it"
Both Companions update, Bob gets notification.

**[1:30-1:45] The Reverse**
Bob types: "What's happening Saturday?"
Bob's Companion: "You have dinner with Alice at 7pm at Trattoria. She mentioned she might be a few minutes late - wants to stop for flowers for her mom."

**[1:45-2:00] Closing**
"Your AI talks to their AI. So you can focus on dinner, not scheduling it."
"Companion Network. Built with Google ADK and A2A Protocol."

---

## Implementation Phases

### Phase 1: Single Companion (Days 1-3)
- [ ] Basic Companion agent with Gemini
- [ ] User context and memory
- [ ] Simple chat interface
- [ ] MCP server setup with Gradio

### Phase 2: Companion-to-Companion (Days 4-7)
- [ ] Second Companion instance
- [ ] A2A communication between Companions
- [ ] `check_availability` and `propose_event` tools
- [ ] Split-screen Gradio UI

### Phase 3: Coordination Logic (Days 8-10)
- [ ] Preference matching
- [ ] Trust levels and sharing rules
- [ ] Network activity visualization
- [ ] Error handling and edge cases

### Phase 4: Polish & Demo (Days 11-14)
- [ ] UI polish
- [ ] Demo scenario scripting
- [ ] Demo video creation
- [ ] Submission

---

## Scoped Features (Hackathon MVP)

### In Scope ✅
- Two Companions (Alice and Bob)
- Basic user preferences (food, times)
- Availability checking
- Event proposal and acceptance
- Network activity log
- Split-screen Gradio UI

### Out of Scope ❌ (Future)
- Real calendar integration
- More than 2 users
- Complex trust hierarchies
- Mobile interface
- Long-term memory persistence
- Proactive suggestions

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| A2A complexity | High | High | Start with direct MCP calls, add A2A protocol later |
| Two-agent coordination bugs | Medium | Medium | Extensive testing with scripted scenarios |
| Demo timing | Medium | Medium | Pre-script the demo, have fallback |
| Latency with two agents | Medium | Medium | Use gemini-flash for sub-agents |
| UI complexity | Medium | Low | Keep UI simple - two chat panels + log |

---

## Differentiation

### What Makes This Unique

| Aspect | Other Projects | Companion Network |
|--------|----------------|-------------------|
| Users | Single user | Multi-user coordination |
| Agents | Single agent | Agent-to-agent communication |
| MCP Use | Tools for one agent | Agents as MCP servers for each other |
| Demo | "AI does X" | "AIs coordinate Y together" |
| A2A | Not used | Core feature |

### The Demo Moment

The "wow moment" is when Bob's Companion responds to Alice's Companion without Bob doing anything. That's not something anyone else will demo.

---

## Success Metrics

### Primary Goals
- [ ] MCP Hackathon Track 1 Consumer placement
- [ ] MCP Hackathon Track 2 Consumer placement
- [ ] Google Gemini Award consideration
- [ ] Kaggle Capstone badge

### What Success Looks Like
- "Wait, the AIs are talking to each other?" reaction
- Judges recognizing novel use of A2A Protocol
- Demo runs smoothly with visible coordination

---

## Future Vision (Post-Hackathon)

If successful, Companion Network could evolve into:

1. **Household Networks** - Family Companions sharing context
2. **Professional Companions** - Work scheduling and delegation
3. **Public Companion Directories** - Find and connect with others' Companions
4. **Companion API** - Let any app integrate with Companion Network

This hackathon proves the core concept: **AIs can coordinate with each other on behalf of humans.**

---

## Resources & References

### Documentation
- [ADK A2A Protocol](https://google.github.io/adk-docs/a2a/)
- [ADK Multi-Agent Systems](https://google.github.io/adk-docs/agents/multi-agents/)
- [Gradio MCP Server](https://www.gradio.app/docs/mcp)
- [MCP Specification](https://modelcontextprotocol.io/)

### Related Work
- Google Codelabs: InstaVibe (ADK + A2A example)
- ADK Samples: A2A examples

---

## Appendix A: Configuration

### Environment Variables

```bash
GOOGLE_API_KEY=your_gemini_api_key
HF_TOKEN=your_huggingface_token
```

### Demo User Profiles

**Alice:**
```json
{
  "name": "Alice",
  "preferences": {
    "cuisine": ["Italian", "Japanese", "Mexican"],
    "dining_times": ["7pm", "7:30pm"],
    "locations": ["downtown", "midtown"]
  },
  "trusted_contacts": ["bob"],
  "sharing_rules": {
    "bob": ["preferences", "availability", "general_context"]
  }
}
```

**Bob:**
```json
{
  "name": "Bob",
  "preferences": {
    "cuisine": ["Italian", "Thai", "Indian"],
    "dining_times": ["6:30pm", "7pm", "8pm"],
    "locations": ["downtown"]
  },
  "trusted_contacts": ["alice"],
  "sharing_rules": {
    "alice": ["preferences", "availability", "general_context"]
  }
}
```

---

## Appendix B: The Full Companion Vision

> **Note:** The hackathon project demonstrates a scoped proof-of-concept. Below is the complete long-term vision that the Companion Network is building toward.

---

# Companion: A Comprehensive Vision Document

## What Is Companion?

Companion is an intelligent personal assistant that lives with you — learning your life, thinking with you, managing what you don't want to carry, and connecting with the companions of people around you to make coordination effortless.

It's not an app you use. It's a relationship you develop. One that deepens over time as it learns who you are, what matters to you, and how to genuinely help.

---

## The World Today

People are overwhelmed. Not primarily by the tasks themselves, but by the invisible work of managing life — the tracking, remembering, planning, coordinating, deciding, and following up that runs constantly in the background.

Research calls this the "mental load." It causes real harm: stress, burnout, strained relationships, things falling through the cracks despite best efforts. One person in each household typically carries most of it, often without recognition.

Current tools don't help. They add more systems to manage — another app, another list, another place to check. They demand structure when your thoughts are unstructured. They start fresh every time when what you need is continuity. They answer questions but don't understand context. They can't think with you. They don't know you.

And they require you to learn them. Prompt engineering, context provision, figuring out how to phrase things so the AI understands. The burden falls on you to communicate properly rather than on the system to understand naturally.

Meanwhile, coordinating with other people remains friction-filled. Endless texts to find a time that works. Forgetting to tell your partner something important. Losing track of what you told whom. Being the family switchboard that routes all information.

People don't need more productivity tools. They need something that actually takes the burden away.

---

## The Vision

Companion is an intelligent presence that absorbs the complexity of your life so you can be present in it.

You talk to it naturally about anything — your random thoughts, your big decisions, your daily logistics, your questions about the world. It understands, remembers, organizes, and acts. It asks questions when you're unclear. It guides you when you lack knowledge. It pushes back when you're missing something. It gets better the longer you know each other.

And it connects with the companions of people in your life, handling coordination and sharing what needs to be shared, so the logistics of relationships disappear and you can focus on the relationships themselves.

---

## Core Experience

### Talk About Anything, Anytime

Companion is always available for whatever's on your mind:

**Life logistics**
- "Remind me to ask Dr. Patel about my knee"
- "The dryer is making that squeaking noise again"
- "Emma's friend Lily is allergic to peanuts"

**Questions about the world**
- "How does a 529 plan work?"
- "Is it safe to take ibuprofen with my medication?"
- "What's the best way to remove a red wine stain?"

**Thinking through problems**
- "I need to figure out what to do about my mom's living situation"
- "I'm not sure if I should take this job offer"
- "My kid said something concerning — is this normal?"

**Unstructured thoughts**
- "I'd love to take the kids to Japan someday"
- "Jake recommended a Thai place, Lotus something"
- "We should do something special for our anniversary"

No structure required. No app to open. No categorization decisions. Just externalize the thought and let go.

### Human-Native Interaction

You don't learn to talk to Companion. Companion learns to understand you.

There's no prompt engineering. No special syntax. No tricks to get better results. You talk like you'd talk to a trusted friend — incomplete thoughts, vague references, assumed context — and Companion does the work to understand.

**When you're vague, Companion asks rather than guesses badly:**

> You: "Help me with the thing for my mom"
> Companion: "I want to help — are you thinking about her birthday coming up, or something else?"

**When context is needed, Companion draws from what it already knows:**

> You: "What should I do about the car?"
> Companion: "You mean the squeaking noise that's been getting worse? You've mentioned it three times now. Probably worth getting it looked at — want me to schedule something with Mike's Auto?"

You don't have to provide context because Companion has been paying attention.

**When your intent is unclear, Companion confirms before acting:**

> You: "Can you deal with the insurance thing?"
> Companion: "You mean following up on the claim for the water damage? Just want to make sure I'm acting on the right thing."

**When you don't know what you want, Companion offers options:**

> You: "Write an email to my boss about taking time off"
> Companion: "A few ways I could approach this — brief and direct, warmer with an offer to prep for your absence, or more formal if this needs documentation. Which feels right?"

You pick from options rather than constructing specifications.

**When something is complex, Companion provides scaffolding:**

> You: "I need to plan this whole Europe trip"
> Companion: "Let's break this down. First — when are you thinking, and how long? Then we can figure out destinations, and the logistics will follow from there."

It guides you through structure so you don't have to know it in advance.

**When Companion is genuinely stuck, it's specific about why:**

> You: "Handle the situation with Mike"
> Companion: "I'm not sure which Mike or which situation you mean. I know Mike Chen from your work and Mike your neighbor. Can you give me a bit more?"

Not "please provide more details" — but specifically what's missing and why.

**And Companion never makes you feel stupid:**

The framing is always "I want to understand you better" — never "you didn't communicate properly."

Over time, Companion learns your communication patterns — your shorthand, your references, your priorities. What required clarification in your first month needs none by your sixth. The intelligence isn't in you learning the system. It's in the system learning you.

### Intelligent Understanding

Companion doesn't just store what you say. It comprehends.

When you mention "the dryer is making that noise again," Companion connects this to:
- The dryer in your home (purchased 2019, warranty expired)
- The similar noise you mentioned two months ago
- The appliance repair service you've used before

It understands: this is a recurring issue that's getting worse with an out-of-warranty appliance.

When you mention "Emma's friend Lily is allergic to peanuts," Companion recognizes this as safety information relevant to future playdates, birthday parties, and school events. It will surface at the right moments.

When you say "I need to figure out what to do about my mom's living situation," Companion doesn't just file it. It engages:

> "That's a big decision. Is something changing with her health, or is this more about planning ahead?"

It thinks with you, not just for you.

### Proactive Surfacing

Companion brings things to your attention at the right moment — not overwhelming you with notifications, but intelligently surfacing what matters when it matters.

**Time-based:**
- "Your dentist appointment is tomorrow. You wanted to ask about a night guard."
- "Mom's birthday is in two weeks. She mentioned wanting a weighted blanket."

**Event-triggered:**
- "Lily is coming to Emma's party this weekend — remember, she has a peanut allergy."

**Location-aware:**
- "You're near the dry cleaner. You have items ready for pickup."

**Pattern-noticed:**
- "The car noise you've mentioned three times is getting worse. Want to schedule service?"
- "You've canceled plans three weekends in a row. That's not like you — is everything okay?"

The goal is signal, not noise. Companion earns trust by only interrupting when it matters.

### Guided Thinking

When you bring problems to Companion, it helps you think more clearly.

**When you're vague:**

> You: "I need to get my finances in order"
> Companion: "That can mean different things. Are you trying to get out of debt, save for something specific, get visibility into where your money goes, or something else? And is this urgent or more of a 'someday' feeling?"

**When you lack knowledge:**

> You: "I think I need a will"
> Companion: "Good thinking. A will is one piece — depending on your situation, you might also want healthcare directives, power of attorney, or beneficiary updates on accounts. Want me to explain the landscape, or would you rather just start with the basics?"

**When you might be missing something:**

> You: "Find me the cheapest flight to Denver next weekend"
> Companion: "I can look, but your sister's graduation is that Saturday. Were you planning to be back in time, or did you forget about the date?"

It respects your autonomy while having your back.

### Action Execution

When appropriate, Companion doesn't just track things — it does them.

**With your permission:**
- "The check engine light came on. Want me to schedule a diagnostic? Mike's Auto has Thursday at 10am."
- "I found a good option for the weighted blanket — $89, 4.5 stars, arrives before Mom's birthday. Want me to order it?"

**Handling coordination:**
- "I found a time that works for everyone for family dinner — the 22nd at 6pm. Want me to send the invite?"

**Managing follow-ups:**
- "The insurance company said they'd call back in 48 hours. It's been three days. Want me to follow up?"

The level of autonomy is yours to set. Start with Companion just surfacing and suggesting. As trust builds, let it act more independently.

---

## Companion Network

### Your Companion, Connected to Others

Each person has their own Companion — private, personal, fully under their control. But Companions can communicate with each other, creating a mesh that handles coordination while respecting everyone's privacy.

### Household Synchronization

Families, couples, and roommates can form household networks.

**Shared awareness:**
When one person's Companion learns that soccer practice moved to 5pm Thursdays, that information flows to other household Companions. When Dad tries to schedule a call at that time, his Companion knows there's a conflict.

**Task coordination:**

> You: "We need to get the chimney inspected"
> Companion: "Want me to handle this, or pass it to Sarah's Companion? She has the vendor contacts from last time."

**Distributed responsibility:**
No single person has to be the household information hub. Context flows to where it's needed.

### Companion-to-Companion Communication

Sometimes the Companions handle logistics so humans don't have to.

**Simple coordination:**

> Your Companion to your partner's: "He's running 15 minutes late. She's planning dinner for 7 — should I suggest she delay, or is there flexibility?"

Neither person sent a text. The information just moved.

**Group scheduling:**

> You: "Find a time for everyone to get together for Dad's birthday"

Your Companion reaches out to your siblings' and parents' Companions. They negotiate based on calendars and preferences. Your Companion returns with options.

**Softer messaging:**

> You: "Tell my sister I can't make her thing Saturday, but I don't want a whole conversation"

Your Companion communicates to her Companion with context about you being overextended. Her Companion relays the message with the warmth intact.

### Shared Household Memory

Some information belongs to the household:
- Home maintenance history
- Vendor relationships and quality notes
- Important documents and their locations
- Family medical information
- Recurring schedules and patterns

This shared context is accessible to all household Companions, persists over time, and survives individual changes.

### Extended Networks

Beyond household, Companions can connect with:

**Close friends and family:**
Your mom's Companion can know your kids' current sizes and preferences — making gift-giving easier without awkward questions.

**Professional relationships:**
Your Companion can interface with your doctor's office, your accountant, your lawyer — carrying context so you don't have to re-explain your situation every time.

### Permission and Privacy

You have complete control over what's shared.

**Sharing levels:**
- **Private** — Only your Companion knows. Never shared.
- **Household** — Shared with household Companions automatically
- **Approved contacts** — Shared with specific people you've authorized
- **On request** — Companion asks you before sharing
- **Public** — Rarely used; available to anyone

You set the defaults. You can always override.

- "Don't share anything about my job search"
- "Share my location with Mom's Companion while I'm traveling"
- "Never share health information with my in-laws' Companions"

Your privacy is absolute. Sharing is always opt-in and revocable.

---

## What Companion Provides

### Functional Value

**Peace of mind** — Stop carrying everything in your head. Once you've told Companion, you can let go.

**Reliability** — Things don't fall through the cracks. Deadlines are met. Follow-ups happen. Nothing is forgotten.

**Efficiency** — Tasks get done faster. Coordination happens in the background. Research is handled for you.

**Reduced friction** — The gap between "I should do this" and it being done shrinks dramatically.

### Cognitive Value

**Clarity** — Work through complex decisions with an intelligent partner. Understand your options. Think more clearly.

**Confidence** — Make decisions knowing you have good information and have considered what matters.

**Capability** — Do things you couldn't do alone — complex research, persistent follow-up, multi-party coordination.

**Guidance** — When you don't know what you don't know, Companion helps you navigate unfamiliar territory.

### Personal Value

**Presence** — When you're not managing everything mentally, you can actually be where you are.

**Self-knowledge** — Companion reflects patterns back to you, helping you understand yourself better over time.

**Continuity** — Your life has a thread. Decisions you made years ago, why you made them, how your thinking has evolved — it's all there.

**Possibility** — Dreams and someday-maybes don't get lost. Companion holds them until you're ready.

### Relational Value

**Lighter coordination** — The logistics of relationships handled, so you can focus on connection.

**Information flow** — What needs to be known gets known, without someone being the switchboard.

**Softer communication** — Context travels with messages, reducing misunderstandings.

**Shared memory** — Households and relationships accumulate knowledge that persists.

---

## The Relationship Over Time

Companion isn't static. The relationship deepens.

**Early days:**
Companion knows little. It asks more questions. It's helpful but generic. You're building trust.

**Months in:**
Companion knows your people, your patterns, your preferences. Suggestions are more relevant. You're delegating more.

**Years in:**
Companion is an extension of you. It anticipates needs before you articulate them. It knows your history, your values, your quirks. It can represent you to others' Companions authentically.

The assistant you have after three years is profoundly different from day one — not because the software changed, but because the relationship grew.

---

## The Promise

- **Tell me once, then let go.** I'll hold it, understand it, connect it to what I know about you, and bring it back when it matters.
- **Talk to me like a human.** Messy, incomplete, in the middle of something. I'll do the work to understand.
- **Think out loud with me.** I'll ask questions, offer perspectives, and help you find clarity — without judgment, without agenda.
- **Let me handle what drains you.** The tracking, the coordinating, the following up, the remembering — I'll take it.
- **Connect me with the people in your life.** I'll make coordination invisible so your relationships can be about what matters.
- **Trust builds over time.** Start small. Let me earn it.

---

## What Companion Is Not

**Not a to-do app with AI features** — Companion isn't about managing tasks. It's about absorbing the mental load so you don't have to manage anything.

**Not a voice assistant that answers questions** — Companion has memory, context, and continuity. It knows you. It thinks with you. It's not starting fresh every time.

**Not a productivity system** — There's no methodology to learn, no structure to maintain, no habits to build. Just talk naturally and let Companion handle the rest.

**Not a tool you have to learn** — No prompt engineering. No special commands. No tricks. You talk like a human; Companion figures it out.

**Not a replacement for human relationships** — Companion handles logistics so you can be more present with people. It makes human connection easier, not unnecessary.

**Not a therapist** — Companion can be a thinking partner for life's challenges, but it knows its limits and will suggest professional help when appropriate.

---

## The World With Companion

Imagine a life where:
- You never wonder if you forgot something important
- Your household runs smoothly without anyone being the manager
- Decisions feel less overwhelming because you have help thinking through them
- Coordinating with family and friends happens effortlessly
- You can be fully present because nothing is nagging at the back of your mind
- Your dreams and intentions don't get lost in the chaos of daily life
- The longer you live, the more support you have — not less
- You just talk naturally and things happen

This is what Companion makes possible.

Not just productivity. Not just organization. A fundamentally lighter way of moving through life.

---

## Summary

**Companion is:**
- An intelligent assistant you talk to naturally about anything
- A memory that never forgets and organizes itself
- A thinking partner that helps you navigate complexity
- An agent that takes action on your behalf
- A presence that connects with others' Companions to coordinate life seamlessly
- A relationship that deepens over time
- A system that learns you, not one you learn

**Companion provides:**
- Peace of mind from releasing the mental load
- Clarity in decisions through guided thinking
- Presence by freeing your attention from logistics
- Connection by making relationships easier to maintain
- Continuity by holding the thread of your life over time

**Companion promises:**
- Talk to me about anything. I'll understand.
- Talk to me like a human. I'll do the work.
- Tell me once. I'll remember.
- Let me help you think. I'll ask the right questions.
- Let me handle the details. You focus on living.
- The more you share, the better I get. Trust builds over time.

---

**Companion. Your life, lighter.**

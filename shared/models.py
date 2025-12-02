"""Data models for user context, event proposals, and sharing rules.

This module defines Python dataclasses for type-safe data structures used
across both Alice and Bob's companion agents. Models follow the architecture
specification and use default factories to prevent mutable default argument issues.
"""

from dataclasses import dataclass, field


@dataclass
class UserContext:
    """User context data model storing preferences, schedule, and sharing rules.
    
    Attributes:
        user_id: Unique identifier for the user
        name: User's display name
        preferences: Dictionary storing cuisine types, dining_times, weekend_availability
        schedule: Dictionary storing busy_slots as ISO 8601 time ranges
        trusted_contacts: List of trusted contact user IDs
        sharing_rules: Dictionary mapping contact_id to allowed_categories lists
    """
    user_id: str
    name: str
    preferences: dict = field(default_factory=dict)  # {"cuisine": [...], "dining_times": [...]}
    schedule: dict = field(default_factory=dict)     # {"busy_slots": [...]}
    trusted_contacts: list = field(default_factory=list)
    sharing_rules: dict = field(default_factory=dict)  # {contact_id: [allowed_categories]}


@dataclass
class EventProposal:
    """Event proposal data model for coordination between companion agents.
    
    Attributes:
        event_id: Unique identifier for the event proposal
        proposer: User ID of the person proposing the event
        recipient: User ID of the person receiving the proposal
        status: Proposal status - "pending", "accepted", "declined", or "counter"
        details: Dictionary containing event details (title, time, location)
        timestamp: ISO 8601 formatted timestamp of when proposal was created
    """
    event_id: str
    proposer: str
    recipient: str
    status: str  # "pending", "accepted", "declined", "counter"
    timestamp: str
    details: dict = field(default_factory=dict)  # {"title", "time", "location"}


@dataclass
class SharingRule:
    """Sharing rule data model defining what context categories can be shared with a contact.
    
    Attributes:
        contact_id: User ID of the contact this rule applies to
        allowed_categories: List of category strings that can be shared
                          ["availability", "cuisine_preferences", "dietary", "schedule"]
    """
    contact_id: str
    allowed_categories: list = field(default_factory=list)  # ["availability", "cuisine_preferences", "dietary", "schedule"]


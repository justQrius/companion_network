"""Alice's pre-configured user context for demo scenarios.

This module provides Alice's demo user context data, including preferences,
schedule, trusted contacts, and sharing rules. The context is loaded into
agent session state during initialization (not on every message).

Demo data structure follows the UserContext dataclass from shared.models
and matches the specifications in the PRD (lines 329-346).
"""

from shared.models import UserContext


def get_alice_context() -> UserContext:
    """Get Alice's pre-configured user context for demo scenarios.
    
    Returns:
        UserContext instance with Alice's demo data:
        - User ID: "alice", Name: "Alice"
        - Preferences: cuisine=["Italian", "Thai", "Sushi"], 
          dining_times=["19:00", "19:30", "20:00"]
        - Schedule: busy_slots with demo weekend conflicts
        - Trusted contacts: ["bob"]
        - Sharing rules: {"bob": ["availability", "cuisine_preferences"]}
    
    The context is designed for hackathon demo scenarios and includes
    realistic schedule conflicts to demonstrate availability checking logic.
    """
    return UserContext(
        user_id="alice",
        name="Alice",
        preferences={
            "cuisine": ["Italian", "Thai", "Sushi"],
            "dining_times": ["19:00", "19:30", "20:00"],
            "weekend_availability": "high"
        },
        schedule={
            "busy_slots": [
                "2024-12-07T14:00:00/2024-12-07T16:00:00"  # Saturday 2pm-4pm busy (demo weekend conflict)
            ]
        },
        trusted_contacts=["bob"],
        sharing_rules={
            "bob": ["availability", "cuisine_preferences"]
        }
    )


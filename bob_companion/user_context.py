"""Bob's pre-configured user context for demo scenarios.

This module provides Bob's demo user context data, including preferences,
schedule, trusted contacts, and sharing rules. The context is loaded into
agent session state during initialization (not on every message).

Demo data structure follows the UserContext dataclass from shared.models
and is designed to be complementary to Alice's schedule to demonstrate
overlap logic and coordination scenarios.
"""

from shared.models import UserContext


def get_bob_context() -> UserContext:
    """Get Bob's pre-configured user context for demo scenarios.
    
    Returns:
        UserContext instance with Bob's demo data:
        - User ID: "bob", Name: "Bob"
        - Preferences: cuisine=["Italian", "Mexican"], 
          dining_times=["18:30", "19:00"]
        - Schedule: busy_slots complementary to Alice's (different times)
        - Trusted contacts: ["alice"]
        - Sharing rules: {"alice": ["availability", "cuisine_preferences"]}
    
    The context is designed for hackathon demo scenarios with a schedule
    complementary to Alice's to show overlap detection and coordination logic.
    """
    return UserContext(
        user_id="bob",
        name="Bob",
        preferences={
            "cuisine": ["Italian", "Mexican"],
            "dining_times": ["18:30", "19:00"],
            "weekend_availability": "high"
        },
        schedule={
            "busy_slots": [
                "2024-12-07T10:00:00/2024-12-07T12:00:00"  # Saturday 10am-12pm busy (different from Alice's 2pm-4pm)
            ]
        },
        trusted_contacts=["alice"],
        sharing_rules={
            "alice": ["availability", "cuisine_preferences"]
        }
    )


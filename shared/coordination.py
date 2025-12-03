"""Coordination logic for finding mutual availability and synthesizing recommendations.

This module provides functions for coordinating availability between two users by:
1. Finding overlapping free time slots (slot intersection)
2. Prioritizing slots based on preferences (dining times, cuisine)
3. Synthesizing natural language recommendations
4. Handling cases where no overlaps exist

Functions follow ISO 8601 format for date/time handling per architecture spec.
All functions are designed to work with the results from Story 2.7 (availability checking)
and Story 2.8 (A2A communication).
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple


def find_overlapping_slots(
    alice_slots: List[str],
    bob_slots: List[str]
) -> List[str]:
    """Find overlapping time slots between Alice's and Bob's availability.
    
    Intersects two lists of ISO 8601 time range strings to find slots where
    both users are available. Uses datetime.fromisoformat() for parsing per
    architecture specification.
    
    Algorithm:
    1. Parse both slot lists into datetime tuples
    2. For each Alice slot, check for overlaps with Bob slots
    3. Calculate intersection of overlapping time ranges
    4. Return overlapping slots in ISO 8601 format
    
    Args:
        alice_slots: List of ISO 8601 time range strings for Alice (e.g., 
                    ["2025-12-07T19:00:00/2025-12-07T21:00:00"])
        bob_slots: List of ISO 8601 time range strings for Bob (same format)
        
    Returns:
        List of ISO 8601 time range strings representing overlapping slots.
        Returns empty list if no overlaps exist.
        
    Example:
        alice = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        bob = ["2025-12-07T18:00:00/2025-12-07T20:00:00"]
        overlaps = find_overlapping_slots(alice, bob)
        # Returns: ["2025-12-07T19:00:00/2025-12-07T20:00:00"]
    """
    if not alice_slots or not bob_slots:
        return []
    
    # Parse ISO 8601 time ranges into datetime tuples
    def parse_slot(slot_str: str) -> Optional[Tuple[datetime, datetime]]:
        """Parse ISO 8601 time range string into (start, end) datetime tuple."""
        if '/' not in slot_str:
            return None
        try:
            parts = slot_str.split('/')
            if len(parts) == 2:
                start = datetime.fromisoformat(parts[0])
                end = datetime.fromisoformat(parts[1])
                return (start, end)
        except (ValueError, AttributeError):
            return None
        return None
    
    alice_parsed = [parse_slot(s) for s in alice_slots]
    bob_parsed = [parse_slot(s) for s in bob_slots]
    
    # Filter out None values (invalid slots)
    alice_parsed = [s for s in alice_parsed if s is not None]
    bob_parsed = [s for s in bob_parsed if s is not None]
    
    if not alice_parsed or not bob_parsed:
        return []
    
    # Find overlapping slots
    overlapping = []
    for alice_start, alice_end in alice_parsed:
        for bob_start, bob_end in bob_parsed:
            # Calculate intersection: max(start) to min(end)
            overlap_start = max(alice_start, bob_start)
            overlap_end = min(alice_end, bob_end)
            
            # Only add if there's actual overlap (start < end)
            if overlap_start < overlap_end:
                # Format as ISO 8601 time range string
                overlap_str = f"{overlap_start.isoformat()}/{overlap_end.isoformat()}"
                overlapping.append(overlap_str)
    
    return overlapping


def prioritize_slots_by_preferences(
    overlapping_slots: List[str],
    alice_preferences: Dict[str, Any],
    bob_preferences: Dict[str, Any]
) -> List[str]:
    """Prioritize overlapping slots based on user preferences.
    
    Prioritizes slots that match both users' dining time preferences and
    cuisine preferences. Slots matching more preferences are ranked higher.
    
    Preference Matching:
    - Dining times: Check if slot start time matches preferred dining times
    - Cuisine: Check if both users have matching cuisine preferences (not used
      for slot selection, but noted for recommendation synthesis)
    
    Args:
        overlapping_slots: List of ISO 8601 time range strings for overlapping slots
        alice_preferences: Alice's preferences dict (dining_times, cuisine, etc.)
        bob_preferences: Bob's preferences dict (dining_times, cuisine, etc.)
        
    Returns:
        Prioritized list of ISO 8601 time range strings (best matches first).
        If no preferences match, returns original list unchanged.
        
    Example:
        slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00", 
                 "2025-12-07T20:00:00/2025-12-07T22:00:00"]
        alice_prefs = {"dining_times": ["19:00", "19:30"]}
        bob_prefs = {"dining_times": ["19:00"]}
        prioritized = prioritize_slots_by_preferences(slots, alice_prefs, bob_prefs)
        # First slot (19:00) will be prioritized over second (20:00)
    """
    if not overlapping_slots:
        return []
    
    # Extract dining time preferences
    alice_dining_times = alice_preferences.get("dining_times", [])
    bob_dining_times = bob_preferences.get("dining_times", [])
    
    # If no preferences, return original list
    if not alice_dining_times and not bob_dining_times:
        return overlapping_slots
    
    # Score each slot based on preference matches
    scored_slots = []
    
    for slot_str in overlapping_slots:
        # Parse slot to get start time
        if '/' not in slot_str:
            scored_slots.append((0, slot_str))
            continue
        
        try:
            parts = slot_str.split('/')
            if len(parts) == 2:
                start = datetime.fromisoformat(parts[0])
                slot_hour = start.hour
                slot_minute = start.minute
                
                # Calculate preference match score
                score = 0
                
                # Check Alice's dining time preferences
                for time_str in alice_dining_times:
                    try:
                        pref_hour, pref_minute = map(int, time_str.split(':'))
                        time_diff = abs((slot_hour * 60 + slot_minute) - (pref_hour * 60 + pref_minute))
                        if time_diff <= 30:  # Within 30 minutes
                            score += 2  # Higher weight for dining time match
                            break
                    except (ValueError, AttributeError):
                        continue
                
                # Check Bob's dining time preferences
                for time_str in bob_dining_times:
                    try:
                        pref_hour, pref_minute = map(int, time_str.split(':'))
                        time_diff = abs((slot_hour * 60 + slot_minute) - (pref_hour * 60 + pref_minute))
                        if time_diff <= 30:  # Within 30 minutes
                            score += 2  # Higher weight for dining time match
                            break
                    except (ValueError, AttributeError):
                        continue
                
                scored_slots.append((score, slot_str))
            else:
                scored_slots.append((0, slot_str))
        except (ValueError, AttributeError):
            scored_slots.append((0, slot_str))
    
    # Sort by score (descending), then by time (earlier slots first if same score)
    scored_slots.sort(key=lambda x: (-x[0], x[1]))
    
    # Return just the slot strings in prioritized order
    return [slot for _, slot in scored_slots]


def synthesize_recommendation(
    prioritized_slots: List[str],
    alice_preferences: Dict[str, Any],
    bob_preferences: Dict[str, Any],
    bob_name: str = "Bob"
) -> str:
    """Synthesize natural language recommendation from prioritized slots and preferences.
    
    Creates a conversational recommendation text that includes:
    - Time and date of the recommended slot
    - Any relevant preference context (cuisine preferences, dining times)
    - Natural, conversational tone (not JSON dump)
    
    Note: This function provides structured data for natural language synthesis.
    The actual natural language generation should be done by the agent's LLM
    (Gemini) via system prompt, as per architecture specification.
    
    Args:
        prioritized_slots: List of ISO 8601 time range strings (prioritized, best first)
        alice_preferences: Alice's preferences dict
        bob_preferences: Bob's preferences dict (may include cuisine from check_availability)
        bob_name: Name of the other user (default: "Bob")
        
    Returns:
        Natural language recommendation string (e.g., "Saturday 7pm, Bob prefers Italian")
        If no slots available, returns message indicating no suitable times found.
        
    Example:
        slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        alice_prefs = {"dining_times": ["19:00"]}
        bob_prefs = {"cuisine": ["Italian"]}
        recommendation = synthesize_recommendation(slots, alice_prefs, bob_prefs)
        # Returns: "Saturday, December 7th at 7:00pm. Bob prefers Italian cuisine."
    """
    if not prioritized_slots:
        return "No suitable times found where both users are available."
    
    # Use the best (first) slot
    best_slot = prioritized_slots[0]
    
    # Parse slot to extract date and time
    if '/' not in best_slot:
        return "Found an available time slot, but unable to parse details."
    
    try:
        parts = best_slot.split('/')
        if len(parts) == 2:
            start = datetime.fromisoformat(parts[0])
            end = datetime.fromisoformat(parts[1])
            
            # Format date and time
            day_name = start.strftime("%A")  # e.g., "Saturday"
            month_name = start.strftime("%B")  # e.g., "December"
            day = start.day
            hour = start.hour
            minute = start.minute
            time_str = f"{hour}:{minute:02d}" if minute > 0 else f"{hour}:00"
            
            # Build recommendation text
            recommendation_parts = [
                f"{day_name}, {month_name} {day} at {time_str}"
            ]
            
            # Add cuisine preference context if available
            bob_cuisine = bob_preferences.get("cuisine", [])
            if bob_cuisine:
                cuisine_str = ", ".join(bob_cuisine[:2])  # Limit to 2 cuisines
                recommendation_parts.append(f"{bob_name} prefers {cuisine_str} cuisine")
            
            # Add dining time context if relevant
            alice_dining = alice_preferences.get("dining_times", [])
            bob_dining = bob_preferences.get("dining_times", [])
            if alice_dining and bob_dining:
                # Check if times align
                start_time_minutes = start.hour * 60 + start.minute
                for time_str in alice_dining:
                    try:
                        pref_hour, pref_minute = map(int, time_str.split(':'))
                        pref_minutes = pref_hour * 60 + pref_minute
                        if abs(start_time_minutes - pref_minutes) <= 30:
                            recommendation_parts.append("This time aligns with both users' preferred dining times")
                            break
                    except (ValueError, AttributeError):
                        continue
            
            return ". ".join(recommendation_parts) + "."
            
    except (ValueError, AttributeError) as e:
        return f"Found an available time slot, but encountered an error: {str(e)}"
    
    return "Found an available time slot, but unable to format recommendation."


def handle_no_overlaps(
    alice_slots: List[str],
    bob_slots: List[str],
    alice_name: str = "Alice",
    bob_name: str = "Bob"
) -> Dict[str, Any]:
    """Handle case where no overlapping slots exist.
    
    Generates alternative suggestions and flexibility requests when users
    have no overlapping availability. Returns structured response with
    alternatives in natural language format.
    
    Args:
        alice_slots: List of ISO 8601 time range strings for Alice's availability
        bob_slots: List of ISO 8601 time range strings for Bob's availability
        alice_name: Name of first user (default: "Alice")
        bob_name: Name of second user (default: "Bob")
        
    Returns:
        Dictionary with keys:
        - "has_overlaps": False
        - "message": Natural language message explaining no overlaps
        - "alice_alternatives": List of Alice's available times (formatted)
        - "bob_alternatives": List of Bob's available times (formatted)
        - "suggestion": Natural language suggestion for flexibility
        
    Example:
        alice = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        bob = ["2025-12-08T19:00:00/2025-12-08T21:00:00"]
        result = handle_no_overlaps(alice, bob)
        # Returns dict with alternatives and flexibility suggestion
    """
    # Format slots for display
    def format_slot_for_display(slot_str: str) -> str:
        """Format ISO 8601 slot into readable text."""
        if '/' not in slot_str:
            return slot_str
        try:
            parts = slot_str.split('/')
            if len(parts) == 2:
                start = datetime.fromisoformat(parts[0])
                day_name = start.strftime("%A")
                month_name = start.strftime("%B")
                day = start.day
                hour = start.hour
                minute = start.minute
                time_str = f"{hour}:{minute:02d}" if minute > 0 else f"{hour}:00"
                return f"{day_name}, {month_name} {day} at {time_str}"
        except (ValueError, AttributeError):
            return slot_str
        return slot_str
    
    alice_formatted = [format_slot_for_display(s) for s in alice_slots[:3]]  # Limit to 3
    bob_formatted = [format_slot_for_display(s) for s in bob_slots[:3]]  # Limit to 3
    
    # Build message
    message_parts = [
        f"No overlapping times found where both {alice_name} and {bob_name} are available."
    ]
    
    if alice_formatted:
        message_parts.append(f"{alice_name} is available: {', '.join(alice_formatted)}")
    
    if bob_formatted:
        message_parts.append(f"{bob_name} is available: {', '.join(bob_formatted)}")
    
    message = " ".join(message_parts)
    
    # Build suggestion
    suggestion = (
        f"Would either {alice_name} or {bob_name} be flexible to adjust their schedule? "
        f"Alternatively, we could look for times further in the future."
    )
    
    return {
        "has_overlaps": False,
        "message": message,
        "alice_alternatives": alice_formatted,
        "bob_alternatives": bob_formatted,
        "suggestion": suggestion
    }


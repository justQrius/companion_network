"""Availability checking utilities for companion agents.

This module provides functions for checking user availability by parsing timeframes,
retrieving schedules from session state, and identifying free time slots that align
with user preferences.

Functions follow ISO 8601 format for date/time handling per architecture spec.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


def parse_timeframe(timeframe: str, reference_date: Optional[datetime] = None) -> tuple[datetime, datetime]:
    """Parse natural language timeframe into specific date range.
    
    Supports timeframes like:
    - "this weekend" → Saturday-Sunday of current week
    - "next week" → Next 7 days from Monday
    - "tomorrow" → Next day
    - Specific dates: "2024-12-07" → That day
    - ISO 8601 ranges: "2024-12-07T19:00:00/2024-12-07T21:00:00" → Parsed directly
    
    Args:
        timeframe: Natural language timeframe or ISO 8601 range
        reference_date: Reference date for relative timeframes (defaults to today)
        
    Returns:
        Tuple of (start_datetime, end_datetime) for the parsed timeframe
        
    Raises:
        ValueError: If timeframe cannot be parsed
    """
    if reference_date is None:
        reference_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Handle ISO 8601 time ranges directly
    if '/' in timeframe and 'T' in timeframe:
        parts = timeframe.split('/')
        if len(parts) == 2:
            try:
                start = datetime.fromisoformat(parts[0])
                end = datetime.fromisoformat(parts[1])
                return start, end
            except ValueError:
                pass  # Fall through to natural language parsing
    
    timeframe_lower = timeframe.lower().strip()
    
    # Parse "this weekend" → Saturday-Sunday of current week
    if timeframe_lower == "this weekend":
        # Find Saturday of current week
        days_until_saturday = (5 - reference_date.weekday()) % 7
        if days_until_saturday == 0 and reference_date.weekday() != 5:
            # If today is not Saturday, go to next Saturday
            days_until_saturday = 7
        saturday = reference_date + timedelta(days=days_until_saturday)
        saturday = saturday.replace(hour=0, minute=0, second=0, microsecond=0)
        sunday = saturday + timedelta(days=1)
        return saturday, sunday.replace(hour=23, minute=59, second=59)
    
    # Parse "next week" → Next 7 days from Monday
    if timeframe_lower == "next week":
        days_until_monday = (7 - reference_date.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7  # If today is Monday, go to next Monday
        monday = reference_date + timedelta(days=days_until_monday)
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = monday + timedelta(days=7)
        return monday, end.replace(hour=23, minute=59, second=59)
    
    # Parse "tomorrow" → Next day
    if timeframe_lower == "tomorrow":
        tomorrow = reference_date + timedelta(days=1)
        start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        end = tomorrow.replace(hour=23, minute=59, second=59)
        return start, end
    
    # Parse specific date: "2024-12-07"
    try:
        date_only = datetime.fromisoformat(timeframe)
        start = date_only.replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_only.replace(hour=23, minute=59, second=59)
        return start, end
    except ValueError:
        pass
    
    # Default: treat as single day if can't parse
    raise ValueError(f"Unable to parse timeframe: {timeframe}")


def parse_busy_slots(busy_slots: List[str]) -> List[tuple[datetime, datetime]]:
    """Parse ISO 8601 time range strings into datetime tuples.
    
    Args:
        busy_slots: List of ISO 8601 time range strings (e.g., ["2024-12-07T14:00:00/2024-12-07T16:00:00"])
        
    Returns:
        List of (start, end) datetime tuples
    """
    parsed = []
    for slot in busy_slots:
        if '/' in slot:
            parts = slot.split('/')
            if len(parts) == 2:
                try:
                    start = datetime.fromisoformat(parts[0])
                    end = datetime.fromisoformat(parts[1])
                    parsed.append((start, end))
                except ValueError:
                    continue  # Skip invalid slots
    return parsed


def calculate_free_slots(
    timeframe_start: datetime,
    timeframe_end: datetime,
    busy_slots: List[tuple[datetime, datetime]],
    duration_hours: int = 2
) -> List[tuple[datetime, datetime]]:
    """Calculate free time slots within a timeframe, excluding busy periods.
    
    Breaks large free periods into multiple slots of the specified duration.
    
    Args:
        timeframe_start: Start of the timeframe to check
        timeframe_end: End of the timeframe to check
        busy_slots: List of (start, end) datetime tuples for busy periods
        duration_hours: Duration of the event in hours (default: 2 for dinner)
        
    Returns:
        List of (start, end) datetime tuples for available slots
    """
    # Sort busy slots by start time
    sorted_busy = sorted(busy_slots, key=lambda x: x[0])
    
    free_slots = []
    current_time = timeframe_start
    
    def add_slots_from_period(period_start: datetime, period_end: datetime):
        """Break a free period into multiple slots of duration_hours."""
        slot_start = period_start
        while slot_start < period_end:
            slot_end = slot_start + timedelta(hours=duration_hours)
            if slot_end > period_end:
                break  # Not enough time for another full slot
            free_slots.append((slot_start, slot_end))
            # Move to next slot (start 30 minutes after previous slot for overlap/options)
            slot_start += timedelta(minutes=30)
    
    for busy_start, busy_end in sorted_busy:
        # If there's a gap before this busy slot, break it into slots
        if current_time < busy_start:
            period_end = min(busy_start, timeframe_end)
            add_slots_from_period(current_time, period_end)
        
        # Move current_time to after this busy slot
        current_time = max(current_time, busy_end)
    
    # Check if there's free time after the last busy slot
    if current_time < timeframe_end:
        add_slots_from_period(current_time, timeframe_end)
    
    return free_slots


def filter_by_preferences(
    free_slots: List[tuple[datetime, datetime]],
    dining_times: List[str],
    duration_hours: int = 2
) -> List[tuple[datetime, datetime]]:
    """Filter and prioritize slots that align with preferred dining times.
    
    Preferences are preferred start times (e.g., ["19:00", "19:30", "20:00"]),
    not hard constraints. If no slots match preferences, return best available slots.
    
    Args:
        free_slots: List of (start, end) datetime tuples for available slots
        dining_times: List of preferred start times as "HH:MM" strings
        duration_hours: Duration of the event in hours
        
    Returns:
        List of slots prioritized by preference alignment (preferred slots first)
    """
    if not dining_times:
        return free_slots
    
    # Parse preferred times
    preferred_times = []
    for time_str in dining_times:
        try:
            hour, minute = map(int, time_str.split(':'))
            preferred_times.append((hour, minute))
        except ValueError:
            continue
    
    if not preferred_times:
        return free_slots
    
    # Categorize slots: preferred vs non-preferred
    preferred_slots = []
    other_slots = []
    
    for slot_start, slot_end in free_slots:
        slot_hour = slot_start.hour
        slot_minute = slot_start.minute
        
        # Check if slot start time matches any preference (within 30 minutes)
        matches_preference = False
        for pref_hour, pref_minute in preferred_times:
            time_diff = abs((slot_hour * 60 + slot_minute) - (pref_hour * 60 + pref_minute))
            if time_diff <= 30:  # Within 30 minutes of preferred time
                matches_preference = True
                break
        
        # Try to adjust slot to match preference if close
        if not matches_preference:
            for pref_hour, pref_minute in preferred_times:
                preferred_start = slot_start.replace(hour=pref_hour, minute=pref_minute, second=0, microsecond=0)
                preferred_end = preferred_start + timedelta(hours=duration_hours)
                
                # Check if adjusted slot fits within original slot
                if preferred_start >= slot_start and preferred_end <= slot_end:
                    preferred_slots.append((preferred_start, preferred_end))
                    matches_preference = True
                    break
        
        if matches_preference:
            # Already added to preferred_slots if adjusted
            if (slot_start, slot_end) not in preferred_slots:
                preferred_slots.append((slot_start, slot_end))
        else:
            other_slots.append((slot_start, slot_end))
    
    # Return preferred slots first, then others
    return preferred_slots + other_slots


def format_slot_iso8601(slot_start: datetime, slot_end: datetime) -> str:
    """Format a time slot as ISO 8601 time range string.
    
    Args:
        slot_start: Start datetime
        slot_end: End datetime
        
    Returns:
        ISO 8601 time range string (e.g., "2024-12-07T19:00:00/2024-12-07T21:00:00")
    """
    return f"{slot_start.isoformat()}/{slot_end.isoformat()}"


def check_availability(
    user_context: Dict[str, Any],
    timeframe: str,
    duration_hours: int = 2,
    max_slots: int = 5,
    min_slots: int = 3
) -> List[str]:
    """Check user availability for a given timeframe.
    
    This is the main function for availability checking. It:
    1. Retrieves schedule from user_context
    2. Parses timeframe into date range
    3. Calculates free slots excluding busy periods
    4. Filters/prioritizes slots by dining preferences
    5. Returns ISO 8601 formatted time ranges
    
    Args:
        user_context: User context dict with schedule and preferences
        timeframe: Natural language timeframe (e.g., "this weekend") or ISO 8601 range
        duration_hours: Duration of event in hours (default: 2 for dinner)
        max_slots: Maximum number of slots to return (default: 5)
        min_slots: Minimum number of slots to aim for (default: 3)
        
    Returns:
        List of ISO 8601 time range strings (e.g., ["2024-12-07T19:00:00/2024-12-07T21:00:00"])
        Returns empty list if all times are busy (edge case handling)
    """
    # Retrieve schedule from user_context
    schedule = user_context.get("schedule", {})
    busy_slots_str = schedule.get("busy_slots", [])
    
    # Retrieve preferences
    preferences = user_context.get("preferences", {})
    dining_times = preferences.get("dining_times", [])
    
    # Parse timeframe
    try:
        timeframe_start, timeframe_end = parse_timeframe(timeframe)
    except ValueError as e:
        # If timeframe parsing fails, return empty list
        return []
    
    # Parse busy slots
    busy_slots = parse_busy_slots(busy_slots_str)
    
    # Calculate free slots
    free_slots = calculate_free_slots(
        timeframe_start,
        timeframe_end,
        busy_slots,
        duration_hours
    )
    
    # Handle edge case: all times busy
    if not free_slots:
        return []
    
    # Filter by preferences (prioritizes preferred slots)
    preferred_slots = filter_by_preferences(free_slots, dining_times, duration_hours)
    
    # Limit to max_slots, but ensure we return at least what's available (up to max)
    result_slots = preferred_slots[:max_slots]
    
    # Format as ISO 8601 strings
    formatted_slots = [
        format_slot_iso8601(start, end)
        for start, end in result_slots
    ]
    
    return formatted_slots


"""Unit tests for availability checking logic.

Tests cover schedule retrieval, timeframe parsing, free slot calculation,
preference consideration, ISO 8601 formatting, and edge cases.
"""

import pytest
from datetime import datetime, timedelta
from shared.availability import (
    parse_timeframe,
    parse_busy_slots,
    calculate_free_slots,
    filter_by_preferences,
    format_slot_iso8601,
    check_availability
)


class TestParseTimeframe:
    """Test timeframe parsing functionality."""
    
    def test_parse_this_weekend(self):
        """Test parsing 'this weekend' into Saturday-Sunday."""
        # Use a known date: 2024-12-05 (Thursday)
        ref_date = datetime(2024, 12, 5, 12, 0, 0)
        start, end = parse_timeframe("this weekend", ref_date)
        
        # Should be Saturday 2024-12-07
        assert start.date() == datetime(2024, 12, 7).date()
        assert start.hour == 0
        # Should be Sunday 2024-12-08
        assert end.date() == datetime(2024, 12, 8).date()
        assert end.hour == 23
        assert end.minute == 59
    
    def test_parse_next_week(self):
        """Test parsing 'next week' into next 7 days from Monday."""
        ref_date = datetime(2024, 12, 5, 12, 0, 0)  # Thursday
        start, end = parse_timeframe("next week", ref_date)
        
        # Should start on next Monday (2024-12-09)
        assert start.weekday() == 0  # Monday
        assert start.date() == datetime(2024, 12, 9).date()
    
    def test_parse_tomorrow(self):
        """Test parsing 'tomorrow' into next day."""
        ref_date = datetime(2024, 12, 5, 12, 0, 0)
        start, end = parse_timeframe("tomorrow", ref_date)
        
        assert start.date() == datetime(2024, 12, 6).date()
        assert end.date() == datetime(2024, 12, 6).date()
    
    def test_parse_iso8601_range(self):
        """Test parsing ISO 8601 time range directly."""
        timeframe = "2024-12-07T19:00:00/2024-12-07T21:00:00"
        start, end = parse_timeframe(timeframe)
        
        assert start == datetime(2024, 12, 7, 19, 0, 0)
        assert end == datetime(2024, 12, 7, 21, 0, 0)
    
    def test_parse_specific_date(self):
        """Test parsing specific date string."""
        start, end = parse_timeframe("2024-12-07")
        
        assert start.date() == datetime(2024, 12, 7).date()
        assert start.hour == 0
        assert end.date() == datetime(2024, 12, 7).date()
        assert end.hour == 23
    
    def test_parse_invalid_timeframe(self):
        """Test parsing invalid timeframe raises ValueError."""
        with pytest.raises(ValueError):
            parse_timeframe("invalid timeframe")


class TestParseBusySlots:
    """Test busy slot parsing functionality."""
    
    def test_parse_valid_busy_slots(self):
        """Test parsing valid ISO 8601 busy slots."""
        busy_slots = [
            "2024-12-07T14:00:00/2024-12-07T16:00:00",
            "2024-12-08T10:00:00/2024-12-08T12:00:00"
        ]
        parsed = parse_busy_slots(busy_slots)
        
        assert len(parsed) == 2
        assert parsed[0] == (datetime(2024, 12, 7, 14, 0, 0), datetime(2024, 12, 7, 16, 0, 0))
        assert parsed[1] == (datetime(2024, 12, 8, 10, 0, 0), datetime(2024, 12, 8, 12, 0, 0))
    
    def test_parse_empty_busy_slots(self):
        """Test parsing empty busy slots list."""
        parsed = parse_busy_slots([])
        assert parsed == []
    
    def test_parse_invalid_busy_slots(self):
        """Test parsing invalid busy slots (skipped)."""
        busy_slots = [
            "invalid",
            "2024-12-07T14:00:00",  # Missing end time
            "2024-12-07T14:00:00/2024-12-07T16:00:00"  # Valid
        ]
        parsed = parse_busy_slots(busy_slots)
        
        # Only valid slot should be parsed
        assert len(parsed) == 1
        assert parsed[0] == (datetime(2024, 12, 7, 14, 0, 0), datetime(2024, 12, 7, 16, 0, 0))


class TestCalculateFreeSlots:
    """Test free slot calculation functionality."""
    
    def test_calculate_free_slots_no_busy(self):
        """Test free slot calculation with no busy slots."""
        start = datetime(2024, 12, 7, 0, 0, 0)
        end = datetime(2024, 12, 7, 23, 59, 59)
        busy = []
        
        free = calculate_free_slots(start, end, busy, duration_hours=2)
        
        # Should generate multiple 2-hour slots
        assert len(free) > 1
        # All slots should be 2 hours duration
        for slot_start, slot_end in free:
            duration = (slot_end - slot_start).total_seconds() / 3600
            assert duration == 2.0
    
    def test_calculate_free_slots_with_busy(self):
        """Test free slot calculation excluding busy periods."""
        start = datetime(2024, 12, 7, 0, 0, 0)
        end = datetime(2024, 12, 7, 23, 59, 59)
        busy = [
            (datetime(2024, 12, 7, 14, 0, 0), datetime(2024, 12, 7, 16, 0, 0))
        ]
        
        free = calculate_free_slots(start, end, busy, duration_hours=2)
        
        # Should have slots before and after busy period
        assert len(free) >= 1
        # All free slots should not overlap with busy period
        for slot_start, slot_end in free:
            assert slot_end <= busy[0][0] or slot_start >= busy[0][1]
    
    def test_calculate_free_slots_insufficient_duration(self):
        """Test free slot calculation filters slots shorter than duration."""
        start = datetime(2024, 12, 7, 0, 0, 0)
        end = datetime(2024, 12, 7, 1, 0, 0)  # Only 1 hour
        busy = []
        
        free = calculate_free_slots(start, end, busy, duration_hours=2)
        
        # Should return empty since slot is shorter than 2 hours
        assert len(free) == 0


class TestFilterByPreferences:
    """Test preference filtering functionality."""
    
    def test_filter_by_preferences_matches(self):
        """Test filtering slots that match preferences."""
        free_slots = [
            (datetime(2024, 12, 7, 19, 0, 0), datetime(2024, 12, 7, 21, 0, 0)),
            (datetime(2024, 12, 7, 20, 0, 0), datetime(2024, 12, 7, 22, 0, 0)),
            (datetime(2024, 12, 7, 15, 0, 0), datetime(2024, 12, 7, 17, 0, 0))
        ]
        dining_times = ["19:00", "19:30", "20:00"]
        
        filtered = filter_by_preferences(free_slots, dining_times, duration_hours=2)
        
        # Preferred slots should come first
        assert len(filtered) == 3
        # First two should be preferred times
        assert filtered[0][0].hour in [19, 20]
        assert filtered[1][0].hour in [19, 20]
    
    def test_filter_by_preferences_no_matches(self):
        """Test filtering when no slots match preferences."""
        free_slots = [
            (datetime(2024, 12, 7, 15, 0, 0), datetime(2024, 12, 7, 17, 0, 0))
        ]
        dining_times = ["19:00", "19:30", "20:00"]
        
        filtered = filter_by_preferences(free_slots, dining_times, duration_hours=2)
        
        # Should return all slots even if no matches
        assert len(filtered) == 1
    
    def test_filter_by_preferences_empty_preferences(self):
        """Test filtering with empty preferences list."""
        free_slots = [
            (datetime(2024, 12, 7, 19, 0, 0), datetime(2024, 12, 7, 21, 0, 0))
        ]
        
        filtered = filter_by_preferences(free_slots, [], duration_hours=2)
        
        # Should return all slots unchanged
        assert len(filtered) == 1


class TestFormatSlotISO8601:
    """Test ISO 8601 formatting functionality."""
    
    def test_format_slot_iso8601(self):
        """Test formatting slot as ISO 8601 time range."""
        start = datetime(2024, 12, 7, 19, 0, 0)
        end = datetime(2024, 12, 7, 21, 0, 0)
        
        formatted = format_slot_iso8601(start, end)
        
        assert formatted == "2024-12-07T19:00:00/2024-12-07T21:00:00"


class TestCheckAvailability:
    """Test main availability checking function."""
    
    def test_check_availability_this_weekend(self):
        """Test checking availability for 'this weekend'."""
        user_context = {
            "schedule": {
                "busy_slots": ["2024-12-07T14:00:00/2024-12-07T16:00:00"]
            },
            "preferences": {
                "dining_times": ["19:00", "19:30", "20:00"]
            }
        }
        
        # Use reference date of Thursday 2024-12-05
        ref_date = datetime(2024, 12, 5, 12, 0, 0)
        
        # Mock parse_timeframe to use our reference date
        # For this test, we'll use ISO 8601 range directly
        slots = check_availability(
            user_context=user_context,
            timeframe="2024-12-07T00:00:00/2024-12-08T23:59:59",
            duration_hours=2
        )
        
        # Should return some available slots
        assert len(slots) > 0
        assert len(slots) <= 5
        # All slots should be ISO 8601 formatted
        for slot in slots:
            assert '/' in slot
            assert 'T' in slot
    
    def test_check_availability_all_busy(self):
        """Test edge case: all times busy."""
        user_context = {
            "schedule": {
                "busy_slots": [
                    "2024-12-07T00:00:00/2024-12-07T23:59:59"  # Entire day busy
                ]
            },
            "preferences": {
                "dining_times": ["19:00", "19:30", "20:00"]
            }
        }
        
        slots = check_availability(
            user_context=user_context,
            timeframe="2024-12-07T00:00:00/2024-12-07T23:59:59",
            duration_hours=2
        )
        
        # Should return empty list
        assert slots == []
    
    def test_check_availability_no_preferences_match(self):
        """Test edge case: no preferences match available slots."""
        user_context = {
            "schedule": {
                "busy_slots": []  # No busy slots
            },
            "preferences": {
                "dining_times": ["19:00", "19:30", "20:00"]
            }
        }
        
        slots = check_availability(
            user_context=user_context,
            timeframe="2024-12-07T00:00:00/2024-12-07T23:59:59",
            duration_hours=2
        )
        
        # Should still return slots (best available)
        assert len(slots) > 0
    
    def test_check_availability_slot_count(self):
        """Test that function returns 3-5 slots when available."""
        user_context = {
            "schedule": {
                "busy_slots": []  # No busy slots, lots of availability
            },
            "preferences": {
                "dining_times": ["19:00", "19:30", "20:00"]
            }
        }
        
        slots = check_availability(
            user_context=user_context,
            timeframe="2024-12-07T00:00:00/2024-12-08T23:59:59",  # 2 days
            duration_hours=2,
            max_slots=5
        )
        
        # Should return between 3-5 slots
        assert len(slots) >= 3
        assert len(slots) <= 5
    
    def test_check_availability_invalid_timeframe(self):
        """Test handling of invalid timeframe."""
        user_context = {
            "schedule": {
                "busy_slots": []
            },
            "preferences": {
                "dining_times": ["19:00"]
            }
        }
        
        slots = check_availability(
            user_context=user_context,
            timeframe="invalid timeframe",
            duration_hours=2
        )
        
        # Should return empty list on parse failure
        assert slots == []
    
    def test_check_availability_missing_schedule(self):
        """Test handling of missing schedule in user_context."""
        user_context = {
            "preferences": {
                "dining_times": ["19:00"]
            }
        }
        
        slots = check_availability(
            user_context=user_context,
            timeframe="2024-12-07T00:00:00/2024-12-07T23:59:59",
            duration_hours=2
        )
        
        # Should handle gracefully (empty busy_slots)
        assert isinstance(slots, list)


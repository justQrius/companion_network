"""Unit tests for coordination logic.

Tests cover slot intersection, preference prioritization, natural language synthesis,
no overlap handling, ISO 8601 format consistency, and edge cases.
"""

import pytest
from datetime import datetime
from shared.coordination import (
    find_overlapping_slots,
    prioritize_slots_by_preferences,
    synthesize_recommendation,
    handle_no_overlaps
)


class TestFindOverlappingSlots:
    """Test slot intersection functionality (AC: 1, 7)."""
    
    def test_perfect_overlap(self):
        """Test finding perfect overlap (same slots)."""
        alice_slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        bob_slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        
        overlaps = find_overlapping_slots(alice_slots, bob_slots)
        
        assert len(overlaps) == 1
        assert overlaps[0] == "2025-12-07T19:00:00/2025-12-07T21:00:00"
    
    def test_partial_overlap(self):
        """Test finding partial overlap (slots partially overlap)."""
        alice_slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        bob_slots = ["2025-12-07T18:00:00/2025-12-07T20:00:00"]
        
        overlaps = find_overlapping_slots(alice_slots, bob_slots)
        
        assert len(overlaps) == 1
        # Overlap should be 19:00-20:00
        assert overlaps[0] == "2025-12-07T19:00:00/2025-12-07T20:00:00"
    
    def test_no_overlap(self):
        """Test no overlap (completely separate slots)."""
        alice_slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        bob_slots = ["2025-12-08T19:00:00/2025-12-08T21:00:00"]
        
        overlaps = find_overlapping_slots(alice_slots, bob_slots)
        
        assert overlaps == []
    
    def test_multiple_overlaps(self):
        """Test finding multiple overlapping slots."""
        alice_slots = [
            "2025-12-07T19:00:00/2025-12-07T21:00:00",
            "2025-12-08T19:00:00/2025-12-08T21:00:00"
        ]
        bob_slots = [
            "2025-12-07T18:00:00/2025-12-07T20:00:00",
            "2025-12-08T19:00:00/2025-12-08T21:00:00"
        ]
        
        overlaps = find_overlapping_slots(alice_slots, bob_slots)
        
        assert len(overlaps) == 2
        assert "2025-12-07T19:00:00/2025-12-07T20:00:00" in overlaps
        assert "2025-12-08T19:00:00/2025-12-08T21:00:00" in overlaps
    
    def test_empty_availability_lists(self):
        """Test edge case: empty availability lists."""
        overlaps = find_overlapping_slots([], [])
        assert overlaps == []
        
        overlaps2 = find_overlapping_slots(["2025-12-07T19:00:00/2025-12-07T21:00:00"], [])
        assert overlaps2 == []
    
    def test_iso8601_format_consistency(self):
        """Test that overlapping slots maintain ISO 8601 format (AC: 7)."""
        alice_slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        bob_slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        
        overlaps = find_overlapping_slots(alice_slots, bob_slots)
        
        for overlap in overlaps:
            assert '/' in overlap
            assert 'T' in overlap
            # Verify can be parsed
            parts = overlap.split('/')
            assert len(parts) == 2
            datetime.fromisoformat(parts[0])
            datetime.fromisoformat(parts[1])


class TestPrioritizeSlotsByPreferences:
    """Test preference-based prioritization (AC: 2, 3, 5)."""
    
    def test_dining_time_preference_match(self):
        """Test prioritizing slots that match dining time preferences."""
        slots = [
            "2025-12-07T19:00:00/2025-12-07T21:00:00",  # Matches 19:00
            "2025-12-07T20:00:00/2025-12-07T22:00:00",  # Matches 20:00
            "2025-12-07T18:00:00/2025-12-07T20:00:00"   # Doesn't match
        ]
        alice_prefs = {"dining_times": ["19:00", "19:30", "20:00"]}
        bob_prefs = {"dining_times": ["19:00", "20:00"]}
        
        prioritized = prioritize_slots_by_preferences(slots, alice_prefs, bob_prefs)
        
        # First two slots should be prioritized (match preferences)
        assert len(prioritized) == 3
        # Slots matching preferences should come first
        assert prioritized[0] in ["2025-12-07T19:00:00/2025-12-07T21:00:00", 
                                   "2025-12-07T20:00:00/2025-12-07T22:00:00"]
    
    def test_no_preferences(self):
        """Test that original order is maintained when no preferences."""
        slots = [
            "2025-12-07T19:00:00/2025-12-07T21:00:00",
            "2025-12-07T20:00:00/2025-12-07T22:00:00"
        ]
        alice_prefs = {}
        bob_prefs = {}
        
        prioritized = prioritize_slots_by_preferences(slots, alice_prefs, bob_prefs)
        
        assert prioritized == slots
    
    def test_cuisine_preferences_available(self):
        """Test that function accepts cuisine preferences (used in synthesis, not prioritization)."""
        slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        alice_prefs = {"dining_times": ["19:00"], "cuisine": ["Italian"]}
        bob_prefs = {"dining_times": ["19:00"], "cuisine": ["Italian"]}
        
        prioritized = prioritize_slots_by_preferences(slots, alice_prefs, bob_prefs)
        
        # Function should handle cuisine preferences without error
        assert len(prioritized) == 1
        assert prioritized[0] == slots[0]
    
    def test_multiple_preference_matches(self):
        """Test prioritization when multiple slots match preferences."""
        slots = [
            "2025-12-07T18:00:00/2025-12-07T20:00:00",  # No match
            "2025-12-07T19:00:00/2025-12-07T21:00:00",  # Matches both
            "2025-12-07T20:00:00/2025-12-07T22:00:00"   # Matches Alice only
        ]
        alice_prefs = {"dining_times": ["19:00", "20:00"]}
        bob_prefs = {"dining_times": ["19:00"]}
        
        prioritized = prioritize_slots_by_preferences(slots, alice_prefs, bob_prefs)
        
        # Slot matching both preferences should be first
        assert prioritized[0] == "2025-12-07T19:00:00/2025-12-07T21:00:00"


class TestSynthesizeRecommendation:
    """Test natural language recommendation synthesis (AC: 4)."""
    
    def test_basic_recommendation(self):
        """Test synthesizing basic recommendation with time and date."""
        slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        alice_prefs = {}
        bob_prefs = {}
        
        recommendation = synthesize_recommendation(slots, alice_prefs, bob_prefs)
        
        assert "Saturday" in recommendation or "December" in recommendation
        assert "7" in recommendation or "19:00" in recommendation or "7pm" in recommendation.lower()
        assert isinstance(recommendation, str)
    
    def test_recommendation_with_cuisine(self):
        """Test recommendation includes cuisine preferences."""
        slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        alice_prefs = {}
        bob_prefs = {"cuisine": ["Italian"]}
        
        recommendation = synthesize_recommendation(slots, alice_prefs, bob_prefs, bob_name="Bob")
        
        assert "Italian" in recommendation
        assert "Bob" in recommendation
    
    def test_recommendation_natural_language(self):
        """Test that recommendation is natural language, not JSON."""
        slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        alice_prefs = {}
        bob_prefs = {}
        
        recommendation = synthesize_recommendation(slots, alice_prefs, bob_prefs)
        
        # Should not be JSON format
        assert not recommendation.startswith("{")
        assert not recommendation.startswith("[")
        # Should be conversational
        assert len(recommendation) > 20  # Reasonable length for natural language
    
    def test_no_slots_handling(self):
        """Test handling when no slots available."""
        recommendation = synthesize_recommendation([], {}, {})
        
        assert "No suitable times" in recommendation or "not found" in recommendation.lower()
    
    def test_multiple_slots_uses_best(self):
        """Test that function uses best (first) slot from prioritized list."""
        slots = [
            "2025-12-07T19:00:00/2025-12-07T21:00:00",  # Best slot
            "2025-12-07T20:00:00/2025-12-07T22:00:00"   # Alternative
        ]
        alice_prefs = {}
        bob_prefs = {}
        
        recommendation = synthesize_recommendation(slots, alice_prefs, bob_prefs)
        
        # Should reference the first slot (19:00)
        assert "19:00" in recommendation or "7pm" in recommendation.lower()


class TestHandleNoOverlaps:
    """Test no overlap handling (AC: 6)."""
    
    def test_no_overlaps_returns_alternatives(self):
        """Test that function returns alternatives when no overlaps exist."""
        alice_slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        bob_slots = ["2025-12-08T19:00:00/2025-12-08T21:00:00"]
        
        result = handle_no_overlaps(alice_slots, bob_slots)
        
        assert result["has_overlaps"] is False
        assert "message" in result
        assert "suggestion" in result
        assert "alice_alternatives" in result
        assert "bob_alternatives" in result
    
    def test_alternatives_in_natural_language(self):
        """Test that alternatives are formatted in natural language."""
        alice_slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        bob_slots = ["2025-12-08T19:00:00/2025-12-08T21:00:00"]
        
        result = handle_no_overlaps(alice_slots, bob_slots)
        
        # Message should be natural language
        assert isinstance(result["message"], str)
        assert len(result["message"]) > 20
        # Should mention both users
        assert "Alice" in result["message"] or "alice" in result["message"].lower()
        assert "Bob" in result["message"] or "bob" in result["message"].lower()
    
    def test_flexibility_request(self):
        """Test that suggestion asks for flexibility."""
        alice_slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        bob_slots = ["2025-12-08T19:00:00/2025-12-08T21:00:00"]
        
        result = handle_no_overlaps(alice_slots, bob_slots)
        
        suggestion = result["suggestion"]
        assert "flexible" in suggestion.lower() or "adjust" in suggestion.lower()
    
    def test_empty_slots_handling(self):
        """Test handling when one or both users have no slots."""
        result = handle_no_overlaps([], ["2025-12-07T19:00:00/2025-12-07T21:00:00"])
        
        assert result["has_overlaps"] is False
        assert "message" in result


class TestEdgeCases:
    """Test edge cases for coordination logic."""
    
    def test_invalid_time_range_format(self):
        """Test handling of invalid time range formats."""
        # Function should handle gracefully
        overlaps = find_overlapping_slots(["invalid"], ["2025-12-07T19:00:00/2025-12-07T21:00:00"])
        
        # Should return empty list or handle gracefully
        assert isinstance(overlaps, list)
    
    def test_missing_preferences_keys(self):
        """Test handling when preferences dict is missing keys."""
        slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        
        # Missing dining_times key
        prioritized = prioritize_slots_by_preferences(slots, {}, {})
        
        assert len(prioritized) == 1
    
    def test_timezone_handling(self):
        """Test that function works with ISO 8601 format (no timezone for MVP)."""
        # MVP assumes same timezone, so no timezone in ISO strings
        alice_slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        bob_slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        
        overlaps = find_overlapping_slots(alice_slots, bob_slots)
        
        # Should work without timezone info
        assert len(overlaps) == 1

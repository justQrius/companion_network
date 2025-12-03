"""Verification script for Coordination Logic with Mutual Availability (Story 2.9).

Validates all acceptance criteria for Story 2.9:
- AC1: Overlapping Slot Identification - Finds time slots where both are available
- AC2: Preference Consideration - Considers both users' dining time preferences
- AC3: Cuisine Preference Integration - Considers cuisine preferences if shared
- AC4: Natural Language Recommendation - Synthesizes recommendation in natural language
- AC5: Multiple Slot Prioritization - Prioritizes based on preferences
- AC6: No Overlap Handling - Suggests alternatives or asks for flexibility
- AC7: ISO 8601 Slot Format - Uses ISO 8601 time range format
- AC8: Integration with A2A Flow - Integrates with availability checking and A2A calls

Usage:
    # With uv (recommended):
    uv run python tests/verify_coordination_parsing.py
    
    # Or ensure dependencies are installed:
    python tests/verify_coordination_parsing.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_ac1_overlapping_slot_identification():
    """AC1: Overlapping Slot Identification.
    
    Given Alice's availability is known (Story 2.7) and Bob's availability is retrieved via A2A (Story 2.8),
    when the agent identifies overlapping free slots,
    then the coordination logic finds time slots where both are available.
    """
    print("\n📋 Checking AC1: Overlapping Slot Identification...")
    try:
        from shared.coordination import find_overlapping_slots
        
        # Test perfect overlap
        alice_slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        bob_slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        overlaps = find_overlapping_slots(alice_slots, bob_slots)
        
        if len(overlaps) != 1:
            print(f"❌ AC1 FAILED: Expected 1 overlap, got {len(overlaps)}")
            return False
        
        # Test partial overlap
        alice_slots2 = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        bob_slots2 = ["2025-12-07T18:00:00/2025-12-07T20:00:00"]
        overlaps2 = find_overlapping_slots(alice_slots2, bob_slots2)
        
        if len(overlaps2) != 1:
            print(f"❌ AC1 FAILED: Expected 1 partial overlap, got {len(overlaps2)}")
            return False
        
        # Verify overlap is correct (19:00-20:00)
        if overlaps2[0] != "2025-12-07T19:00:00/2025-12-07T20:00:00":
            print(f"❌ AC1 FAILED: Partial overlap incorrect. Got {overlaps2[0]}")
            return False
        
        print("✅ AC1 PASSED: Coordination logic finds overlapping time slots")
        return True
        
    except Exception as e:
        print(f"❌ AC1 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac2_preference_consideration():
    """AC2: Preference Consideration.
    
    The coordination logic considers both users' dining time preferences when identifying overlapping slots.
    """
    print("\n📋 Checking AC2: Preference Consideration...")
    try:
        from shared.coordination import prioritize_slots_by_preferences
        
        slots = [
            "2025-12-07T19:00:00/2025-12-07T21:00:00",  # Matches 19:00
            "2025-12-07T20:00:00/2025-12-07T22:00:00",  # Matches 20:00
            "2025-12-07T18:00:00/2025-12-07T20:00:00"   # Doesn't match
        ]
        alice_prefs = {"dining_times": ["19:00", "19:30", "20:00"]}
        bob_prefs = {"dining_times": ["19:00", "20:00"]}
        
        prioritized = prioritize_slots_by_preferences(slots, alice_prefs, bob_prefs)
        
        if len(prioritized) != 3:
            print(f"❌ AC2 FAILED: Expected 3 slots, got {len(prioritized)}")
            return False
        
        # Slots matching preferences should be prioritized
        # First slot should match preferences
        first_slot = prioritized[0]
        if "19:00" not in first_slot and "20:00" not in first_slot:
            print(f"❌ AC2 FAILED: First slot doesn't match preferences. Got {first_slot}")
            return False
        
        print("✅ AC2 PASSED: Coordination logic considers dining time preferences")
        return True
        
    except Exception as e:
        print(f"❌ AC2 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac3_cuisine_preference_integration():
    """AC3: Cuisine Preference Integration.
    
    The coordination logic considers cuisine preferences if Bob shared them via share_context or check_availability response.
    """
    print("\n📋 Checking AC3: Cuisine Preference Integration...")
    try:
        from shared.coordination import synthesize_recommendation
        
        slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        alice_prefs = {}
        bob_prefs = {"cuisine": ["Italian"]}
        
        recommendation = synthesize_recommendation(slots, alice_prefs, bob_prefs, bob_name="Bob")
        
        # Recommendation should include cuisine preference
        if "Italian" not in recommendation:
            print(f"❌ AC3 FAILED: Recommendation doesn't include cuisine preference. Got: {recommendation}")
            return False
        
        # Test with cuisine from check_availability response pattern
        bob_prefs2 = {"cuisine": ["Italian", "French"]}
        recommendation2 = synthesize_recommendation(slots, alice_prefs, bob_prefs2, bob_name="Bob")
        
        if "Italian" not in recommendation2:
            print(f"❌ AC3 FAILED: Multiple cuisine preferences not handled. Got: {recommendation2}")
            return False
        
        print("✅ AC3 PASSED: Coordination logic considers cuisine preferences")
        return True
        
    except Exception as e:
        print(f"❌ AC3 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac4_natural_language_recommendation():
    """AC4: Natural Language Recommendation.
    
    The coordination logic synthesizes recommendation in natural language format (e.g., "Saturday 7pm, Bob prefers Italian"),
    not just raw data.
    """
    print("\n📋 Checking AC4: Natural Language Recommendation...")
    try:
        from shared.coordination import synthesize_recommendation
        
        slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        alice_prefs = {}
        bob_prefs = {"cuisine": ["Italian"]}
        
        recommendation = synthesize_recommendation(slots, alice_prefs, bob_prefs, bob_name="Bob")
        
        # Should be natural language (not JSON)
        if recommendation.startswith("{") or recommendation.startswith("["):
            print(f"❌ AC4 FAILED: Recommendation is JSON, not natural language. Got: {recommendation}")
            return False
        
        # Should include time/date
        if "19:00" not in recommendation and "7pm" not in recommendation.lower():
            print(f"❌ AC4 FAILED: Recommendation missing time. Got: {recommendation}")
            return False
        
        # Should be conversational
        if len(recommendation) < 20:
            print(f"❌ AC4 FAILED: Recommendation too short to be natural language. Got: {recommendation}")
            return False
        
        print("✅ AC4 PASSED: Coordination logic synthesizes natural language recommendation")
        return True
        
    except Exception as e:
        print(f"❌ AC4 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac5_multiple_slot_prioritization():
    """AC5: Multiple Slot Prioritization.
    
    If multiple slots are available, the logic prioritizes based on preferences (dining times, cuisine matches).
    """
    print("\n📋 Checking AC5: Multiple Slot Prioritization...")
    try:
        from shared.coordination import prioritize_slots_by_preferences
        
        slots = [
            "2025-12-07T18:00:00/2025-12-07T20:00:00",  # No match
            "2025-12-07T19:00:00/2025-12-07T21:00:00",  # Matches both
            "2025-12-07T20:00:00/2025-12-07T22:00:00"   # Matches Alice only
        ]
        alice_prefs = {"dining_times": ["19:00", "20:00"]}
        bob_prefs = {"dining_times": ["19:00"]}
        
        prioritized = prioritize_slots_by_preferences(slots, alice_prefs, bob_prefs)
        
        if len(prioritized) != 3:
            print(f"❌ AC5 FAILED: Expected 3 slots, got {len(prioritized)}")
            return False
        
        # Slot matching both preferences should be first
        if prioritized[0] != "2025-12-07T19:00:00/2025-12-07T21:00:00":
            print(f"❌ AC5 FAILED: Best matching slot not prioritized first. Got: {prioritized[0]}")
            return False
        
        print("✅ AC5 PASSED: Multiple slots prioritized based on preferences")
        return True
        
    except Exception as e:
        print(f"❌ AC5 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac6_no_overlap_handling():
    """AC6: No Overlap Handling.
    
    If no overlaps exist, the logic suggests alternatives or asks users for flexibility.
    """
    print("\n📋 Checking AC6: No Overlap Handling...")
    try:
        from shared.coordination import handle_no_overlaps
        
        alice_slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        bob_slots = ["2025-12-08T19:00:00/2025-12-08T21:00:00"]
        
        result = handle_no_overlaps(alice_slots, bob_slots)
        
        if result["has_overlaps"] is not False:
            print(f"❌ AC6 FAILED: has_overlaps should be False. Got: {result['has_overlaps']}")
            return False
        
        if "message" not in result:
            print("❌ AC6 FAILED: Missing 'message' in result")
            return False
        
        if "suggestion" not in result:
            print("❌ AC6 FAILED: Missing 'suggestion' in result")
            return False
        
        # Suggestion should ask for flexibility
        suggestion = result["suggestion"]
        if "flexible" not in suggestion.lower() and "adjust" not in suggestion.lower():
            print(f"❌ AC6 FAILED: Suggestion doesn't ask for flexibility. Got: {suggestion}")
            return False
        
        # Should include alternatives
        if "alice_alternatives" not in result or "bob_alternatives" not in result:
            print("❌ AC6 FAILED: Missing alternatives in result")
            return False
        
        print("✅ AC6 PASSED: No overlap handling suggests alternatives and asks for flexibility")
        return True
        
    except Exception as e:
        print(f"❌ AC6 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac7_iso8601_format():
    """AC7: ISO 8601 Slot Format.
    
    Overlapping slots are identified using ISO 8601 time range format for consistency.
    """
    print("\n📋 Checking AC7: ISO 8601 Slot Format...")
    try:
        from shared.coordination import find_overlapping_slots
        
        alice_slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        bob_slots = ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
        
        overlaps = find_overlapping_slots(alice_slots, bob_slots)
        
        for overlap in overlaps:
            # Verify ISO 8601 format
            if '/' not in overlap:
                print(f"❌ AC7 FAILED: Slot {overlap} missing '/' separator")
                return False
            
            if 'T' not in overlap:
                print(f"❌ AC7 FAILED: Slot {overlap} missing 'T' separator")
                return False
            
            # Verify can be parsed
            parts = overlap.split('/')
            if len(parts) != 2:
                print(f"❌ AC7 FAILED: Slot {overlap} has incorrect format")
                return False
            
            try:
                datetime.fromisoformat(parts[0])
                datetime.fromisoformat(parts[1])
            except ValueError:
                print(f"❌ AC7 FAILED: Slot {overlap} cannot be parsed as ISO 8601")
                return False
        
        print("✅ AC7 PASSED: Overlapping slots use ISO 8601 time range format")
        return True
        
    except Exception as e:
        print(f"❌ AC7 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac8_a2a_integration():
    """AC8: Integration with A2A Flow.
    
    Coordination logic integrates seamlessly with A2A communication flow
    (availability checking → A2A call → coordination → proposal).
    """
    print("\n📋 Checking AC8: Integration with A2A Flow...")
    try:
        # Verify coordination functions exist in both agents
        alice_agent_path = project_root / "alice_companion" / "agent.py"
        bob_agent_path = project_root / "bob_companion" / "agent.py"
        
        if not alice_agent_path.exists():
            print("❌ AC8 FAILED: alice_companion/agent.py not found")
            return False
        
        if not bob_agent_path.exists():
            print("❌ AC8 FAILED: bob_companion/agent.py not found")
            return False
        
        # Check for coordinate_mutual_availability function
        alice_source = alice_agent_path.read_text()
        if "coordinate_mutual_availability" not in alice_source:
            print("❌ AC8 FAILED: coordinate_mutual_availability() not found in alice_companion/agent.py")
            return False
        
        if "call_other_companion_tool" not in alice_source:
            print("❌ AC8 FAILED: call_other_companion_tool() not found (required for A2A)")
            return False
        
        bob_source = bob_agent_path.read_text()
        if "coordinate_mutual_availability" not in bob_source:
            print("❌ AC8 FAILED: coordinate_mutual_availability() not found in bob_companion/agent.py")
            return False
        
        # Verify shared coordination module exists
        coordination_path = project_root / "shared" / "coordination.py"
        if not coordination_path.exists():
            print("❌ AC8 FAILED: shared/coordination.py not found")
            return False
        
        coordination_source = coordination_path.read_text()
        required_functions = [
            "find_overlapping_slots",
            "prioritize_slots_by_preferences",
            "synthesize_recommendation",
            "handle_no_overlaps"
        ]
        
        for func_name in required_functions:
            if func_name not in coordination_source:
                print(f"❌ AC8 FAILED: {func_name}() not found in shared/coordination.py")
                return False
        
        print("✅ AC8 PASSED: Coordination logic integrated with A2A flow")
        return True
        
    except Exception as e:
        print(f"❌ AC8 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all acceptance criteria checks."""
    print("=" * 60)
    print("Coordination Logic with Mutual Availability Verification (Story 2.9)")
    print("=" * 60)
    
    results = []
    
    # Run all AC checks
    results.append(("AC1: Overlapping Slot Identification", check_ac1_overlapping_slot_identification()))
    results.append(("AC2: Preference Consideration", check_ac2_preference_consideration()))
    results.append(("AC3: Cuisine Preference Integration", check_ac3_cuisine_preference_integration()))
    results.append(("AC4: Natural Language Recommendation", check_ac4_natural_language_recommendation()))
    results.append(("AC5: Multiple Slot Prioritization", check_ac5_multiple_slot_prioritization()))
    results.append(("AC6: No Overlap Handling", check_ac6_no_overlap_handling()))
    results.append(("AC7: ISO 8601 Slot Format", check_ac7_iso8601_format()))
    results.append(("AC8: Integration with A2A Flow", check_ac8_a2a_integration()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All acceptance criteria verified!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

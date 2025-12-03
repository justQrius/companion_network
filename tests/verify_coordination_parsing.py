"""Verification script for Natural Language Coordination Request Parsing (Story 2.5).

Validates all acceptance criteria for Story 2.5:
- AC1: Natural Language Parsing - Agent extracts coordination type, other party, timeframe, intent
- AC2: Natural Language Response - Agent responds with natural language acknowledgment
- AC3: Contact Identification - Agent identifies need to contact Bob's Companion
- AC4: No Rigid Parsing - No rigid command parsing required (natural language understanding)
- AC5: System Prompt Enhancement - System prompt includes examples of coordination requests
- AC6: Extraction Capability - Agent extracts: activity type, participants, time constraints

Usage:
    # With uv (recommended):
    uv run python tests/verify_coordination_parsing.py
    
    # Or ensure dependencies are installed:
    pip install google-adk>=1.19.0
    python tests/verify_coordination_parsing.py
"""

import sys
import os
from pathlib import Path

# Check for required dependencies before proceeding
try:
    import google.adk
except ImportError:
    print("=" * 60)
    print("ERROR: Missing required dependency 'google-adk'")
    print("=" * 60)
    print("\nTo install dependencies:")
    print("  Option 1 (recommended): uv run python tests/verify_coordination_parsing.py")
    print("  Option 2: pip install google-adk>=1.19.0")
    print("\nThe project uses 'uv' for dependency management.")
    print("Run: uv sync  (to install all dependencies)")
    print("Then: uv run python tests/verify_coordination_parsing.py")
    sys.exit(1)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_ac1_natural_language_parsing():
    """AC1: Natural Language Parsing - Agent extracts coordination info.
    
    Given: Alice's agent has user context loaded (Story 2.4)
    When: Alice sends "Find a time for dinner with Bob this weekend"
    Then: Agent extracts: coordination type ("dinner"), other party ("Bob"), 
          timeframe ("this weekend" - Saturday-Sunday), intent (Initiate coordination)
    """
    print("\n📋 Checking AC1: Natural Language Parsing...")
    try:
        from alice_companion.agent import run
        
        message = "Find a time for dinner with Bob this weekend"
        response = run(message)
        
        if not response or len(response) == 0:
            print("❌ AC1 FAILED: Agent returned empty response")
            return False
        
        response_lower = response.lower()
        
        # Check for extraction indicators
        # Should mention dinner (coordination type)
        has_dinner = "dinner" in response_lower
        # Should mention Bob (other party)
        has_bob = "bob" in response_lower
        # Should mention weekend or time-related terms (timeframe)
        has_timeframe = any(term in response_lower for term in [
            "weekend", "saturday", "sunday", "time", "schedule"
        ])
        # Should show coordination intent
        has_coordination_intent = any(term in response_lower for term in [
            "coordinate", "find", "schedule", "plan", "arrange"
        ])
        
        if not has_dinner:
            print(f"❌ AC1 FAILED: Response doesn't mention 'dinner' (coordination type)")
            print(f"   Response: {response[:200]}...")
            return False
        
        if not has_bob:
            print(f"❌ AC1 FAILED: Response doesn't mention 'Bob' (other party)")
            print(f"   Response: {response[:200]}...")
            return False
        
        if not has_timeframe:
            print(f"❌ AC1 FAILED: Response doesn't acknowledge timeframe")
            print(f"   Response: {response[:200]}...")
            return False
        
        if not has_coordination_intent:
            print(f"❌ AC1 FAILED: Response doesn't show coordination intent")
            print(f"   Response: {response[:200]}...")
            return False
        
        print("✅ AC1 PASSED: Agent extracts coordination type, other party, timeframe, and intent")
        return True
        
    except Exception as e:
        print(f"❌ AC1 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac2_natural_language_response():
    """AC2: Natural Language Response - Agent responds with natural language acknowledgment.
    
    Agent should respond: "I'll coordinate with Bob's Companion to find a time 
    for dinner this weekend..."
    """
    print("\n📋 Checking AC2: Natural Language Response...")
    try:
        from alice_companion.agent import run
        
        message = "Find a time for dinner with Bob this weekend"
        response = run(message)
        
        if not response or len(response) == 0:
            print("❌ AC2 FAILED: Agent returned empty response")
            return False
        
        # Should be natural language, not JSON or structured format
        if "{" in response or "[" in response:
            # Check if it's just a code block or actual JSON structure
            if response.strip().startswith("{") or response.strip().startswith("["):
                print(f"❌ AC2 FAILED: Response appears to be JSON/structured format")
                print(f"   Response: {response[:200]}...")
                return False
        
        # Should acknowledge coordination naturally
        response_lower = response.lower()
        has_acknowledgment = any(term in response_lower for term in [
            "coordinate", "bob", "dinner", "weekend", "find", "time", "schedule"
        ])
        
        if not has_acknowledgment:
            print(f"❌ AC2 FAILED: Response doesn't acknowledge coordination naturally")
            print(f"   Response: {response[:200]}...")
            return False
        
        print("✅ AC2 PASSED: Agent responds with natural language acknowledgment")
        return True
        
    except Exception as e:
        print(f"❌ AC2 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac3_contact_identification():
    """AC3: Contact Identification - Agent identifies need to contact Bob's Companion."""
    print("\n📋 Checking AC3: Contact Identification...")
    try:
        from alice_companion.agent import run
        
        message = "Find a time for dinner with Bob this weekend"
        response = run(message)
        
        if not response or len(response) == 0:
            print("❌ AC3 FAILED: Agent returned empty response")
            return False
        
        response_lower = response.lower()
        
        # Should mention Bob (the contact to coordinate with)
        has_bob = "bob" in response_lower
        
        if not has_bob:
            print(f"❌ AC3 FAILED: Response doesn't identify Bob as contact")
            print(f"   Response: {response[:200]}...")
            return False
        
        print("✅ AC3 PASSED: Agent identifies need to contact Bob's Companion")
        return True
        
    except Exception as e:
        print(f"❌ AC3 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac4_no_rigid_parsing():
    """AC4: No Rigid Parsing - No rigid command parsing required (natural language understanding).
    
    Test alternative phrasings to verify natural language understanding.
    """
    print("\n📋 Checking AC4: No Rigid Parsing...")
    try:
        from alice_companion.agent import run
        
        alternative_phrasings = [
            "Schedule dinner with Bob for this weekend",
            "I want to have dinner with Bob this weekend"
        ]
        
        for message in alternative_phrasings:
            response = run(message)
            
            if not response or len(response) == 0:
                print(f"❌ AC4 FAILED: Agent returned empty response for: {message}")
                return False
            
            response_lower = response.lower()
            
            # Should still understand and acknowledge, even with different phrasing
            has_understanding = any(term in response_lower for term in [
                "coordinate", "bob", "dinner", "weekend", "schedule", "time"
            ])
            
            if not has_understanding:
                print(f"❌ AC4 FAILED: Agent doesn't understand alternative phrasing")
                print(f"   Message: {message}")
                print(f"   Response: {response[:200]}...")
                return False
        
        print("✅ AC4 PASSED: Agent handles natural language without rigid parsing")
        return True
        
    except Exception as e:
        print(f"❌ AC4 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac5_system_prompt_enhancement():
    """AC5: System Prompt Enhancement - System prompt includes examples of coordination requests."""
    print("\n📋 Checking AC5: System Prompt Enhancement...")
    try:
        from alice_companion.agent import SYSTEM_INSTRUCTION
        
        instruction_lower = SYSTEM_INSTRUCTION.lower()
        
        # Check for coordination examples
        has_examples = any(example in instruction_lower for example in [
            "find a time for dinner with bob",
            "schedule lunch with sarah",
            "plan a meeting with mike"
        ])
        
        # Check for natural language understanding emphasis
        has_natural_language = any(term in instruction_lower for term in [
            "natural language", "no rigid", "no command", "conversational"
        ])
        
        # Check for extraction instructions
        has_extraction = any(term in instruction_lower for term in [
            "extract", "activity type", "participants", "time constraints"
        ])
        
        if not has_examples:
            print("❌ AC5 FAILED: System prompt missing coordination request examples")
            return False
        
        if not has_natural_language:
            print("❌ AC5 FAILED: System prompt doesn't emphasize natural language understanding")
            return False
        
        if not has_extraction:
            print("❌ AC5 FAILED: System prompt missing extraction instructions")
            return False
        
        # Also check Bob's agent has same enhancement
        from bob_companion.agent import SYSTEM_INSTRUCTION as BOB_INSTRUCTION
        bob_instruction_lower = BOB_INSTRUCTION.lower()
        
        bob_has_examples = any(example in bob_instruction_lower for example in [
            "find a time for dinner", "schedule lunch", "plan a meeting"
        ])
        
        if not bob_has_examples:
            print("❌ AC5 FAILED: Bob's system prompt missing coordination examples")
            return False
        
        print("✅ AC5 PASSED: System prompts include coordination request examples")
        return True
        
    except Exception as e:
        print(f"❌ AC5 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac6_extraction_capability():
    """AC6: Extraction Capability - Agent extracts: activity type, participants, time constraints."""
    print("\n📋 Checking AC6: Extraction Capability...")
    try:
        from alice_companion.agent import run
        
        test_cases = [
            ("Find a time for dinner with Bob", "dinner"),
            ("Schedule lunch with Sarah next week", "lunch"),
            ("Plan a meeting with Mike tomorrow", "meeting")
        ]
        
        for message, expected_activity in test_cases:
            response = run(message)
            
            if not response or len(response) == 0:
                print(f"❌ AC6 FAILED: Empty response for: {message}")
                return False
            
            response_lower = response.lower()
            
            # Should extract and acknowledge activity type
            if expected_activity.lower() not in response_lower:
                print(f"❌ AC6 FAILED: Activity type '{expected_activity}' not extracted")
                print(f"   Message: {message}")
                print(f"   Response: {response[:200]}...")
                return False
        
        # Test participant extraction
        response = run("Find a time for dinner with Bob this weekend")
        response_lower = response.lower()
        
        if "bob" not in response_lower:
            print("❌ AC6 FAILED: Participant 'Bob' not extracted")
            return False
        
        # Test time constraint extraction
        time_test_cases = [
            ("Find a time for dinner with Bob this weekend", "weekend"),
            ("Schedule lunch with Sarah next week", "week"),
            ("Plan a meeting with Mike tomorrow", "tomorrow")
        ]
        
        for message, expected_timeframe in time_test_cases:
            response = run(message)
            response_lower = response.lower()
            
            # Should acknowledge timeframe (may use related terms)
            has_timeframe = any(term in response_lower for term in [
                expected_timeframe, "time", "schedule", "when"
            ])
            
            if not has_timeframe:
                print(f"❌ AC6 FAILED: Time constraint not acknowledged for: {message}")
                return False
        
        print("✅ AC6 PASSED: Agent extracts activity type, participants, and time constraints")
        return True
        
    except Exception as e:
        print(f"❌ AC6 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_bob_agent_parsing():
    """Additional check: Bob's agent also parses coordination requests correctly."""
    print("\n📋 Checking: Bob's Agent Parsing...")
    try:
        from bob_companion.agent import run
        
        message = "Find a time for dinner with Alice this weekend"
        response = run(message)
        
        if not response or len(response) == 0:
            print("❌ Bob's agent FAILED: Empty response")
            return False
        
        response_lower = response.lower()
        
        # Should understand and acknowledge
        has_understanding = any(term in response_lower for term in [
            "coordinate", "alice", "dinner", "weekend"
        ])
        
        if not has_understanding:
            print(f"❌ Bob's agent FAILED: Doesn't parse coordination request")
            print(f"   Response: {response[:200]}...")
            return False
        
        print("✅ Bob's agent PASSED: Parses coordination requests correctly")
        return True
        
    except Exception as e:
        print(f"❌ Bob's agent FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all acceptance criteria checks."""
    print("=" * 60)
    print("Natural Language Coordination Parsing Verification (Story 2.5)")
    print("=" * 60)
    
    results = []
    
    # Run all AC checks
    results.append(("AC1: Natural Language Parsing", check_ac1_natural_language_parsing()))
    results.append(("AC2: Natural Language Response", check_ac2_natural_language_response()))
    results.append(("AC3: Contact Identification", check_ac3_contact_identification()))
    results.append(("AC4: No Rigid Parsing", check_ac4_no_rigid_parsing()))
    results.append(("AC5: System Prompt Enhancement", check_ac5_system_prompt_enhancement()))
    results.append(("AC6: Extraction Capability", check_ac6_extraction_capability()))
    results.append(("Bob's Agent Parsing", check_bob_agent_parsing()))
    
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


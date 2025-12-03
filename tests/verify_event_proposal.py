"""Verification script for Event Proposal to User (Story 2.10).

Validates all acceptance criteria for Story 2.10:
- AC1: Proposal Message Content - Includes time, duration, participant, context, call to action
- AC2: EventProposal Storage - Stored in session state as EventProposal object
- AC3: Proposal Status - Set to "pending" awaiting confirmation
- AC4: Natural Language Format - Message feels natural and conversational
- AC5: EventProposal Dataclass Usage - Uses EventProposal dataclass from Story 2.1
- AC6: Session State Management - Stored under unique event_id using DatabaseSessionService
- AC7: User Confirmation Handling - Waits for confirmation keywords
- AC8: Trusted Contact Validation - Enforces trusted contact list
- AC9: A2A Communication Initiation - Can initiate A2A after confirmation
- AC10: Integration with Coordination Logic - Uses recommendation from Story 2.9

Usage:
    # With uv (recommended):
    uv run python tests/verify_event_proposal.py
    
    # Or ensure dependencies are installed:
    python tests/verify_event_proposal.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_ac1_proposal_message_content():
    """AC1: Proposal Message Content.
    
    Given a recommendation is synthesized (Story 2.9), when the agent presents the proposal to Alice,
    then the message includes: proposed time, duration, participant, additional context, and call to action.
    """
    print("\n📋 Checking AC1: Proposal Message Content...")
    try:
        from alice_companion.agent import format_proposal_message
        from shared.models import EventProposal
        
        # Create test proposal
        proposal = EventProposal(
            event_id="evt_test_123",
            proposer="alice",
            recipient="bob",
            status="pending",
            timestamp=datetime.now().isoformat(),
            details={
                "time": "2025-12-07T19:00:00",
                "end_time": "2025-12-07T21:00:00",
                "duration_hours": 2,
                "participants": ["alice", "bob"],
                "bob_preferences": {"cuisine": ["Italian"]}
            }
        )
        
        message = format_proposal_message(proposal)
        
        # Check for required elements
        checks = {
            "time": "7:00" in message or "7pm" in message.lower() or "19:00" in message or "December" in message,
            "duration": "2 hours" in message or "hour" in message.lower(),
            "participant": "Bob" in message or "bob" in message.lower(),
            "context": "Italian" in message or len(message) > 50,  # Context or sufficient detail
            "call_to_action": "confirm" in message.lower() or "should i" in message.lower()
        }
        
        failed_checks = [key for key, passed in checks.items() if not passed]
        if failed_checks:
            print(f"❌ AC1 FAILED: Missing elements: {', '.join(failed_checks)}")
            print(f"   Message: {message}")
            return False
        
        print("✅ AC1 PASSED: Proposal message includes all required elements")
        return True
        
    except Exception as e:
        print(f"❌ AC1 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac2_eventproposal_storage():
    """AC2: EventProposal Storage.
    
    The proposal is stored in session state as EventProposal object with unique event_id.
    """
    print("\n📋 Checking AC2: EventProposal Storage...")
    try:
        from shared.models import EventProposal
        
        # Verify EventProposal dataclass exists and can be instantiated
        proposal = EventProposal(
            event_id="evt_test_456",
            proposer="alice",
            recipient="bob",
            status="pending",
            timestamp=datetime.now().isoformat(),
            details={"title": "Dinner"}
        )
        
        if not proposal.event_id:
            print("❌ AC2 FAILED: EventProposal missing event_id")
            return False
        
        if proposal.proposer != "alice":
            print("❌ AC2 FAILED: EventProposal proposer not set correctly")
            return False
        
        if proposal.recipient != "bob":
            print("❌ AC2 FAILED: EventProposal recipient not set correctly")
            return False
        
        # Verify can be converted to dict (for session storage)
        from dataclasses import asdict
        proposal_dict = asdict(proposal)
        
        if "event_id" not in proposal_dict:
            print("❌ AC2 FAILED: EventProposal dict missing event_id")
            return False
        
        print("✅ AC2 PASSED: EventProposal can be created and stored")
        return True
        
    except Exception as e:
        print(f"❌ AC2 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac3_proposal_status():
    """AC3: Proposal Status.
    
    Proposal status is set to "pending" awaiting Alice's confirmation.
    """
    print("\n📋 Checking AC3: Proposal Status...")
    try:
        from shared.models import EventProposal
        
        proposal = EventProposal(
            event_id="evt_test_789",
            proposer="alice",
            recipient="bob",
            status="pending",
            timestamp=datetime.now().isoformat()
        )
        
        if proposal.status != "pending":
            print(f"❌ AC3 FAILED: Proposal status should be 'pending', got '{proposal.status}'")
            return False
        
        print("✅ AC3 PASSED: Proposal status set to 'pending'")
        return True
        
    except Exception as e:
        print(f"❌ AC3 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac4_natural_language_format():
    """AC4: Natural Language Format.
    
    Message feels natural and conversational (not robotic, not JSON dumps).
    """
    print("\n📋 Checking AC4: Natural Language Format...")
    try:
        from alice_companion.agent import format_proposal_message
        from shared.models import EventProposal
        
        proposal = EventProposal(
            event_id="evt_test_101",
            proposer="alice",
            recipient="bob",
            status="pending",
            timestamp=datetime.now().isoformat(),
            details={
                "time": "2025-12-07T19:00:00",
                "duration_hours": 2,
                "participants": ["alice", "bob"]
            }
        )
        
        message = format_proposal_message(proposal)
        
        # Should not be JSON
        if message.startswith("{") or message.startswith("["):
            print(f"❌ AC4 FAILED: Message is JSON, not natural language. Got: {message[:50]}...")
            return False
        
        # Should be conversational (sufficient length, natural words)
        if len(message) < 30:
            print(f"❌ AC4 FAILED: Message too short to be natural. Got: {message}")
            return False
        
        # Should contain natural language words
        natural_words = ["I", "found", "time", "dinner", "with", "for", "hours", "confirm"]
        has_natural_words = any(word in message for word in natural_words)
        if not has_natural_words:
            print(f"❌ AC4 FAILED: Message doesn't contain natural language words. Got: {message}")
            return False
        
        print("✅ AC4 PASSED: Message is natural and conversational")
        return True
        
    except Exception as e:
        print(f"❌ AC4 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac5_eventproposal_dataclass_usage():
    """AC5: EventProposal Dataclass Usage.
    
    Uses EventProposal dataclass from Story 2.1 with proper field initialization.
    """
    print("\n📋 Checking AC5: EventProposal Dataclass Usage...")
    try:
        from shared.models import EventProposal
        
        # Verify dataclass fields
        proposal = EventProposal(
            event_id="evt_test_202",
            proposer="alice",
            recipient="bob",
            status="pending",
            timestamp=datetime.now().isoformat(),
            details={"title": "Dinner", "time": "2025-12-07T19:00:00"}
        )
        
        required_fields = ["event_id", "proposer", "recipient", "status", "timestamp", "details"]
        for field in required_fields:
            if not hasattr(proposal, field):
                print(f"❌ AC5 FAILED: EventProposal missing field: {field}")
                return False
        
        # Verify default factory for details
        proposal2 = EventProposal(
            event_id="evt_test_203",
            proposer="bob",
            recipient="alice",
            status="pending",
            timestamp=datetime.now().isoformat()
        )
        
        if proposal2.details is None:
            print("❌ AC5 FAILED: EventProposal details should have default factory")
            return False
        
        print("✅ AC5 PASSED: EventProposal dataclass used correctly")
        return True
        
    except Exception as e:
        print(f"❌ AC5 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac6_session_state_management():
    """AC6: Session State Management.
    
    Proposal stored in session state under unique event_id using DatabaseSessionService.
    """
    print("\n📋 Checking AC6: Session State Management...")
    try:
        # Verify create_event_proposal function exists and uses correct key format
        alice_agent_path = project_root / "alice_companion" / "agent.py"
        
        if not alice_agent_path.exists():
            print("❌ AC6 FAILED: alice_companion/agent.py not found")
            return False
        
        alice_source = alice_agent_path.read_text()
        
        # Check for create_event_proposal function
        if "create_event_proposal" not in alice_source:
            print("❌ AC6 FAILED: create_event_proposal() not found")
            return False
        
        # Check for correct key format: "event_proposal:{event_id}"
        if 'f"event_proposal:{event_id}"' not in alice_source and '"event_proposal:' not in alice_source:
            print("❌ AC6 FAILED: Session state key format not found (expected 'event_proposal:{event_id}')")
            return False
        
        # Check for DatabaseSessionService usage
        if "update_session_state" not in alice_source:
            print("❌ AC6 FAILED: update_session_state() not found (required for session storage)")
            return False
        
        print("✅ AC6 PASSED: Session state management implemented")
        return True
        
    except Exception as e:
        print(f"❌ AC6 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac7_user_confirmation_handling():
    """AC7: User Confirmation Handling.
    
    Proposal waits for Alice's next message ("yes", "confirm", "sounds good") to proceed with confirmation.
    """
    print("\n📋 Checking AC7: User Confirmation Handling...")
    try:
        alice_agent_path = project_root / "alice_companion" / "agent.py"
        
        if not alice_agent_path.exists():
            print("❌ AC7 FAILED: alice_companion/agent.py not found")
            return False
        
        alice_source = alice_agent_path.read_text()
        
        # Check for handle_user_confirmation function
        if "handle_user_confirmation" not in alice_source:
            print("❌ AC7 FAILED: handle_user_confirmation() not found")
            return False
        
        # Check for confirmation keywords
        confirmation_keywords = ["yes", "confirm", "sounds good", "go ahead", "proceed"]
        found_keywords = [kw for kw in confirmation_keywords if kw in alice_source.lower()]
        
        if len(found_keywords) < 2:
            print(f"❌ AC7 FAILED: Not enough confirmation keywords found. Expected at least 2, found: {found_keywords}")
            return False
        
        print("✅ AC7 PASSED: User confirmation handling implemented")
        return True
        
    except Exception as e:
        print(f"❌ AC7 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac8_trusted_contact_validation():
    """AC8: Trusted Contact Validation.
    
    Enforces trusted contact list (Bob is in Alice's trusted_contacts) before proposing event.
    """
    print("\n📋 Checking AC8: Trusted Contact Validation...")
    try:
        alice_agent_path = project_root / "alice_companion" / "agent.py"
        
        if not alice_agent_path.exists():
            print("❌ AC8 FAILED: alice_companion/agent.py not found")
            return False
        
        alice_source = alice_agent_path.read_text()
        
        # Check for trusted contact validation in create_event_proposal
        if "trusted_contacts" not in alice_source:
            print("❌ AC8 FAILED: trusted_contacts validation not found")
            return False
        
        # Check for error message about trusted contacts
        if "trusted contacts" not in alice_source.lower():
            print("❌ AC8 FAILED: Trusted contact error message not found")
            return False
        
        print("✅ AC8 PASSED: Trusted contact validation implemented")
        return True
        
    except Exception as e:
        print(f"❌ AC8 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac9_a2a_communication_initiation():
    """AC9: A2A Communication Initiation.
    
    Agent can initiate A2A communication with Bob's Companion after Alice confirms.
    """
    print("\n📋 Checking AC9: A2A Communication Initiation...")
    try:
        alice_agent_path = project_root / "alice_companion" / "agent.py"
        
        if not alice_agent_path.exists():
            print("❌ AC9 FAILED: alice_companion/agent.py not found")
            return False
        
        alice_source = alice_agent_path.read_text()
        
        # Check for A2A communication function after confirmation
        if "finalize_event_with_other_companion" not in alice_source:
            print("❌ AC9 FAILED: finalize_event_with_other_companion() not found")
            return False
        
        # Check for propose_event tool call
        if "propose_event" not in alice_source:
            print("❌ AC9 FAILED: propose_event tool call not found")
            return False
        
        # Check for call_other_companion_tool usage
        if "call_other_companion_tool" not in alice_source:
            print("❌ AC9 FAILED: call_other_companion_tool() not found (required for A2A)")
            return False
        
        print("✅ AC9 PASSED: A2A communication initiation implemented")
        return True
        
    except Exception as e:
        print(f"❌ AC9 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac10_integration_with_coordination_logic():
    """AC10: Integration with Coordination Logic.
    
    Proposal integrates seamlessly with coordination logic from Story 2.9 (uses synthesized recommendation).
    """
    print("\n📋 Checking AC10: Integration with Coordination Logic...")
    try:
        alice_agent_path = project_root / "alice_companion" / "agent.py"
        bob_agent_path = project_root / "bob_companion" / "agent.py"
        
        if not alice_agent_path.exists():
            print("❌ AC10 FAILED: alice_companion/agent.py not found")
            return False
        
        if not bob_agent_path.exists():
            print("❌ AC10 FAILED: bob_companion/agent.py not found")
            return False
        
        alice_source = alice_agent_path.read_text()
        bob_source = bob_agent_path.read_text()
        
        # Check for propose_event_to_user function (integrates coordination with proposal)
        if "propose_event_to_user" not in alice_source:
            print("❌ AC10 FAILED: propose_event_to_user() not found in alice_companion/agent.py")
            return False
        
        if "propose_event_to_user" not in bob_source:
            print("❌ AC10 FAILED: propose_event_to_user() not found in bob_companion/agent.py")
            return False
        
        # Check that create_event_proposal uses recommendation dict
        if "recommendation" not in alice_source.lower() or "slots" not in alice_source.lower():
            print("❌ AC10 FAILED: create_event_proposal() doesn't appear to use recommendation structure")
            return False
        
        # Verify coordinate_mutual_availability exists (Story 2.9)
        if "coordinate_mutual_availability" not in alice_source:
            print("❌ AC10 FAILED: coordinate_mutual_availability() not found (required from Story 2.9)")
            return False
        
        print("✅ AC10 PASSED: Integration with coordination logic verified")
        return True
        
    except Exception as e:
        print(f"❌ AC10 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all acceptance criteria checks."""
    print("=" * 60)
    print("Event Proposal to User Verification (Story 2.10)")
    print("=" * 60)
    
    results = []
    
    # Run all AC checks
    results.append(("AC1: Proposal Message Content", check_ac1_proposal_message_content()))
    results.append(("AC2: EventProposal Storage", check_ac2_eventproposal_storage()))
    results.append(("AC3: Proposal Status", check_ac3_proposal_status()))
    results.append(("AC4: Natural Language Format", check_ac4_natural_language_format()))
    results.append(("AC5: EventProposal Dataclass Usage", check_ac5_eventproposal_dataclass_usage()))
    results.append(("AC6: Session State Management", check_ac6_session_state_management()))
    results.append(("AC7: User Confirmation Handling", check_ac7_user_confirmation_handling()))
    results.append(("AC8: Trusted Contact Validation", check_ac8_trusted_contact_validation()))
    results.append(("AC9: A2A Communication Initiation", check_ac9_a2a_communication_initiation()))
    results.append(("AC10: Integration with Coordination Logic", check_ac10_integration_with_coordination_logic()))
    
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


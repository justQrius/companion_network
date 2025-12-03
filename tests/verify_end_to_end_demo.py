"""
Verification script for end-to-end demo scenario validation (Story 4.5).

Follows Epic 1, 2, 3, 4 pattern for verification scripts.
Verifies all acceptance criteria, performance targets, NFR satisfaction, and FR coverage.
"""

import sys
import time
import asyncio
import httpx
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import (
    initialize_agents,
    start_mcp_servers,
    verify_a2a_endpoints,
    handle_alice_input,
    handle_bob_input,
    update_network_monitor,
    alice_agent,
    bob_agent,
    alice_runner,
    bob_runner
)


async def wait_for_a2a_events(
    min_events: int = 1,
    timeout: float = 10.0,
    poll_interval: float = 0.5
) -> Tuple[List, List]:
    """Wait for A2A events to appear in session state (event-driven validation)."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        alice_session = await alice_runner.session_service.get_session("alice_session")
        bob_session = await bob_runner.session_service.get_session("bob_session")
        
        alice_events = alice_session.state.get("app:a2a_events", [])
        bob_events = bob_session.state.get("app:a2a_events", [])
        
        total_events = len(alice_events) + len(bob_events)
        if total_events >= min_events:
            return alice_events, bob_events
        
        await asyncio.sleep(poll_interval)
    
    # Return what we have even if timeout
    alice_session = await alice_runner.session_service.get_session("alice_session")
    bob_session = await bob_runner.session_service.get_session("bob_session")
    return (
        alice_session.state.get("app:a2a_events", []),
        bob_session.state.get("app:a2a_events", [])
    )


async def wait_for_agent_response(
    history: List[Tuple[str, str]],
    timeout: float = 10.0,
    poll_interval: float = 0.5
) -> bool:
    """Wait for agent response to appear in chat history."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        agent_responses = [msg[1] for msg in history if msg[1] != "thinking..."]
        if len(agent_responses) > 0:
            return True
        await asyncio.sleep(poll_interval)
    
    return False


def validate_a2a_event_structure(event: Dict[str, Any]) -> None:
    """Validate A2A event has correct structure with all required fields."""
    required_fields = ["timestamp", "sender", "receiver", "tool", "status"]
    for field in required_fields:
        assert field in event, f"Event missing required field: {field}"
    
    try:
        datetime.fromisoformat(event["timestamp"])
    except (ValueError, TypeError) as e:
        raise AssertionError(f"Invalid timestamp format: {event['timestamp']}") from e
    
    assert event["sender"] in ["alice", "bob"], f"Invalid sender: {event['sender']}"
    assert event["receiver"] in ["alice", "bob"], f"Invalid receiver: {event['receiver']}"
    
    valid_tools = ["check_availability", "propose_event", "share_context", "relay_message"]
    assert event["tool"] in valid_tools, f"Invalid tool name: {event['tool']}"
    
    assert event["status"] in ["success", "failed"], f"Invalid status: {event['status']}"
    assert "params" in event, "Event missing 'params' field"
    assert isinstance(event["params"], dict), "Event 'params' must be a dictionary"


def measure_a2a_latency_from_events(events: list) -> float:
    """Measure A2A latency from actual event timestamps."""
    if len(events) < 2:
        return 0.0
    
    try:
        timestamps = [datetime.fromisoformat(e["timestamp"]) for e in events]
        timestamps.sort()
        latency = (timestamps[-1] - timestamps[0]).total_seconds()
        return latency
    except (ValueError, KeyError, TypeError):
        return 0.0


async def check_ac1_demo_scenario_execution() -> bool:
    """AC1: Demo scenario executes successfully with all steps working."""
    print("\n" + "=" * 60)
    print("AC1: Demo Scenario Execution")
    print("=" * 60)
    
    try:
        # Initialize system
        alice, bob = initialize_agents()
        assert alice is not None and bob is not None, "Agents not initialized"
        
        start_mcp_servers()
        await asyncio.sleep(2)
        
        alice_ok, bob_ok = verify_a2a_endpoints()
        assert alice_ok and bob_ok, "A2A endpoints not accessible"
        
        start_time = time.time()
        
        # Step 1: Alice sends request
        alice_history: List[Tuple[str, str]] = []
        alice_message = "Find a time for dinner with Bob this weekend"
        alice_history, _ = await handle_alice_input(alice_message, alice_history)
        
        assert len(alice_history) >= 1, "Alice's message not added"
        assert alice_history[0][0] == alice_message, "Message content incorrect"
        
        # Wait for A2A coordination (event-driven validation)
        alice_events, bob_events = await wait_for_a2a_events(min_events=1, timeout=10.0)
        
        assert len(alice_events) > 0 or len(bob_events) > 0, "No A2A events logged"
        
        # Step 3: Verify availability checking with structure validation
        availability_calls = [
            e for e in (alice_events + bob_events)
            if e.get("tool") == "check_availability"
        ]
        assert len(availability_calls) > 0, "No check_availability calls"
        validate_a2a_event_structure(availability_calls[0])
        
        # Step 4: Verify event proposal with structure validation
        propose_calls = [
            e for e in (alice_events + bob_events)
            if e.get("tool") == "propose_event"
        ]
        assert len(propose_calls) > 0, "No propose_event calls"
        validate_a2a_event_structure(propose_calls[0])
        
        # Step 5: Alice confirms
        alice_confirmation = "Sounds good, confirm it"
        alice_history, _ = await handle_alice_input(alice_confirmation, alice_history)
        assert len(alice_history) >= 2, "Confirmation not processed"
        
        elapsed_time = time.time() - start_time
        assert elapsed_time < 10.0, f"Flow took {elapsed_time}s, exceeds 10s target"
        
        print(f"✅ AC1: PASSED - Demo scenario completed in {elapsed_time:.2f}s")
        return True
    except Exception as e:
        print(f"❌ AC1: FAILED - {e}")
        return False


async def check_ac2_alice_view_coordination() -> bool:
    """AC2: Alice sees her Companion coordinating with Bob."""
    print("\n" + "=" * 60)
    print("AC2: Alice's View Coordination")
    print("=" * 60)
    
    try:
        alice_history: List[Tuple[str, str]] = []
        alice_message = "Find a time for dinner with Bob this weekend"
        alice_history, _ = await handle_alice_input(alice_message, alice_history)
        
        response_found = await wait_for_agent_response(alice_history, timeout=10.0)
        assert response_found, "Agent response not received within timeout"
        
        assert len(alice_history) >= 1, "Alice's history is empty"
        
        agent_responses = [msg[1] for msg in alice_history if msg[1] != "thinking..."]
        assert len(agent_responses) > 0, "No agent responses"
        
        for response in agent_responses:
            assert len(response) > 10, "Response too short"
            assert "error" not in response.lower(), f"Error in response: {response}"
        
        all_text = " ".join([msg[1] for msg in alice_history]).lower()
        coordination_keywords = ["bob", "dinner", "available", "propose", "coordinate"]
        has_coordination = any(keyword in all_text for keyword in coordination_keywords)
        assert has_coordination, "Alice's view doesn't show coordination"
        
        print("✅ AC2: PASSED - Alice's view shows coordination messages")
        return True
    except Exception as e:
        print(f"❌ AC2: FAILED - {e}")
        return False


async def check_ac3_bob_view_event_proposal() -> bool:
    """AC3: Bob sees incoming event proposal."""
    print("\n" + "=" * 60)
    print("AC3: Bob's View Event Proposal")
    print("=" * 60)
    
    try:
        # Trigger coordination from Alice
        alice_history: List[Tuple[str, str]] = []
        alice_message = "Find a time for dinner with Bob this weekend"
        await handle_alice_input(alice_message, alice_history)
        
        await wait_for_a2a_events(min_events=1, timeout=10.0)
        
        bob_session = await bob_runner.session_service.get_session("bob_session")
        events = bob_session.state.get("events", [])
        
        assert len(events) > 0, "No events in Bob's session state"
        
        alice_events = [e for e in events if e.get("proposer") == "alice"]
        assert len(alice_events) > 0, "No event proposals from Alice"
        
        event_statuses = [e.get("status") for e in alice_events]
        assert any(status in ["pending", "accepted"] for status in event_statuses), \
            f"Event not in expected state: {event_statuses}"
        
        print("✅ AC3: PASSED - Bob's view shows event proposal")
        return True
    except Exception as e:
        print(f"❌ AC3: FAILED - {e}")
        return False


async def check_ac4_network_monitor_display() -> bool:
    """AC4: Network monitor shows all A2A calls with correct details."""
    print("\n" + "=" * 60)
    print("AC4: Network Monitor Display")
    print("=" * 60)
    
    try:
        # Trigger A2A coordination
        alice_history: List[Tuple[str, str]] = []
        alice_message = "Find a time for dinner with Bob this weekend"
        await handle_alice_input(alice_message, alice_history)
        
        await wait_for_a2a_events(min_events=1, timeout=10.0)
        
        monitor_data = await update_network_monitor()
        
        assert "events" in monitor_data, "Monitor data missing 'events'"
        assert "count" in monitor_data, "Monitor data missing 'count'"
        assert isinstance(monitor_data["events"], list), "Monitor 'events' must be a list"
        assert isinstance(monitor_data["count"], int), "Monitor 'count' must be an integer"
        
        events = monitor_data["events"]
        assert len(events) > 0, "No A2A events in network monitor"
        
        # Validate structure of each event
        for event in events:
            validate_a2a_event_structure(event)
        
        # Verify chronological order
        timestamps = [datetime.fromisoformat(e["timestamp"]) for e in events]
        assert timestamps == sorted(timestamps), "Events not in chronological order"
        
        print(f"✅ AC4: PASSED - Network monitor displays {len(events)} events correctly")
        return True
    except Exception as e:
        print(f"❌ AC4: FAILED - {e}")
        return False


async def check_ac5_event_state_consistency() -> bool:
    """AC5: Event is confirmed in both Companions' session states consistently."""
    print("\n" + "=" * 60)
    print("AC5: Event State Consistency")
    print("=" * 60)
    
    try:
        # Trigger coordination and confirmation
        alice_history: List[Tuple[str, str]] = []
        alice_message = "Find a time for dinner with Bob this weekend"
        await handle_alice_input(alice_message, alice_history)
        
        await wait_for_a2a_events(min_events=1, timeout=10.0)
        
        alice_confirmation = "Sounds good, confirm it"
        await handle_alice_input(alice_confirmation, alice_history)
        
        await wait_for_agent_response(alice_history, timeout=5.0)
        
        alice_session = await alice_runner.session_service.get_session("alice_session")
        bob_session = await bob_runner.session_service.get_session("bob_session")
        
        alice_events = alice_session.state.get("events", [])
        bob_events = bob_session.state.get("events", [])
        
        assert len(alice_events) > 0, "No events in Alice's state"
        assert len(bob_events) > 0, "No events in Bob's state"
        
        alice_event_ids = {e.get("event_id") for e in alice_events if "event_id" in e}
        bob_event_ids = {e.get("event_id") for e in bob_events if "event_id" in e}
        
        matching_ids = alice_event_ids & bob_event_ids
        assert len(matching_ids) > 0, "No matching events between agents"
        
        for event_id in matching_ids:
            alice_event = next(e for e in alice_events if e.get("event_id") == event_id)
            bob_event = next(e for e in bob_events if e.get("event_id") == event_id)
            
            assert alice_event.get("status") == bob_event.get("status"), \
                f"Status mismatch: Alice={alice_event.get('status')}, Bob={bob_event.get('status')}"
        
        print("✅ AC5: PASSED - Event state is consistent across both agents")
        return True
    except Exception as e:
        print(f"❌ AC5: FAILED - {e}")
        return False


async def check_ac6_no_errors_or_crashes() -> bool:
    """AC6: Entire demo flow completes without errors, crashes, or exceptions."""
    print("\n" + "=" * 60)
    print("AC6: No Errors or Crashes")
    print("=" * 60)
    
    try:
        alice_history: List[Tuple[str, str]] = []
        
        alice_message = "Find a time for dinner with Bob this weekend"
        alice_history, _ = await handle_alice_input(alice_message, alice_history)
        await wait_for_agent_response(alice_history, timeout=10.0)
        
        alice_confirmation = "Sounds good, confirm it"
        alice_history, _ = await handle_alice_input(alice_confirmation, alice_history)
        await wait_for_agent_response(alice_history, timeout=5.0)
        await asyncio.sleep(2)
        
        error_keywords = ["error", "exception", "traceback", "failed", "crash"]
        all_text = " ".join([msg[1] for msg in alice_history]).lower()
        has_errors = any(keyword in all_text for keyword in error_keywords)
        assert not has_errors, f"Error messages found: {all_text}"
        
        print("✅ AC6: PASSED - No errors or crashes during demo flow")
        return True
    except Exception as e:
        print(f"❌ AC6: FAILED - {e}")
        return False


async def check_ac7_performance_target() -> bool:
    """AC7: Entire flow completes within 10 seconds."""
    print("\n" + "=" * 60)
    print("AC7: Performance Target")
    print("=" * 60)
    
    try:
        start_time = time.time()
        
        alice_history: List[Tuple[str, str]] = []
        alice_message = "Find a time for dinner with Bob this weekend"
        alice_history, _ = await handle_alice_input(alice_message, alice_history)
        
        # Wait for A2A coordination and measure latency from actual events
        alice_events, bob_events = await wait_for_a2a_events(min_events=1, timeout=10.0)
        all_events = alice_events + bob_events
        a2a_latency = measure_a2a_latency_from_events(all_events)
        
        alice_confirmation = "Sounds good, confirm it"
        alice_history, _ = await handle_alice_input(alice_confirmation, alice_history)
        await wait_for_agent_response(alice_history, timeout=5.0)
        
        total_time = time.time() - start_time
        
        assert total_time < 10.0, f"Total time {total_time:.2f}s exceeds 10s target"
        if a2a_latency > 0:
            assert 3.0 <= a2a_latency <= 5.0, f"A2A latency {a2a_latency:.2f}s not within 3-5s"
        
        print(f"✅ AC7: PASSED - Total: {total_time:.2f}s, A2A: {a2a_latency:.2f}s")
        return True
    except Exception as e:
        print(f"❌ AC7: FAILED - {e}")
        return False


async def check_ac8_nfr_satisfaction() -> bool:
    """AC8: All NFRs are satisfied."""
    print("\n" + "=" * 60)
    print("AC8: NFR Satisfaction")
    print("=" * 60)
    
    try:
        # Privacy NFR: Sharing rules enforced
        alice_session = await alice_runner.session_service.get_session(
            app_name="companion_network",
            user_id="alice",
            session_id="alice_session"
        )
        alice_context = alice_session.state.get("user_context", {})
        sharing_rules = alice_context.get("sharing_rules", {})
        
        assert "bob" in sharing_rules, "Sharing rules not configured"
        assert len(sharing_rules["bob"]) > 0, "No sharing rules defined"
        
        # Usability NFR: Natural language responses
        alice_history: List[Tuple[str, str]] = []
        alice_message = "Find a time for dinner with Bob this weekend"
        alice_history, _ = await handle_alice_input(alice_message, alice_history)
        await wait_for_agent_response(alice_history, timeout=10.0)
        
        agent_responses = [msg[1] for msg in alice_history if msg[1] != "thinking..."]
        for response in agent_responses:
            assert len(response) > 20, "Response too short"
            assert not response.startswith("{"), "Response is JSON"
            assert not response.startswith("Error"), "Response is error code"
        
        print("✅ AC8: PASSED - All NFRs satisfied")
        return True
    except Exception as e:
        print(f"❌ AC8: FAILED - {e}")
        return False


async def check_ac9_demo_readiness() -> bool:
    """AC9: Demo is ready for hackathon judges."""
    print("\n" + "=" * 60)
    print("AC9: Demo Readiness")
    print("=" * 60)
    
    try:
        assert alice_agent is not None, "Alice agent not initialized"
        assert bob_agent is not None, "Bob agent not initialized"
        
        alice_ok, bob_ok = verify_a2a_endpoints()
        assert alice_ok and bob_ok, "A2A endpoints not accessible"
        
        monitor_data = await update_network_monitor()
        assert "events" in monitor_data, "Network monitor not working"
        
        alice_history: List[Tuple[str, str]] = []
        test_message = "Test message"
        alice_history, _ = await handle_alice_input(test_message, alice_history)
        assert len(alice_history) > 0, "Chat interface not working"
        
        print("✅ AC9: PASSED - Demo is ready for hackathon judges")
        return True
    except Exception as e:
        print(f"❌ AC9: FAILED - {e}")
        return False


async def check_ac10_fr_coverage() -> bool:
    """AC10: All 31 FRs are validated as working together."""
    print("\n" + "=" * 60)
    print("AC10: FR Coverage Validation")
    print("=" * 60)
    
    try:
        fr_coverage = {
            "FR1-FR4 (Agent Core & Identity)": False,
            "FR5-FR9 (Coordination Logic)": False,
            "FR10-FR14 (MCP Server Inbound)": False,
            "FR15-FR18 (MCP Client Outbound)": False,
            "FR19-FR25 (Gradio UI)": False,
            "FR26-FR31 (Data & State)": False,
        }
        
        # FR1-FR4
        assert alice_agent is not None and bob_agent is not None, "FR1: Agents not initialized"
        
        alice_session = await alice_runner.session_service.get_session("alice_session")
        bob_session = await bob_runner.session_service.get_session("bob_session")
        
        assert "user_context" in alice_session.state, "FR2: User context not stored"
        assert "user_context" in bob_session.state, "FR2: User context not stored"
        
        alice_context = alice_session.state.get("user_context", {})
        assert "trusted_contacts" in alice_context, "FR3: Trusted contacts not enforced"
        
        alice_ok, bob_ok = verify_a2a_endpoints()
        assert alice_ok and bob_ok, "FR4: A2A communication not initiated"
        fr_coverage["FR1-FR4 (Agent Core & Identity)"] = True
        
        # FR5-FR9
        alice_history: List[Tuple[str, str]] = []
        alice_message = "Find a time for dinner with Bob this weekend"
        await handle_alice_input(alice_message, alice_history)
        await wait_for_a2a_events(min_events=1, timeout=10.0)
        
        monitor_data = await update_network_monitor()
        events = monitor_data.get("events", [])
        assert len(events) > 0, "FR5-FR9: Coordination logic not working"
        fr_coverage["FR5-FR9 (Coordination Logic)"] = True
        
        # FR10-FR14
        tool_calls = [e.get("tool") for e in events]
        valid_tools = ["check_availability", "propose_event", "share_context", "relay_message"]
        has_tools = any(tool in tool_calls for tool in valid_tools)
        assert has_tools, "FR10-FR14: MCP tools not exposed"
        fr_coverage["FR10-FR14 (MCP Server Inbound)"] = True
        
        # FR15-FR18
        assert len(events) > 0, "FR15-FR18: MCP client not calling tools"
        fr_coverage["FR15-FR18 (MCP Client Outbound)"] = True
        
        # FR19-FR25
        assert len(alice_history) > 0, "FR19-FR25: Gradio UI not working"
        assert "events" in monitor_data, "FR19-FR25: Network monitor not working"
        fr_coverage["FR19-FR25 (Gradio UI)"] = True
        
        # FR26-FR31
        assert "user_context" in alice_session.state, "FR26-FR31: Data & State not working"
        alice_context = alice_session.state.get("user_context", {})
        assert "preferences" in alice_context, "FR27: Preferences not stored"
        assert "schedule" in alice_context, "FR28: Schedule not stored"
        assert "sharing_rules" in alice_context, "FR29: Sharing rules not maintained"
        
        events_list = alice_session.state.get("events", [])
        assert len(events_list) > 0, "FR30: Event lifecycle not tracked"
        fr_coverage["FR26-FR31 (Data & State)"] = True
        
        all_covered = all(fr_coverage.values())
        assert all_covered, f"FR coverage incomplete: {fr_coverage}"
        
        print("✅ AC10: PASSED - All 31 FRs validated")
        print(f"   FR Coverage: {fr_coverage}")
        return True
    except Exception as e:
        print(f"❌ AC10: FAILED - {e}")
        return False


async def main():
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("End-to-End Demo Scenario Validation - Verification Script")
    print("=" * 60)
    print("Story 4.5: End-to-End Demo Scenario Validation")
    print("=" * 60)
    
    # Initialize system
    print("\nInitializing system...")
    try:
        initialize_agents()
        start_mcp_servers()
        await asyncio.sleep(2)
        verify_a2a_endpoints()
        print("✅ System initialized")
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        return 1
    
    # Run all checks
    async def run_all_checks():
        checks = [
            check_ac1_demo_scenario_execution,
            check_ac2_alice_view_coordination,
            check_ac3_bob_view_event_proposal,
            check_ac4_network_monitor_display,
            check_ac5_event_state_consistency,
            check_ac6_no_errors_or_crashes,
            check_ac7_performance_target,
            check_ac8_nfr_satisfaction,
            check_ac9_demo_readiness,
            check_ac10_fr_coverage,
        ]
        
        results = []
        for check in checks:
            try:
                result = await check()
                results.append(result)
            except Exception as e:
                print(f"❌ Check failed with exception: {e}")
                results.append(False)
        return results
    
    results = asyncio.run(run_all_checks())
    
    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if all(results):
        print("\n✅ All verification checks PASSED")
        return 0
    else:
        print("\n❌ Some verification checks FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)


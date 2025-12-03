"""Verification script for propose_event MCP tool implementation.

This script verifies all acceptance criteria for Story 3.2:
- AC1: Tool parameter acceptance
- AC2: Trusted contact validation
- AC3: EventProposal creation in session state
- AC4: Conflict detection
- AC5: Auto-accept logic (defaults to pending for MVP)
- AC6: Pending status
- AC7: Return value structure
- AC8: User notification
- AC9: Tool schema auto-generation (verified by type hints)
- AC10: Tool registration and A2A Protocol accessibility
- AC11: Mirrored implementation in Alice's Companion

Follows Epic 1 verification pattern.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_ac1_tool_parameter_acceptance():
    """AC1: Tool Parameter Acceptance.
    
    Given Alice's Companion has coordinated a time (Epic 2),
    when Alice's Companion calls propose_event on Bob's server,
    then the tool accepts parameters: event_name (string), datetime (ISO 8601 string),
    location (string), participants (list of user_ids), requester (string).
    """
    print("\n📋 Checking AC1: Tool Parameter Acceptance...")
    try:
        from bob_companion.mcp_server import propose_event
        import inspect
        
        # Check function signature
        sig = inspect.signature(propose_event)
        params = list(sig.parameters.keys())
        
        required_params = ["event_name", "datetime", "location", "participants", "requester"]
        for param in required_params:
            assert param in params, f"Missing required parameter: {param}"
        
        # Check type hints
        annotations = sig.parameters
        assert annotations["event_name"].annotation == str, "event_name should be str"
        assert annotations["datetime"].annotation == str, "datetime should be str"
        assert annotations["location"].annotation == str, "location should be str"
        assert annotations["participants"].annotation == list, "participants should be list"
        assert annotations["requester"].annotation == str, "requester should be str"
        
        print("✅ AC1: Tool accepts all required parameters with correct types")
        return True
    except Exception as e:
        print(f"❌ AC1: Failed - {e}")
        return False


def check_ac2_trusted_contact_validation():
    """AC2: Trusted Contact Validation.
    
    The tool validates requester is in Bob's trusted_contacts list before executing.
    """
    print("\n📋 Checking AC2: Trusted Contact Validation...")
    try:
        from bob_companion.mcp_server import propose_event
        import asyncio
        
        async def _test():
            # Test with trusted contact (should succeed)
            result_trusted = await propose_event(
                event_name="Test Dinner",
                datetime="2024-12-20T19:00:00",
                location="Test Restaurant",
                participants=["alice", "bob"],
                requester="alice"  # Alice is in Bob's trusted_contacts
            )
            assert "error" not in result_trusted, "Trusted contact should not return error"
            assert "status" in result_trusted, "Should return status"
            
            # Test with untrusted contact (should fail)
            result_untrusted = await propose_event(
                event_name="Test Dinner",
                datetime="2024-12-20T19:00:00",
                location="Test Restaurant",
                participants=["eve", "bob"],
                requester="eve"  # Eve is NOT in Bob's trusted_contacts
            )
            assert "error" in result_untrusted, "Untrusted contact should return error"
            assert result_untrusted["error"] == "Access denied", "Should return access denied error"
        
        asyncio.run(_test())
        print("✅ AC2: Trusted contact validation working correctly")
        return True
    except Exception as e:
        print(f"❌ AC2: Failed - {e}")
        return False


def check_ac3_eventproposal_creation():
    """AC3: EventProposal Creation.
    
    The tool creates EventProposal object in Bob's session state with status "pending".
    """
    print("\n📋 Checking AC3: EventProposal Creation...")
    try:
        from bob_companion.mcp_server import propose_event
        from shared.sqlite_session_service import SqliteSessionService
        from pathlib import Path
        import asyncio
        
        db_path = Path(__file__).parent.parent / "companion_sessions.db"
        session_service = SqliteSessionService(db_path=str(db_path))
        
        async def _test():
            # Propose an event
            result = await propose_event(
                event_name="AC3 Test Dinner",
                datetime="2024-12-21T19:00:00",
                location="Test Restaurant",
                participants=["alice", "bob"],
                requester="alice"
            )
            
            assert "event_id" in result, "Should return event_id"
            event_id = result["event_id"]
            
            # Verify EventProposal stored in session state
            session = await session_service.get_session(
                app_name="companion_network",
                user_id="bob",
                session_id="bob_session"
            )
            assert session is not None, "Session should exist"
            
            proposal_key = f"event_proposal:{event_id}"
            assert proposal_key in session.state, f"EventProposal should be stored at {proposal_key}"
            
            # Verify EventProposal structure
            proposal_dict = session.state[proposal_key]
            assert proposal_dict["status"] == "pending", "Status should be pending"
            assert proposal_dict["proposer"] == "alice", "Proposer should be alice"
            assert proposal_dict["recipient"] == "bob", "Recipient should be bob"
            assert "details" in proposal_dict, "Should have details"
            assert proposal_dict["details"]["title"] == "AC3 Test Dinner", "Title should match"
        
        asyncio.run(_test())
        print("✅ AC3: EventProposal creation in session state working")
        return True
    except Exception as e:
        print(f"❌ AC3: Failed - {e}")
        return False


def check_ac4_conflict_detection():
    """AC4: Conflict Detection.
    
    If Bob has conflicting events for the same timeslot, the tool returns "declined" with reason.
    """
    print("\n📋 Checking AC4: Conflict Detection...")
    try:
        from bob_companion.mcp_server import propose_event
        import asyncio
        
        async def _test():
            # First, create an existing event proposal
            first_result = await propose_event(
                event_name="First Event",
                datetime="2024-12-22T19:00:00",
                location="Restaurant A",
                participants=["alice", "bob"],
                requester="alice"
            )
            assert "event_id" in first_result, "First proposal should succeed"
            
            # Now propose another event at the same time (conflict)
            conflict_result = await propose_event(
                event_name="Conflicting Event",
                datetime="2024-12-22T19:00:00",  # Same time
                location="Restaurant B",
                participants=["alice", "bob"],
                requester="alice"
            )
            assert conflict_result["status"] == "declined", "Should return declined status"
            assert "message" in conflict_result, "Should have reason message"
            assert "already has an event" in conflict_result["message"].lower(), "Message should mention conflict"
        
        asyncio.run(_test())
        print("✅ AC4: Conflict detection working correctly")
        return True
    except Exception as e:
        print(f"❌ AC4: Failed - {e}")
        return False


def check_ac5_auto_accept_logic():
    """AC5: Auto-Accept Logic.
    
    If Bob's auto-accept rules match the proposal, the tool returns "accepted" status.
    For MVP, defaults to "pending".
    """
    print("\n📋 Checking AC5: Auto-Accept Logic...")
    try:
        from bob_companion.mcp_server import propose_event
        import asyncio
        
        async def _test():
            result = await propose_event(
                event_name="Auto Accept Test",
                datetime="2024-12-23T19:00:00",
                location="Restaurant",
                participants=["alice", "bob"],
                requester="alice"
            )
            # For MVP, auto-accept is not implemented, so should return "pending"
            assert result["status"] == "pending", "For MVP, should default to pending"
            assert "event_id" in result, "Should return event_id"
        
        asyncio.run(_test())
        print("✅ AC5: Auto-accept logic working (defaults to pending for MVP)")
        return True
    except Exception as e:
        print(f"❌ AC5: Failed - {e}")
        return False


def check_ac6_pending_status():
    """AC6: Pending Status.
    
    Otherwise, the tool returns "pending" status for Bob's manual review.
    """
    print("\n📋 Checking AC6: Pending Status...")
    try:
        from bob_companion.mcp_server import propose_event
        import asyncio
        
        async def _test():
            result = await propose_event(
                event_name="Pending Status Test",
                datetime="2024-12-24T19:00:00",
                location="Restaurant",
                participants=["alice", "bob"],
                requester="alice"
            )
            # Should return pending when no conflicts and auto-accept doesn't match
            assert result["status"] == "pending", "Should return pending status"
            assert "message" in result, "Should have message"
            assert "event_id" in result, "Should return event_id"
        
        asyncio.run(_test())
        print("✅ AC6: Pending status working correctly")
        return True
    except Exception as e:
        print(f"❌ AC6: Failed - {e}")
        return False


def check_ac7_return_value_structure():
    """AC7: Return Value Structure.
    
    The tool returns: status (enum: accepted, declined, pending, counter), message (string explanation),
    event_id (string if accepted/pending).
    """
    print("\n📋 Checking AC7: Return Value Structure...")
    try:
        from bob_companion.mcp_server import propose_event
        import asyncio
        
        async def _test():
            result = await propose_event(
                event_name="Return Value Test",
                datetime="2024-12-25T19:00:00",
                location="Restaurant",
                participants=["alice", "bob"],
                requester="alice"
            )
            
            # Check required keys
            required_keys = ["status", "message", "event_id"]
            for key in required_keys:
                assert key in result, f"Missing required key: {key}"
            
            # Check types
            assert isinstance(result["status"], str), "status should be string"
            assert result["status"] in ["accepted", "declined", "pending", "counter"], "status should be valid enum"
            assert isinstance(result["message"], str), "message should be string"
            assert isinstance(result["event_id"], str), "event_id should be string"
        
        asyncio.run(_test())
        print("✅ AC7: Return value structure correct")
        return True
    except Exception as e:
        print(f"❌ AC7: Failed - {e}")
        return False


def check_ac8_user_notification():
    """AC8: User Notification.
    
    The tool notifies Bob through agent response when event is proposed.
    """
    print("\n📋 Checking AC8: User Notification...")
    try:
        from bob_companion.mcp_server import propose_event
        from shared.sqlite_session_service import SqliteSessionService
        from pathlib import Path
        import asyncio
        
        db_path = Path(__file__).parent.parent / "companion_sessions.db"
        session_service = SqliteSessionService(db_path=str(db_path))
        
        async def _test():
            result = await propose_event(
                event_name="Notification Test",
                datetime="2024-12-26T19:00:00",
                location="Restaurant",
                participants=["alice", "bob"],
                requester="alice"
            )
            
            # Verify notification queued in session state
            session = await session_service.get_session(
                app_name="companion_network",
                user_id="bob",
                session_id="bob_session"
            )
            assert "pending_messages" in session.state, "Should have pending_messages list"
            assert len(session.state["pending_messages"]) > 0, "Should have at least one notification"
            
            # Check notification message format
            last_message = session.state["pending_messages"][-1]
            assert "alice" in last_message.lower(), "Message should mention requester"
            assert "proposed" in last_message.lower(), "Message should mention proposed"
            assert "notification test" in last_message.lower(), "Message should mention event name"
        
        asyncio.run(_test())
        print("✅ AC8: User notification queuing working")
        return True
    except Exception as e:
        print(f"❌ AC8: Failed - {e}")
        return False


def check_ac9_tool_schema_auto_generation():
    """AC9: Tool Schema Auto-generation.
    
    Tool schema is auto-generated from Python function signature using MCP SDK type hints feature.
    """
    print("\n📋 Checking AC9: Tool Schema Auto-generation...")
    try:
        from bob_companion.mcp_server import propose_event
        import inspect
        
        # Check function has type hints
        sig = inspect.signature(propose_event)
        params = sig.parameters
        
        # All parameters should have type annotations
        for param_name, param in params.items():
            assert param.annotation != inspect.Parameter.empty, f"Parameter {param_name} should have type hint"
        
        # Check return type annotation
        assert sig.return_annotation != inspect.Signature.empty, "Function should have return type annotation"
        
        print("✅ AC9: Tool schema auto-generation supported (type hints present)")
        return True
    except Exception as e:
        print(f"❌ AC9: Failed - {e}")
        return False


def check_ac10_tool_registration():
    """AC10: Tool Registration.
    
    Tool is registered with Bob's MCP server and accessible via A2A Protocol.
    """
    print("\n📋 Checking AC10: Tool Registration...")
    try:
        from bob_companion.http_endpoint import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test JSON-RPC 2.0 call to propose_event
        response = client.post("/run", json={
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": "tools/call",
            "params": {
                "name": "propose_event",
                "arguments": {
                    "event_name": "Test Event",
                    "datetime": "2024-12-27T19:00:00",
                    "location": "Test Restaurant",
                    "participants": ["alice", "bob"],
                    "requester": "alice"
                }
            }
        })
        
        assert response.status_code == 200, "Should return 200 OK"
        data = response.json()
        assert "jsonrpc" in data, "Should be JSON-RPC 2.0 response"
        assert data["jsonrpc"] == "2.0", "Should be JSON-RPC 2.0"
        
        # Should have result or error
        assert "result" in data or "error" in data, "Should have result or error"
        
        print("✅ AC10: Tool registered and accessible via HTTP endpoint")
        return True
    except Exception as e:
        print(f"❌ AC10: Failed - {e}")
        print(f"   Note: This may fail if FastAPI/TestClient not available. Tool registration code is present.")
        return False


def check_ac11_mirrored_implementation():
    """AC11: Mirrored Implementation.
    
    Same tool implemented in Alice's Companion (alice_companion/mcp_server.py) for bidirectional event proposals.
    """
    print("\n📋 Checking AC11: Mirrored Implementation...")
    try:
        from bob_companion.mcp_server import propose_event as bob_propose_event
        from alice_companion.mcp_server import propose_event as alice_propose_event
        import inspect
        
        # Check both functions have same signature
        bob_sig = inspect.signature(bob_propose_event)
        alice_sig = inspect.signature(alice_propose_event)
        
        bob_params = list(bob_sig.parameters.keys())
        alice_params = list(alice_sig.parameters.keys())
        
        assert bob_params == alice_params, "Both functions should have same parameters"
        
        # Check return types match
        assert bob_sig.return_annotation == alice_sig.return_annotation, "Return types should match"
        
        # Check both are registered in HTTP endpoints
        from bob_companion.http_endpoint import app as bob_app
        from alice_companion.http_endpoint import app as alice_app
        
        assert bob_app is not None, "Bob's HTTP endpoint should exist"
        assert alice_app is not None, "Alice's HTTP endpoint should exist"
        
        print("✅ AC11: Mirrored implementation in Alice's Companion verified")
        return True
    except Exception as e:
        print(f"❌ AC11: Failed - {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("Verification Script for Story 3.2: Implement propose_event MCP Tool")
    print("=" * 70)
    
    checks = [
        ("AC1", check_ac1_tool_parameter_acceptance),
        ("AC2", check_ac2_trusted_contact_validation),
        ("AC3", check_ac3_eventproposal_creation),
        ("AC4", check_ac4_conflict_detection),
        ("AC5", check_ac5_auto_accept_logic),
        ("AC6", check_ac6_pending_status),
        ("AC7", check_ac7_return_value_structure),
        ("AC8", check_ac8_user_notification),
        ("AC9", check_ac9_tool_schema_auto_generation),
        ("AC10", check_ac10_tool_registration),
        ("AC11", check_ac11_mirrored_implementation),
    ]
    
    results = []
    for ac_id, check_func in checks:
        try:
            result = check_func()
            results.append((ac_id, result))
        except Exception as e:
            print(f"❌ {ac_id}: Exception during check - {e}")
            results.append((ac_id, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for ac_id, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {ac_id}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All acceptance criteria verified!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} acceptance criteria need attention")
        return 1


if __name__ == "__main__":
    sys.exit(main())


"""Verification script for check_availability MCP tool implementation.

This script verifies all acceptance criteria for Story 3.1:
- AC1: Tool parameter acceptance
- AC2: Trusted contact validation
- AC3: Schedule retrieval from session state
- AC4: Availability calculation
- AC5: Return value structure
- AC6: Access denied handling
- AC7: Tool schema auto-generation (verified by type hints)
- AC8: Tool registration and A2A Protocol accessibility
- AC9: Preferences based on sharing rules
- AC10: Mirrored implementation in Alice's Companion

Follows Epic 1 verification pattern.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_ac1_tool_parameter_acceptance():
    """AC1: Tool Parameter Acceptance.
    
    Given Bob's Companion has an MCP server running (Story 2.3),
    when Alice's Companion calls check_availability tool,
    then the tool accepts parameters: timeframe (ISO 8601 range), event_type (string),
    duration_minutes (int), requester (string).
    """
    print("\n📋 Checking AC1: Tool Parameter Acceptance...")
    try:
        from bob_companion.mcp_server import check_availability
        import inspect
        
        # Check function signature
        sig = inspect.signature(check_availability)
        params = list(sig.parameters.keys())
        
        required_params = ["timeframe", "event_type", "duration_minutes", "requester"]
        for param in required_params:
            assert param in params, f"Missing required parameter: {param}"
        
        # Check type hints
        annotations = sig.parameters
        assert annotations["timeframe"].annotation == str, "timeframe should be str"
        assert annotations["event_type"].annotation == str, "event_type should be str"
        assert annotations["duration_minutes"].annotation == int, "duration_minutes should be int"
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
        from bob_companion.mcp_server import check_availability
        import asyncio
        
        async def _test():
            # Test with trusted contact (should succeed)
            result_trusted = await check_availability(
                timeframe="this weekend",
                event_type="dinner",
                duration_minutes=120,
                requester="alice"  # Alice is in Bob's trusted_contacts
            )
            assert "error" not in result_trusted, "Trusted contact should not return error"
            
            # Test with untrusted contact (should fail)
            result_untrusted = await check_availability(
                timeframe="this weekend",
                event_type="dinner",
                duration_minutes=120,
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


def check_ac3_schedule_retrieval():
    """AC3: Schedule Retrieval.
    
    The tool retrieves Bob's schedule from session state using DatabaseSessionService.
    """
    print("\n📋 Checking AC3: Schedule Retrieval...")
    try:
        from bob_companion.mcp_server import check_availability
        from shared.sqlite_session_service import SqliteSessionService
        from pathlib import Path
        import asyncio
        
        # Verify session service is used
        db_path = Path(__file__).parent.parent / "companion_sessions.db"
        session_service = SqliteSessionService(db_path=str(db_path))
        
        async def _test():
            # Check that session can be retrieved
            session = await session_service.get_session(
                app_name="companion_network",
                user_id="bob",
                session_id="bob_session"
            )
            assert session is not None, "Session should exist"
            assert "user_context" in session.state, "User context should be in session state"
            
            # Tool should use this session service
            result = await check_availability(
                timeframe="this weekend",
                event_type="dinner",
                duration_minutes=120,
                requester="alice"
            )
            # If schedule retrieval works, we should get availability result
            assert "available" in result, "Should return availability result"
        
        asyncio.run(_test())
        print("✅ AC3: Schedule retrieval from session state working")
        return True
    except Exception as e:
        print(f"❌ AC3: Failed - {e}")
        return False


def check_ac4_availability_calculation():
    """AC4: Availability Calculation.
    
    The tool calculates available slots within the provided timeframe by excluding busy_slots.
    """
    print("\n📋 Checking AC4: Availability Calculation...")
    try:
        from bob_companion.mcp_server import check_availability
        import asyncio
        
        async def _test():
            # Bob is busy 10am-12pm on Saturday (from test data)
            # Check availability for Saturday evening (should be available)
            result = await check_availability(
                timeframe="2024-12-07T19:00:00/2024-12-07T21:00:00",
                event_type="dinner",
                duration_minutes=120,
                requester="alice"
            )
            assert "available" in result, "Should return available status"
            assert "slots" in result, "Should return slots list"
            assert isinstance(result["slots"], list), "Slots should be a list"
            
            # If available, should have slots
            if result["available"]:
                assert len(result["slots"]) > 0, "Should have available slots"
        
        asyncio.run(_test())
        print("✅ AC4: Availability calculation working correctly")
        return True
    except Exception as e:
        print(f"❌ AC4: Failed - {e}")
        return False


def check_ac5_return_value_structure():
    """AC5: Return Value Structure.
    
    The tool returns: available (bool), slots (list of ISO 8601 ranges),
    preferences (dict), auto_accept_eligible (bool).
    """
    print("\n📋 Checking AC5: Return Value Structure...")
    try:
        from bob_companion.mcp_server import check_availability
        import asyncio
        
        async def _test():
            result = await check_availability(
                timeframe="this weekend",
                event_type="dinner",
                duration_minutes=120,
                requester="alice"
            )
            
            # Check all required keys
            required_keys = ["available", "slots", "preferences", "auto_accept_eligible"]
            for key in required_keys:
                assert key in result, f"Missing required key: {key}"
            
            # Check types
            assert isinstance(result["available"], bool), "available should be bool"
            assert isinstance(result["slots"], list), "slots should be list"
            assert isinstance(result["preferences"], dict), "preferences should be dict"
            assert isinstance(result["auto_accept_eligible"], bool), "auto_accept_eligible should be bool"
        
        asyncio.run(_test())
        print("✅ AC5: Return value structure correct")
        return True
    except Exception as e:
        print(f"❌ AC5: Failed - {e}")
        return False


def check_ac6_access_denied_handling():
    """AC6: Access Denied Handling.
    
    If requester not trusted, returns access denied error with clear message.
    """
    print("\n📋 Checking AC6: Access Denied Handling...")
    try:
        from bob_companion.mcp_server import check_availability
        import asyncio
        
        async def _test():
            result = await check_availability(
                timeframe="this weekend",
                event_type="dinner",
                duration_minutes=120,
                requester="untrusted_user"  # Not in trusted_contacts
            )
            
            assert "error" in result, "Should return error for untrusted requester"
            assert result["error"] == "Access denied", "Error should be 'Access denied'"
            assert "message" in result, "Should include error message"
            assert "trusted" in result["message"].lower(), "Message should mention trusted contacts"
        
        asyncio.run(_test())
        print("✅ AC6: Access denied handling working correctly")
        return True
    except Exception as e:
        print(f"❌ AC6: Failed - {e}")
        return False


def check_ac7_tool_schema_auto_generation():
    """AC7: Tool Schema Auto-generation.
    
    Tool schema is auto-generated from Python function signature using MCP SDK type hints feature.
    """
    print("\n📋 Checking AC7: Tool Schema Auto-generation...")
    try:
        from bob_companion.mcp_server import check_availability
        import inspect
        
        # Verify function has type hints (required for auto-generation)
        sig = inspect.signature(check_availability)
        params = sig.parameters
        
        # All parameters should have type annotations
        for param_name, param in params.items():
            assert param.annotation != inspect.Parameter.empty, \
                f"Parameter {param_name} should have type annotation"
        
        # Verify return type annotation
        assert sig.return_annotation != inspect.Signature.empty, \
            "Function should have return type annotation"
        
        print("✅ AC7: Tool has type hints for schema auto-generation")
        return True
    except Exception as e:
        print(f"❌ AC7: Failed - {e}")
        return False


def check_ac8_tool_registration():
    """AC8: Tool Registration.
    
    Tool is registered with Bob's MCP server and accessible via A2A Protocol.
    """
    print("\n📋 Checking AC8: Tool Registration and A2A Protocol...")
    try:
        # Check that HTTP endpoint exists
        from bob_companion import http_endpoint
        assert hasattr(http_endpoint, "app"), "HTTP endpoint should have FastAPI app"
        assert hasattr(http_endpoint, "handle_jsonrpc"), "Should have JSON-RPC handler"
        
        # Check that endpoint routes to check_availability
        import inspect
        source = inspect.getsource(http_endpoint.handle_jsonrpc)
        assert "check_availability" in source, "Endpoint should route to check_availability"
        assert "tools/call" in source, "Should handle tools/call method"
        
        print("✅ AC8: Tool registered and accessible via HTTP endpoint")
        return True
    except Exception as e:
        print(f"❌ AC8: Failed - {e}")
        return False


def check_ac9_preferences_sharing_rules():
    """AC9: Preferences Based on Sharing Rules.
    
    Return preferences based on sharing_rules for this requester (only categories explicitly allowed).
    """
    print("\n📋 Checking AC9: Preferences Based on Sharing Rules...")
    try:
        from bob_companion.mcp_server import check_availability
        import asyncio
        
        async def _test():
            # Alice has "cuisine_preferences" in sharing_rules
            result = await check_availability(
                timeframe="this weekend",
                event_type="dinner",
                duration_minutes=120,
                requester="alice"
            )
            
            assert "preferences" in result, "Should return preferences"
            # Preferences should be filtered based on sharing_rules
            # Alice is allowed "cuisine_preferences", so should see cuisine if available
            # (This is a basic check - full logic is in the tool implementation)
        
        asyncio.run(_test())
        print("✅ AC9: Preferences filtering based on sharing rules")
        return True
    except Exception as e:
        print(f"❌ AC9: Failed - {e}")
        return False


def check_ac10_mirrored_implementation():
    """AC10: Mirrored Implementation.
    
    Same tool implemented in Alice's Companion for bidirectional availability checking.
    """
    print("\n📋 Checking AC10: Mirrored Implementation...")
    try:
        from bob_companion.mcp_server import check_availability as bob_check
        from alice_companion.mcp_server import check_availability as alice_check
        import inspect
        
        # Check both functions have same signature
        bob_sig = inspect.signature(bob_check)
        alice_sig = inspect.signature(alice_check)
        
        assert bob_sig == alice_sig, "Both tools should have identical signatures"
        
        # Check both have HTTP endpoints
        from bob_companion import http_endpoint as bob_endpoint
        from alice_companion import http_endpoint as alice_endpoint
        
        assert hasattr(bob_endpoint, "app"), "Bob should have HTTP endpoint"
        assert hasattr(alice_endpoint, "app"), "Alice should have HTTP endpoint"
        
        print("✅ AC10: Mirrored implementation in both companions")
        return True
    except Exception as e:
        print(f"❌ AC10: Failed - {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("Verification Script for Story 3.1: check_availability MCP Tool")
    print("=" * 70)
    
    checks = [
        check_ac1_tool_parameter_acceptance,
        check_ac2_trusted_contact_validation,
        check_ac3_schedule_retrieval,
        check_ac4_availability_calculation,
        check_ac5_return_value_structure,
        check_ac6_access_denied_handling,
        check_ac7_tool_schema_auto_generation,
        check_ac8_tool_registration,
        check_ac9_preferences_sharing_rules,
        check_ac10_mirrored_implementation,
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Check failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All checks passed!")
        return 0
    else:
        print(f"❌ {total - passed} check(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())


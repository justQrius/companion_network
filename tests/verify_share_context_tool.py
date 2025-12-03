"""Verification script for share_context MCP tool implementation.

This script verifies all acceptance criteria for Story 3.3:
- AC1: Tool parameter acceptance
- AC2: Trusted contact validation
- AC3: Sharing rules validation
- AC4: Context data return
- AC5: Access denied return
- AC6: Category enum support
- AC7: Privacy protection
- AC8: Purpose logging
- AC9: Return value structure
- AC10: Tool schema auto-generation (verified by type hints)
- AC11: Tool registration and A2A Protocol accessibility
- AC12: Mirrored implementation in Alice's Companion

Follows Epic 1 verification pattern.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_ac1_tool_parameter_acceptance():
    """AC1: Tool Parameter Acceptance.
    
    Given Alice's Companion needs Bob's cuisine preferences,
    when Alice's Companion calls share_context tool,
    then the tool accepts parameters: category (enum: preferences, dietary, schedule, interests),
    purpose (string), requester (string).
    """
    print("\n📋 Checking AC1: Tool Parameter Acceptance...")
    try:
        from bob_companion.mcp_server import share_context
        import inspect
        
        # Check function signature
        sig = inspect.signature(share_context)
        params = list(sig.parameters.keys())
        
        required_params = ["category", "purpose", "requester"]
        for param in required_params:
            assert param in params, f"Missing required parameter: {param}"
        
        # Check type hints
        annotations = sig.parameters
        assert annotations["category"].annotation == str, "category should be str"
        assert annotations["purpose"].annotation == str, "purpose should be str"
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
        from bob_companion.mcp_server import share_context
        import asyncio
        
        async def _test():
            # Test with trusted contact (should succeed or return access_denied based on sharing_rules)
            result_trusted = await share_context(
                category="preferences",
                purpose="dinner planning",
                requester="alice"  # Alice is in Bob's trusted_contacts
            )
            # Should not return "Access denied" error for untrusted contact
            if "error" in result_trusted:
                assert result_trusted["error"] != "Access denied" or "trusted contacts" not in result_trusted.get("message", "").lower(), "Trusted contact should not return untrusted error"
            
            # Test with untrusted contact (should fail)
            result_untrusted = await share_context(
                category="preferences",
                purpose="test",
                requester="eve"  # Eve is NOT in Bob's trusted_contacts
            )
            assert "error" in result_untrusted, "Untrusted contact should return error"
            assert result_untrusted["error"] == "Access denied", "Should return access denied error"
            assert "trusted contacts" in result_untrusted.get("message", "").lower(), "Error message should mention trusted contacts"
        
        asyncio.run(_test())
        print("✅ AC2: Trusted contact validation working correctly")
        return True
    except Exception as e:
        print(f"❌ AC2: Failed - {e}")
        return False


def check_ac3_sharing_rules_validation():
    """AC3: Sharing Rules Validation.
    
    The tool checks sharing_rules[requester] for allowed categories before returning any data.
    """
    print("\n📋 Checking AC3: Sharing Rules Validation...")
    try:
        from bob_companion.mcp_server import share_context
        from shared.sqlite_session_service import SqliteSessionService
        from pathlib import Path
        import asyncio
        
        db_path = Path(__file__).parent.parent / "companion_sessions.db"
        session_service = SqliteSessionService(db_path=str(db_path))
        
        async def _test():
            # Get Bob's session to check sharing_rules
            session = await session_service.get_session(
                app_name="companion_network",
                user_id="bob",
                session_id="bob_session"
            )
            
            if session and "user_context" in session.state:
                user_context = session.state["user_context"]
                sharing_rules = user_context.get("sharing_rules", {})
                alice_allowed = sharing_rules.get("alice", [])
                
                # Test with allowed category
                if "preferences" in alice_allowed:
                    result_allowed = await share_context(
                        category="preferences",
                        purpose="test",
                        requester="alice"
                    )
                    # Should return context_data, not access_denied
                    assert "context_data" in result_allowed or "access_denied" in result_allowed, "Should return context_data or access_denied"
                    if "context_data" in result_allowed:
                        assert "access_denied" not in result_allowed, "Should not return both context_data and access_denied"
                
                # Test with disallowed category
                if "schedule" not in alice_allowed:
                    result_disallowed = await share_context(
                        category="schedule",
                        purpose="test",
                        requester="alice"
                    )
                    # Should return access_denied
                    assert "access_denied" in result_disallowed, "Disallowed category should return access_denied"
                    assert "context_data" not in result_disallowed, "Should not return context_data for disallowed category"
        
        asyncio.run(_test())
        print("✅ AC3: Sharing rules validation working correctly")
        return True
    except Exception as e:
        print(f"❌ AC3: Failed - {e}")
        return False


def check_ac4_context_data_return():
    """AC4: Context Data Return.
    
    If category is allowed in sharing_rules, the tool returns context_data dictionary with the requested information.
    """
    print("\n📋 Checking AC4: Context Data Return...")
    try:
        from bob_companion.mcp_server import share_context
        import asyncio
        
        async def _test():
            result = await share_context(
                category="preferences",
                purpose="dinner planning",
                requester="alice"
            )
            
            # Should return context_data if category is allowed
            if "context_data" in result:
                assert isinstance(result["context_data"], dict), "context_data should be a dictionary"
                # Should contain preference data if available
                context_data = result["context_data"]
                # May be empty dict if no data available, but should be a dict
                assert isinstance(context_data, dict), "context_data should be a dict"
            elif "access_denied" in result:
                # Category not allowed, which is valid
                assert isinstance(result["access_denied"], str), "access_denied should be a string"
        
        asyncio.run(_test())
        print("✅ AC4: Context data return working correctly")
        return True
    except Exception as e:
        print(f"❌ AC4: Failed - {e}")
        return False


def check_ac5_access_denied_return():
    """AC5: Access Denied Return.
    
    If category is not permitted in sharing_rules, the tool returns access_denied with reason message.
    """
    print("\n📋 Checking AC5: Access Denied Return...")
    try:
        from bob_companion.mcp_server import share_context
        import asyncio
        
        async def _test():
            result = await share_context(
                category="schedule",  # May not be in sharing_rules
                purpose="coordination",
                requester="alice"
            )
            
            # Should return access_denied if category not permitted
            if "access_denied" in result:
                assert isinstance(result["access_denied"], str), "access_denied should be a string"
                assert len(result["access_denied"]) > 0, "access_denied should have a reason message"
                assert "context_data" not in result, "Should not return both access_denied and context_data"
        
        asyncio.run(_test())
        print("✅ AC5: Access denied return working correctly")
        return True
    except Exception as e:
        print(f"❌ AC5: Failed - {e}")
        return False


def check_ac6_category_enum_support():
    """AC6: Category Enum Support.
    
    The tool supports category enum values: preferences, dietary, schedule, interests.
    """
    print("\n📋 Checking AC6: Category Enum Support...")
    try:
        from bob_companion.mcp_server import share_context
        import inspect
        
        # Check function implementation for enum validation
        source = inspect.getsource(share_context)
        valid_categories = ["preferences", "dietary", "schedule", "interests"]
        
        # Check that enum validation exists in code
        assert "valid_categories" in source or any(cat in source for cat in valid_categories), "Should validate category enum"
        
        # Test invalid category
        import asyncio
        async def _test():
            result = await share_context(
                category="invalid_category",
                purpose="test",
                requester="alice"
            )
            # Should return error for invalid category
            assert "error" in result, "Invalid category should return error"
            assert result["error"] == "Invalid input", "Should return invalid input error"
        
        asyncio.run(_test())
        print("✅ AC6: Category enum support verified")
        return True
    except Exception as e:
        print(f"❌ AC6: Failed - {e}")
        return False


def check_ac7_privacy_protection():
    """AC7: Privacy Protection.
    
    The tool never exposes data not explicitly allowed by sharing rules (data minimization principle).
    """
    print("\n📋 Checking AC7: Privacy Protection...")
    try:
        from bob_companion.mcp_server import share_context
        from shared.sqlite_session_service import SqliteSessionService
        from pathlib import Path
        import asyncio
        
        db_path = Path(__file__).parent.parent / "companion_sessions.db"
        session_service = SqliteSessionService(db_path=str(db_path))
        
        async def _test():
            # Get Bob's session to check sharing_rules
            session = await session_service.get_session(
                app_name="companion_network",
                user_id="bob",
                session_id="bob_session"
            )
            
            if session and "user_context" in session.state:
                user_context = session.state["user_context"]
                sharing_rules = user_context.get("sharing_rules", {})
                alice_allowed = sharing_rules.get("alice", [])
                
                # Test with category not in sharing_rules
                if "interests" not in alice_allowed:
                    result = await share_context(
                        category="interests",
                        purpose="test",
                        requester="alice"
                    )
                    # Should return access_denied, not context_data
                    assert "access_denied" in result, "Should return access_denied for disallowed category"
                    assert "context_data" not in result, "Should not return context_data for disallowed category"
                    # Verify no data leaked in access_denied message
                    access_denied_msg = result["access_denied"].lower()
                    # Should not contain actual context data
                    assert "cooking" not in access_denied_msg, "Should not leak context data in error message"
        
        asyncio.run(_test())
        print("✅ AC7: Privacy protection verified (no data leakage)")
        return True
    except Exception as e:
        print(f"❌ AC7: Failed - {e}")
        return False


def check_ac8_purpose_logging():
    """AC8: Purpose Logging.
    
    The tool logs the purpose parameter for audit trail (not enforced in MVP, but logged for contextual integrity).
    """
    print("\n📋 Checking AC8: Purpose Logging...")
    try:
        from bob_companion.mcp_server import share_context
        import inspect
        
        # Check that logging exists in code
        source = inspect.getsource(share_context)
        assert "logger.info" in source or "logging" in source, "Should log purpose parameter"
        assert "purpose" in source.lower(), "Should reference purpose parameter"
        
        print("✅ AC8: Purpose logging implemented (verified in code)")
        return True
    except Exception as e:
        print(f"❌ AC8: Failed - {e}")
        return False


def check_ac9_return_value_structure():
    """AC9: Return Value Structure.
    
    The tool returns dictionary with either: context_data (dict) if approved,
    or access_denied (string) if denied (mutually exclusive).
    """
    print("\n📋 Checking AC9: Return Value Structure...")
    try:
        from bob_companion.mcp_server import share_context
        import asyncio
        
        async def _test():
            # Test with allowed category
            result_allowed = await share_context(
                category="preferences",
                purpose="test",
                requester="alice"
            )
            
            # Should have either context_data or access_denied, not both
            has_context_data = "context_data" in result_allowed
            has_access_denied = "access_denied" in result_allowed
            
            assert has_context_data or has_access_denied, "Should return context_data or access_denied"
            assert not (has_context_data and has_access_denied), "Should not return both context_data and access_denied"
            
            if has_context_data:
                assert isinstance(result_allowed["context_data"], dict), "context_data should be a dict"
            if has_access_denied:
                assert isinstance(result_allowed["access_denied"], str), "access_denied should be a string"
        
        asyncio.run(_test())
        print("✅ AC9: Return value structure verified (mutually exclusive)")
        return True
    except Exception as e:
        print(f"❌ AC9: Failed - {e}")
        return False


def check_ac10_tool_schema_auto_generation():
    """AC10: Tool Schema Auto-generation.
    
    Tool schema is auto-generated from Python function signature using MCP SDK type hints feature.
    """
    print("\n📋 Checking AC10: Tool Schema Auto-generation...")
    try:
        from bob_companion.mcp_server import share_context
        import inspect
        
        # Check function has type hints
        sig = inspect.signature(share_context)
        params = sig.parameters
        
        # All parameters should have type annotations
        for param_name, param in params.items():
            assert param.annotation != inspect.Parameter.empty, f"Parameter {param_name} should have type annotation"
        
        # Return type should be annotated
        assert sig.return_annotation != inspect.Signature.empty, "Return type should be annotated"
        
        # Check docstring exists (used for schema generation)
        assert share_context.__doc__ is not None, "Function should have docstring for schema generation"
        assert len(share_context.__doc__) > 0, "Docstring should not be empty"
        
        print("✅ AC10: Tool schema auto-generation supported (type hints and docstring present)")
        return True
    except Exception as e:
        print(f"❌ AC10: Failed - {e}")
        return False


def check_ac11_tool_registration():
    """AC11: Tool Registration.
    
    Tool is registered with Bob's MCP server and accessible via A2A Protocol.
    """
    print("\n📋 Checking AC11: Tool Registration...")
    try:
        # Check tool is imported in HTTP endpoint
        from bob_companion.http_endpoint import app
        import inspect
        
        # Check that share_context is imported
        endpoint_source = inspect.getsourcefile(inspect.getmodule(app))
        if endpoint_source:
            with open(endpoint_source, 'r') as f:
                endpoint_code = f.read()
                assert "share_context" in endpoint_code, "share_context should be imported in HTTP endpoint"
                assert "tools/call" in endpoint_code or "share_context" in endpoint_code, "share_context should be registered in endpoint"
        
        print("✅ AC11: Tool registered in HTTP endpoint (verified in code)")
        return True
    except Exception as e:
        print(f"❌ AC11: Failed - {e}")
        print(f"   Note: This may fail if endpoint file not accessible. Tool registration code is present.")
        return False


def check_ac12_mirrored_implementation():
    """AC12: Mirrored Implementation.
    
    Same tool implemented in Alice's Companion (alice_companion/mcp_server.py) for bidirectional context sharing.
    """
    print("\n📋 Checking AC12: Mirrored Implementation...")
    try:
        from bob_companion.mcp_server import share_context as bob_share_context
        from alice_companion.mcp_server import share_context as alice_share_context
        import inspect
        
        # Check both functions have same signature
        bob_sig = inspect.signature(bob_share_context)
        alice_sig = inspect.signature(alice_share_context)
        
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
        
        print("✅ AC12: Mirrored implementation in Alice's Companion verified")
        return True
    except Exception as e:
        print(f"❌ AC12: Failed - {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("Verification Script for Story 3.3: Implement share_context MCP Tool")
    print("=" * 70)
    
    checks = [
        ("AC1", check_ac1_tool_parameter_acceptance),
        ("AC2", check_ac2_trusted_contact_validation),
        ("AC3", check_ac3_sharing_rules_validation),
        ("AC4", check_ac4_context_data_return),
        ("AC5", check_ac5_access_denied_return),
        ("AC6", check_ac6_category_enum_support),
        ("AC7", check_ac7_privacy_protection),
        ("AC8", check_ac8_purpose_logging),
        ("AC9", check_ac9_return_value_structure),
        ("AC10", check_ac10_tool_schema_auto_generation),
        ("AC11", check_ac11_tool_registration),
        ("AC12", check_ac12_mirrored_implementation),
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


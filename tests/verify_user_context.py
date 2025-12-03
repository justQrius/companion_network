"""Verification script for User Context loading (Story 2.4).

Validates all acceptance criteria for Story 2.4:
- AC1: Alice's Context Configuration matches requirements
- AC2: Bob's Context Configuration matches requirements
- AC3: Context Loading into session state on initialization
- AC4: Context Retrieval from session state
- AC5: Data Model Usage - Context uses UserContext dataclass
- AC6: Session Storage - Context stored in DatabaseSessionService under session scope
- AC7: Initialization Timing - Context loading happens in agent initialization, not every message

Usage:
    # With uv (recommended):
    uv run python tests/verify_user_context.py
    
    # Or ensure dependencies are installed:
    pip install google-adk>=1.19.0
    python tests/verify_user_context.py
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
    print("  Option 1 (recommended): uv run python tests/verify_user_context.py")
    print("  Option 2: pip install google-adk>=1.19.0")
    print("\nThe project uses 'uv' for dependency management.")
    print("Run: uv sync  (to install all dependencies)")
    print("Then: uv run python tests/verify_user_context.py")
    sys.exit(1)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_ac1_alice_context():
    """AC1: Alice's Context Configuration matches requirements."""
    print("\n📋 Checking AC1: Alice's Context Configuration...")
    try:
        from alice_companion.user_context import get_alice_context
        from shared.models import UserContext
        
        context = get_alice_context()
        
        # Verify it's a UserContext instance
        if not isinstance(context, UserContext):
            print(f"❌ AC1 FAILED: Context is not UserContext instance, got {type(context)}")
            return False
        
        # Verify user_id and name
        if context.user_id != "alice":
            print(f"❌ AC1 FAILED: user_id is '{context.user_id}', expected 'alice'")
            return False
        
        if context.name != "Alice":
            print(f"❌ AC1 FAILED: name is '{context.name}', expected 'Alice'")
            return False
        
        # Verify preferences
        if context.preferences.get("cuisine") != ["Italian", "Thai", "Sushi"]:
            print(f"❌ AC1 FAILED: cuisine preferences don't match")
            print(f"   Got: {context.preferences.get('cuisine')}")
            return False
        
        if context.preferences.get("dining_times") != ["19:00", "19:30", "20:00"]:
            print(f"❌ AC1 FAILED: dining_times don't match")
            print(f"   Got: {context.preferences.get('dining_times')}")
            return False
        
        # Verify schedule has busy_slots
        if "busy_slots" not in context.schedule:
            print(f"❌ AC1 FAILED: schedule missing 'busy_slots'")
            return False
        
        if not isinstance(context.schedule["busy_slots"], list) or len(context.schedule["busy_slots"]) == 0:
            print(f"❌ AC1 FAILED: busy_slots should be non-empty list")
            return False
        
        # Verify trusted_contacts
        if context.trusted_contacts != ["bob"]:
            print(f"❌ AC1 FAILED: trusted_contacts is {context.trusted_contacts}, expected ['bob']")
            return False
        
        # Verify sharing_rules
        if context.sharing_rules.get("bob") != ["availability", "cuisine_preferences"]:
            print(f"❌ AC1 FAILED: sharing_rules for bob don't match")
            print(f"   Got: {context.sharing_rules.get('bob')}")
            return False
        
        print("✅ AC1 PASSED: Alice's context matches all requirements")
        return True
        
    except Exception as e:
        print(f"❌ AC1 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac2_bob_context():
    """AC2: Bob's Context Configuration matches requirements."""
    print("\n📋 Checking AC2: Bob's Context Configuration...")
    try:
        from bob_companion.user_context import get_bob_context
        from shared.models import UserContext
        
        context = get_bob_context()
        
        # Verify it's a UserContext instance
        if not isinstance(context, UserContext):
            print(f"❌ AC2 FAILED: Context is not UserContext instance, got {type(context)}")
            return False
        
        # Verify user_id and name
        if context.user_id != "bob":
            print(f"❌ AC2 FAILED: user_id is '{context.user_id}', expected 'bob'")
            return False
        
        if context.name != "Bob":
            print(f"❌ AC2 FAILED: name is '{context.name}', expected 'Bob'")
            return False
        
        # Verify preferences
        if context.preferences.get("cuisine") != ["Italian", "Mexican"]:
            print(f"❌ AC2 FAILED: cuisine preferences don't match")
            print(f"   Got: {context.preferences.get('cuisine')}")
            return False
        
        if context.preferences.get("dining_times") != ["18:30", "19:00"]:
            print(f"❌ AC2 FAILED: dining_times don't match")
            print(f"   Got: {context.preferences.get('dining_times')}")
            return False
        
        # Verify schedule has busy_slots (complementary to Alice's)
        if "busy_slots" not in context.schedule:
            print(f"❌ AC2 FAILED: schedule missing 'busy_slots'")
            return False
        
        if not isinstance(context.schedule["busy_slots"], list) or len(context.schedule["busy_slots"]) == 0:
            print(f"❌ AC2 FAILED: busy_slots should be non-empty list")
            return False
        
        # Verify trusted_contacts
        if context.trusted_contacts != ["alice"]:
            print(f"❌ AC2 FAILED: trusted_contacts is {context.trusted_contacts}, expected ['alice']")
            return False
        
        # Verify sharing_rules
        if context.sharing_rules.get("alice") != ["availability", "cuisine_preferences"]:
            print(f"❌ AC2 FAILED: sharing_rules for alice don't match")
            print(f"   Got: {context.sharing_rules.get('alice')}")
            return False
        
        print("✅ AC2 PASSED: Bob's context matches all requirements")
        return True
        
    except Exception as e:
        print(f"❌ AC2 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac3_context_loading():
    """AC3: Context Loading into session state on initialization."""
    print("\n📋 Checking AC3: Context Loading...")
    try:
        import asyncio
        from alice_companion.agent import session_service, SESSION_ID as ALICE_SESSION_ID
        from bob_companion.agent import SESSION_ID as BOB_SESSION_ID
        
        async def test_loading():
            # Check Alice's session has context
            alice_session = await session_service.get_session(
                app_name="companion_network",
                user_id="alice",
                session_id=ALICE_SESSION_ID
            )
            
            if alice_session is None:
                print("❌ AC3 FAILED: Alice's session not found after initialization")
                return False
            
            if "user_context" not in alice_session.state:
                print("❌ AC3 FAILED: Alice's session state missing 'user_context' key")
                return False
            
            # Check Bob's session has context
            bob_session = await session_service.get_session(
                app_name="companion_network",
                user_id="bob",
                session_id=BOB_SESSION_ID
            )
            
            if bob_session is None:
                print("❌ AC3 FAILED: Bob's session not found after initialization")
                return False
            
            if "user_context" not in bob_session.state:
                print("❌ AC3 FAILED: Bob's session state missing 'user_context' key")
                return False
            
            print("✅ AC3 PASSED: Both contexts loaded into session state")
            return True
        
        result = asyncio.run(test_loading())
        return result
        
    except Exception as e:
        print(f"❌ AC3 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac4_context_retrieval():
    """AC4: Context Retrieval from session state."""
    print("\n📋 Checking AC4: Context Retrieval...")
    try:
        import asyncio
        from alice_companion.agent import session_service, SESSION_ID as ALICE_SESSION_ID
        from bob_companion.agent import SESSION_ID as BOB_SESSION_ID
        
        async def test_retrieval():
            # Retrieve Alice's context
            alice_session = await session_service.get_session(
                app_name="companion_network",
                user_id="alice",
                session_id=ALICE_SESSION_ID
            )
            
            alice_context_dict = alice_session.state.get("user_context")
            if not alice_context_dict:
                print("❌ AC4 FAILED: Could not retrieve Alice's context from session state")
                return False
            
            # Verify context data structure
            if alice_context_dict.get("user_id") != "alice":
                print("❌ AC4 FAILED: Retrieved Alice context has wrong user_id")
                return False
            
            # Retrieve Bob's context
            bob_session = await session_service.get_session(
                app_name="companion_network",
                user_id="bob",
                session_id=BOB_SESSION_ID
            )
            
            bob_context_dict = bob_session.state.get("user_context")
            if not bob_context_dict:
                print("❌ AC4 FAILED: Could not retrieve Bob's context from session state")
                return False
            
            # Verify context data structure
            if bob_context_dict.get("user_id") != "bob":
                print("❌ AC4 FAILED: Retrieved Bob context has wrong user_id")
                return False
            
            print("✅ AC4 PASSED: Contexts can be retrieved from session state")
            return True
        
        result = asyncio.run(test_retrieval())
        return result
        
    except Exception as e:
        print(f"❌ AC4 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac5_data_model_usage():
    """AC5: Data Model Usage - Context uses UserContext dataclass."""
    print("\n📋 Checking AC5: Data Model Usage...")
    try:
        from alice_companion.user_context import get_alice_context
        from bob_companion.user_context import get_bob_context
        from shared.models import UserContext
        
        alice_context = get_alice_context()
        bob_context = get_bob_context()
        
        if not isinstance(alice_context, UserContext):
            print(f"❌ AC5 FAILED: Alice's context is not UserContext instance")
            return False
        
        if not isinstance(bob_context, UserContext):
            print(f"❌ AC5 FAILED: Bob's context is not UserContext instance")
            return False
        
        # Verify it's from shared.models
        if alice_context.__class__.__module__ != "shared.models":
            print(f"❌ AC5 FAILED: Alice's context not from shared.models module")
            return False
        
        if bob_context.__class__.__module__ != "shared.models":
            print(f"❌ AC5 FAILED: Bob's context not from shared.models module")
            return False
        
        print("✅ AC5 PASSED: Contexts use UserContext dataclass from shared.models")
        return True
        
    except Exception as e:
        print(f"❌ AC5 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac6_session_storage():
    """AC6: Session Storage - Context stored in DatabaseSessionService under session scope."""
    print("\n📋 Checking AC6: Session Storage...")
    try:
        import asyncio
        from alice_companion.agent import session_service, SESSION_ID as ALICE_SESSION_ID
        from bob_companion.agent import SESSION_ID as BOB_SESSION_ID
        from alice_companion.sqlite_session_service import SqliteSessionService
        
        if not isinstance(session_service, SqliteSessionService):
            print("❌ AC6 FAILED: Session service is not DatabaseSessionService (SqliteSessionService)")
            return False
        
        async def test_storage():
            # Verify context is stored in session scope (not user or app scope)
            # Session scope means it's tied to the specific session_id
            alice_session = await session_service.get_session(
                app_name="companion_network",
                user_id="alice",
                session_id=ALICE_SESSION_ID
            )
            
            # Verify context is in session state (session scope)
            if "user_context" not in alice_session.state:
                print("❌ AC6 FAILED: Context not stored in session state")
                return False
            
            # Verify it's stored under the correct session key
            if alice_session.id != ALICE_SESSION_ID:
                print("❌ AC6 FAILED: Session ID mismatch")
                return False
            
            print("✅ AC6 PASSED: Context stored in DatabaseSessionService under session scope")
            return True
        
        result = asyncio.run(test_storage())
        return result
        
    except Exception as e:
        print(f"❌ AC6 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ac7_initialization_timing():
    """AC7: Initialization Timing - Context loading happens in agent initialization, not every message."""
    print("\n📋 Checking AC7: Initialization Timing...")
    try:
        import asyncio
        from alice_companion.agent import session_service, SESSION_ID as ALICE_SESSION_ID
        from bob_companion.agent import SESSION_ID as BOB_SESSION_ID
        
        async def test_timing():
            # Context should already be loaded from module import
            # We'll verify it's present without calling any message processing
            
            alice_session = await session_service.get_session(
                app_name="companion_network",
                user_id="alice",
                session_id=ALICE_SESSION_ID
            )
            
            if alice_session is None or "user_context" not in alice_session.state:
                print("❌ AC7 FAILED: Context not loaded during initialization")
                return False
            
            # Verify context persists (was loaded once, not on-demand)
            # If it were loaded on every message, we'd need to call run() to trigger it
            # But we can verify it's already there from module import
            
            bob_session = await session_service.get_session(
                app_name="companion_network",
                user_id="bob",
                session_id=BOB_SESSION_ID
            )
            
            if bob_session is None or "user_context" not in bob_session.state:
                print("❌ AC7 FAILED: Bob's context not loaded during initialization")
                return False
            
            print("✅ AC7 PASSED: Context loaded during agent initialization (module import)")
            return True
        
        result = asyncio.run(test_timing())
        return result
        
    except Exception as e:
        print(f"❌ AC7 FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all acceptance criteria checks."""
    print("=" * 60)
    print("User Context Verification (Story 2.4)")
    print("=" * 60)
    
    results = []
    
    # Run all AC checks
    results.append(("AC1: Alice's Context Configuration", check_ac1_alice_context()))
    results.append(("AC2: Bob's Context Configuration", check_ac2_bob_context()))
    results.append(("AC3: Context Loading", check_ac3_context_loading()))
    results.append(("AC4: Context Retrieval", check_ac4_context_retrieval()))
    results.append(("AC5: Data Model Usage", check_ac5_data_model_usage()))
    results.append(("AC6: Session Storage", check_ac6_session_storage()))
    results.append(("AC7: Initialization Timing", check_ac7_initialization_timing()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} acceptance criteria passed")
    
    if passed == total:
        print("\n🎉 All acceptance criteria verified!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} acceptance criteria failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())


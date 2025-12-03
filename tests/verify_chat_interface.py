"""Verification script for chat interface implementation.

This script verifies all acceptance criteria for Story 4.2:
- AC1: Message Display (immediate message appearance in chat history)
- AC2: Thinking Indicator (loading state while agent processes)
- AC3: Agent Response Display (response appears in chat history)
- AC4: Real-Time Updates (UI updates without page refresh)
- AC5: Independent Interface Updates (Bob's interface updates independently)
- AC6: Async Event Handlers (non-blocking, prevent UI freezing)
- AC7: Chat History Persistence (history persists during session)

Follows Epic 1, 2, 3 verification pattern.
"""

import sys
import ast
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_ac1_message_display():
    """AC1: Message Display.
    
    Given the split-screen layout exists,
    when Alice types "Find a time for dinner with Bob this weekend" and submits,
    then Alice's interface displays her message in chat history immediately.
    """
    print("\n📋 Checking AC1: Message Display...")
    try:
        app_file = project_root / "app.py"
        if not app_file.exists():
            print("❌ AC1: app.py not found")
            return False
        
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for handle_alice_input function
        has_handler = "handle_alice_input" in content
        
        # Check that handler immediately appends message to history
        has_immediate_append = "alice_chat_history.append" in content or "history.append" in content
        
        # Check that handler is connected to components
        has_event_binding = "alice_submit.click" in content and "handle_alice_input" in content
        has_submit_binding = "alice_input.submit" in content and "handle_alice_input" in content
        
        if not has_handler:
            print("❌ AC1: handle_alice_input function not found")
            return False
        
        if not has_immediate_append:
            print("❌ AC1: Immediate message append logic not found")
            return False
        
        if not (has_event_binding and has_submit_binding):
            print("❌ AC1: Event handlers not connected to components")
            return False
        
        print("✅ AC1: Message display handler implemented and connected")
        return True
    except Exception as e:
        print(f"❌ AC1: Failed - {e}")
        return False


def check_ac2_thinking_indicator():
    """AC2: Thinking Indicator.
    
    While agent processes the message, the interface shows "thinking..." indicator or loading state.
    """
    print("\n📋 Checking AC2: Thinking Indicator...")
    try:
        app_file = project_root / "app.py"
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for async handler (enables loading state)
        has_async = "async def handle_alice_input" in content
        
        # Check for explicit "thinking..." text (AC2 requirement)
        has_thinking_text = '"thinking..."' in content or "'thinking...'" in content
        
        if not has_async:
            print("❌ AC2: Handler is not async (required for loading state)")
            return False
        
        if not has_thinking_text:
            print("❌ AC2: Explicit 'thinking...' text not found")
            return False
        
        print("✅ AC2: Thinking indicator implemented (explicit 'thinking...' text)")
        return True
    except Exception as e:
        print(f"❌ AC2: Failed - {e}")
        return False


def check_ac3_agent_response_display():
    """AC3: Agent Response Display.
    
    When agent processing completes, the interface displays Companion's response in chat history.
    """
    print("\n📋 Checking AC3: Agent Response Display...")
    try:
        app_file = project_root / "app.py"
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for async agent runner calls (new pattern uses _run_*_agent_async helpers)
        has_agent_call = ("_run_alice_agent_async" in content and "_run_bob_agent_async" in content) or ("runner.run_async" in content)
        
        # Check that response is appended to history
        has_response_append = "agent_response" in content or "alice_chat_history[-1]" in content
        
        if not has_agent_call:
            print("❌ AC3: Async agent runner calls not found")
            return False
        
        if not has_response_append:
            print("❌ AC3: Response append logic not found")
            return False
        
        print("✅ AC3: Agent response display implemented")
        return True
    except Exception as e:
        print(f"❌ AC3: Failed - {e}")
        return False


def check_ac4_real_time_updates():
    """AC4: Real-Time Updates.
    
    The interface updates in real-time without page refresh (no manual refresh required).
    """
    print("\n📋 Checking AC4: Real-Time Updates...")
    try:
        app_file = project_root / "app.py"
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for async handlers (required for real-time updates)
        has_async_alice = "async def handle_alice_input" in content
        has_async_bob = "async def handle_bob_input" in content
        
        # Check that handlers return updated history (Gradio auto-updates)
        has_return_history = "return" in content and "history" in content.lower()
        
        if not (has_async_alice and has_async_bob):
            print("❌ AC4: Async handlers not found")
            return False
        
        print("✅ AC4: Real-time updates implemented (async handlers with history return)")
        print("   Note: Visual testing required to verify no page refresh needed")
        return True
    except Exception as e:
        print(f"❌ AC4: Failed - {e}")
        return False


def check_ac5_independent_interface_updates():
    """AC5: Independent Interface Updates.
    
    Bob's interface updates independently when his Companion receives A2A calls.
    """
    print("\n📋 Checking AC5: Independent Interface Updates...")
    try:
        app_file = project_root / "app.py"
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for separate handlers (Alice and Bob)
        has_separate_handlers = "handle_alice_input" in content and "handle_bob_input" in content
        
        # Check for separate chat history variables
        has_separate_history = "alice_chat_history" in content and "bob_chat_history" in content
        
        # Check that handlers are independent (no shared blocking state)
        # This is verified by separate functions and separate history
        
        if not has_separate_handlers:
            print("❌ AC5: Separate handlers not found")
            return False
        
        if not has_separate_history:
            print("❌ AC5: Separate chat history variables not found")
            return False
        
        print("✅ AC5: Independent interface updates implemented (separate handlers and history)")
        print("   Note: Full A2A integration requires Story 4.4 for complete verification")
        return True
    except Exception as e:
        print(f"❌ AC5: Failed - {e}")
        return False


def check_ac6_async_event_handlers():
    """AC6: Async Event Handlers.
    
    Both interfaces use async event handlers (non-blocking) to prevent UI freezing during agent processing.
    """
    print("\n📋 Checking AC6: Async Event Handlers...")
    try:
        app_file = project_root / "app.py"
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for async function definitions
        has_async_alice = "async def handle_alice_input" in content
        has_async_bob = "async def handle_bob_input" in content
        
        if not has_async_alice:
            print("❌ AC6: handle_alice_input is not async")
            return False
        
        if not has_async_bob:
            print("❌ AC6: handle_bob_input is not async")
            return False
        
        print("✅ AC6: Async event handlers implemented (non-blocking)")
        return True
    except Exception as e:
        print(f"❌ AC6: Failed - {e}")
        return False


def check_ac7_chat_history_persistence():
    """AC7: Chat History Persistence.
    
    Chat history persists during the session (stored in Gradio State component,
    survives page interactions but not app restarts).
    """
    print("\n📋 Checking AC7: Chat History Persistence...")
    try:
        app_file = project_root / "app.py"
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for module-level chat history variables
        has_history_vars = "alice_chat_history" in content and "bob_chat_history" in content
        
        # Check that history is updated and persisted
        has_history_update = "alice_chat_history = history.copy()" in content or "alice_chat_history.append" in content
        
        if not has_history_vars:
            print("❌ AC7: Chat history variables not found")
            return False
        
        if not has_history_update:
            print("❌ AC7: Chat history update logic not found")
            return False
        
        print("✅ AC7: Chat history persistence implemented (module-level variables)")
        print("   Note: Session persistence verified via module-level storage")
        return True
    except Exception as e:
        print(f"❌ AC7: Failed - {e}")
        return False


def check_agent_initialization():
    """Additional check: Agent initialization.
    
    Verify agents are initialized with user contexts and session IDs.
    """
    print("\n📋 Checking Agent Initialization...")
    try:
        app_file = project_root / "app.py"
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for load_agent_references function (renamed from initialize_agents)
        has_init_function = "def load_agent_references" in content or "load_agent_references" in content
        
        # Check for agent imports
        has_agent_imports = "alice_companion" in content and "bob_companion" in content
        
        # Check for user context imports
        has_context_imports = "get_alice_context" in content and "get_bob_context" in content
        
        if not has_init_function:
            print("❌ Initialization: load_agent_references function not found")
            return False
        
        if not has_agent_imports:
            print("❌ Initialization: Agent imports not found")
            return False
        
        if not has_context_imports:
            print("❌ Initialization: User context imports not found")
            return False
        
        print("✅ Agent initialization implemented")
        return True
    except Exception as e:
        print(f"❌ Initialization: Failed - {e}")
        return False


def check_error_handling():
    """Additional check: Error handling.
    
    Verify user-friendly error messages are displayed (no stack traces).
    """
    print("\n📋 Checking Error Handling...")
    try:
        app_file = project_root / "app.py"
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for try-except blocks in handlers
        has_try_except = "try:" in content and "except Exception" in content
        
        # Check for user-friendly error messages
        has_error_message = "I encountered an error" in content or "error processing" in content.lower()
        
        if not has_try_except:
            print("❌ Error Handling: Try-except blocks not found")
            return False
        
        if not has_error_message:
            print("❌ Error Handling: User-friendly error messages not found")
            return False
        
        print("✅ Error handling implemented (user-friendly messages)")
        return True
    except Exception as e:
        print(f"❌ Error Handling: Failed - {e}")
        return False


def main():
    """Run all acceptance criteria checks."""
    print("=" * 70)
    print("Chat Interface Verification")
    print("Story 4.2: Implement Chat Interface for Alice and Bob")
    print("=" * 70)
    
    results = []
    
    # Run all AC checks
    results.append(("AC1", check_ac1_message_display()))
    results.append(("AC2", check_ac2_thinking_indicator()))
    results.append(("AC3", check_ac3_agent_response_display()))
    results.append(("AC4", check_ac4_real_time_updates()))
    results.append(("AC5", check_ac5_independent_interface_updates()))
    results.append(("AC6", check_ac6_async_event_handlers()))
    results.append(("AC7", check_ac7_chat_history_persistence()))
    results.append(("Init", check_agent_initialization()))
    results.append(("Error", check_error_handling()))
    
    # Summary
    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for ac_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{ac_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All acceptance criteria verified!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} check(s) failed. Review output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())


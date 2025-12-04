"""Check session state for user context."""
import asyncio
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from alice_companion.agent import session_service

async def check():
    print("\n" + "="*60)
    print("Session State Debug")
    print("="*60)

    session_ids = ["alice_session", "test_app_pattern_session", "test_explicit_tool_session"]

    for sess_id in session_ids:
        print(f"\nChecking session: {sess_id}")
        try:
            session = await session_service.get_session(
                app_name="companion_network",
                user_id="alice",
                session_id=sess_id
            )
            if session:
                print(f"  ✅ Session exists")
                print(f"  State keys: {list(session.state.keys())}")
                if "user_context" in session.state:
                    print(f"  User context keys: {list(session.state['user_context'].keys())}")
                    if "trusted_contacts" in session.state["user_context"]:
                        contacts = session.state["user_context"]["trusted_contacts"]
                        print(f"  Trusted contacts: {contacts}")
                else:
                    print(f"  ⚠️  NO user_context in state!")
            else:
                print(f"  ❌ Session not found")
        except Exception as e:
            print(f"  ❌ Error: {e}")

asyncio.run(check())

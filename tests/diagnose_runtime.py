"""Diagnose runtime agent configuration."""
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("\n" + "="*60)
print("RUNTIME DIAGNOSTIC - Agent Configuration")
print("="*60)

# Import the actual modules used by app.py
from alice_companion import agent as alice_module
from bob_companion import agent as bob_module

print("\n📋 ALICE'S COMPANION:")
print(f"  Agent name: {alice_module.agent.name}")
print(f"  Model: {alice_module.agent.model}")
print(f"  Tools count: {len(alice_module.agent.tools) if hasattr(alice_module.agent, 'tools') and alice_module.agent.tools else 0}")
if hasattr(alice_module.agent, 'tools') and alice_module.agent.tools:
    for i, tool in enumerate(alice_module.agent.tools, 1):
        print(f"    {i}. {tool.__name__ if hasattr(tool, '__name__') else tool}")

print(f"\n  Has 'app' variable: {hasattr(alice_module, 'app')}")
if hasattr(alice_module, 'app'):
    print(f"  App name: {alice_module.app.name}")
    print(f"  App root_agent: {alice_module.app.root_agent.name}")

print(f"\n  Has 'runner' variable: {hasattr(alice_module, 'runner')}")
if hasattr(alice_module, 'runner'):
    print(f"  Runner type: {type(alice_module.runner).__name__}")
    # Try to inspect runner's internal structure
    if hasattr(alice_module.runner, '_app'):
        print(f"  Runner._app exists: True")
    if hasattr(alice_module.runner, 'app'):
        print(f"  Runner.app exists: True")

print("\n📋 BOB'S COMPANION:")
print(f"  Agent name: {bob_module.agent.name}")
print(f"  Model: {bob_module.agent.model}")
print(f"  Tools count: {len(bob_module.agent.tools) if hasattr(bob_module.agent, 'tools') and bob_module.agent.tools else 0}")
if hasattr(bob_module.agent, 'tools') and bob_module.agent.tools:
    for i, tool in enumerate(bob_module.agent.tools, 1):
        print(f"    {i}. {tool.__name__ if hasattr(tool, '__name__') else tool}")

print(f"\n  Has 'app' variable: {hasattr(bob_module, 'app')}")
if hasattr(bob_module, 'app'):
    print(f"  App name: {bob_module.app.name}")
    print(f"  App root_agent: {bob_module.app.root_agent.name}")

print("\n" + "="*60)
print("CONCLUSION:")
print("="*60)

if (hasattr(alice_module, 'app') and hasattr(bob_module, 'app')):
    print("✅ Both agents have App wrappers")
    if (hasattr(alice_module.agent, 'tools') and alice_module.agent.tools and
        hasattr(bob_module.agent, 'tools') and bob_module.agent.tools):
        print("✅ Both agents have tools registered")
        print("\n🎯 EXPECTED BEHAVIOR: Agents SHOULD use tools")
        print("   If agents still show generic greetings, the issue is:")
        print("   1. Model choosing not to call tools (check system instruction)")
        print("   2. Session missing user_context (check alice_session state)")
        print("   3. A2A endpoints not accessible (check MCP servers)")
    else:
        print("❌ Tools are NOT registered!")
else:
    print("❌ App pattern NOT applied!")

print("\n")

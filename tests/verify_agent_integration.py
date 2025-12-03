"""
Verification script for agent integration (Story 4.4).

Follows Epic 1, 2, 3 pattern for verification scripts.
Verifies agent initialization, MCP server startup, and A2A endpoint exposure.
"""

import sys
import time
import httpx
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import (
    initialize_agents,
    start_mcp_servers,
    verify_a2a_endpoints,
    startup_sequence,
    alice_agent,
    bob_agent,
    alice_runner,
    bob_runner
)


def verify_agent_initialization():
    """Verify agents are initialized correctly."""
    print("=" * 60)
    print("Verifying Agent Initialization...")
    print("=" * 60)
    
    try:
        alice, bob = initialize_agents()
        
        assert alice is not None, "Alice agent not initialized"
        assert bob is not None, "Bob agent not initialized"
        assert alice_runner is not None, "Alice runner not initialized"
        assert bob_runner is not None, "Bob runner not initialized"
        
        print("✅ Agent initialization: PASSED")
        print(f"   - Alice agent: {type(alice).__name__}")
        print(f"   - Bob agent: {type(bob).__name__}")
        return True
    except Exception as e:
        print(f"❌ Agent initialization: FAILED - {e}")
        return False


def verify_mcp_servers():
    """Verify MCP servers can be started."""
    print("=" * 60)
    print("Verifying MCP Server Startup...")
    print("=" * 60)
    
    try:
        start_mcp_servers()
        time.sleep(2)  # Give servers time to start
        
        # Check Alice's endpoint
        try:
            response = httpx.get("http://localhost:8001/run", timeout=2.0)
            alice_ok = response.status_code in [405, 200]
        except Exception:
            alice_ok = False
        
        # Check Bob's endpoint
        try:
            response = httpx.get("http://localhost:8002/run", timeout=2.0)
            bob_ok = response.status_code in [405, 200]
        except Exception:
            bob_ok = False
        
        if alice_ok and bob_ok:
            print("✅ MCP server startup: PASSED")
            print("   - Alice MCP server: running on localhost:8001")
            print("   - Bob MCP server: running on localhost:8002")
            return True
        else:
            print("⚠️  MCP server startup: PARTIAL")
            if not alice_ok:
                print("   - Alice MCP server: not accessible")
            if not bob_ok:
                print("   - Bob MCP server: not accessible")
            return False
    except Exception as e:
        print(f"❌ MCP server startup: FAILED - {e}")
        return False


def verify_a2a_endpoints_accessible():
    """Verify A2A endpoints are accessible."""
    print("=" * 60)
    print("Verifying A2A Endpoint Accessibility...")
    print("=" * 60)
    
    try:
        verify_a2a_endpoints()
        print("✅ A2A endpoint verification: PASSED")
        print("   - Alice endpoint: http://localhost:8001/run")
        print("   - Bob endpoint: http://localhost:8002/run")
        return True
    except Exception as e:
        print(f"❌ A2A endpoint verification: FAILED - {e}")
        return False


def verify_startup_sequence():
    """Verify complete startup sequence."""
    print("=" * 60)
    print("Verifying Complete Startup Sequence...")
    print("=" * 60)
    
    try:
        startup_sequence()
        print("✅ Startup sequence: PASSED")
        return True
    except Exception as e:
        print(f"❌ Startup sequence: FAILED - {e}")
        return False


def main():
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("Agent Integration Verification (Story 4.4)")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run verifications
    results.append(("Agent Initialization", verify_agent_initialization()))
    results.append(("MCP Server Startup", verify_mcp_servers()))
    results.append(("A2A Endpoint Accessibility", verify_a2a_endpoints_accessible()))
    results.append(("Startup Sequence", verify_startup_sequence()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} checks passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All verifications passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} verification(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())


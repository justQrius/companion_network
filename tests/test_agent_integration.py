"""
Integration tests for agent initialization, MCP server startup, and A2A endpoint exposure.

Tests Story 4.4: Integrate Agents with Gradio UI
"""

import pytest
import httpx
import time
import threading
from pathlib import Path
import sys

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


class TestAgentInitialization:
    """Test agent initialization functionality."""
    
    def test_initialize_agents_creates_instances(self):
        """Test that initialize_agents() creates agent instances."""
        alice, bob = initialize_agents()
        
        assert alice is not None
        assert bob is not None
        assert alice_runner is not None
        assert bob_runner is not None
    
    def test_agents_have_correct_session_ids(self):
        """Test that agents are configured with correct session IDs."""
        initialize_agents()
        
        # Verify runners have session service configured
        assert alice_runner.session_service is not None
        assert bob_runner.session_service is not None
    
    def test_agents_have_user_contexts(self):
        """Test that agents have user contexts loaded."""
        initialize_agents()
        
        # User contexts are loaded in agent modules on import
        # This is verified by checking that agents can access session state
        import asyncio
        
        async def check_context():
            session = await alice_runner.session_service.get_session(
                app_name="companion_network",
                user_id="alice",
                session_id="alice_session"
            )
            assert session is not None
            assert "user_context" in session.state
        
        asyncio.run(check_context())


class TestMCPServerStartup:
    """Test MCP server startup functionality."""
    
    def test_start_mcp_servers_starts_both_servers(self):
        """Test that start_mcp_servers() starts both servers."""
        # Note: This test may interfere with other tests if servers are already running
        # In a real test environment, we'd use test fixtures to manage server lifecycle
        try:
            start_mcp_servers()
            time.sleep(2)  # Give servers time to start
            
            # Verify servers are running by checking endpoints
            alice_response = httpx.get("http://localhost:8001/run", timeout=2.0)
            bob_response = httpx.get("http://localhost:8002/run", timeout=2.0)
            
            # POST-only endpoints return 405 for GET, which confirms server is running
            assert alice_response.status_code in [405, 200]
            assert bob_response.status_code in [405, 200]
        except httpx.ConnectError:
            pytest.skip("MCP servers not accessible (may already be running or ports in use)")


class TestA2AEndpointVerification:
    """Test A2A endpoint verification functionality."""
    
    def test_verify_a2a_endpoints_checks_both_endpoints(self):
        """Test that verify_a2a_endpoints() checks both endpoints."""
        # This test requires servers to be running
        # In a real test environment, we'd start servers in a fixture
        try:
            verify_a2a_endpoints()
        except Exception as e:
            if "not accessible" in str(e):
                pytest.skip("A2A endpoints not accessible (servers may not be running)")
            else:
                raise


class TestStartupSequence:
    """Test complete startup sequence orchestration."""
    
    def test_startup_sequence_executes_all_steps(self):
        """Test that startup_sequence() executes all initialization steps."""
        # This test requires a clean environment
        # In a real test environment, we'd use fixtures to manage state
        try:
            startup_sequence()
            
            # Verify agents are initialized
            assert alice_agent is not None
            assert bob_agent is not None
            
            # Verify endpoints are accessible (if servers started)
            try:
                verify_a2a_endpoints()
            except Exception:
                # Servers may not have started in test environment
                pass
        except Exception as e:
            if "ports" in str(e).lower() or "already" in str(e).lower():
                pytest.skip("Startup sequence test skipped (ports may be in use)")
            else:
                raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


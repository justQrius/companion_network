"""Integration tests for network activity monitor end-to-end A2A event flow.

Tests the complete flow:
1. A2A tool call is made (via call_other_companion_tool)
2. Event is logged to session state (via log_a2a_event)
3. Network monitor reads and displays the event (via update_network_monitor)
4. Real-time updates work correctly

This addresses the advisory note from code review about adding integration
test for end-to-end A2A event flow.

Note: These tests require mocking of external dependencies (gradio, google.adk)
since they test the integration between components. For full end-to-end testing
with real dependencies, see manual testing guide.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
from typing import Dict, Any
import sys
from pathlib import Path

# Mock external dependencies before importing
sys.modules['gradio'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.adk'] = MagicMock()

# Import functions from app.py and agent modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import with mocked dependencies
with patch.dict('sys.modules', {
    'gradio': MagicMock(),
    'google.adk': MagicMock(),
    'alice_companion.agent': MagicMock(),
    'bob_companion.agent': MagicMock(),
}):
    try:
        from app import update_network_monitor
        from alice_companion.agent import call_other_companion_tool
        from shared.a2a_logging import log_a2a_event
    except ImportError:
        # If imports fail due to missing dependencies, tests will be skipped
        pytest.skip("Required dependencies not available for integration tests")


class TestNetworkMonitorIntegration:
    """Integration tests for network monitor with A2A event flow."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_a2a_event_flow(self):
        """Test complete flow: A2A call → event logged → monitor displays.
        
        This test verifies:
        1. A2A tool call triggers event logging
        2. Event appears in session state
        3. Network monitor can read and format the event
        4. Event is displayed with all required fields
        """
        with patch('alice_companion.agent.session_service') as mock_session_service, \
             patch('alice_companion.agent.get_mcp_client') as mock_get_client, \
             patch('app.alice_runner') as mock_alice_runner, \
             patch('app.bob_runner') as mock_bob_runner:
            
            # Setup: Create mock session with empty events
            mock_alice_session = Mock()
            mock_alice_session.state = {"app:a2a_events": []}
            mock_bob_session = Mock()
            mock_bob_session.state = {}
            
            # Mock session service for A2A call
            mock_session_service.get_session = AsyncMock(return_value=mock_alice_session)
            mock_session_service.update_session_state = AsyncMock()
            
            # Mock MCP client for successful tool call
            mock_client = AsyncMock()
            mock_client.call_tool = AsyncMock(return_value={
                "available": True,
                "slots": ["2025-12-07T19:00:00/2025-12-07T21:00:00"]
            })
            mock_get_client.return_value = mock_client
            
            # Step 1: Make A2A tool call (this should log an event)
            result = await call_other_companion_tool(
                "check_availability",
                timeframe="this weekend",
                requester="alice"
            )
            
            # Verify tool call succeeded
            assert result is not None
            assert "available" in result
            
            # Step 2: Verify event was logged to session state
            events = mock_alice_session.state.get("app:a2a_events", [])
            assert len(events) == 1, "Event should be logged to session state"
            
            logged_event = events[0]
            assert logged_event["sender"] == "alice"
            assert logged_event["receiver"] == "bob"
            assert logged_event["tool"] == "check_availability"
            assert logged_event["status"] == "success"
            assert "timestamp" in logged_event
            assert "requester" not in logged_event["params"], "Sensitive parameter should be redacted"
            
            # Step 3: Mock runners for network monitor
            mock_alice_runner.session_service.get_session = AsyncMock(return_value=mock_alice_session)
            mock_bob_runner.session_service.get_session = AsyncMock(return_value=mock_bob_session)
            
            # Step 4: Network monitor should read and display the event
            monitor_result = await update_network_monitor()
            
            # Verify monitor result structure
            assert "events" in monitor_result
            assert "count" in monitor_result
            assert monitor_result["count"] == 1
            
            # Verify event is formatted correctly
            formatted_events = monitor_result["events"]
            assert len(formatted_events) == 1
            
            formatted_event = formatted_events[0]
            assert formatted_event["sender"] == "Alice's Companion"
            assert formatted_event["receiver"] == "Bob's Companion"
            assert formatted_event["tool"] == "check_availability"
            assert formatted_event["status_info"]["status"] == "success"
            assert formatted_event["status_info"]["icon"] == "✅"
            assert "timestamp" in formatted_event
            assert "params" in formatted_event
    
    @pytest.mark.asyncio
    async def test_end_to_end_failed_a2a_event_flow(self):
        """Test complete flow with failed A2A call.
        
        Verifies that failed A2A calls are also logged and displayed correctly.
        """
        with patch('alice_companion.agent.session_service') as mock_session_service, \
             patch('alice_companion.agent.get_mcp_client') as mock_get_client, \
             patch('app.alice_runner') as mock_alice_runner, \
             patch('app.bob_runner') as mock_bob_runner:
            
            # Setup: Create mock session
            mock_alice_session = Mock()
            mock_alice_session.state = {"app:a2a_events": []}
            mock_bob_session = Mock()
            mock_bob_session.state = {}
            
            # Mock session service
            mock_session_service.get_session = AsyncMock(return_value=mock_alice_session)
            mock_session_service.update_session_state = AsyncMock()
            
            # Mock MCP client to raise connection error
            mock_client = AsyncMock()
            mock_client.call_tool = AsyncMock(side_effect=ConnectionError("Connection failed"))
            mock_get_client.return_value = mock_client
            
            # Step 1: Make A2A tool call (should fail and log failed event)
            result = await call_other_companion_tool(
                "check_availability",
                timeframe="this weekend",
                requester="alice"
            )
            
            # Verify error result is returned
            assert result is not None
            assert "error" in result
            
            # Step 2: Verify failed event was logged
            events = mock_alice_session.state.get("app:a2a_events", [])
            assert len(events) == 1, "Failed event should be logged"
            
            logged_event = events[0]
            assert logged_event["status"] == "failed"
            
            # Step 3: Network monitor should display failed event
            mock_alice_runner.session_service.get_session = AsyncMock(return_value=mock_alice_session)
            mock_bob_runner.session_service.get_session = AsyncMock(return_value=mock_bob_session)
            
            monitor_result = await update_network_monitor()
            
            # Verify failed event is displayed
            formatted_events = monitor_result["events"]
            assert len(formatted_events) == 1
            
            formatted_event = formatted_events[0]
            assert formatted_event["status_info"]["status"] == "failed"
            assert formatted_event["status_info"]["icon"] == "❌"
            assert formatted_event["status_info"]["color"] == "red"
    
    @pytest.mark.asyncio
    async def test_end_to_end_multiple_events_chronological_order(self):
        """Test that multiple A2A events are displayed in chronological order.
        
        Verifies the complete flow with multiple events from both agents.
        """
        with patch('app.alice_runner') as mock_alice_runner, \
             patch('app.bob_runner') as mock_bob_runner:
            
            # Create events with different timestamps (out of order)
            alice_events = [
                {
                    "timestamp": "2025-12-03T15:00:00",
                    "sender": "alice",
                    "receiver": "bob",
                    "tool": "check_availability",
                    "params": {"timeframe": "this weekend"},
                    "status": "success"
                },
                {
                    "timestamp": "2025-12-03T15:02:00",
                    "sender": "alice",
                    "receiver": "bob",
                    "tool": "propose_event",
                    "params": {"event_name": "dinner"},
                    "status": "success"
                }
            ]
            
            bob_events = [
                {
                    "timestamp": "2025-12-03T15:01:00",  # Between Alice's events
                    "sender": "bob",
                    "receiver": "alice",
                    "tool": "share_context",
                    "params": {"category": "preferences"},
                    "status": "success"
                }
            ]
            
            mock_alice_session = Mock()
            mock_alice_session.state = {"app:a2a_events": alice_events}
            mock_bob_session = Mock()
            mock_bob_session.state = {"app:a2a_events": bob_events}
            
            mock_alice_runner.session_service.get_session = AsyncMock(return_value=mock_alice_session)
            mock_bob_runner.session_service.get_session = AsyncMock(return_value=mock_bob_session)
            
            # Network monitor should merge and sort events chronologically
            monitor_result = await update_network_monitor()
            
            formatted_events = monitor_result["events"]
            assert len(formatted_events) == 3, "Should display all 3 events"
            
            # Verify chronological order (oldest to newest)
            assert formatted_events[0]["timestamp_iso"] == "2025-12-03T15:00:00"  # First event
            assert formatted_events[1]["timestamp_iso"] == "2025-12-03T15:01:00"  # Second event
            assert formatted_events[2]["timestamp_iso"] == "2025-12-03T15:02:00"  # Third event
    
    @pytest.mark.asyncio
    async def test_real_time_update_simulation(self):
        """Test that network monitor can detect recent events for activity indicator.
        
        Simulates real-time updates by checking if recent events trigger activity status.
        """
        with patch('app.alice_runner') as mock_alice_runner, \
             patch('app.bob_runner') as mock_bob_runner, \
             patch('app.datetime') as mock_datetime:
            
            # Mock current time
            now = datetime(2025, 12, 3, 15, 0, 0)
            mock_datetime.now.return_value = now
            mock_datetime.fromisoformat = datetime.fromisoformat
            
            # Create recent event (within last 2 seconds)
            recent_event = {
                "timestamp": "2025-12-03T14:59:59",  # 1 second ago
                "sender": "alice",
                "receiver": "bob",
                "tool": "check_availability",
                "params": {},
                "status": "success"
            }
            
            mock_alice_session = Mock()
            mock_alice_session.state = {"app:a2a_events": [recent_event]}
            mock_bob_session = Mock()
            mock_bob_session.state = {}
            
            mock_alice_runner.session_service.get_session = AsyncMock(return_value=mock_alice_session)
            mock_bob_runner.session_service.get_session = AsyncMock(return_value=mock_bob_session)
            
            # Network monitor should detect recent activity
            monitor_result = await update_network_monitor()
            
            # Verify activity indicator shows active
            assert monitor_result["activity_status"] == "🟢 Active"
            assert monitor_result["recent_activity"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


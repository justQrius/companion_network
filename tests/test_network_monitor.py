"""Unit tests for network activity monitor.

Tests the network monitor component that displays A2A events,
including event formatting, chronological ordering, real-time updates,
and edge case handling.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import Dict, Any

# Import monitor function from app.py
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import update_network_monitor


class TestUpdateNetworkMonitor:
    """Test suite for update_network_monitor function."""
    
    @pytest.mark.asyncio
    async def test_update_network_monitor_empty_events(self):
        """Test AC1, AC6: Empty events list shows empty state message."""
        with patch('app.alice_runner') as mock_alice_runner, \
             patch('app.bob_runner') as mock_bob_runner:
            
            # Mock sessions with empty events
            mock_alice_session = Mock()
            mock_alice_session.state = {}
            mock_bob_session = Mock()
            mock_bob_session.state = {}
            
            mock_alice_runner.session_service.get_session = AsyncMock(return_value=mock_alice_session)
            mock_bob_runner.session_service.get_session = AsyncMock(return_value=mock_bob_session)
            
            result = await update_network_monitor()
            
            assert result["message"] == "No A2A events yet"
            assert result["events"] == []
            assert result["count"] == 0
    
    @pytest.mark.asyncio
    async def test_update_network_monitor_chronological_ordering(self):
        """Test AC2: Events displayed in chronological order (oldest to newest)."""
        with patch('app.alice_runner') as mock_alice_runner, \
             patch('app.bob_runner') as mock_bob_runner:
            
            # Create events with different timestamps (out of order)
            event1 = {
                "timestamp": "2025-12-03T15:00:00",
                "sender": "alice",
                "receiver": "bob",
                "tool": "check_availability",
                "params": {"timeframe": "this weekend"},
                "status": "success"
            }
            event2 = {
                "timestamp": "2025-12-03T14:00:00",  # Earlier timestamp
                "sender": "bob",
                "receiver": "alice",
                "tool": "propose_event",
                "params": {"event_name": "dinner"},
                "status": "success"
            }
            
            mock_alice_session = Mock()
            mock_alice_session.state = {"app:a2a_events": [event1]}
            mock_bob_session = Mock()
            mock_bob_session.state = {"app:a2a_events": [event2]}
            
            mock_alice_runner.session_service.get_session = AsyncMock(return_value=mock_alice_session)
            mock_bob_runner.session_service.get_session = AsyncMock(return_value=mock_bob_session)
            
            result = await update_network_monitor()
            
            # Verify events are sorted chronologically (oldest first)
            events = result["events"]
            assert len(events) == 2
            assert events[0]["timestamp_iso"] == "2025-12-03T14:00:00"  # Earlier event first
            assert events[1]["timestamp_iso"] == "2025-12-03T15:00:00"  # Later event second
    
    @pytest.mark.asyncio
    async def test_update_network_monitor_event_formatting(self):
        """Test AC1, AC3: Events formatted with all required fields."""
        with patch('app.alice_runner') as mock_alice_runner, \
             patch('app.bob_runner') as mock_bob_runner:
            
            event = {
                "timestamp": "2025-12-03T15:00:00",
                "sender": "alice",
                "receiver": "bob",
                "tool": "check_availability",
                "params": {"timeframe": "this weekend", "event_type": "dinner"},
                "status": "success"
            }
            
            mock_alice_session = Mock()
            mock_alice_session.state = {"app:a2a_events": [event]}
            mock_bob_session = Mock()
            mock_bob_session.state = {}
            
            mock_alice_runner.session_service.get_session = AsyncMock(return_value=mock_alice_session)
            mock_bob_runner.session_service.get_session = AsyncMock(return_value=mock_bob_session)
            
            result = await update_network_monitor()
            
            formatted_event = result["events"][0]
            
            # Verify all required fields are present
            assert "timestamp" in formatted_event
            assert "sender" in formatted_event
            assert "receiver" in formatted_event
            assert "tool" in formatted_event
            assert "params" in formatted_event
            assert "status_info" in formatted_event
            
            # Verify formatted values
            assert formatted_event["sender"] == "Alice's Companion"
            assert formatted_event["receiver"] == "Bob's Companion"
            assert formatted_event["tool"] == "check_availability"
            assert formatted_event["params"] == {"timeframe": "this weekend", "event_type": "dinner"}
            assert formatted_event["status_info"]["status"] == "success"
            assert formatted_event["status_info"]["icon"] == "✅"
    
    @pytest.mark.asyncio
    async def test_update_network_monitor_status_display(self):
        """Test AC7: Status displayed clearly with visual distinction."""
        with patch('app.alice_runner') as mock_alice_runner, \
             patch('app.bob_runner') as mock_bob_runner:
            
            success_event = {
                "timestamp": "2025-12-03T15:00:00",
                "sender": "alice",
                "receiver": "bob",
                "tool": "check_availability",
                "params": {},
                "status": "success"
            }
            
            failed_event = {
                "timestamp": "2025-12-03T15:01:00",
                "sender": "alice",
                "receiver": "bob",
                "tool": "check_availability",
                "params": {},
                "status": "failed"
            }
            
            mock_alice_session = Mock()
            mock_alice_session.state = {"app:a2a_events": [success_event, failed_event]}
            mock_bob_session = Mock()
            mock_bob_session.state = {}
            
            mock_alice_runner.session_service.get_session = AsyncMock(return_value=mock_alice_session)
            mock_bob_runner.session_service.get_session = AsyncMock(return_value=mock_bob_session)
            
            result = await update_network_monitor()
            
            events = result["events"]
            assert len(events) == 2
            
            # Verify success event
            assert events[0]["status_info"]["status"] == "success"
            assert events[0]["status_info"]["icon"] == "✅"
            assert events[0]["status_info"]["color"] == "green"
            
            # Verify failed event
            assert events[1]["status_info"]["status"] == "failed"
            assert events[1]["status_info"]["icon"] == "❌"
            assert events[1]["status_info"]["color"] == "red"
    
    @pytest.mark.asyncio
    async def test_update_network_monitor_malformed_events(self):
        """Test AC7: Malformed events handled gracefully."""
        with patch('app.alice_runner') as mock_alice_runner, \
             patch('app.bob_runner') as mock_bob_runner:
            
            valid_event = {
                "timestamp": "2025-12-03T15:00:00",
                "sender": "alice",
                "receiver": "bob",
                "tool": "check_availability",
                "params": {},
                "status": "success"
            }
            
            # Malformed events (missing required fields, wrong types)
            malformed_event1 = "not a dict"
            malformed_event2 = {"timestamp": "", "tool": ""}  # Missing required fields
            
            mock_alice_session = Mock()
            mock_alice_session.state = {"app:a2a_events": [valid_event, malformed_event1, malformed_event2]}
            mock_bob_session = Mock()
            mock_bob_session.state = {}
            
            mock_alice_runner.session_service.get_session = AsyncMock(return_value=mock_alice_session)
            mock_bob_runner.session_service.get_session = AsyncMock(return_value=mock_bob_session)
            
            result = await update_network_monitor()
            
            # Should only include valid event
            assert len(result["events"]) == 1
            assert result["events"][0]["tool"] == "check_availability"
    
    @pytest.mark.asyncio
    async def test_update_network_monitor_long_event_list(self):
        """Test AC2: Very long event lists handled (limited to most recent 100)."""
        with patch('app.alice_runner') as mock_alice_runner, \
             patch('app.bob_runner') as mock_bob_runner:
            
            # Create 150 events
            events = []
            for i in range(150):
                event = {
                    "timestamp": f"2025-12-03T{10 + i//60:02d}:{i%60:02d}:00",
                    "sender": "alice",
                    "receiver": "bob",
                    "tool": "check_availability",
                    "params": {},
                    "status": "success"
                }
                events.append(event)
            
            mock_alice_session = Mock()
            mock_alice_session.state = {"app:a2a_events": events}
            mock_bob_session = Mock()
            mock_bob_session.state = {}
            
            mock_alice_runner.session_service.get_session = AsyncMock(return_value=mock_alice_session)
            mock_bob_runner.session_service.get_session = AsyncMock(return_value=mock_bob_session)
            
            result = await update_network_monitor()
            
            # Should limit to 100 most recent events
            assert len(result["events"]) == 100
            assert result["total_count"] == 150
            assert "Showing 100 of 150 events" in result["message"]
    
    @pytest.mark.asyncio
    async def test_update_network_monitor_activity_indicator(self):
        """Test AC4: Visual activity indicator shows when communication is active."""
        with patch('app.alice_runner') as mock_alice_runner, \
             patch('app.bob_runner') as mock_bob_runner, \
             patch('app.datetime') as mock_datetime:
            
            # Mock current time
            now = datetime(2025, 12, 3, 15, 0, 0)
            mock_datetime.now.return_value = now
            mock_datetime.fromisoformat = datetime.fromisoformat
            
            # Recent event (within last 2 seconds)
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
            
            result = await update_network_monitor()
            
            # Should show active status
            assert result["activity_status"] == "🟢 Active"
            assert result["recent_activity"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


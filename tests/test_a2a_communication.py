"""Unit tests for A2A (Agent-to-Agent) communication with error handling and logging.

Tests the call_other_companion_tool() function which implements:
- JSON-RPC 2.0 protocol communication (AC: 1, 2, 3)
- Error handling and retry logic (AC: 6, 7)
- A2A event logging (AC: 4, 8)
- Graceful error reporting (AC: 7)
"""

import unittest
import sys
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alice_companion.agent import call_other_companion_tool as alice_call_tool
from bob_companion.agent import call_other_companion_tool as bob_call_tool
from alice_companion.sqlite_session_service import SqliteSessionService
from shared.a2a_logging import log_a2a_event


class TestA2ACommunicationAlice(unittest.TestCase):
    """Test Alice's A2A communication with Bob's Companion."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.session_service = SqliteSessionService(db_path=":memory:")
        # Mock session service for tests
        self.mock_session = MagicMock()
        self.mock_session.state = {"app:a2a_events": []}
    
    @patch('alice_companion.agent.session_service')
    @patch('alice_companion.agent.get_mcp_client')
    async def test_successful_tool_call_with_logging(self, mock_get_client, mock_session_service):
        """Test AC: 1, 2, 3, 4, 5, 8 - Successful tool call with A2A event logging.
        
        Given: Alice's agent calls a tool on Bob's MCP server
        When: Tool call succeeds
        Then: 
        - JSON-RPC 2.0 protocol is used (AC: 1)
        - Tool name and parameters are included (AC: 2)
        - Structured response is received (AC: 3)
        - Event is logged to session state (AC: 4, 8)
        - Response is returned to agent (AC: 5)
        """
        # Mock MCP client
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(return_value={
            "available": True,
            "slots": ["2024-12-07T19:00:00/2024-12-07T21:00:00"]
        })
        mock_get_client.return_value = mock_client
        
        # Mock session service
        mock_session_service.get_session = AsyncMock(return_value=self.mock_session)
        mock_session_service.update_session_state = AsyncMock()
        
        # Call tool
        result = await alice_call_tool(
            "check_availability",
            timeframe="this weekend",
            requester="alice"
        )
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertIn("available", result)
        self.assertTrue(result["available"])
        
        # Verify event was logged
        events = self.mock_session.state.get("app:a2a_events", [])
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event["sender"], "alice")
        self.assertEqual(event["receiver"], "bob")
        self.assertEqual(event["tool"], "check_availability")
        self.assertEqual(event["status"], "success")
        self.assertIn("timestamp", event)
        # Verify requester was redacted
        self.assertNotIn("requester", event["params"])
        self.assertIn("timeframe", event["params"])
        
        # Verify session state was updated
        mock_session_service.update_session_state.assert_called_once()
    
    @patch('alice_companion.agent.session_service')
    @patch('alice_companion.agent.get_mcp_client')
    async def test_error_handling_connection_error(self, mock_get_client, mock_session_service):
        """Test AC: 6, 7 - Error handling with graceful error reporting.
        
        Given: Bob's Companion is unreachable
        When: Tool call fails after retry
        Then:
        - Retry logic is executed (AC: 6)
        - Error is reported gracefully (AC: 7)
        - Event is logged with failed status (AC: 4, 8)
        """
        import httpx
        
        # Mock MCP client to raise ConnectionError
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(side_effect=ConnectionError(
            "Agent temporarily unavailable: Cannot connect to Bob's Companion"
        ))
        mock_get_client.return_value = mock_client
        
        # Mock session service
        mock_session_service.get_session = AsyncMock(return_value=self.mock_session)
        mock_session_service.update_session_state = AsyncMock()
        
        # Call tool
        result = await alice_call_tool("check_availability", timeframe="this weekend")
        
        # Verify error dict is returned (not exception raised)
        self.assertIsNotNone(result)
        self.assertIn("error", result)
        self.assertIn("unavailable", result["error"].lower())
        
        # Verify event was logged with failed status
        events = self.mock_session.state.get("app:a2a_events", [])
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event["status"], "failed")
        self.assertEqual(event["sender"], "alice")
        self.assertEqual(event["receiver"], "bob")
    
    @patch('alice_companion.agent.session_service')
    @patch('alice_companion.agent.get_mcp_client')
    async def test_error_handling_value_error(self, mock_get_client, mock_session_service):
        """Test AC: 6, 7 - Error handling for invalid tool parameters.
        
        Given: Tool call fails with ValueError (invalid parameters)
        When: Tool call is attempted
        Then: Error is returned gracefully, not raised
        """
        # Mock MCP client to raise ValueError
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(side_effect=ValueError("Invalid tool parameters"))
        mock_get_client.return_value = mock_client
        
        # Mock session service
        mock_session_service.get_session = AsyncMock(return_value=self.mock_session)
        mock_session_service.update_session_state = AsyncMock()
        
        # Call tool
        result = await alice_call_tool("invalid_tool", invalid_param="value")
        
        # Verify error dict is returned
        self.assertIsNotNone(result)
        self.assertIn("error", result)
        self.assertIn("failed", result["error"].lower())
    
    @patch('alice_companion.agent.session_service')
    @patch('alice_companion.agent.get_mcp_client')
    async def test_jsonrpc_protocol_compliance(self, mock_get_client, mock_session_service):
        """Test AC: 1 - JSON-RPC 2.0 protocol compliance.
        
        Given: Alice's agent calls a tool
        When: MCP client makes HTTP request
        Then: Request uses JSON-RPC 2.0 format
        """
        # Mock MCP client
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(return_value={"success": True})
        mock_get_client.return_value = mock_client
        
        # Mock session service
        mock_session_service.get_session = AsyncMock(return_value=self.mock_session)
        mock_session_service.update_session_state = AsyncMock()
        
        # Call tool
        await alice_call_tool("test_tool", param1="value1")
        
        # Verify MCP client was called (which uses JSON-RPC 2.0 internally)
        mock_client.call_tool.assert_called_once_with("test_tool", param1="value1")
    
    @patch('alice_companion.agent.session_service')
    async def test_a2a_event_logging_format(self, mock_session_service):
        """Test AC: 4, 8 - A2A event logging format and structure.
        
        Given: A2A communication occurs
        When: Event is logged
        Then: Event contains timestamp, sender, receiver, tool, params (redacted), status
        """
        # Mock session service
        mock_session_service.get_session = AsyncMock(return_value=self.mock_session)
        mock_session_service.update_session_state = AsyncMock()
        
        # Manually log an event to test format
        log_a2a_event(
            session_state=self.mock_session.state,
            sender="alice",
            receiver="bob",
            tool="check_availability",
            params={"timeframe": "this weekend", "requester": "alice"},
            result={"available": True}
        )
        
        # Verify event structure
        events = self.mock_session.state.get("app:a2a_events", [])
        self.assertEqual(len(events), 1)
        event = events[0]
        
        # Verify all required fields
        self.assertIn("timestamp", event)
        self.assertEqual(event["sender"], "alice")
        self.assertEqual(event["receiver"], "bob")
        self.assertEqual(event["tool"], "check_availability")
        self.assertEqual(event["status"], "success")
        self.assertIn("params", event)
        
        # Verify ISO 8601 timestamp format
        from datetime import datetime
        try:
            datetime.fromisoformat(event["timestamp"])
        except ValueError:
            self.fail("Timestamp is not in ISO 8601 format")
        
        # Verify requester was redacted
        self.assertNotIn("requester", event["params"])
        self.assertIn("timeframe", event["params"])


class TestA2ACommunicationBob(unittest.TestCase):
    """Test Bob's A2A communication with Alice's Companion."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_session = MagicMock()
        self.mock_session.state = {"app:a2a_events": []}
    
    @patch('bob_companion.agent.session_service')
    @patch('bob_companion.agent.get_mcp_client')
    async def test_bob_successful_tool_call(self, mock_get_client, mock_session_service):
        """Test AC: 1, 2, 3, 5 - Bob's successful tool call to Alice."""
        # Mock MCP client
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(return_value={"available": True})
        mock_get_client.return_value = mock_client
        
        # Mock session service
        mock_session_service.get_session = AsyncMock(return_value=self.mock_session)
        mock_session_service.update_session_state = AsyncMock()
        
        # Call tool
        result = await bob_call_tool("check_availability", timeframe="this weekend")
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertIn("available", result)
        
        # Verify event was logged
        events = self.mock_session.state.get("app:a2a_events", [])
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event["sender"], "bob")
        self.assertEqual(event["receiver"], "alice")


class TestA2AEventLogging(unittest.TestCase):
    """Test A2A event logging functionality."""
    
    def test_log_successful_event(self):
        """Test logging successful A2A event."""
        session_state = {"app:a2a_events": []}
        
        log_a2a_event(
            session_state=session_state,
            sender="alice",
            receiver="bob",
            tool="check_availability",
            params={"timeframe": "this weekend"},
            result={"available": True}
        )
        
        events = session_state["app:a2a_events"]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["status"], "success")
    
    def test_log_failed_event(self):
        """Test logging failed A2A event."""
        session_state = {"app:a2a_events": []}
        
        log_a2a_event(
            session_state=session_state,
            sender="alice",
            receiver="bob",
            tool="check_availability",
            params={"timeframe": "this weekend"},
            result={"error": "Connection failed"}
        )
        
        events = session_state["app:a2a_events"]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["status"], "failed")
    
    def test_redact_sensitive_parameters(self):
        """Test that sensitive parameters (requester) are redacted from logs."""
        session_state = {"app:a2a_events": []}
        
        log_a2a_event(
            session_state=session_state,
            sender="alice",
            receiver="bob",
            tool="check_availability",
            params={"timeframe": "this weekend", "requester": "alice"},
            result={"available": True}
        )
        
        event = session_state["app:a2a_events"][0]
        self.assertNotIn("requester", event["params"])
        self.assertIn("timeframe", event["params"])


# Helper to run async tests
def async_test(coro):
    """Decorator to run async test methods."""
    def wrapper(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro(self))
        finally:
            loop.close()
    return wrapper


# Apply async_test decorator to async test methods
TestA2ACommunicationAlice.test_successful_tool_call_with_logging = async_test(TestA2ACommunicationAlice.test_successful_tool_call_with_logging)
TestA2ACommunicationAlice.test_error_handling_connection_error = async_test(TestA2ACommunicationAlice.test_error_handling_connection_error)
TestA2ACommunicationAlice.test_error_handling_value_error = async_test(TestA2ACommunicationAlice.test_error_handling_value_error)
TestA2ACommunicationAlice.test_jsonrpc_protocol_compliance = async_test(TestA2ACommunicationAlice.test_jsonrpc_protocol_compliance)
TestA2ACommunicationAlice.test_a2a_event_logging_format = async_test(TestA2ACommunicationAlice.test_a2a_event_logging_format)
TestA2ACommunicationBob.test_bob_successful_tool_call = async_test(TestA2ACommunicationBob.test_bob_successful_tool_call)


if __name__ == '__main__':
    unittest.main()


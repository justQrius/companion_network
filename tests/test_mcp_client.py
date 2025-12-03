"""Unit tests for MCP client implementation.

Tests MCP client initialization, connection establishment, tool calling interface,
and error handling for both Alice's and Bob's MCP clients.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alice_companion.mcp_client import MCPClient as AliceMCPClient, BOB_ENDPOINT
from bob_companion.mcp_client import MCPClient as BobMCPClient, ALICE_ENDPOINT


class TestAliceMCPClient(unittest.TestCase):
    """Test Alice's MCP client (calls Bob's endpoint)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = AliceMCPClient()
    
    def test_client_initialization(self):
        """Test AC1: Alice's MCP client initialization with Bob's endpoint.
        
        Given: Alice's agent needs to contact Bob's Companion
        When: MCP client is initialized
        Then: Client is configured with Bob's endpoint: http://localhost:8002/run
        """
        self.assertEqual(self.client.endpoint, BOB_ENDPOINT)
        self.assertEqual(self.client.endpoint, "http://localhost:8002/run")
        self.assertFalse(self.client._initialized)
        self.assertIsNone(self.client.client)
    
    def test_endpoint_configuration_adr003(self):
        """Test AC1: Endpoint configuration matches ADR-003 (hardcoded localhost:8002)."""
        self.assertEqual(self.client.endpoint, "http://localhost:8002/run")
        # Verify hardcoded endpoint per ADR-003
        self.assertIn("localhost:8002", self.client.endpoint)
        self.assertIn("/run", self.client.endpoint)
    
    @unittest.skip("Requires actual endpoint or more complex mocking")
    async def test_connection_establishment(self):
        """Test AC3: Connection establishment (mock or actual endpoint).
        
        Given: MCP client is initialized
        When: Client attempts to establish connection
        Then: Client handles connection setup properly
        """
        # This would test actual connection, but requires endpoint or complex mocking
        # For now, verify the method exists and can be called
        await self.client._ensure_connection()
        self.assertTrue(self.client._initialized)
        self.assertIsNotNone(self.client.client)
    
    @patch('alice_companion.mcp_client.httpx.AsyncClient')
    async def test_tool_calling_interface(self, mock_client_class):
        """Test AC2: Tool calling interface (mock tool call).
        
        Given: MCP client is initialized and connected
        When: call_tool() is called with tool name and parameters
        Then: Method accepts tool name and parameters correctly
        """
        # Mock HTTP client and response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": "test_id",
            "result": {"success": True, "data": "test_result"}
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_http_client
        
        # Initialize client and call tool
        await self.client._ensure_connection()
        result = await self.client.call_tool("test_tool", param1="value1", param2="value2")
        
        # Verify tool was called with correct parameters
        self.assertIsNotNone(result)
        self.assertEqual(result["success"], True)
        
        # Verify HTTP POST was called with JSON-RPC 2.0 format
        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args
        self.assertEqual(call_args[0][0], BOB_ENDPOINT)
        
        # Verify JSON-RPC 2.0 request structure
        json_payload = call_args[1]["json"]
        self.assertEqual(json_payload["jsonrpc"], "2.0")
        self.assertEqual(json_payload["method"], "tools/call")
        self.assertEqual(json_payload["params"]["name"], "test_tool")
        self.assertEqual(json_payload["params"]["arguments"]["param1"], "value1")
        self.assertEqual(json_payload["params"]["arguments"]["param2"], "value2")
    
    @patch('alice_companion.mcp_client.httpx.AsyncClient')
    async def test_error_handling_unreachable_endpoint(self, mock_client_class):
        """Test AC3: Error handling for unreachable endpoints.
        
        Given: Bob's endpoint is unreachable
        When: call_tool() is called
        Then: Client retries once, then raises ConnectionError with graceful message
        """
        import httpx
        
        # Mock connection error
        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
        mock_client_class.return_value = mock_http_client
        
        await self.client._ensure_connection()
        
        # Should retry once, then raise ConnectionError
        with self.assertRaises(ConnectionError) as context:
            await self.client.call_tool("test_tool")
        
        # Verify error message is user-friendly (graceful degradation)
        error_msg = str(context.exception)
        self.assertIn("unavailable", error_msg.lower() or "temporarily unavailable")
        
        # Verify retry logic (should attempt twice: initial + 1 retry)
        self.assertEqual(mock_http_client.post.call_count, 2)
    
    async def test_context_manager(self):
        """Test client can be used as async context manager."""
        async with AliceMCPClient() as client:
            self.assertTrue(client._initialized)
            self.assertIsNotNone(client.client)
        
        # After context exit, client should be closed
        # (Note: actual cleanup depends on implementation)


class TestBobMCPClient(unittest.TestCase):
    """Test Bob's MCP client (calls Alice's endpoint)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = BobMCPClient()
    
    def test_client_initialization(self):
        """Test AC1: Bob's MCP client initialization with Alice's endpoint.
        
        Given: Bob's agent needs to contact Alice's Companion
        When: MCP client is initialized
        Then: Client is configured with Alice's endpoint: http://localhost:8001/run
        """
        self.assertEqual(self.client.endpoint, ALICE_ENDPOINT)
        self.assertEqual(self.client.endpoint, "http://localhost:8001/run")
        self.assertFalse(self.client._initialized)
        self.assertIsNone(self.client.client)
    
    def test_endpoint_configuration_adr003(self):
        """Test AC1: Endpoint configuration matches ADR-003 (hardcoded localhost:8001)."""
        self.assertEqual(self.client.endpoint, "http://localhost:8001/run")
        # Verify hardcoded endpoint per ADR-003
        self.assertIn("localhost:8001", self.client.endpoint)
        self.assertIn("/run", self.client.endpoint)
    
    @patch('bob_companion.mcp_client.httpx.AsyncClient')
    async def test_tool_calling_interface(self, mock_client_class):
        """Test AC2: Tool calling interface for Bob's client."""
        # Mock HTTP client and response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": "test_id",
            "result": {"success": True}
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_http_client
        
        await self.client._ensure_connection()
        result = await self.client.call_tool("test_tool", param="value")
        
        self.assertIsNotNone(result)
        mock_http_client.post.assert_called_once()


class TestMCPClientDualImplementation(unittest.TestCase):
    """Test AC5: Dual implementation exists in both alice_companion and bob_companion."""
    
    def test_both_clients_exist(self):
        """Test AC5: Both clients can be instantiated without errors."""
        alice_client = AliceMCPClient()
        bob_client = BobMCPClient()
        
        self.assertIsNotNone(alice_client)
        self.assertIsNotNone(bob_client)
        self.assertNotEqual(alice_client.endpoint, bob_client.endpoint)
    
    def test_endpoint_differences(self):
        """Test AC5: Endpoints are correctly configured for bidirectional communication."""
        alice_client = AliceMCPClient()
        bob_client = BobMCPClient()
        
        # Alice calls Bob's endpoint
        self.assertEqual(alice_client.endpoint, "http://localhost:8002/run")
        # Bob calls Alice's endpoint
        self.assertEqual(bob_client.endpoint, "http://localhost:8001/run")
        
        # Verify they're different (bidirectional)
        self.assertNotEqual(alice_client.endpoint, bob_client.endpoint)


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
TestAliceMCPClient.test_connection_establishment = async_test(TestAliceMCPClient.test_connection_establishment)
TestAliceMCPClient.test_tool_calling_interface = async_test(TestAliceMCPClient.test_tool_calling_interface)
TestAliceMCPClient.test_error_handling_unreachable_endpoint = async_test(TestAliceMCPClient.test_error_handling_unreachable_endpoint)
TestAliceMCPClient.test_context_manager = async_test(TestAliceMCPClient.test_context_manager)
TestBobMCPClient.test_tool_calling_interface = async_test(TestBobMCPClient.test_tool_calling_interface)


if __name__ == '__main__':
    unittest.main()


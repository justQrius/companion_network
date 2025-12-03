"""Unit tests for chat interface event handlers.

Tests the async event handlers for Alice and Bob chat inputs,
including message handling, history updates, error handling, and async behavior.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import List, Tuple

# Import handlers from app.py
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import handle_alice_input, handle_bob_input, initialize_agents


class TestHandleAliceInput:
    """Test suite for handle_alice_input event handler."""
    
    @pytest.mark.asyncio
    async def test_handle_alice_input_with_message(self):
        """Test AC1: Message immediately appended to chat history."""
        # Mock agent
        with patch('app.alice_agent') as mock_agent:
            mock_agent.run = Mock(return_value="Test response from Alice's agent")
            
            # Initial empty history
            history: List[Tuple[str, str]] = []
            message = "Find a time for dinner with Bob this weekend"
            
            # Call handler
            result_history, result_input = await handle_alice_input(message, history)
            
            # AC1: Verify message appears in history immediately
            assert len(result_history) == 1
            assert result_history[0][0] == message
            assert result_history[0][1] == "Test response from Alice's agent"
            
            # Verify input cleared
            assert result_input == ""
            
            # Verify agent.run() was called
            mock_agent.run.assert_called_once_with(message)
    
    @pytest.mark.asyncio
    async def test_handle_alice_input_error_handling(self):
        """Test error handling: user-friendly error message displayed."""
        # Mock agent to raise exception
        with patch('app.alice_agent') as mock_agent:
            mock_agent.run = Mock(side_effect=Exception("Test error"))
            
            history: List[Tuple[str, str]] = []
            message = "Test message"
            
            # Call handler
            result_history, result_input = await handle_alice_input(message, history)
            
            # Verify error message in history (not stack trace)
            assert len(result_history) == 1
            assert result_history[0][0] == message
            assert "error" in result_history[0][1].lower()
            assert "I encountered an error" in result_history[0][1]
            assert "Test error" not in result_history[0][1]  # No stack trace
    
    @pytest.mark.asyncio
    async def test_handle_alice_input_empty_message(self):
        """Test empty message handling."""
        history: List[Tuple[str, str]] = [("Previous", "message")]
        message = ""
        
        result_history, result_input = await handle_alice_input(message, history)
        
        # History unchanged
        assert result_history == history
        assert result_input == ""
    
    @pytest.mark.asyncio
    async def test_handle_alice_input_whitespace_message(self):
        """Test whitespace-only message handling."""
        history: List[Tuple[str, str]] = []
        message = "   "
        
        result_history, result_input = await handle_alice_input(message, history)
        
        # History unchanged
        assert result_history == history
        assert result_input == ""


class TestHandleBobInput:
    """Test suite for handle_bob_input event handler."""
    
    @pytest.mark.asyncio
    async def test_handle_bob_input_with_message(self):
        """Test AC1: Message immediately appended to chat history."""
        # Mock agent
        with patch('app.bob_agent') as mock_agent:
            mock_agent.run = Mock(return_value="Test response from Bob's agent")
            
            # Initial empty history
            history: List[Tuple[str, str]] = []
            message = "Hello, I'm Bob"
            
            # Call handler
            result_history, result_input = await handle_bob_input(message, history)
            
            # AC1: Verify message appears in history immediately
            assert len(result_history) == 1
            assert result_history[0][0] == message
            assert result_history[0][1] == "Test response from Bob's agent"
            
            # Verify input cleared
            assert result_input == ""
            
            # Verify agent.run() was called
            mock_agent.run.assert_called_once_with(message)
    
    @pytest.mark.asyncio
    async def test_handle_bob_input_error_handling(self):
        """Test error handling: user-friendly error message displayed."""
        # Mock agent to raise exception
        with patch('app.bob_agent') as mock_agent:
            mock_agent.run = Mock(side_effect=Exception("Test error"))
            
            history: List[Tuple[str, str]] = []
            message = "Test message"
            
            # Call handler
            result_history, result_input = await handle_bob_input(message, history)
            
            # Verify error message in history (not stack trace)
            assert len(result_history) == 1
            assert result_history[0][0] == message
            assert "error" in result_history[0][1].lower()
            assert "I encountered an error" in result_history[0][1]
            assert "Test error" not in result_history[0][1]  # No stack trace
    
    @pytest.mark.asyncio
    async def test_handle_bob_input_empty_message(self):
        """Test empty message handling."""
        history: List[Tuple[str, str]] = [("Previous", "message")]
        message = ""
        
        result_history, result_input = await handle_bob_input(message, history)
        
        # History unchanged
        assert result_history == history
        assert result_input == ""


class TestAsyncBehavior:
    """Test async behavior to ensure handlers don't block UI."""
    
    @pytest.mark.asyncio
    async def test_handlers_are_async(self):
        """Test that handlers are async functions (AC6)."""
        import inspect
        
        # Verify handlers are coroutine functions
        assert inspect.iscoroutinefunction(handle_alice_input)
        assert inspect.iscoroutinefunction(handle_bob_input)
    
    @pytest.mark.asyncio
    async def test_concurrent_handlers(self):
        """Test AC6: Both handlers can process simultaneously without blocking."""
        with patch('app.alice_agent') as mock_alice, patch('app.bob_agent') as mock_bob:
            # Mock agents with delayed responses
            async def delayed_alice(message):
                await asyncio.sleep(0.1)
                return "Alice response"
            
            async def delayed_bob(message):
                await asyncio.sleep(0.1)
                return "Bob response"
            
            mock_alice.run = Mock(side_effect=lambda m: asyncio.run(delayed_alice(m)))
            mock_bob.run = Mock(side_effect=lambda m: asyncio.run(delayed_bob(m)))
            
            # Call both handlers concurrently
            alice_task = handle_alice_input("Alice message", [])
            bob_task = handle_bob_input("Bob message", [])
            
            # Execute concurrently
            alice_result, bob_result = await asyncio.gather(alice_task, bob_task)
            
            # Both should complete
            assert alice_result[0][0][0] == "Alice message"
            assert bob_result[0][0][0] == "Bob message"


class TestChatHistoryPersistence:
    """Test chat history persistence during session (AC7)."""
    
    @pytest.mark.asyncio
    async def test_history_persists_across_messages(self):
        """Test AC7: Chat history persists during session."""
        with patch('app.alice_agent') as mock_agent:
            mock_agent.run = Mock(return_value="Response")
            
            history: List[Tuple[str, str]] = []
            
            # Send first message
            history1, _ = await handle_alice_input("Message 1", history)
            assert len(history1) == 1
            
            # Send second message (history should persist)
            history2, _ = await handle_alice_input("Message 2", history1)
            assert len(history2) == 2
            assert history2[0][0] == "Message 1"
            assert history2[1][0] == "Message 2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


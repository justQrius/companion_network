"""Unit tests for Alice's Companion Agent.

Tests agent initialization, message processing, and session persistence.
"""

import unittest
import asyncio
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alice_companion.agent import (
    agent, runner, session_service, memory_service,
    AGENT_NAME, MODEL, SESSION_ID, DATABASE_PATH, run
)
from google.adk.memory import InMemoryMemoryService
from alice_companion.sqlite_session_service import SqliteSessionService


class TestAliceAgentInitialization(unittest.TestCase):
    """Test agent initialization with all required components."""
    
    def test_agent_name(self):
        """Test agent has correct name identifier."""
        self.assertEqual(agent.name, "alices_companion")
        self.assertIn("Alice's Companion", agent.description or "")
    
    def test_agent_model(self):
        """Test agent uses Gemini 2.5 Pro model."""
        self.assertEqual(agent.model, "gemini-2.5-pro")
    
    def test_agent_instruction(self):
        """Test agent has system instruction."""
        self.assertIsNotNone(agent.instruction)
        self.assertIn("Alice's personal Companion", agent.instruction)
        self.assertIn("coordinate plans", agent.instruction.lower())
    
    def test_session_service_type(self):
        """Test session service is SQLite-based."""
        self.assertIsInstance(session_service, SqliteSessionService)
        self.assertEqual(session_service.db_path, DATABASE_PATH)
    
    def test_memory_service_type(self):
        """Test memory service is InMemoryMemoryService."""
        self.assertIsInstance(memory_service, InMemoryMemoryService)
    
    def test_session_id_constant(self):
        """Test session ID constant is set correctly."""
        self.assertEqual(SESSION_ID, "alice_session")


class TestAliceAgentRun(unittest.TestCase):
    """Test agent.run() functionality."""
    
    def test_run_function_exists(self):
        """Test run() function is available and callable."""
        self.assertTrue(callable(run))
    
    def test_run_function_signature(self):
        """Test run() function accepts message parameter."""
        import inspect
        sig = inspect.signature(run)
        params = list(sig.parameters.keys())
        self.assertIn('message', params)


class TestSessionPersistence(unittest.TestCase):
    """Test session persistence across restarts."""
    
    def setUp(self):
        """Set up test session."""
        self.app_name = "companion_network"
        self.user_id = "alice"
        self.session_id = SESSION_ID
    
    async def _create_test_session(self):
        """Helper to create a test session."""
        return await session_service.create_session(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=self.session_id,
            state={"test": "value", "number": 42}
        )
    
    async def _get_test_session(self):
        """Helper to retrieve test session."""
        return await session_service.get_session(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=self.session_id
        )
    
    def test_session_creation(self):
        """Test session can be created."""
        async def test():
            session = await self._create_test_session()
            self.assertIsNotNone(session)
            self.assertEqual(session.id, self.session_id)
            self.assertEqual(session.state.get("test"), "value")
        
        asyncio.run(test())
    
    def test_session_retrieval(self):
        """Test session can be retrieved after creation."""
        async def test():
            # Create session
            await self._create_test_session()
            
            # Retrieve session
            retrieved = await self._get_test_session()
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.state.get("test"), "value")
            self.assertEqual(retrieved.state.get("number"), 42)
        
        asyncio.run(test())
    
    def test_session_persistence_across_restart(self):
        """Test session persists after creating new service instance (simulates restart)."""
        async def test():
            # Create session with original service
            await self._create_test_session()
            
            # Simulate restart: create new service instance
            new_service = SqliteSessionService(db_path=str(DATABASE_PATH))
            restarted_session = await new_service.get_session(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=self.session_id
            )
            
            # Verify session persisted
            self.assertIsNotNone(restarted_session)
            self.assertEqual(restarted_session.state.get("test"), "value")
            self.assertEqual(restarted_session.state.get("number"), 42)
        
        asyncio.run(test())
    
    def test_session_state_update(self):
        """Test session state can be updated."""
        async def test():
            # Create session
            await self._create_test_session()
            
            # Update state
            await session_service.update_session_state(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=self.session_id,
                state={"test": "updated", "new_key": "new_value"}
            )
            
            # Verify update
            retrieved = await self._get_test_session()
            self.assertEqual(retrieved.state.get("test"), "updated")
            self.assertEqual(retrieved.state.get("new_key"), "new_value")
        
        asyncio.run(test())


if __name__ == '__main__':
    unittest.main()


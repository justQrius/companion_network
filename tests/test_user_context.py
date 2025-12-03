"""Unit tests for user context loading (Story 2.4).

Tests UserContext creation, context loading into session state,
context retrieval, and persistence across restarts.
"""

import unittest
import asyncio
from pathlib import Path
import tempfile
import os

# Add project root to path
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.models import UserContext
from alice_companion.user_context import get_alice_context
from bob_companion.user_context import get_bob_context
from alice_companion.sqlite_session_service import SqliteSessionService


class TestUserContextCreation(unittest.TestCase):
    """Test UserContext creation with demo data."""
    
    def test_alice_context_creation(self):
        """Test Alice's context creation matches AC requirements."""
        context = get_alice_context()
        
        self.assertIsInstance(context, UserContext)
        self.assertEqual(context.user_id, "alice")
        self.assertEqual(context.name, "Alice")
        self.assertEqual(context.preferences["cuisine"], ["Italian", "Thai", "Sushi"])
        self.assertEqual(context.preferences["dining_times"], ["19:00", "19:30", "20:00"])
        self.assertIn("busy_slots", context.schedule)
        self.assertEqual(context.trusted_contacts, ["bob"])
        self.assertEqual(context.sharing_rules["bob"], ["availability", "cuisine_preferences"])
    
    def test_bob_context_creation(self):
        """Test Bob's context creation matches AC requirements."""
        context = get_bob_context()
        
        self.assertIsInstance(context, UserContext)
        self.assertEqual(context.user_id, "bob")
        self.assertEqual(context.name, "Bob")
        self.assertEqual(context.preferences["cuisine"], ["Italian", "Mexican"])
        self.assertEqual(context.preferences["dining_times"], ["18:30", "19:00"])
        self.assertIn("busy_slots", context.schedule)
        self.assertEqual(context.trusted_contacts, ["alice"])
        self.assertEqual(context.sharing_rules["alice"], ["availability", "cuisine_preferences"])


class TestContextLoading(unittest.TestCase):
    """Test context loading into session state."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.session_service = SqliteSessionService(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_alice_context_loading(self):
        """Test loading Alice's context into session state."""
        async def _test():
            from dataclasses import asdict
            
            alice_context = get_alice_context()
            context_dict = asdict(alice_context)
            
            # Create session with context
            session = await self.session_service.create_session(
                app_name="companion_network",
                user_id="alice",
                session_id="alice_session",
                state={"user_context": context_dict}
            )
            
            self.assertIsNotNone(session)
            self.assertIn("user_context", session.state)
            self.assertEqual(session.state["user_context"]["user_id"], "alice")
        
        asyncio.run(_test())
    
    def test_bob_context_loading(self):
        """Test loading Bob's context into session state."""
        async def _test():
            from dataclasses import asdict
            
            bob_context = get_bob_context()
            context_dict = asdict(bob_context)
            
            # Create session with context
            session = await self.session_service.create_session(
                app_name="companion_network",
                user_id="bob",
                session_id="bob_session",
                state={"user_context": context_dict}
            )
            
            self.assertIsNotNone(session)
            self.assertIn("user_context", session.state)
            self.assertEqual(session.state["user_context"]["user_id"], "bob")
        
        asyncio.run(_test())


class TestContextRetrieval(unittest.TestCase):
    """Test context retrieval from session state."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.session_service = SqliteSessionService(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_alice_context_retrieval(self):
        """Test retrieving Alice's context from session state."""
        async def _test():
            from dataclasses import asdict
            
            alice_context = get_alice_context()
            context_dict = asdict(alice_context)
            
            # Create session with context
            await self.session_service.create_session(
                app_name="companion_network",
                user_id="alice",
                session_id="alice_session",
                state={"user_context": context_dict}
            )
            
            # Retrieve session
            session = await self.session_service.get_session(
                app_name="companion_network",
                user_id="alice",
                session_id="alice_session"
            )
            
            self.assertIsNotNone(session)
            self.assertIn("user_context", session.state)
            retrieved_context = session.state["user_context"]
            self.assertEqual(retrieved_context["user_id"], "alice")
            self.assertEqual(retrieved_context["name"], "Alice")
        
        asyncio.run(_test())
    
    def test_bob_context_retrieval(self):
        """Test retrieving Bob's context from session state."""
        async def _test():
            from dataclasses import asdict
            
            bob_context = get_bob_context()
            context_dict = asdict(bob_context)
            
            # Create session with context
            await self.session_service.create_session(
                app_name="companion_network",
                user_id="bob",
                session_id="bob_session",
                state={"user_context": context_dict}
            )
            
            # Retrieve session
            session = await self.session_service.get_session(
                app_name="companion_network",
                user_id="bob",
                session_id="bob_session"
            )
            
            self.assertIsNotNone(session)
            self.assertIn("user_context", session.state)
            retrieved_context = session.state["user_context"]
            self.assertEqual(retrieved_context["user_id"], "bob")
            self.assertEqual(retrieved_context["name"], "Bob")
        
        asyncio.run(_test())


class TestContextPersistence(unittest.TestCase):
    """Test context persistence across agent restarts."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_context_persistence_across_restarts(self):
        """Test context persists across agent restarts (new service instance)."""
        async def _test():
            from dataclasses import asdict
            
            # First service instance - create session with context
            service1 = SqliteSessionService(db_path=self.db_path)
            alice_context = get_alice_context()
            context_dict = asdict(alice_context)
            
            await service1.create_session(
                app_name="companion_network",
                user_id="alice",
                session_id="alice_session",
                state={"user_context": context_dict}
            )
            
            # Simulate restart - create new service instance
            service2 = SqliteSessionService(db_path=self.db_path)
            
            # Retrieve session from new instance
            session = await service2.get_session(
                app_name="companion_network",
                user_id="alice",
                session_id="alice_session"
            )
            
            self.assertIsNotNone(session)
            self.assertIn("user_context", session.state)
            self.assertEqual(session.state["user_context"]["user_id"], "alice")
        
        asyncio.run(_test())


if __name__ == "__main__":
    unittest.main()


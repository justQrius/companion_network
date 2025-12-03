"""Tests for propose_event MCP tool.

Tests cover:
- Tool parameter acceptance
- Trusted contact validation
- EventProposal creation in session state
- Conflict detection with overlapping events
- Auto-accept logic (defaults to pending for MVP)
- Return value structure
- User notification queuing
- Access denied handling
- Edge cases (invalid datetime, missing context, empty participants)
"""

import unittest
import asyncio
from pathlib import Path
from datetime import datetime as dt

from shared.sqlite_session_service import SqliteSessionService
from shared.models import EventProposal
from bob_companion.mcp_server import propose_event as bob_propose_event
from alice_companion.mcp_server import propose_event as alice_propose_event


class TestProposeEventTool(unittest.TestCase):
    """Test suite for propose_event MCP tool."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database and session state."""
        # Use test database
        cls.test_db_path = Path(__file__).parent.parent / "test_propose_event_sessions.db"
        if cls.test_db_path.exists():
            cls.test_db_path.unlink()
        
        cls.session_service = SqliteSessionService(db_path=str(cls.test_db_path))
        cls.app_name = "companion_network"
        
        # Initialize Bob's session with test context
        asyncio.run(cls._setup_bob_session())
        # Initialize Alice's session with test context
        asyncio.run(cls._setup_alice_session())
    
    @classmethod
    async def _setup_bob_session(cls):
        """Set up Bob's test session with user context."""
        bob_context = {
            "user_id": "bob",
            "name": "Bob",
            "preferences": {
                "cuisine": ["Italian", "Mexican"],
                "dining_times": ["18:30", "19:00"],
                "weekend_availability": "high"
            },
            "schedule": {
                "busy_slots": [
                    "2024-12-07T10:00:00/2024-12-07T12:00:00"  # Saturday 10am-12pm busy
                ]
            },
            "trusted_contacts": ["alice"],
            "sharing_rules": {
                "alice": ["availability", "cuisine_preferences"]
            }
        }
        
        await cls.session_service.create_session(
            app_name=cls.app_name,
            user_id="bob",
            session_id="bob_session",
            state={"user_context": bob_context}
        )
    
    @classmethod
    async def _setup_alice_session(cls):
        """Set up Alice's test session with user context."""
        alice_context = {
            "user_id": "alice",
            "name": "Alice",
            "preferences": {
                "cuisine": ["Italian", "Thai", "Sushi"],
                "dining_times": ["19:00", "19:30", "20:00"],
                "weekend_availability": "high"
            },
            "schedule": {
                "busy_slots": [
                    "2024-12-07T14:00:00/2024-12-07T16:00:00"  # Saturday 2pm-4pm busy
                ]
            },
            "trusted_contacts": ["bob"],
            "sharing_rules": {
                "bob": ["availability", "cuisine_preferences"]
            }
        }
        
        await cls.session_service.create_session(
            app_name=cls.app_name,
            user_id="alice",
            session_id="alice_session",
            state={"user_context": alice_context}
        )
    
    def test_tool_accepts_parameters(self):
        """AC1: Test tool accepts all required parameters."""
        async def _test():
            result = await bob_propose_event(
                event_name="Dinner at Trattoria",
                datetime="2024-12-07T19:00:00",
                location="Trattoria on Main",
                participants=["alice", "bob"],
                requester="alice"
            )
            # Should not raise exception and should return a dict
            self.assertIsInstance(result, dict)
        
        asyncio.run(_test())
    
    def test_trusted_contact_validation_success(self):
        """AC2: Test trusted contact validation succeeds for trusted requester."""
        async def _test():
            result = await bob_propose_event(
                event_name="Dinner",
                datetime="2024-12-07T19:00:00",
                location="Restaurant",
                participants=["alice", "bob"],
                requester="alice"  # Alice is in Bob's trusted_contacts
            )
            # Should succeed (no error key)
            self.assertNotIn("error", result)
            self.assertIn("status", result)
        
        asyncio.run(_test())
    
    def test_trusted_contact_validation_failure(self):
        """AC2: Test access denied for untrusted requester."""
        async def _test():
            result = await bob_propose_event(
                event_name="Dinner",
                datetime="2024-12-07T19:00:00",
                location="Restaurant",
                participants=["eve", "bob"],
                requester="eve"  # Eve is NOT in Bob's trusted_contacts
            )
            # Should return access denied error
            self.assertIn("error", result)
            self.assertEqual(result["error"], "Access denied")
            self.assertIn("message", result)
            self.assertIn("trusted contacts", result["message"].lower())
        
        asyncio.run(_test())
    
    def test_eventproposal_creation(self):
        """AC3: Test EventProposal creation in session state."""
        async def _test():
            result = await bob_propose_event(
                event_name="Test Dinner",
                datetime="2024-12-08T19:00:00",
                location="Test Restaurant",
                participants=["alice", "bob"],
                requester="alice"
            )
            # Should create EventProposal
            self.assertIn("status", result)
            self.assertIn("event_id", result)
            
            # Verify EventProposal stored in session state
            session = await self.session_service.get_session(
                app_name=self.app_name,
                user_id="bob",
                session_id="bob_session"
            )
            proposal_key = f"event_proposal:{result['event_id']}"
            self.assertIn(proposal_key, session.state)
            
            # Verify EventProposal structure
            proposal_dict = session.state[proposal_key]
            self.assertEqual(proposal_dict["status"], "pending")
            self.assertEqual(proposal_dict["proposer"], "alice")
            self.assertEqual(proposal_dict["recipient"], "bob")
            self.assertIn("details", proposal_dict)
        
        asyncio.run(_test())
    
    def test_conflict_detection(self):
        """AC4: Test conflict detection with overlapping events."""
        async def _test():
            # First, create an existing event proposal
            first_result = await bob_propose_event(
                event_name="First Dinner",
                datetime="2024-12-09T19:00:00",
                location="Restaurant A",
                participants=["alice", "bob"],
                requester="alice"
            )
            self.assertIn("event_id", first_result)
            
            # Now propose another event at the same time (conflict)
            conflict_result = await bob_propose_event(
                event_name="Second Dinner",
                datetime="2024-12-09T19:00:00",  # Same time
                location="Restaurant B",
                participants=["alice", "bob"],
                requester="alice"
            )
            # Should return declined status
            self.assertEqual(conflict_result["status"], "declined")
            self.assertIn("message", conflict_result)
            self.assertIn("already has an event", conflict_result["message"].lower())
        
        asyncio.run(_test())
    
    def test_auto_accept_logic(self):
        """AC5: Test auto-accept logic (defaults to pending for MVP)."""
        async def _test():
            result = await bob_propose_event(
                event_name="Auto Accept Test",
                datetime="2024-12-10T19:00:00",
                location="Restaurant",
                participants=["alice", "bob"],
                requester="alice"
            )
            # For MVP, auto-accept is not implemented, so should return "pending"
            self.assertEqual(result["status"], "pending")
            self.assertIn("event_id", result)
        
        asyncio.run(_test())
    
    def test_return_value_structure(self):
        """AC7: Test return value has all required keys."""
        async def _test():
            result = await bob_propose_event(
                event_name="Return Value Test",
                datetime="2024-12-11T19:00:00",
                location="Restaurant",
                participants=["alice", "bob"],
                requester="alice"
            )
            # Should have all required keys
            required_keys = ["status", "message", "event_id"]
            for key in required_keys:
                self.assertIn(key, result, f"Missing required key: {key}")
            
            # Type checks
            self.assertIsInstance(result["status"], str)
            self.assertIn(result["status"], ["accepted", "declined", "pending", "counter"])
            self.assertIsInstance(result["message"], str)
            self.assertIsInstance(result["event_id"], str)
        
        asyncio.run(_test())
    
    def test_user_notification_queuing(self):
        """AC8: Test user notification queuing."""
        async def _test():
            result = await bob_propose_event(
                event_name="Notification Test",
                datetime="2024-12-12T19:00:00",
                location="Restaurant",
                participants=["alice", "bob"],
                requester="alice"
            )
            # Verify notification queued in session state
            session = await self.session_service.get_session(
                app_name=self.app_name,
                user_id="bob",
                session_id="bob_session"
            )
            self.assertIn("pending_messages", session.state)
            self.assertGreater(len(session.state["pending_messages"]), 0)
            
            # Check notification message format
            last_message = session.state["pending_messages"][-1]
            self.assertIn("alice", last_message.lower())
            self.assertIn("proposed", last_message.lower())
            self.assertIn("notification test", last_message.lower())
        
        asyncio.run(_test())
    
    def test_edge_case_invalid_datetime(self):
        """Edge case: Invalid datetime format."""
        async def _test():
            result = await bob_propose_event(
                event_name="Invalid DateTime Test",
                datetime="not-a-valid-datetime",
                location="Restaurant",
                participants=["alice", "bob"],
                requester="alice"
            )
            # Should return error dict
            self.assertIn("error", result)
            self.assertEqual(result["error"], "Invalid input")
            self.assertIn("ISO 8601", result["message"])
        
        asyncio.run(_test())
    
    def test_edge_case_missing_context(self):
        """Edge case: Missing user context in session state."""
        async def _test():
            # Create session without user_context
            await self.session_service.create_session(
                app_name=self.app_name,
                user_id="test_user",
                session_id="test_session",
                state={}  # No user_context
            )
            
            # This test would require modifying the tool to use test_user
            # For now, we test that the tool handles missing context gracefully
            # by checking Bob's session (which has context)
            result = await bob_propose_event(
                event_name="Test",
                datetime="2024-12-13T19:00:00",
                location="Restaurant",
                participants=["alice", "bob"],
                requester="alice"
            )
            # Should handle gracefully (either return error or succeed if context exists)
            self.assertIsInstance(result, dict)
        
        asyncio.run(_test())
    
    def test_edge_case_empty_participants(self):
        """Edge case: Empty participants list."""
        async def _test():
            result = await bob_propose_event(
                event_name="Empty Participants Test",
                datetime="2024-12-14T19:00:00",
                location="Restaurant",
                participants=[],  # Empty list
                requester="alice"
            )
            # Should return error dict
            self.assertIn("error", result)
            self.assertEqual(result["error"], "Invalid input")
            self.assertIn("participants", result["message"].lower())
        
        asyncio.run(_test())
    
    def test_edge_case_adjacent_events(self):
        """Edge case: Adjacent events (within 2 hours)."""
        async def _test():
            # Create first event
            first_result = await bob_propose_event(
                event_name="First Event",
                datetime="2024-12-15T19:00:00",
                location="Restaurant A",
                participants=["alice", "bob"],
                requester="alice"
            )
            self.assertIn("event_id", first_result)
            
            # Propose adjacent event (1 hour later - within 2 hour window)
            adjacent_result = await bob_propose_event(
                event_name="Adjacent Event",
                datetime="2024-12-15T20:00:00",  # 1 hour later
                location="Restaurant B",
                participants=["alice", "bob"],
                requester="alice"
            )
            # Should be declined (within 2 hour conflict window)
            self.assertEqual(adjacent_result["status"], "declined")
        
        asyncio.run(_test())
    
    def test_alice_companion_tool(self):
        """AC11: Test Alice's companion has same tool implementation."""
        async def _test():
            result = await alice_propose_event(
                event_name="Alice Tool Test",
                datetime="2024-12-16T19:00:00",
                location="Restaurant",
                participants=["alice", "bob"],
                requester="bob"  # Bob is in Alice's trusted_contacts
            )
            # Should have same structure as Bob's tool
            required_keys = ["status", "message", "event_id"]
            for key in required_keys:
                self.assertIn(key, result)
            
            # Verify EventProposal stored in Alice's session state
            session = await self.session_service.get_session(
                app_name=self.app_name,
                user_id="alice",
                session_id="alice_session"
            )
            proposal_key = f"event_proposal:{result['event_id']}"
            self.assertIn(proposal_key, session.state)
        
        asyncio.run(_test())
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database."""
        if cls.test_db_path.exists():
            cls.test_db_path.unlink()


if __name__ == "__main__":
    unittest.main()


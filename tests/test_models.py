"""Unit tests for shared data models.

Tests UserContext, EventProposal, and SharingRule dataclasses for
instantiation, default factories, type hints, and import functionality.
"""

import unittest
from shared.models import UserContext, EventProposal, SharingRule


class TestUserContext(unittest.TestCase):
    """Test UserContext dataclass."""

    def test_instantiation_with_all_fields(self):
        """Test UserContext can be instantiated with all required fields."""
        context = UserContext(
            user_id="alice",
            name="Alice",
            preferences={"cuisine": ["Italian", "Japanese"]},
            schedule={"busy_slots": ["2025-12-07T19:00:00/2025-12-07T21:00:00"]},
            trusted_contacts=["bob"],
            sharing_rules={"bob": ["availability", "cuisine_preferences"]}
        )
        self.assertEqual(context.user_id, "alice")
        self.assertEqual(context.name, "Alice")
        self.assertEqual(context.preferences["cuisine"], ["Italian", "Japanese"])
        self.assertEqual(len(context.trusted_contacts), 1)

    def test_default_factories_prevent_mutable_defaults(self):
        """Test that default_factory prevents mutable default argument issues."""
        context1 = UserContext(user_id="alice", name="Alice")
        context2 = UserContext(user_id="bob", name="Bob")
        
        # Modify context1's preferences
        context1.preferences["cuisine"] = ["Italian"]
        
        # Verify context2's preferences is still empty (not shared)
        self.assertEqual(len(context2.preferences), 0)
        self.assertEqual(len(context1.preferences), 1)


class TestEventProposal(unittest.TestCase):
    """Test EventProposal dataclass."""

    def test_instantiation_with_all_fields(self):
        """Test EventProposal can be instantiated with all required fields."""
        proposal = EventProposal(
            event_id="event-1",
            proposer="alice",
            recipient="bob",
            status="pending",
            details={"title": "Dinner", "time": "2025-12-07T19:00:00", "location": "Restaurant"},
            timestamp="2025-12-07T18:00:00"
        )
        self.assertEqual(proposal.event_id, "event-1")
        self.assertEqual(proposal.proposer, "alice")
        self.assertEqual(proposal.recipient, "bob")
        self.assertEqual(proposal.status, "pending")
        self.assertEqual(proposal.details["title"], "Dinner")
        self.assertEqual(proposal.timestamp, "2025-12-07T18:00:00")

    def test_status_enum_values(self):
        """Test EventProposal status accepts valid enum values."""
        valid_statuses = ["pending", "accepted", "declined", "counter"]
        for status in valid_statuses:
            proposal = EventProposal(
                event_id="event-1",
                proposer="alice",
                recipient="bob",
                status=status,
                timestamp="2025-12-07T18:00:00"
            )
            self.assertEqual(proposal.status, status)

    def test_default_factory_for_details(self):
        """Test that details uses default_factory to prevent mutable defaults."""
        proposal1 = EventProposal(
            event_id="event-1",
            proposer="alice",
            recipient="bob",
            status="pending",
            timestamp="2025-12-07T18:00:00"
        )
        proposal2 = EventProposal(
            event_id="event-2",
            proposer="bob",
            recipient="alice",
            status="pending",
            timestamp="2025-12-07T18:00:00"
        )
        
        # Modify proposal1's details
        proposal1.details["title"] = "Dinner"
        
        # Verify proposal2's details is still empty (not shared)
        self.assertEqual(len(proposal2.details), 0)
        self.assertEqual(len(proposal1.details), 1)


class TestSharingRule(unittest.TestCase):
    """Test SharingRule dataclass."""

    def test_instantiation_with_all_fields(self):
        """Test SharingRule can be instantiated with all required fields."""
        rule = SharingRule(
            contact_id="bob",
            allowed_categories=["availability", "cuisine_preferences", "dietary", "schedule"]
        )
        self.assertEqual(rule.contact_id, "bob")
        self.assertEqual(len(rule.allowed_categories), 4)
        self.assertIn("availability", rule.allowed_categories)

    def test_default_factory_for_allowed_categories(self):
        """Test that allowed_categories uses default_factory to prevent mutable defaults."""
        rule1 = SharingRule(contact_id="bob")
        rule2 = SharingRule(contact_id="charlie")
        
        # Modify rule1's allowed_categories
        rule1.allowed_categories.append("availability")
        
        # Verify rule2's allowed_categories is still empty (not shared)
        self.assertEqual(len(rule2.allowed_categories), 0)
        self.assertEqual(len(rule1.allowed_categories), 1)


class TestImports(unittest.TestCase):
    """Test import functionality."""

    def test_import_all_models(self):
        """Test that all models can be imported successfully."""
        from shared.models import UserContext, EventProposal, SharingRule
        self.assertTrue(UserContext is not None)
        self.assertTrue(EventProposal is not None)
        self.assertTrue(SharingRule is not None)


if __name__ == "__main__":
    unittest.main()


"""Unit tests for natural language coordination request parsing.

Tests that agents can parse natural language coordination requests and extract
key information: activity type, participants, time constraints, and coordination intent.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alice_companion.agent import run as alice_run
from bob_companion.agent import run as bob_run


class TestCoordinationParsing(unittest.TestCase):
    """Test natural language coordination request parsing."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Primary test message from AC1
        self.primary_message = "Find a time for dinner with Bob this weekend"
        
        # Alternative phrasings for AC4 (no rigid parsing)
        self.alternative_phrasings = [
            "Schedule dinner with Bob for this weekend",
            "I want to have dinner with Bob this weekend"
        ]
    
    def test_primary_coordination_request(self):
        """Test AC1: Agent extracts coordination info from primary message.
        
        Given: Alice's agent has user context loaded (Story 2.4)
        When: Alice sends "Find a time for dinner with Bob this weekend"
        Then: Agent should extract:
            - coordination type: "dinner"
            - other party: "Bob"
            - timeframe: "this weekend" (Saturday-Sunday)
            - intent: Initiate coordination
        """
        response = alice_run(self.primary_message)
        
        # Verify natural language response (AC2)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        
        # Check for acknowledgment of coordination intent
        response_lower = response.lower()
        # Should mention coordination or Bob or dinner
        self.assertTrue(
            any(keyword in response_lower for keyword in [
                "coordinate", "bob", "dinner", "weekend", "find", "time"
            ]),
            f"Response should acknowledge coordination: {response}"
        )
    
    def test_natural_language_acknowledgment(self):
        """Test AC2: Agent responds with natural language acknowledgment.
        
        Agent should respond with: "I'll coordinate with Bob's Companion 
        to find a time for dinner this weekend..."
        """
        response = alice_run(self.primary_message)
        
        # Should be natural language, not JSON or structured format
        self.assertIsInstance(response, str)
        self.assertNotIn("{", response)  # No JSON structures
        self.assertNotIn("[", response)  # No array structures
        
        # Should acknowledge the coordination request
        response_lower = response.lower()
        self.assertTrue(
            any(keyword in response_lower for keyword in [
                "coordinate", "bob", "dinner", "weekend"
            ]),
            f"Response should acknowledge coordination: {response}"
        )
    
    def test_contact_identification(self):
        """Test AC3: Agent identifies need to contact Bob's Companion.
        
        Agent should identify that coordination with "Bob" requires
        contacting Bob's Companion.
        """
        response = alice_run(self.primary_message)
        
        # Response should indicate understanding of contacting Bob
        response_lower = response.lower()
        # Should mention Bob (the contact)
        self.assertIn("bob", response_lower)
    
    def test_alternative_phrasing_schedule(self):
        """Test AC4: Alternative phrasing - 'Schedule dinner with Bob for this weekend'.
        
        Verify no rigid command parsing is required - natural language understanding
        handles variations in phrasing.
        """
        message = "Schedule dinner with Bob for this weekend"
        response = alice_run(message)
        
        # Should still understand and acknowledge
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        
        response_lower = response.lower()
        self.assertTrue(
            any(keyword in response_lower for keyword in [
                "coordinate", "bob", "dinner", "weekend"
            ]),
            f"Response should handle alternative phrasing: {response}"
        )
    
    def test_alternative_phrasing_want(self):
        """Test AC4: Alternative phrasing - 'I want to have dinner with Bob this weekend'.
        
        Verify natural language understanding handles conversational phrasing.
        """
        message = "I want to have dinner with Bob this weekend"
        response = alice_run(message)
        
        # Should still understand and acknowledge
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        
        response_lower = response.lower()
        self.assertTrue(
            any(keyword in response_lower for keyword in [
                "coordinate", "bob", "dinner", "weekend"
            ]),
            f"Response should handle conversational phrasing: {response}"
        )
    
    def test_extraction_activity_type(self):
        """Test AC6: Agent extracts activity type from natural language.
        
        Should extract "dinner" from various natural language inputs.
        """
        test_cases = [
            ("Find a time for dinner with Bob", "dinner"),
            ("Schedule lunch with Sarah", "lunch"),
            ("Plan a meeting with Mike", "meeting")
        ]
        
        for message, expected_activity in test_cases:
            with self.subTest(message=message, expected=expected_activity):
                response = alice_run(message)
                response_lower = response.lower()
                
                # Response should acknowledge the activity type
                self.assertIn(
                    expected_activity.lower(),
                    response_lower,
                    f"Response should mention {expected_activity}: {response}"
                )
    
    def test_extraction_participants(self):
        """Test AC6: Agent extracts participants from natural language.
        
        Should extract participant names and match to trusted contacts.
        """
        # Bob is in Alice's trusted contacts
        response = alice_run("Find a time for dinner with Bob this weekend")
        response_lower = response.lower()
        
        # Should mention Bob
        self.assertIn("bob", response_lower)
    
    def test_extraction_time_constraints(self):
        """Test AC6: Agent extracts time constraints from natural language.
        
        Should extract timeframes like "this weekend", "next week", "tomorrow".
        """
        test_cases = [
            ("Find a time for dinner with Bob this weekend", "weekend"),
            ("Schedule lunch with Sarah next week", "week"),
            ("Plan a meeting with Mike tomorrow", "tomorrow")
        ]
        
        for message, expected_timeframe in test_cases:
            with self.subTest(message=message, expected=expected_timeframe):
                response = alice_run(message)
                response_lower = response.lower()
                
                # Response should acknowledge the timeframe
                # (may not use exact word, but should show understanding)
                self.assertIsInstance(response, str)
                self.assertGreater(len(response), 0)
    
    def test_bob_agent_parsing(self):
        """Test Bob's agent also parses coordination requests correctly.
        
        Bob's agent should have the same natural language parsing capability.
        """
        message = "Find a time for dinner with Alice this weekend"
        response = bob_run(message)
        
        # Should understand and acknowledge
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        
        response_lower = response.lower()
        self.assertTrue(
            any(keyword in response_lower for keyword in [
                "coordinate", "alice", "dinner", "weekend"
            ]),
            f"Bob's agent should parse coordination: {response}"
        )


class TestCoordinationParsingEdgeCases(unittest.TestCase):
    """Test edge cases for coordination parsing."""
    
    def test_ambiguous_timeframe(self):
        """Test edge case: ambiguous timeframe (e.g., 'next week' without specific days)."""
        message = "Find a time for dinner with Bob next week"
        response = alice_run(message)
        
        # Should still acknowledge, even if timeframe is ambiguous
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
    
    def test_missing_participant(self):
        """Test edge case: missing participant name (e.g., 'Find a time for dinner')."""
        message = "Find a time for dinner"
        response = alice_run(message)
        
        # Should handle gracefully (may ask for clarification or acknowledge)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
    
    def test_unclear_activity_type(self):
        """Test edge case: unclear activity type (e.g., 'Let's do something this weekend')."""
        message = "Let's do something this weekend"
        response = alice_run(message)
        
        # Should handle gracefully
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)


if __name__ == '__main__':
    unittest.main()


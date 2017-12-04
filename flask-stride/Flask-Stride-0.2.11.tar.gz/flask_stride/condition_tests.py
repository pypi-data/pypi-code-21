import unittest
from .condition import BuiltinConditionClause, CompositeConditionClause

class BuiltinConditionClauseTests(unittest.TestCase):
    def test_init_public(self):
        """Create a Builtin Condition Clause to denote a public conversation."""
        bcc = BuiltinConditionClause('conversation_is_public')

        bcc_descriptor = bcc.to_descriptor()
        expected = {'condition': 'conversation_is_public'}

        self.assertEqual(bcc_descriptor, expected)

    def test_init_public(self):
        """Create a Builtin Condition Clause to denote a private conversation."""
        bcc = BuiltinConditionClause('conversation_is_public', invert=True)

        bcc_descriptor = bcc.to_descriptor()
        expected = {'condition': 'conversation_is_public', 'invert': True}

        self.assertEqual(bcc_descriptor, expected)

    def test_init_room(self):
        """Create a Builtin Condition Clause to denote a conversation in a room."""
        bcc = BuiltinConditionClause('conversation_is_room')

        bcc_descriptor = bcc.to_descriptor()
        expected = {'condition': 'conversation_is_room'}

        self.assertEqual(bcc_descriptor, expected)

    def test_init_dm(self):
        """Create a Builtin Condition Clause to denote a direct 1-to-1 conversation."""
        bcc = BuiltinConditionClause('conversation_is_room', invert=True)

        bcc_descriptor = bcc.to_descriptor()
        expected = {'condition': 'conversation_is_room', 'invert': True}

        self.assertEqual(bcc_descriptor, expected)

class CompositeConditionClauseTests(unittest.TestCase):
    def test_private_room(self):
        """Test the private room condition."""
        priv = BuiltinConditionClause('conversation_is_public', invert=True)

        room = BuiltinConditionClause('conversation_is_room')

        priv_room = CompositeConditionClause(type='and', conditions=[room, priv])

        pr_descriptor = priv_room.to_descriptor()
        expected = {'type': 'and', 'conditions': [{'condition': 'conversation_is_room'}, {'invert': True, 'condition': 'conversation_is_public'}]}

        self.assertEqual(pr_descriptor, expected)

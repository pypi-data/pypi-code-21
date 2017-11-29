import unittest
from docbase.memo import Memo
from docbase.group import Group


class TestMemo(unittest.TestCase):

    def test_scope(self):
        memo = Memo()
        self.assertEqual(memo.scope, "everyone",
                         "default scope must be 'everyone'")

        memo.scope = "group"
        self.assertEqual(memo.scope, "group")

        memo.scope = "private"
        self.assertEqual(memo.scope, "private")

        with self.assertRaises(Exception):
            memo.scope = "public"

    def test_add_group(self):
        memo = Memo()
        memo.scope = "everyone"
        with self.assertRaises(Exception):
            memo.add_group(Group(name="one_group", id=1))

        memo.scope = "private"
        with self.assertRaises(Exception):
            memo.add_group(Group(name="one_group", id=1))

        memo.scope = "group"
        memo.add_group(Group(name="one_group", id=1))
        self.assertIn(Group(id=1, name="one_group"), memo.groups)

    def test_remove_group(self):
        memo = Memo()
        memo.scope = "group"
        memo.add_group(Group(name="one_group", id=1))
        memo.remove_group(Group(id=1, name="one_group"))
        self.assertNotIn("one_group", memo.groups)

    def test_scope_clear_groups(self):
        memo = Memo()
        memo.scope = "group"
        memo.add_group(Group(name="one_group", id=1))
        memo.scope = "everyone"
        self.assertEqual(len(memo.groups), 0)


if __name__ == "__main__":
    unittest.main()

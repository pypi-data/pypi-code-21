import trust
from .common_tests import CommonTests


class TestFileFinder(CommonTests):
    def test_empty_path(self):
        with self.assertRaises(ValueError) as context:
            self._finder.find("")

    def test_invalid_path(self):
        with self.assertRaises(ValueError) as context:
            self._finder.find("hello")

    def test_missing_file(self):
        with self.assertRaises(trust.NodeNotFoundException) as context:
            self._finder.find("/hello")

    def test_missing_node(self):
        self._writeJson(
            "hello.json", {
                "world": "Hello, World!"
            }
        )

        with self.assertRaises(trust.NodeNotFoundException) as context:
            self._finder.find("/hello/abc")

    def test_missing_file_optional(self):
        actual = self._finder.find("/hello", optional=True)
        self.assertIsNone(actual)

    def test_missing_node_optional(self):
        self._writeJson(
            "hello.json", {
                "world": "Hello, World!"
            }
        )

        actual = self._finder.find("/hello/abc", optional=True)
        self.assertIsNone(actual)

    def test_root_value(self):
        self._writeJson(
            "hello.json", {
                "world": "Hello, World!"
            }
        )

        actual = self._finder.find("/hello/world")
        expected = "Hello, World!"
        self.assertEqual(expected, actual)

    def test_child_value(self):
        self._writeJson(
            "hello.json", {
                "world": {
                    "child": "Hello, World!"
                }
            }
        )

        actual = self._finder.find("/hello/world/child")
        expected = "Hello, World!"
        self.assertEqual(expected, actual)

    def test_value_in_directory(self):
        self._writeJson(
            "hello/child.json", {
                "world": "Hello, World!"
            }
        )

        actual = self._finder.find("/hello/child/world")
        expected = "Hello, World!"
        self.assertEqual(expected, actual)

    def test_int(self):
        self._writeJson(
            "hello.json", {
                "world": 3
            }
        )

        actual = self._finder.find("/hello/world")
        expected = 3
        self.assertEqual(expected, actual)

    def test_float(self):
        self._writeJson(
            "hello.json", {
                "world": 3.14
            }
        )

        actual = self._finder.find("/hello/world")
        expected = 3.14
        self.assertEqual(expected, actual)

    def test_array(self):
        self._writeJson(
            "hello.json", {
                "world": [2, 5, 1, 4]
            }
        )

        actual = self._finder.find("/hello/world")
        expected = [2, 5, 1, 4]
        self.assertEqual(expected, actual)

    def test_indexes(self):
        self._writeJson(
            "hello.json", {
                "world": [2, 5, 1, 4]
            }
        )

        actual = self._finder.find("/hello/world/1")
        expected = 5
        self.assertEqual(expected, actual)

    def test_keys(self):
        self._writeJson(
            "hello.json", {
                "world": {
                    "a": 4,
                    "f": 1,
                    "c": 8
                }
            }
        )

        actual = self._finder.find("/hello/world/.keys")
        expected = ["a", "c", "f"]
        self.assertEqual(expected, actual)

    def test_keys_escape(self):
        self._writeJson(
            "hello.json", {
                "world": {
                    ".keys": "Hello, World!"
                }
            }
        )

        actual = self._finder.find("/hello/world/.plain:.keys")
        expected = "Hello, World!"
        self.assertEqual(expected, actual)

    def test_double_escape(self):
        self._writeJson(
            "hello.json", {
                ".plain:.plain:.keys": "Hello, World!"
            }
        )

        actual = self._finder.find("/hello/.plain:.plain:.plain:.keys")
        expected = "Hello, World!"
        self.assertEqual(expected, actual)

    def test_keys_escape_go_inside(self):
        self._writeJson(
            "hello.json", {
                "world": {
                    ".keys": {
                        "a": "Hello, World!"
                    }
                }
            }
        )

        actual = self._finder.find("/hello/world/.plain:.keys/a")
        expected = "Hello, World!"
        self.assertEqual(expected, actual)

    def test_keys_above_file(self):
        self._writeJson("hello.json", {"a": 2})
        self._writeJson("world.json", {"a": 7})
        actual = self._finder.find("/.keys")
        expected = ["hello", "world"]
        self.assertEqual(expected, actual)

    def test_keys_above_file_deep(self):
        self._writeJson("parent/hello.json", {"a": 2})
        self._writeJson("parent/world.json", {"a": 7})
        actual = self._finder.find("/parent/.keys")
        expected = ["hello", "world"]
        self.assertEqual(expected, actual)

    def test_json(self):
        self._writeJson(
            "hello.json", {
                "world": {
                    "a": 5
                }
            }
        )

        actual = self._finder.find("/hello/world")
        expected = {"a": 5}
        self.assertEqual(expected, actual)

    def test_root(self):
        self._writeJson(
            "hello.json", {
                "world": 5
            }
        )

        actual = self._finder.find("/hello")
        expected = {"world": 5}
        self.assertEqual(expected, actual)

    def test_inheritance(self):
        self._writeJson(
            "parent.json", {
                "world": 5
            }
        )

        self._writeJson(
            "child.json", {
                ".special:inherit": "/parent",
                "hello": 2
            }
        )

        actual = self._finder.find("/child/world")
        expected = 5
        self.assertEqual(expected, actual)

    def test_deep_inheritance(self):
        self._writeJson(
            "parent.json", {
                "world": 5
            }
        )

        self._writeJson(
            "child.json", {
                "sub": {
                    ".special:inherit": "/parent",
                    "hello": 2
                }
            }
        )

        actual = self._finder.find("/child/sub/world")
        expected = 5
        self.assertEqual(expected, actual)

    def test_inheritance_inside(self):
        self._writeJson(
            "parent.json", {
                "world": 5
            }
        )

        self._writeJson(
            "child.json", {
                "sub": {
                    ".special:inherit": "/parent",
                    "hello": 2
                }
            }
        )

        actual = self._finder.find("/child")
        expected = {"sub": {"hello": 2, "world": 5}}
        self.assertEqual(expected, actual)

    def test_inheritance_replacing(self):
        self._writeJson(
            "parent.json", {
                "world": 5
            }
        )

        self._writeJson(
            "child.json", {
                ".special:inherit": "/parent",
                "hello": 2,
                "world": 4
            }
        )

        actual = self._finder.find("/child/world")
        expected = 4
        self.assertEqual(expected, actual)

    def test_inheritance_replacing_by_value(self):
        self._writeJson(
            "parent.json", {
                "hello": 4
            }
        )

        self._writeJson(
            "child.json", {
                "hello": {
                    ".special:inherit": "/parent/hello",
                }
            }
        )

        actual = self._finder.find("/child")
        expected = {"hello": 4}
        self.assertEqual(expected, actual)

    def test_inheritance_replacing_by_value_direct(self):
        self._writeJson(
            "parent.json", {
                "hello": 4
            }
        )

        self._writeJson(
            "child.json", {
                "hello": {
                    ".special:inherit": "/parent/hello",
                }
            }
        )

        actual = self._finder.find("/child/hello")
        expected = 4
        self.assertEqual(expected, actual)

    def test_deep_inheritance_replacing(self):
        self._writeJson(
            "parent.json", {
                "world": {
                    "a": 3,
                    "b": 6
                }
            }
        )

        self._writeJson(
            "child.json", {
                ".special:inherit": "/parent",
                "world": {
                    ".special:actions": ["replace"],
                    "b": 4,
                    "c": 8
                }
            }
        )

        actual = self._finder.find("/child/world")
        expected = {"b": 4, "c": 8}
        self.assertEqual(expected, actual)

    def test_deep_inheritance_merge(self):
        self._writeJson(
            "parent.json", {
                "world": {
                    "a": 3,
                    "b": 6
                }
            }
        )

        self._writeJson(
            "child.json", {
                ".special:inherit": "/parent",
                "world": {
                    ".special:actions": ["merge"],
                    "b": 4,
                    "c": 8
                }
            }
        )

        actual = self._finder.find("/child/world")
        expected = {"a": 3, "b": 4, "c": 8}
        self.assertEqual(expected, actual)

    def test_inheritance_array_replace(self):
        self._writeJson(
            "parent.json", {
                "world": [3, 6]
            }
        )

        self._writeJson(
            "child.json", {
                ".special:inherit": "/parent",
                "world": [2, 1]
            }
        )

        actual = sorted(self._finder.find("/child/world"))
        expected = [1, 2]
        self.assertSequenceEqual(expected, actual)

    def test_inheritance_array_add(self):
        self._writeJson(
            "parent.json", {
                "world": [3, 6]
            }
        )

        self._writeJson(
            "child.json", {
                ".special:inherit": "/parent",
                "world": {
                    ".special:actions": ["add"],
                    ".special:values": [2, 1, 3]
                }
            }
        )

        actual = sorted(self._finder.find("/child/world"))
        expected = [1, 2, 3, 3, 6]
        self.assertSequenceEqual(expected, actual)

    def test_inheritance_array_merge(self):
        self._writeJson(
            "parent.json", {
                "world": [3, 6]
            }
        )

        self._writeJson(
            "child.json", {
                ".special:inherit": "/parent",
                "world": {
                    ".special:actions": ["merge"],
                    ".special:values": [2, 1, 3]
                }
            }
        )

        actual = sorted(self._finder.find("/child/world"))
        expected = [1, 2, 3, 6]
        self.assertSequenceEqual(expected, actual)

    def test_inheritance_array_add_duplicates(self):
        self._writeJson(
            "parent.json", {
                "world": [3, 6, 6]
            }
        )

        self._writeJson(
            "child.json", {
                ".special:inherit": "/parent",
                "world": {
                    ".special:actions": ["add"],
                    ".special:values": [2, 1, 1, 3]
                }
            }
        )

        actual = sorted(self._finder.find("/child/world"))
        expected = [1, 1, 2, 3, 3, 6, 6]
        self.assertSequenceEqual(expected, actual)

    def test_inheritance_array_merge_duplicates(self):
        self._writeJson(
            "parent.json", {
                "world": [3, 6, 6]
            }
        )

        self._writeJson(
            "child.json", {
                ".special:inherit": "/parent",
                "world": {
                    ".special:actions": ["merge"],
                    ".special:values": [2, 1, 1, 3]
                }
            }
        )

        actual = sorted(self._finder.find("/child/world"))
        expected = [1, 2, 3, 6]
        self.assertSequenceEqual(expected, actual)

    def test_replacing_list_with_object(self):
        self._writeJson(
            "parent.json", {
                "world": [3, 2, 7]
            }
        )

        self._writeJson(
            "child.json", {
                ".special:inherit": "/parent",
                "world": {
                    "a": "Hello",
                    "b": "World"
                }
            }
        )

        actual = self._finder.find("/child/world")
        expected = [3, 2, 7]
        self.assertEqual(expected, actual)

    def test_replacing_object_with_list(self):
        self._writeJson(
            "parent.json", {
                "world": {
                    "a": "Hello",
                    "b": "World"
                }
            }
        )

        self._writeJson(
            "child.json", {
                ".special:inherit": "/parent",
                "world": [3, 2, 7]
            }
        )

        actual = self._finder.find("/child/world")
        expected = [3, 2, 7]
        self.assertSequenceEqual(expected, actual)

    def test_whole_file(self):
        self._writeJson(
            "demo/hello.json", {
                "world": "Hello, World!"
            }
        )

        actual = self._finder.find("/demo/hello")
        expected = {
            "world": "Hello, World!"
        }

        self.assertEqual(expected, actual)

    def test_whole_directory(self):
        self._writeJson(
            "demo/hello.json", {
                "world": "Hello, World!"
            }
        )

        actual = self._finder.find("/demo")
        expected = {
            "hello": {
                "world": "Hello, World!"
            }
        }

        self.assertEqual(expected, actual)

    def test_whole_directory_hierarchy(self):
        self._writeJson(
            "demo/example/hello.json", {
                "world": "Hello, World!"
            }
        )

        actual = self._finder.find("/demo")
        expected = {
            "example": {
                "hello": {
                    "world": "Hello, World!"
                }
            }
        }

        self.assertEqual(expected, actual)

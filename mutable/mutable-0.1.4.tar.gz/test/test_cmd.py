import unittest
import subprocess
import json

class TestCmd(unittest.TestCase):

    def test_help1(self):
        out = subprocess.check_output([
            "python",
            "test/cmd_1.py",
            "--help"
            ],
            shell=False
        )

        # Class name as decription
        self.assertEqual(out.startswith("Child"), True)

        # Props
        self.assertEqual("--a" in out, True)
        self.assertEqual("--b.c" in out, True)

    def test_help2(self):
        out = subprocess.check_output([
            "python",
            "test/cmd_2.py",
            "--help"
            ],
            shell=False
        )

        # Class name as decription
        self.assertEqual(out.startswith("Child"), True)

        # props
        self.assertEqual("--a" in out, True)
        self.assertEqual("--b.c" in out, True)
        self.assertEqual("--c" in out, True)
        self.assertEqual("--d" in out, True)

    def test_help3(self):
        out = subprocess.check_output([
            "python",
            "test/cmd_3.py",
            "--help"
            ],
            shell=False
        )

        # Class name as decription
        self.assertEqual(out.startswith("Child"), True)

        # props
        self.assertEqual("--a" in out, True)
        self.assertEqual("--b.c" in out, True)
        self.assertEqual("--c" in out, True)
        self.assertEqual("--d" in out, True)

        # description
        self.assertEqual("description a" in out, True)
        self.assertEqual("description c" in out, True)

    def test_help4(self):
        out = subprocess.check_output([
            "python",
            "test/cmd_4.py",
            "--help"
            ],
            shell=False
        )

        # Class name as decription
        self.assertEqual(out.startswith("Child"), True)

        # props
        self.assertEqual("--a.0.a" in out, True)
        self.assertEqual("--a.1.b" in out, True)

        # description
        self.assertEqual("description 0" in out, True)
        self.assertEqual("description 1" in out, True)

    def test_assign1(self):
        out = subprocess.check_output([
            "python",
            "test/cmd_1.py",
            "--a=2"
            ],
            shell=False
        )

        o = json.loads(out)

        self.assertEqual(o["a"], 2)
        self.assertEqual(o["b"]["c"], "test")

    def test_assign2(self):
        out = subprocess.check_output([
            "python",
            "test/cmd_2.py",
            "--a=2",
            "--c=baz",
            "--b.c=1"
            ],
            shell=False
        )

        o = json.loads(out)

        self.assertEqual(o["a"], 2)
        self.assertEqual(o["c"], "baz")
        self.assertEqual(o["b"]["c"], 1)

    def test_assign4(self):
        out = subprocess.check_output([
            "python",
            "test/cmd_4.py",
            "--a.0.a=2",
            ],
            shell=False
        )

        o = json.loads(out)

        self.assertEqual(o["a"][0]["a"], 2)

if __name__ == '__main__':
    unittest.main()

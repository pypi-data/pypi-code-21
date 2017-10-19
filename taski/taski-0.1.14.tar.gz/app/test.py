import unittest
from todoist import FileCache
from planner import PriorityPlanner
from base import Project, Task

class TestGTD(unittest.TestCase):
    def test_file_cache(self):
        fc = FileCache()
        fc.clear()
        r1 = fc.get("foo")
        r2 = fc.set("foo", {"name":"bob"})
        r3 = fc.get("foo")

        self.assertEqual(None, r1)
        self.assertEqual(True, r2)
        self.assertEqual({"name":"bob"}, r3)

class TestPlanner(unittest.TestCase):
    def test_priority_planner(self):
        def choose_func(planner_item):
            tasks = planner_item.item.tasks
            if len(tasks) > 0:
                r = tasks[0]
                planner_item.item.tasks = tasks[1:]
                return r
            else:
                return None

        planner = PriorityPlanner({})

        P1 = Project()
        P1.id = 1
        P1.tasks = ["A1", "A2", "A3", "A4", "A5"]
        P1.priority = 6
        P2 = Project()
        P2.id = 2
        P2.tasks = ["B1", "B2", "B3", "B4", "B5"]
        P2.priority = 3
        P3 = Project()
        P3.id = 3
        P3.tasks = ["C1", "C2", "C3", "C4", "C5"]
        P3.priority = 1
        projects = [P1, P2, P3]

        res = []
        for t in planner.plan(projects, choose_func):
            res.append(t)

        print(res)

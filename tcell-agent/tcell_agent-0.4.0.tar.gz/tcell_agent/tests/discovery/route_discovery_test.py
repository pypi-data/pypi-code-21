import unittest

from ...agent import TCellAgent


class AppSensorPolicyTest(unittest.TestCase):
    def simple_database_route_test(self):
        events = []

        def addEvent(self, event):
            event.post_process()
            events.append(event)

        TCellAgent.addEvent = addEvent

        TCellAgent.tCell_agent = TCellAgent()
        policy_json = {
            "dlp": {
                "policy_id": "nyzd",
                "data": {
                    "data_discovery": {
                        "database_enabled": True
                    },
                }
            }
        }
        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)

        TCellAgent.discover_database_fields("databasex", "schemax", "tablex", ["fieldx"], "routex")
        TCellAgent.discover_database_fields("databasex", "schemax", "tablex", ["fieldx"], "routex")
        TCellAgent.discover_database_fields("databasex", "schemax", "tablex", ["fieldx"], "routex")
        TCellAgent.discover_database_fields("databasex", "schemax", "tablex", ["fieldx"], "routex")

        self.assertEqual(TCellAgent.tCell_agent.route_table.routes["routex"].database_fields[
                             hash("databasex,schemax,tablex," + ",".join(["fieldx"]))].discovered, True)
        self.assertEqual(TCellAgent.tCell_agent.route_table.routes["routex"].database_fields[
                             hash("databasex,schemax,tabley," + ",".join(["fieldx"]))].discovered, False)

        self.assertEqual(len(events), 1)

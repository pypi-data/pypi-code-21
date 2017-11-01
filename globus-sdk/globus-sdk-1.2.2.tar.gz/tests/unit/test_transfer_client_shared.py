from random import getrandbits

import globus_sdk
from tests.framework import TransferClientTestCase, get_user_data, GO_EP1_ID
from globus_sdk.exc import TransferAPIError
from globus_sdk.transfer.paging import PaginatedResource


class SharedTransferClientTests(TransferClientTestCase):
    """
    Transfer Client tests that require a unique shared endpoint per test.
    tearDown takes significantly time since a delete task needs to complete.
    """

    __test__ = True  # marks sub-class as having tests

    def setUp(self):
        """
        calls BaseTransferClientTest setUp,
        then sets up a test shared endpoint
        """
        super(SharedTransferClientTests, self).setUp()

        # shared endpoint hosted on go#ep1,
        # name and dir randomized to prevent collision
        share_path = "/~/share-" + str(getrandbits(128))
        self.tc.operation_mkdir(GO_EP1_ID, path=share_path)
        shared_data = {"DATA_TYPE": "shared_endpoint",
                       "host_endpoint": GO_EP1_ID,
                       "host_path": share_path,
                       "display_name":
                       "SDK Test Shared Endpoint-" + str(getrandbits(128)),
                       "description": "Shared Endpoint for testing the SDK"
                       }
        r = self.tc.create_shared_endpoint(shared_data)
        self.test_share_ep_id = r["id"]

        # track assets for cleanup
        self.asset_cleanup.append({"function": self.tc.delete_endpoint,
                                   "args": [r["id"]]})
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP1_ID, share_path]})

    def test_endpoint_search(self):
        """
        Searches by fulltext, owner_id, and scopes, validates results
        """

        # full-text and cap of num_results
        search_string = "tutorial"
        cap = 5
        text_doc = self.tc.endpoint_search(search_string, num_results=cap)
        # confirm the results are in the right format, are capped correctly,
        # and that the results have the search string in their display names
        self.assertIsInstance(text_doc, PaginatedResource)
        results_count = 0
        for ep in text_doc:
            self.assertIn(search_string, str.lower(str(ep["display_name"])))
            results_count += 1
        self.assertEqual(results_count, cap)

        # owner-id param
        params = {"filter_owner_id": get_user_data()["go"]["id"]}
        owner_doc = self.tc.endpoint_search(**params)
        # confirm format, and that all results are from GO
        self.assertIsInstance(owner_doc, PaginatedResource)
        for ep in owner_doc:
            self.assertEqual(ep["owner_id"], get_user_data()["go"]["id"])

        # scope: my endpoints
        my_doc = self.tc.endpoint_search(filter_scope="my-endpoints")
        # confirm format, and that all results are owned by SDK tester
        self.assertIsInstance(my_doc, PaginatedResource)
        for ep in my_doc:
            self.assertEqual(ep["owner_id"],
                             get_user_data()["sdktester1a"]["id"])

        # scope: shared endpoints
        my_doc = self.tc.endpoint_search(filter_scope="shared-by-me")
        # confirm format, and that all results are shared by SDK tester
        self.assertIsInstance(my_doc, PaginatedResource)
        for ep in my_doc:
            self.assertEqual(ep["owner_id"],
                             get_user_data()["sdktester1a"]["id"])
            self.assertIsNotNone(ep["sharing_target_root_path"])
            self.assertIsNotNone(ep["host_endpoint_id"])

    def test_endpoint_autoactivate(self):
        """
        Deactivates, then auto-activates shared endpoint,
        confirms activation through get,
        confirms trying again with if_expires_in returns AlreadyActivated
        """
        # deactivate
        self.tc.endpoint_deactivate(self.test_share_ep_id)

        # auto-activate and check for successful response code
        auto_doc = self.tc.endpoint_autoactivate(self.test_share_ep_id)
        self.assertEqual(auto_doc["code"],
                         "AutoActivated.GlobusOnlineCredential")

        # confirm get sees the endpoint as activated now
        get_doc = self.tc.get_endpoint(self.test_share_ep_id)
        self.assertTrue(get_doc["activated"])

        # confirm if_expires_in sees the endpoint as activated
        params = {"if_expires_in": "60"}
        expires_doc = self.tc.endpoint_autoactivate(
            self.test_share_ep_id, **params)
        self.assertEqual(expires_doc["code"], "AlreadyActivated")

        # TODO: test against an endpoint we are not allowed to activate

    def test_endpoint_deactivate(self):
        """
        Auto-activates, then deactivates shared endpoint,
        confirms deactivation through get
        """

        # activate
        self.tc.endpoint_autoactivate(self.test_share_ep_id)

        # deactivate and check for successful response code
        deact_doc = self.tc.endpoint_deactivate(self.test_share_ep_id)
        self.assertEqual(deact_doc["code"], "Deactivated")

        # confirm get sees the endpoint as deactivated now
        get_doc = self.tc.get_endpoint(self.test_share_ep_id)
        self.assertFalse(get_doc["activated"])

    def test_my_shared_endpoint_list(self):
        """
        Gets my shared endpoint list, validates results
        """

        # get shared endpoint list
        share_doc = self.tc.my_shared_endpoint_list(GO_EP1_ID)

        # confirm doc type, and that test_share_ep_id is on the list
        self.assertEqual(share_doc["DATA_TYPE"], "endpoint_list")
        for ep in share_doc:
            if ep["id"] == self.test_share_ep_id:
                break
        else:
            self.assertFalse("test share not found")

    def test_endpoint_acl_list(self):
        """
        Gets endpoint access rule list from test_share_ep, validates results
        """

        # get endpoint role list
        list_doc = self.tc.endpoint_acl_list(self.test_share_ep_id)

        # validate responce has been put into
        self.assertEqual(list_doc["DATA_TYPE"], "access_list")
        self.assertIn("DATA", list_doc)
        # confirm that each access rule has some expected values
        for access in list_doc["DATA"]:
            self.assertEqual(access["DATA_TYPE"], "access")
            self.assertIn("id", access)
            self.assertIn("principal_type", access)
            self.assertIn("principal", access)
            self.assertIn("permissions", access)

    def test_get_endpoint_acl_rule(self):
        """
        Adds access rule to test_share_ep, gets it by id, validates results
        """

        # get access rule id through test_add_endpoint_acl_rule
        access_id = self.test_add_endpoint_acl_rule()

        # get the access rule by id
        get_doc = self.tc.get_endpoint_acl_rule(self.test_share_ep_id,
                                                access_id)

        # validate results
        self.assertEqual(get_doc["DATA_TYPE"], "access")
        self.assertEqual(get_doc["id"], access_id)

    def test_add_endpoint_acl_rule(self):
        """
        Adds access rule to test_share_ep, validates results,
        then confirms get sees the new access rule,
        returns the access_id for use in testing get update and delete
        """

        # add root read access to all users logged in with auth
        add_data = {"DATA_TYPE": "access",
                    "principal_type": "all_authenticated_users",
                    "principal": "",
                    "path": "/",
                    "permissions": "r"
                    }
        add_doc = self.tc.add_endpoint_acl_rule(self.test_share_ep_id,
                                                add_data)

        # validate results
        self.assertEqual(add_doc["DATA_TYPE"], "access_create_result")
        self.assertEqual(add_doc["code"], "Created")
        self.assertEqual(add_doc["message"],
                         "Access rule created successfully.")
        self.assertIn("access_id", add_doc)

        # confirm get sees new access rule
        access_id = add_doc["access_id"]
        get_doc = self.tc.get_endpoint_acl_rule(self.test_share_ep_id,
                                                access_id)
        self.assertEqual(get_doc["id"], access_id)
        for item in add_data:
            self.assertEqual(get_doc[item], add_data[item])

        # return access_id
        return access_id

    def test_update_endpoint_acl_rule(self):
        """
        Adds access rule to test_share_ep, updates that access rule,
        validates results, then confirms get sees the new changes
        """

        # get access rule id through test_add_endpoint_acl_rule
        access_id = self.test_add_endpoint_acl_rule()

        # update the access rule by id
        update_data = {"permissions": "rw"}
        update_doc = self.tc.update_endpoint_acl_rule(self.test_share_ep_id,
                                                      access_id, update_data)

        # validate results
        self.assertEqual(update_doc["DATA_TYPE"], "result")
        self.assertEqual(update_doc["code"], "Updated")
        self.assertIn("permissions updated successfully",
                      update_doc["message"])

        # confirm get sees new permissions
        get_doc = self.tc.get_endpoint_acl_rule(self.test_share_ep_id,
                                                access_id)
        self.assertEqual(get_doc["permissions"], update_data["permissions"])

    def test_delete_endpoint_acl_rule(self):
        """
        Adds access rule to test_share_ep, deletes that access rule,
        validates results, then confirms get no longer sees the access rule
        """

        # get access rule id through test_add_endpoint_acl_rule
        access_id = self.test_add_endpoint_acl_rule()

        # delete the access rule by id
        delete_doc = self.tc.delete_endpoint_acl_rule(self.test_share_ep_id,
                                                      access_id)

        # validate results
        self.assertEqual(delete_doc["DATA_TYPE"], "result")
        self.assertEqual(delete_doc["code"], "Deleted")
        self.assertIn("deleted successfully", delete_doc["message"])

        # confirm get no longer sees the access rule
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.get_endpoint_acl_rule(self.test_share_ep_id, access_id)
        self.assertEqual(apiErr.exception.http_status, 404)
        self.assertEqual(apiErr.exception.code, "AccessRuleNotFound")

    def test_endpoint_manager_create_pause_rule(self):
        """
        Creates a pause rule on the shared endpoint, validates results.
        Returns the rule's id for use in other tests that need a pause rule.
        Confirms 403 when non manager attempts to use this resource.
        """
        rule_data = {
            "DATA_TYPE": "pause_rule",
            "message": "SDK Test Pause Rule",
            "endpoint_id": self.test_share_ep_id,
            "identity_id": None,  # affect all users on endpoint
            "start_time": None  # start now
        }
        create_doc = self.tc.endpoint_manager_create_pause_rule(rule_data)

        # verify results
        for key in rule_data:
            self.assertEqual(create_doc[key], rule_data[key])
        self.assertTrue(create_doc["editable"])
        self.assertFalse(create_doc["created_by_host_manager"])
        rule_id = create_doc["id"]

        # 403 for non managers
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc2.endpoint_manager_create_pause_rule(rule_data)
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "PermissionDenied")

        # track for cleanup, note this must be placed earlier in the
        # list than the shared endpoint
        self.asset_cleanup.insert(
            0,
            {"function": self.tc.endpoint_manager_delete_pause_rule,
             "args": [rule_id],
             "name": "test_pause_rule"})

        # return id for use in other tests
        return rule_id

    def test_endpoint_manager_pause_rule_list(self):
        """
        Gets a pause_rule id from test_endpoint_manager_create_pause_rule.
        Gets pause rule lists with/without endpoint filters, validates results.
        Confirms 403 when non manager attempts to use this resource.
        """
        rule_id = self.test_endpoint_manager_create_pause_rule()

        # all endpoint_rules
        list_doc = self.tc.endpoint_manager_pause_rule_list()
        self.assertEqual(list_doc["DATA_TYPE"], "pause_rule_list")
        for rule in list_doc:
            self.assertEqual(rule["DATA_TYPE"], "pause_rule")
            if rule["id"] == rule_id:
                break
        else:
            self.assertFalse("rule_id not found")

        # filtered by endpoint, should only have the created rule
        list_doc = self.tc.endpoint_manager_pause_rule_list(
            filter_endpoint=self.test_share_ep_id)
        rule = list_doc["DATA"][0]
        self.assertEqual(rule["id"], rule_id)

        # 403 for non managers
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc2.endpoint_manager_pause_rule_list()
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "PermissionDenied")

    def test_endpoint_manager_get_pause_rule(self):
        """
        Gets a pause rule created by test_endpoint_manager_create_pause_rule.
        Validates results and checks expected fields.
        Confirms 403 when non manager attempts to use this resource.
        """
        rule_id = self.test_endpoint_manager_create_pause_rule()
        get_doc = self.tc.endpoint_manager_get_pause_rule(rule_id)

        # validate results have expected fields and values
        expected = {
            "DATA_TYPE": "pause_rule", "id": rule_id,
            "message": "SDK Test Pause Rule", "start_time": None,
            "endpoint_id": self.test_share_ep_id, "identity_id": None,
            "modified_by_id": get_user_data()["sdktester1a"]["id"],
            "created_by_host_manager": False, "editable": True,
            "pause_ls": True, "pause_mkdir": True, "pause_rename": True,
            "pause_task_delete": True, "pause_task_transfer_write": True,
            "pause_task_transfer_read": True}
        for key in expected:
            self.assertEqual(get_doc[key], expected[key])

        # 403 for non managers
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc2.endpoint_manager_get_pause_rule(rule_id)
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "PermissionDenied")

    def test_endpoint_manager_update_pause_rule(self):
        """
        Updates a pause rule created by test_endpoint_manager_create_pause_rule
        Validates results and confirms fields have updated with get.
        Confirms 403 when non manager attempts to use this resource.
        """
        rule_id = self.test_endpoint_manager_create_pause_rule()

        # update the rule
        update_data = {
            "message": "New Message", "pause_ls": False, "pause_mkdir": False,
            "pause_rename": False, "pause_task_delete": False,
            "pause_task_transfer_write": False,
            "pause_task_transfer_read": False}
        update_doc = self.tc.endpoint_manager_update_pause_rule(
            rule_id, update_data)
        self.assertEqual(update_doc["DATA_TYPE"], "pause_rule")

        # get the the rule after update
        get_doc = self.tc.endpoint_manager_get_pause_rule(rule_id)

        # validate results and confirm get sees updated fields
        for key in update_data:
            self.assertEqual(update_doc[key], update_data[key])
            self.assertEqual(get_doc[key], update_data[key])

        # 403 for non managers
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc2.endpoint_manager_update_pause_rule(rule_id, update_data)
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "PermissionDenied")

    def test_endpoint_manager_delete_pause_rule(self):
        """
        Deletes a pause rule created by test_endpoint_manager_create_pause_rule
        Validates results and confirms 404 when trying to get rule.
        Confirms 403 when non manager attempts to use this resource.
        """
        rule_id = self.test_endpoint_manager_create_pause_rule()

        # confirm 403 for non managers before deleting the rule
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc2.endpoint_manager_delete_pause_rule(rule_id)
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "PermissionDenied")

        # delete the rule, validate results
        delete_doc = self.tc.endpoint_manager_delete_pause_rule(rule_id)
        self.assertEqual(delete_doc["DATA_TYPE"], "result")
        self.assertEqual(delete_doc["code"], "Deleted")

        # confirm get returns 404 as rule no longer exists
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.endpoint_manager_get_pause_rule(rule_id)
        self.assertEqual(apiErr.exception.http_status, 404)
        self.assertEqual(apiErr.exception.code, "PauseRuleNotFound")

        # stop tracking pause rule for cleanup
        for cleanup in self.asset_cleanup:
            if "name" in cleanup and cleanup["name"] == "test_pause_rule":
                self.asset_cleanup.remove(cleanup)
                break

    def test_task_pause_info(self):
        """
        Creates a pause rule on the shared endpoint, then submits a task
        against it. Gets pause info for the task, validates results,
        and confirms the task is paused (or about to be).
        """
        # create pause rule
        rule_id = self.test_endpoint_manager_create_pause_rule()

        # submit a no-op delete task
        ddata = globus_sdk.DeleteData(self.tc, self.test_share_ep_id,
                                      notify_on_fail=False)
        ddata.add_item("no-op.txt")
        task_id = self.tc.submit_delete(ddata)["task_id"]

        # get pause info and validate
        pause_doc = self.tc.task_pause_info(task_id)

        # validate top level results
        self.assertEqual(pause_doc["DATA_TYPE"], "pause_info_limited")
        self.assertIsNone(pause_doc["source_pause_message"])
        self.assertIsNone(pause_doc["destination_pause_message"])

        # validate the rule results
        rule = pause_doc["pause_rules"][0]  # should be the only rule
        self.assertEqual(rule["DATA_TYPE"], "pause_rule_limited")
        self.assertEqual(rule["id"], rule_id)
        self.assertEqual(rule["message"], "SDK Test Pause Rule")
        self.assertNotIn("modified_by", rule)
        self.assertNotIn("modified_by_id", rule)

    def test_my_effective_pause_rule_list(self):
        """
        Creates a pause rule on the shared endpoint, then gets pause rule list.
        Validates results and confirms the pause rule is found.
        """
        # create pause rule
        rule_id = self.test_endpoint_manager_create_pause_rule()

        # get the pause list
        pause_doc = self.tc.my_effective_pause_rule_list(self.test_share_ep_id)

        # validate top level results
        self.assertEqual(pause_doc["DATA_TYPE"], "pause_rule_list")

        # validate the rule results
        rule = pause_doc["DATA"][0]  # should be the only rule
        self.assertEqual(rule["DATA_TYPE"], "pause_rule_limited")
        self.assertEqual(rule["id"], rule_id)
        self.assertEqual(rule["message"], "SDK Test Pause Rule")
        self.assertNotIn("modified_by", rule)
        self.assertNotIn("modified_by_id", rule)

    def test_endpoint_manager_task_pause_info(self):
        """
        Creates a pause rule on the shared endpoint, then
        has sdktester2b submit a no-op task on the shared endpoint.
        Confirms sdktester1a can see the task is paused (or about to be).
        Confirms 403 when non manager attempts to use this resource.
        """
        # sdktester1a creates pause rule
        rule_id = self.test_endpoint_manager_create_pause_rule()

        # sdktester2b subits no-op delete task
        ddata = globus_sdk.DeleteData(self.tc2, self.test_share_ep_id,
                                      notify_on_fail=False)
        ddata.add_item("no-op.txt")
        task_id = self.tc2.submit_delete(ddata)["task_id"]

        # sdktester1a gets the task pause info as admin
        pause_doc = self.tc.endpoint_manager_task_pause_info(task_id)

        # validate top level results
        self.assertEqual(pause_doc["DATA_TYPE"], "pause_info_limited")
        self.assertIsNone(pause_doc["source_pause_message"])
        self.assertIsNone(pause_doc["destination_pause_message"])

        # validate the rule results
        rule = pause_doc["pause_rules"][0]  # should be the only rule
        self.assertEqual(rule["DATA_TYPE"], "pause_rule_limited")
        self.assertEqual(rule["id"], rule_id)
        self.assertEqual(rule["message"], "SDK Test Pause Rule")
        # self.assertEqual(rule["modified_by_id"],
        #                  get_user_data()["sdktester1a"]["id"])

        # 403 for non managers, even if they submitted the task
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc2.endpoint_manager_task_pause_info(task_id)
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "PermissionDenied")

    def test_add_endpoint_role(self):
        """
        Adds a role to the test share endpoint, validates results
        returns role_id for use in get and delete
        """
        # add the new role
        add_data = {"principal_type": "identity",
                    "principal": get_user_data()["go"]["id"],
                    "role": "access_manager"
                    }
        add_doc = self.tc.add_endpoint_role(self.test_share_ep_id, add_data)
        role_id = add_doc["id"]

        # track asset for cleanup, make sure role is delete before share
        self.asset_cleanup.insert(0, {"function": self.tc.delete_endpoint_role,
                                      "args": [self.test_share_ep_id, role_id],
                                      "name": "test_role"})

        # validate results
        for key in add_data:
            self.assertEqual(add_doc[key], add_data[key])

        # return role id
        return role_id

    def test_get_endpoint_role(self):
        """
        Gets role created in test_add_endpoint_role, validates results.
        """
        role_id = self.test_add_endpoint_role()
        get_doc = self.tc.get_endpoint_role(self.test_share_ep_id, role_id)

        # validate results
        self.assertEqual(get_doc["DATA_TYPE"], "role")
        self.assertEqual(get_doc["id"], role_id)
        self.assertEqual(get_doc["principal_type"], "identity")
        self.assertEqual(get_doc["principal"],
                         get_user_data()["go"]["id"])
        self.assertEqual(get_doc["role"], "access_manager")

    def test_delete_endpoint_role(self):
        """
        Deletes role created in test_add_endpoint_role, validates results.
        """
        role_id = self.test_add_endpoint_role()
        delete_doc = self.tc.delete_endpoint_role(
            self.test_share_ep_id, role_id)

        # validate results
        self.assertEqual(delete_doc["DATA_TYPE"], "result")
        self.assertEqual(delete_doc["code"], "Deleted")
        self.assertIn("deleted successfully", delete_doc["message"])

        # confirm get no longer sees the role
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.get_endpoint_role(self.test_share_ep_id, role_id)
        self.assertEqual(apiErr.exception.http_status, 404)
        self.assertEqual(apiErr.exception.code, "RoleNotFound")

        # stop tracking asset for cleanup
        for cleanup in self.asset_cleanup:
            if "name" in cleanup and cleanup["name"] == "test_role":
                self.asset_cleanup.remove(cleanup)
                break

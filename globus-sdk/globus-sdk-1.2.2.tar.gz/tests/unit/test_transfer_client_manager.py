import re
import time
from random import getrandbits

import globus_sdk
from tests.framework import (TransferClientTestCase, get_user_data,
                             GO_EP1_ID, GO_EP2_ID,

                             DEFAULT_TASK_WAIT_TIMEOUT,
                             DEFAULT_TASK_WAIT_POLLING_INTERVAL)
from globus_sdk.exc import TransferAPIError
from globus_sdk.transfer.paging import PaginatedResource


class ManagerTransferClientTests(TransferClientTestCase):
    """
    class for Transfer Client Tests that require the activity_manager
    effective role on an endpoint but don't require a unique endpoint per test.
    Setup checks to see if a managed shared endpoint exists and if not creates
    one. This endpoint is not removed during automatic cleanup, but will
    be removed by the clean_sdk_test_assets.py script in manual_tools.
    """

    __test__ = True  # marks sub-class as having tests

    @classmethod
    def setUpClass(self):
        """
        Sets up a shared endpoint on test gp#ep2 managed by sdktester1a,
        and shares it with sdktester2b,
        or sees that this endpoint already exits and gets its id.
        """
        super(ManagerTransferClientTests, self).setUpClass()

        try:
            # shared endpoint hosted on go#ep2 managed by sdktester1a
            host_path = "/~/managed_ep"
            self.tc.operation_mkdir(GO_EP2_ID, path=host_path)
            shared_data = {"DATA_TYPE": "shared_endpoint",
                           "host_endpoint": GO_EP2_ID,
                           "host_path": host_path,
                           "display_name": "SDK Test Managed Endpoint",
                           "description": "Endpoint for managed SDK testing"
                           }
            r = self.tc.create_shared_endpoint(shared_data)
            self.managed_ep_id = r["id"]

            # share read and write to sdktester2b
            add_data = {"DATA_TYPE": "access",
                        "principal_type": "identity",
                        "principal": get_user_data()["sdktester2b"]["id"],
                        "path": "/",
                        "permissions": "rw"}
            self.tc.add_endpoint_acl_rule(self.managed_ep_id, add_data)

        except TransferAPIError as e:
            if "already exists" in str(e):
                shares = self.tc.my_shared_endpoint_list(GO_EP2_ID)
                self.managed_ep_id = shares["DATA"][0]["id"]
            else:
                raise e

    def test_endpoint_manager_monitored_endpoints(self):
        """
        Gets a list of all endpoints sdktester1a is an activity_manager on,
        Confirms list contains managed_ep, and has some expected fields.
        """
        ep_doc = self.tc.endpoint_manager_monitored_endpoints()
        expected_fields = ["my_effective_roles", "display_name",
                           "owner_id", "owner_string"]

        for ep in ep_doc:
            self.assertEqual(ep["DATA_TYPE"], "endpoint")
            for field in expected_fields:
                self.assertIn(field, ep)
            if ep["id"] == self.managed_ep_id:
                break
        else:
            self.assertFalse("managed endpoint not found")

    def test_endpoint_manager_get_endpoint(self):
        """
        Gets the managed endpoint, confirms expected results
        Confirms 403 when non manager attempts to use this resource.
        """
        ep_doc = self.tc.endpoint_manager_get_endpoint(self.managed_ep_id)
        self.assertEqual(ep_doc["DATA_TYPE"], "endpoint")
        self.assertEqual(ep_doc["id"], self.managed_ep_id)
        self.assertIsNone(ep_doc["in_use"])

        # 403 for non managers
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc2.endpoint_manager_hosted_endpoint_list(self.managed_ep_id)
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "PermissionDenied")

    # TODO: test against a non shared endpoint we have the manager role on
    def test_endpoint_manager_hosted_endpoint_list(self):
        """
        Attempts to gets the list of shares hosted on the managed endpoint.
        Confirms this fails as shares cannot themselves host shares.
        Confirms 403 when non manager attempts to use this resource.
        """
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.endpoint_manager_hosted_endpoint_list(self.managed_ep_id)

        self.assertEqual(apiErr.exception.http_status, 409)
        self.assertEqual(apiErr.exception.code, "Conflict")
        self.assertIn("not a host endpoint", apiErr.exception.message)

        # 403 for non managers
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc2.endpoint_manager_hosted_endpoint_list(self.managed_ep_id)
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "PermissionDenied")

    def test_endpoint_manager_acl_list(self):
        """
        Gets ACL list from managed endpoint, validates results
        Confirms 403 when non manager attempts to use this resource.
        """
        list_doc = self.tc.endpoint_manager_acl_list(self.managed_ep_id)

        self.assertEqual(list_doc["DATA_TYPE"], "access_list")
        expected_fields = ["id", "principal", "principal_type", "permissions"]
        for access in list_doc["DATA"]:
            self.assertEqual(access["DATA_TYPE"], "access")
            for field in expected_fields:
                self.assertIn(field, access)

        # 403 for non managers
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc2.endpoint_manager_acl_list(self.managed_ep_id)
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "PermissionDenied")

    def test_endpoint_manager_task_list(self):
        """
        Has sdktester2b submit transfer and delete task to the managed_ep
        Then has sdktester1a get its endpoint manager task list
        Confirms tasks submitted by sdktester2b on the managed endpoint
        are visible, and some expected fields are present.
        """
        # sdktester2b submits tasks
        # new dir with randomized name to prevent collision
        dest_dir = "transfer_dest_dir-" + str(getrandbits(128))
        dest_path = "/" + dest_dir + "/"
        self.tc2.operation_mkdir(self.managed_ep_id, dest_path)

        # transfer a file to the new dir
        tdata = globus_sdk.TransferData(self.tc2, GO_EP1_ID,
                                        self.managed_ep_id,
                                        notify_on_succeeded=False)
        source_path = "/share/godata/"
        file_name = "file1.txt"
        tdata.add_item(source_path + file_name, dest_path + file_name)
        transfer_id = self.tc2.submit_transfer(tdata)["task_id"]

        # delete the new dir
        ddata = globus_sdk.DeleteData(self.tc2, self.managed_ep_id,
                                      recursive=True,
                                      notify_on_succeeded=False)
        ddata.add_item(dest_path)
        delete_id = self.tc2.submit_delete(ddata)["task_id"]

        # sdktester1a gets endpoint manager task list
        tasks_doc = self.tc.endpoint_manager_task_list(
            filter_endpoint=GO_EP2_ID,
            filter_user_id=get_user_data()["sdktester2b"]["id"])

        # confirm submitted tasks can be found
        # and tasks have some expected fields
        expected_fields = ["username", "deadline", "type",
                           "source_endpoint_id"]
        delete_found = False
        transfer_found = False
        self.assertIsInstance(tasks_doc, PaginatedResource)
        for task in tasks_doc:

            for field in expected_fields:
                self.assertIn(field, task)

            if task["task_id"] == transfer_id:
                transfer_found = True
            if task["task_id"] == delete_id:
                delete_found = True
            if transfer_found and delete_found:
                break

        # fail if both not found
        self.assertTrue(delete_found and transfer_found)

    def test_endpoint_manager_get_task(self):
        """
        Has sdktester2b submit a no-op task on the managed endpoint
        Confirms sdktester1a can view the task as an admin.
        Confirms 403 when non manager attempts to use this resource.
        """
        # sdktester2b subits no-op delete task
        ddata = globus_sdk.DeleteData(self.tc2, self.managed_ep_id,
                                      notify_on_fail=False)
        ddata.add_item("no-op.txt")
        task_id = self.tc2.submit_delete(ddata)["task_id"]

        # sdktester1a gets the task as admin
        task_doc = self.tc.endpoint_manager_get_task(task_id)

        self.assertEqual(task_doc["task_id"], task_id)
        self.assertEqual(task_doc["owner_id"],
                         get_user_data()["sdktester2b"]["id"])
        self.assertEqual(task_doc["type"], "DELETE")
        self.assertIn("status", task_doc)

        # 403 for non managers, even if they submitted the task
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc2.endpoint_manager_get_task(task_id)
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "PermissionDenied")

    def test_endpoint_manager_task_event_list(self):
        """
        Has sdktester2b submit a no-op task on the managed endpoint.
        Waits for task to fail, and confirms sdktester1a can see the
        failure event as an admin.
        Confirms 403 when non manager attempts to use this resource.
        """
        # sdktester2b subits no-op delete task and waits for completion
        ddata = globus_sdk.DeleteData(self.tc2, self.managed_ep_id,
                                      notify_on_fail=False)
        ddata.add_item("no-op.txt")
        task_id = self.tc2.submit_delete(ddata)["task_id"]
        self.assertTrue(
            self.tc2.task_wait(
                task_id, timeout=DEFAULT_TASK_WAIT_TIMEOUT,
                polling_interval=DEFAULT_TASK_WAIT_POLLING_INTERVAL))

        # sdktester1a gets the task event list as admin
        events_doc = self.tc.endpoint_manager_task_event_list(task_id)
        self.assertIsInstance(events_doc, PaginatedResource)

        failure_event = events_doc[0]  # most recent event is first
        self.assertEqual(failure_event["DATA_TYPE"], "event")
        self.assertEqual(failure_event["code"], "FILE_NOT_FOUND")
        self.assertEqual(failure_event["description"], "file not found")

        # 403 for non managers, even if they submitted the task
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc2.endpoint_manager_task_event_list(task_id)
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "PermissionDenied")

    def test_endpoint_manager_task_successful_transfers(self):
        """
        Has sdktester2b submit a recursive transfer of share/godata to the
        managed_ep. Waits for the task to complete, then has sdktester1a get
        the successful transfers of the task as an admin. Confirms all 3 files
        are seen, and some expected fields are present.
        """
        # new dir with randomized name to prevent collision
        dest_dir = "transfer_dest_dir-" + str(getrandbits(128))
        dest_path = "/" + dest_dir + "/"
        self.tc2.operation_mkdir(self.managed_ep_id, dest_path)
        # transfer a the files
        tdata = globus_sdk.TransferData(self.tc2, GO_EP1_ID,
                                        self.managed_ep_id,
                                        notify_on_succeeded=False)
        source_path = "/share/godata/"
        tdata.add_item(source_path, dest_path, recursive=True)
        task_id = self.tc2.submit_transfer(tdata)["task_id"]

        # track asset for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [self.managed_ep_id, dest_path]})
        # wait for task to complete
        self.assertTrue(
            self.tc2.task_wait(
                task_id, timeout=DEFAULT_TASK_WAIT_TIMEOUT,
                polling_interval=DEFAULT_TASK_WAIT_POLLING_INTERVAL))

        # sdktester1a gets successful transfers as admin
        success_doc = self.tc.endpoint_manager_task_successful_transfers(
            task_id)

        # confirm results
        self.assertIsInstance(success_doc, PaginatedResource)
        count = 0
        for transfer in success_doc:

            self.assertEqual(transfer["DATA_TYPE"], "successful_transfer")
            self.assertIsNotNone(re.match(dest_path + "file[1-3].txt",
                                          transfer["destination_path"]))
            count += 1
        self.assertEqual(count, 3)

    def _unauthorized_transfers(self):
        """
        Helper that has sdktester2b submit 3 unauthorized transfers from the
        managed endpoint, returns a list of their task_ids,
        and tracks them for cleanup.
        """
        # submit the tasks
        task_ids = []
        for i in range(3):
            tdata = globus_sdk.TransferData(self.tc2, self.managed_ep_id,
                                            GO_EP1_ID, notify_on_fail=False)
            tdata.add_item("/", "/", recursive=True)
            task_ids.append(self.tc2.submit_transfer(tdata)["task_id"])

        # track assets for cleanup
        self.asset_cleanup.append(
            {"function": self.tc.endpoint_manager_cancel_tasks,
             "args": [task_ids, "Cleanup for unauthorized_transfers helper"]})

        return task_ids

    def test_endpoint_manager_cancel_tasks(self):
        """
        Get task ids from _unauthorized transfers, and has sdktester1a cancel
        those tasks. Validates results.
        Confirms 403 when non manager attempts to use this resource.
        """
        # cancel the tasks
        task_ids = self._unauthorized_transfers()
        message = "SDK test cancel tasks"
        cancel_doc = self.tc.endpoint_manager_cancel_tasks(task_ids, message)

        # validate results
        self.assertEqual(cancel_doc["DATA_TYPE"], "admin_cancel")
        self.assertIn("done", cancel_doc)
        self.assertIn("id", cancel_doc)

        # 403 for non managers, even if they submitted the tasks
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc2.endpoint_manager_cancel_tasks(task_ids, message)
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "PermissionDenied")

    def test_endpoint_manager_cancel_status(self):
        """
        Has sdktester2b submit three unauthorized transfers from the managed
        endpoint, and sdktester1a admin_cancel those tasks.
        Gets the cancel status of the cancel and validates results.
        Loops while status is not done, then confirms all tasks canceled.
        """
        # cancel the tasks and get the cancel id
        task_ids = self._unauthorized_transfers()
        message = "SDK test cancel status"
        cancel_id = self.tc.endpoint_manager_cancel_tasks(
            task_ids, message)["id"]

        # loop while not done or fail after 30 tries, 1 try per second
        for tries in range(30):
            # get and validate cancel status
            status_doc = self.tc.endpoint_manager_cancel_status(cancel_id)
            self.assertEqual(status_doc["DATA_TYPE"], "admin_cancel")
            self.assertEqual(status_doc["id"], cancel_id)
            if status_doc["done"]:
                break
            else:
                time.sleep(1)

        # confirm sdktester2b now sees all tasks as canceled by admin.
        for task_id in task_ids:
            task_doc = self.tc2.get_task(task_id)
            self.assertEqual(task_doc["canceled_by_admin"], "SOURCE")
            self.assertEqual(task_doc["canceled_by_admin_message"], message)

    def test_endpoint_manager_pause_tasks(self):
        """
        Has sdktester2b submit three unauthorized transfers,
        and sdktester1a pause the tasks as an admin.
        Validates results and confirms the tasks are paused.
        Confirms 403 when non manager attempts to use this resource.
        """
        # pause the tasks
        task_ids = self._unauthorized_transfers()
        message = "SDK test pause tasks"
        pause_doc = self.tc.endpoint_manager_pause_tasks(task_ids, message)

        # validate results
        self.assertEqual(pause_doc["DATA_TYPE"], "result")
        self.assertEqual(pause_doc["code"], "PauseAccepted")

        # confirm sdktester2b sees the tasks as paused
        for task_id in task_ids:
            task_doc = self.tc2.get_task(task_id)
            self.assertTrue(task_doc["is_paused"])

        # 403 for non managers
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc2.endpoint_manager_pause_tasks(task_ids, message)
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "PermissionDenied")

    def test_endpoint_manager_resume_tasks(self):
        """
        Has sdktester2b submit three unauthorized transfers,
        then sdktester1a pauses then resumes the tasks as an admin.
        Confirms tasks go from paused to active.
        Confirms 403 when non manager attempts to use this resource.
        """
        # pause the tasks and confirm they are paused
        task_ids = self._unauthorized_transfers()
        message = "SDK test resume tasks"
        self.tc.endpoint_manager_pause_tasks(task_ids, message)
        for task_id in task_ids:
            task_doc = self.tc2.get_task(task_id)
            self.assertTrue(task_doc["is_paused"])

        # resume the tasks and validate results
        resume_doc = self.tc.endpoint_manager_resume_tasks(task_ids)
        self.assertEqual(resume_doc["DATA_TYPE"], "result")
        self.assertEqual(resume_doc["code"], "ResumeAccepted")

        # confirm tasks are now active.
        for task_id in task_ids:
            task_doc = self.tc2.get_task(task_id)
            self.assertFalse(task_doc["is_paused"])

        # 403 for non managers
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc2.endpoint_manager_resume_tasks(task_ids)
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "PermissionDenied")

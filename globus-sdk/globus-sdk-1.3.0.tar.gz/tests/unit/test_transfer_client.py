from random import getrandbits

import globus_sdk
from tests.framework import (TransferClientTestCase, get_user_data,
                             GO_EP1_ID, GO_EP2_ID, GO_EP3_ID, GO_S3_ID,
                             GO_EP1_SERVER_ID,

                             DEFAULT_TASK_WAIT_TIMEOUT,
                             DEFAULT_TASK_WAIT_POLLING_INTERVAL)
from globus_sdk.exc import TransferAPIError
from globus_sdk.transfer.paging import PaginatedResource


class TransferClientTests(TransferClientTestCase):
    """
    Transfer client tests that don't require time intensive setUp and tearDown.
    """

    __test__ = True  # marks sub-class as having tests

    def test_get_endpoint(self):
        """
        Gets endpoint on go#ep1 and go#ep2, validate results
        """

        # load the tutorial endpoint documents
        ep1_doc = self.tc.get_endpoint(GO_EP1_ID)
        ep2_doc = self.tc.get_endpoint(GO_EP2_ID)

        # check that their contents are at least basically sane (i.e. we didn't
        # get empty dicts or something)
        self.assertIn("display_name", ep1_doc)
        self.assertIn("display_name", ep2_doc)
        self.assertIn("canonical_name", ep1_doc)
        self.assertIn("canonical_name", ep2_doc)

        # double check the canonical name fields, consider this done
        self.assertEqual(ep1_doc["canonical_name"], "go#ep1")
        self.assertEqual(ep2_doc["canonical_name"], "go#ep2")

    def test_update_endpoint(self):
        """
        Updates test endpoint, validate results,
        repeats with different update data to confirm data is changing
        """

        # update the test endpoint's display name and description
        # name is randomized to prevent collision
        update_data = {"display_name": "Updated-" + str(getrandbits(128)),
                       "description": "Updated description"}
        update_doc = self.tc.update_endpoint(self.test_ep_id, update_data)

        # make sure response is a successful update
        self.assertEqual(update_doc["DATA_TYPE"], "result")
        self.assertEqual(update_doc["code"], "Updated")
        self.assertEqual(update_doc["message"],
                         "Endpoint updated successfully")

        # confirm data matches update
        get_doc = self.tc.get_endpoint(self.test_ep_id)
        self.assertEqual(get_doc["display_name"], update_data["display_name"])
        self.assertEqual(get_doc["description"], update_data["description"])

        # repeat with different data
        update_data2 = {"display_name": "Updated-" + str(getrandbits(128)),
                        "description": "Updated again description"}
        update_doc2 = self.tc.update_endpoint(self.test_ep_id, update_data2)

        # make sure response is a successful update
        self.assertEqual(update_doc["DATA_TYPE"], "result")
        self.assertEqual(update_doc2["code"], "Updated")
        self.assertEqual(update_doc2["message"],
                         "Endpoint updated successfully")

        # confirm data matches update and changed from previous get
        get_doc2 = self.tc.get_endpoint(self.test_ep_id)
        self.assertEqual(get_doc2["display_name"],
                         update_data2["display_name"])
        self.assertEqual(get_doc2["description"], update_data2["description"])

    def test_create_endpoint(self):
        """
        Creates an endpoint, validates results
        """

        # create the endpoint
        create_data = {"display_name": "Test Create-" + str(getrandbits(128))}
        create_doc = self.tc.create_endpoint(create_data)

        # confirm response is a successful creation
        self.assertIn("id", create_doc)
        self.assertEqual(create_doc["DATA_TYPE"], "endpoint_create_result")
        self.assertEqual(create_doc["code"], "Created")
        self.assertEqual(create_doc["message"],
                         "Endpoint created successfully")

        # confirm get works on endpoint and returns expected data
        get_doc = self.tc.get_endpoint(create_doc["id"])
        self.assertEqual(get_doc["display_name"], create_data["display_name"])

        # track asset for cleanup
        self.asset_cleanup.append({"function": self.tc.delete_endpoint,
                                   "args": [create_doc["id"]]})

    def test_delete_endpoint(self):
        """
        Deletes the test endpoint, validates results
        """

        # delete the endpoint
        delete_doc = self.tc.delete_endpoint(self.test_ep_id)

        # confirm response is a successful deletion
        self.assertEqual(delete_doc["DATA_TYPE"], "result")
        self.assertEqual(delete_doc["code"], "Deleted")
        self.assertEqual(delete_doc["message"],
                         "Endpoint deleted successfully")

        # confirm get no longer finds endpoint
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.get_endpoint(self.test_ep_id)
        self.assertEqual(apiErr.exception.http_status, 404)
        self.assertEqual(apiErr.exception.code, "EndpointDeleted")

        # stop tracking endpoint for cleanup
        for cleanup in self.asset_cleanup:
            if "name" in cleanup and cleanup["name"] == "test_ep":
                self.asset_cleanup.remove(cleanup)
                break

    # def test_endpoint_activate(self):
        # TODO: test against an endpoint that uses MyProxy

    def test_endpoint_get_activation_requirements(self):
        """
        Gets activation requirements on tutorial endpoint, validates results
        """
        # get requirements
        reqs_doc = self.tc.endpoint_get_activation_requirements(GO_EP1_ID)

        # validate data fields
        self.assertEqual(reqs_doc["DATA_TYPE"], "activation_requirements")
        self.assertEqual(reqs_doc["DATA"], [])
        self.assertEqual(reqs_doc["expires_in"], -1)
        self.assertIsNone(reqs_doc["expire_time"])
        self.assertIsNone(reqs_doc["oauth_server"])
        self.assertTrue(reqs_doc["auto_activation_supported"])

        # validate ActivationRequirementsResponse properties
        self.assertIsInstance(
            reqs_doc,
            globus_sdk.transfer.response.ActivationRequirementsResponse)
        self.assertTrue(reqs_doc.supports_auto_activation)
        self.assertTrue(reqs_doc.supports_web_activation)
        self.assertTrue(reqs_doc.always_activated)

    def test_create_shared_endpoint(self):
        """
        Creates a shared endpoint, validates results,
        checks existence and sharing status using get
        """

        # create shared endpoint
        # dir and name are randomized to prevent collision
        share_path = "/~/test_share-" + str(getrandbits(128)) + "/"
        self.tc.operation_mkdir(GO_EP1_ID, path=share_path)
        shared_data = {"DATA_TYPE": "shared_endpoint",
                       "host_endpoint": GO_EP1_ID,
                       "host_path": share_path,
                       "display_name":
                       "SDK Test Create Shared Endpoint-"
                       + str(getrandbits(128)),
                       }
        share_doc = self.tc.create_shared_endpoint(shared_data)

        # validate share doc
        self.assertEqual(share_doc["DATA_TYPE"], "endpoint_create_result")
        self.assertEqual(share_doc["code"], "Created")

        # confirm shared endpoint now exists and is hosted from go#ep1
        get_data = self.tc.get_endpoint(share_doc["id"])
        self.assertEqual(get_data["host_endpoint_id"], GO_EP1_ID)
        self.assertEqual(get_data["sharing_target_root_path"], share_path)

        # track assets for cleanup
        self.asset_cleanup.append({"function": self.tc.delete_endpoint,
                                   "args": [share_doc["id"]]})
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP1_ID, share_path]})

    def test_endpoint_server_list(self):
        """
        Gets endpoint server list for go#ep1, validates results
        """

        # get endpoint server list
        list_doc = self.tc.endpoint_server_list(GO_EP1_ID)

        # validate results are a endpoint server list with a DATA field
        self.assertEqual(list_doc["DATA_TYPE"], "endpoint_server_list")
        self.assertIn("DATA", list_doc)
        # validate that data points are servers with an id
        for server in list_doc["DATA"]:
            self.assertEqual(server["DATA_TYPE"], "server")
            self.assertIn("id", server)

    def test_get_endpoint_server(self):
        """
        Gets the go#ep1 server by id, validates results
        """
        # get a server id from the server list
        get_doc = self.tc.get_endpoint_server(GO_EP1_ID, GO_EP1_SERVER_ID)

        # validate data_type and the existence of some expected fields
        self.assertEqual(get_doc["DATA_TYPE"], "server")
        self.assertEqual(get_doc["id"], GO_EP1_SERVER_ID)
        self.assertIn("hostname", get_doc)
        self.assertIn("port", get_doc)

    def test_add_endpoint_server(self):
        """
        Adds a new server with a dummy hostname, validate results
        Returns a server_id for use in testing update and delete
        """

        # add the new server
        add_data = {"hostname": "gridftp.example.org"}
        add_doc = self.tc.add_endpoint_server(self.test_ep_id, add_data)

        # validate results
        self.assertEqual(add_doc["DATA_TYPE"], "endpoint_server_add_result")
        self.assertIn("id", add_doc)
        server_id = add_doc["id"]

        # confirm that get can see the server
        get_doc = self.tc.get_endpoint_server(self.test_ep_id, server_id)
        self.assertEqual(get_doc["id"], server_id)
        self.assertEqual(get_doc["hostname"], add_data["hostname"])

        # return server id
        return server_id

    def test_update_endpoint_server(self):
        """
        Adds a new server, updates server data, validates results,
        then confirms get returns the updated data
        """

        # add the new server
        server_id = self.test_add_endpoint_server()

        # update the server's hostname and port
        update_data = {"hostname": "gridftp.updated.org",
                       "port": 2812}
        update_doc = self.tc.update_endpoint_server(self.test_ep_id, server_id,
                                                    update_data)

        # validate results
        self.assertEqual(update_doc["DATA_TYPE"], "result")
        self.assertEqual(update_doc["code"], "Updated")
        self.assertEqual(update_doc["message"], "Server updated successfully")

        # confirm get returns the new data
        get_doc = self.tc.get_endpoint_server(self.test_ep_id, server_id)
        self.assertEqual(get_doc["hostname"], update_data["hostname"])
        self.assertEqual(get_doc["port"], update_data["port"])

    def test_delete_endpoint_server(self):
        """
        Adds a new server, deletes it, validates results,
        then confirms get can no longer see the server
        """

        # add the new server
        server_id = self.test_add_endpoint_server()

        # delete the server data
        delete_doc = self.tc.delete_endpoint_server(self.test_ep_id, server_id)

        # validate results
        self.assertEqual(delete_doc["DATA_TYPE"], "result")
        self.assertEqual(delete_doc["code"], "Deleted")
        self.assertEqual(delete_doc["message"], "Server deleted successfully")

        # confirm get can no longer see the server data
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.get_endpoint_server(self.test_ep_id, server_id)
        self.assertEqual(apiErr.exception.http_status, 404)
        self.assertEqual(apiErr.exception.code,
                         "ClientError.NotFound.ServerNotFound")

    def test_endpoint_role_list(self):
        """
        Gets the endpoint role list from the test endpoint, validates results
        """

        # get endpoint role list
        list_doc = self.tc.endpoint_role_list(self.test_ep_id)

        # validate data type
        self.assertEqual(list_doc["DATA_TYPE"], "role_list")
        self.assertIn("DATA", list_doc)
        # confirm that each role has the expected values
        for role in list_doc["DATA"]:
            self.assertEqual(role["DATA_TYPE"], "role")
            self.assertIn("id", role)
            self.assertIn("principal_type", role)
            self.assertIn("principal", role)
            self.assertIn("role", role)

    def test_bookmark_list(self):
        """
        Gets SDK user's bookmark list, validates results
        """

        # get bookmark list
        list_doc = self.tc.bookmark_list()

        # validate results
        self.assertEqual(list_doc["DATA_TYPE"], "bookmark_list")
        self.assertIn("DATA", list_doc)
        # confirm that each bookmark in the list has expected fields
        for bookmark in list_doc["DATA"]:
            self.assertEqual(bookmark["DATA_TYPE"], "bookmark")
            self.assertIn("id", bookmark)
            self.assertIn("name", bookmark)
            self.assertIn("endpoint_id", bookmark)
            self.assertIn("path", bookmark)

    def test_create_bookmark(self):
        """
        Creates a bookmark, validates results, confirms get sees bookmark,
        returns bookmark_id for use in testing get update and delete
        """

        # create bookmark, name is randomized to prevent collision
        bookmark_data = {"name": "SDK Test Bookmark-" + str(getrandbits(128)),
                         "endpoint_id": GO_EP1_ID,
                         "path": "/~/"}
        create_doc = self.tc.create_bookmark(bookmark_data)

        # validate results
        self.assertEqual(create_doc["DATA_TYPE"], "bookmark")
        self.assertIn("id", create_doc)
        for item in bookmark_data:
            self.assertEqual(create_doc[item], bookmark_data[item])

        # confirm get sees created bookmark
        bookmark_id = create_doc["id"]
        get_doc = self.tc.get_bookmark(bookmark_id)
        self.assertEqual(get_doc["DATA_TYPE"], "bookmark")
        self.assertEqual(get_doc["id"], bookmark_id)
        for item in bookmark_data:
            self.assertEqual(get_doc[item], bookmark_data[item])

        # track asset for cleanup
        self.asset_cleanup.append({"function": self.tc.delete_bookmark,
                                   "args": [bookmark_id],
                                   "name": "test_bookmark"})  # for removal

        # return bookmark_id
        return bookmark_id

    def test_get_bookmark(self):
        """
        Creates a bookmark, gets it, validates results
        """

        # get bookmark from test_create_bookmark
        bookmark_id = self.test_create_bookmark()

        # get bookmark
        get_doc = self.tc.get_bookmark(bookmark_id)

        # validate results
        self.assertEqual(get_doc["DATA_TYPE"], "bookmark")
        self.assertEqual(get_doc["id"], bookmark_id)
        self.assertIn("name", get_doc)
        self.assertIn("endpoint_id", get_doc)
        self.assertIn("path", get_doc)

    def test_update_bookmark(self):
        """
        Creates a bookmark, updates it, validates results,
        then confirms get sees the updated data
        """

        # get bookmark from test_create_bookmark
        bookmark_id = self.test_create_bookmark()

        # update bookmark name, randomized to prevent collision
        update_data = {"name":
                       "Updated SDK Test Bookmark-" + str(getrandbits(128))}
        update_doc = self.tc.update_bookmark(bookmark_id, update_data)

        # validate results
        self.assertEqual(update_doc["DATA_TYPE"], "bookmark")
        self.assertEqual(update_doc["id"], bookmark_id)
        self.assertEqual(update_doc["name"], update_data["name"])

        # confirm get sees new name
        get_doc = self.tc.get_bookmark(bookmark_id)
        self.assertEqual(get_doc["name"], update_data["name"])

    def test_delete_bookmark(self):
        """
        Creates a bookmark, deletes it, validates results,
        then confirms get no longer sees the bookmark
        """

        # get bookmark from test_create_bookmark
        bookmark_id = self.test_create_bookmark()

        # delete bookmark
        delete_doc = self.tc.delete_bookmark(bookmark_id)

        # validate results
        self.assertEqual(delete_doc["DATA_TYPE"], "result")
        self.assertEqual(delete_doc["code"], "Deleted")
        self.assertIn("deleted successfully", delete_doc["message"])

        # confirm get no longer sees bookmark
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.get_bookmark(bookmark_id)
        self.assertEqual(apiErr.exception.http_status, 404)
        self.assertEqual(apiErr.exception.code, "BookmarkNotFound")

        # stop tracking asset for deletion
        for cleanup in self.asset_cleanup:
            if "name" in cleanup and cleanup["name"] == "test_bookmark":
                self.asset_cleanup.remove(cleanup)
                break

    def test_operation_ls(self):
        """
        Performs ls operations on go#ep1, tests path, show_hidden, limit,
        and filter params, validates results and confirms behavior,
        """

        # perform ls operation without params
        ls_doc = self.tc.operation_ls(GO_EP1_ID)
        # validate results
        self.assertEqual(ls_doc["DATA_TYPE"], "file_list")
        self.assertEqual(ls_doc["endpoint"], GO_EP1_ID)
        self.assertEqual(ls_doc["path"], "/~/")  # default path
        self.assertIn("DATA", ls_doc)

        # perform ls operation with path param
        path = "/share/godata/"
        path_params = {"path": path}
        path_doc = self.tc.operation_ls(GO_EP1_ID, **path_params)
        # validate results
        self.assertEqual(path_doc["DATA_TYPE"], "file_list")
        self.assertEqual(path_doc["endpoint"], GO_EP1_ID)
        self.assertEqual(path_doc["path"], path)
        self.assertIn("DATA", path_doc)
        # confirm the three text files are found as expected
        for item in path_doc["DATA"]:
            self.assertEqual(item["DATA_TYPE"], "file")
            self.assertIn(".txt", item["name"])
            self.assertIn("size", item)
            self.assertIn("permissions", item)

        # perform ls operation show_hidden param set to false
        hidden_params = {"show_hidden": False}
        hidden_doc = self.tc.operation_ls(GO_EP1_ID, **hidden_params)
        # validate results
        self.assertEqual(hidden_doc["DATA_TYPE"], "file_list")
        self.assertEqual(hidden_doc["endpoint"], GO_EP1_ID)
        self.assertIn("DATA", hidden_doc)
        # confirm no hidden files were returned
        for item in hidden_doc["DATA"]:
            self.assertFalse(item["name"][0] == ".")

        # perform ls operation with limit param
        limit = 1
        limit_params = {"path": path, "limit": limit}
        limit_doc = self.tc.operation_ls(GO_EP1_ID, **limit_params)
        # validate results
        self.assertEqual(limit_doc["DATA_TYPE"], "file_list")
        self.assertEqual(limit_doc["endpoint"], GO_EP1_ID)
        self.assertEqual(limit_doc["path"], path)
        # confirm only one of the three files was returned
        self.assertEqual(limit_doc["length"], limit)
        file_count = 0
        for item in limit_doc:
            file_count += 1
        self.assertEqual(file_count, limit)

        # perform ls operation with filter param
        file_name = "file3.txt"
        min_size = 5
        filter_string = "name:" + file_name + "/size:>" + str(min_size)
        filter_params = {"filter": filter_string, "path": path}
        filter_doc = self.tc.operation_ls(GO_EP1_ID, **filter_params)
        # validate results
        self.assertEqual(filter_doc["DATA_TYPE"], "file_list")
        self.assertEqual(filter_doc["endpoint"], GO_EP1_ID)
        self.assertEqual(filter_doc["path"], path)
        # confirm only file 3 was returned
        file_data = filter_doc["DATA"][0]
        self.assertEqual(file_data["name"], file_name)
        self.assertTrue(file_data["size"] > min_size)

    def test_operation_mkdir(self):
        """
        Performs mkdir operation in go#ep1/~/, validates results,
        confirms ls sees the new directory
        """

        # perform mkdir operation, name randomized to prevent collision
        dir_name = "test_dir-" + str(getrandbits(128))
        path = "/~/" + dir_name
        mkdir_doc = self.tc.operation_mkdir(GO_EP1_ID, path)

        # validate results
        self.assertEqual(mkdir_doc["DATA_TYPE"], "mkdir_result")
        self.assertEqual(mkdir_doc["code"], "DirectoryCreated")
        self.assertEqual(mkdir_doc["message"],
                         "The directory was created successfully")

        # confirm ls now sees the dir
        filter_string = "name:" + dir_name
        params = {"filter": filter_string}
        ls_doc = self.tc.operation_ls(GO_EP1_ID, **params)
        self.assertNotEqual(ls_doc["DATA"], [])

        # track asset for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP1_ID, path]})

    def test_operation_rename(self):
        """
        Performs mkdir operation, renames the directory,
        confirms ls sees the new directory and not the old one.
        """

        # perform mkdir operation, name randomized to prevent collision
        old_name = "old_dir-" + str(getrandbits(128))
        old_path = "/~/" + old_name
        self.tc.operation_mkdir(GO_EP1_ID, old_path)

        # rename the directory, name randomized to prevent collision
        new_name = "new_dir-" + str(getrandbits(128))
        new_path = "/~/" + new_name
        rename_doc = self.tc.operation_rename(GO_EP1_ID, old_path, new_path)

        # validate results
        self.assertEqual(rename_doc["DATA_TYPE"], "result")
        self.assertEqual(rename_doc["code"], "FileRenamed")
        self.assertEqual(rename_doc["message"],
                         "File or directory renamed successfully")

        # confirm ls sees new directory
        filter_string = "name:" + new_name
        params = {"filter": filter_string}
        ls_doc = self.tc.operation_ls(GO_EP1_ID, **params)
        self.assertNotEqual(ls_doc["DATA"], [])

        # confirm ls does not see old directory
        filter_string = "name:" + old_name
        params = {"filter": filter_string}
        ls_doc = self.tc.operation_ls(GO_EP1_ID, **params)
        self.assertEqual(ls_doc["DATA"], [])

        # track asset for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP1_ID, new_path]})

    def test_operation_symlink(self):
        """
        Performs operation symlink creating valid and invalid symlinks
        Confirms ls sees the symlinks target_paths and types correctly
        Confirms non supporting endpoints raise 409
        """
        # perform operation_symlink with a valid target_path
        # symlink path randomized to prevent collision
        valid_target = "/share/godata/"
        valid_name = "godata_symlink-" + str(getrandbits(128))
        valid_path = "~/" + valid_name
        self.tc.operation_symlink(GO_EP3_ID, valid_target, valid_path)
        # track asset for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP3_ID, valid_path]})

        # confirm ls sees valid symlink
        filter_string = "name:" + valid_name
        item = self.tc.operation_ls(GO_EP3_ID, filter=filter_string)["DATA"][0]
        self.assertEqual(item["type"], "dir")
        self.assertEqual(item["link_target"], valid_target)

        # perform operation symlink with an invalid target_path
        invalid_target = "/invalid/target/"
        invalid_name = "invalid_symlink-" + str(getrandbits(128))
        invalid_path = "~/" + invalid_name
        self.tc.operation_symlink(GO_EP3_ID, invalid_target, invalid_path)
        # track asset for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP3_ID, invalid_path]})

        # confirm ls sees invalid symlink
        filter_string = "name:" + invalid_name
        item = self.tc.operation_ls(GO_EP3_ID, filter=filter_string)["DATA"][0]
        self.assertEqual(item["type"], "invalid_symlink")
        self.assertEqual(item["link_target"], invalid_target)

        # confirm endpoints not supporting symlinks raise 409 NotSupported
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.operation_symlink(GO_S3_ID, valid_target, valid_path)
        self.assertEqual(apiErr.exception.http_status, 409)
        self.assertEqual(apiErr.exception.code, "NotSupported")

    def test_operation_get_submission_id(self):
        """
        Gets a submission_id, validates results, checks UUID looks reasonable
        """

        # get submission id
        sub_doc = self.tc.get_submission_id()

        # validate results
        self.assertEqual(sub_doc["DATA_TYPE"], "submission_id")
        self.assertIn("value", sub_doc)

        # check that the UUID is in the right format
        uuid = sub_doc["value"]
        self.assertEqual(len(uuid), 36)
        self.assertEqual(uuid[8], "-")
        self.assertEqual(uuid[13], "-")
        self.assertEqual(uuid[18], "-")
        self.assertEqual(uuid[23], "-")

    def test_submit_transfer(self):
        """
        Submits transfer requests, validates results, confirms tasks completed
        tests recursive and submission_id parameters
        """
        # dir for testing transfers in, name randomized to prevent collision
        dest_dir = "transfer_dest_dir-" + str(getrandbits(128))
        dest_path = "/~/" + dest_dir + "/"
        self.tc.operation_mkdir(GO_EP1_ID, dest_path)
        # track asset for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP1_ID, dest_path]})

        # individual file and recursive dir transfer
        source_path = "/share/godata/"
        kwargs = {"notify_on_succeeded": False}  # prevent email spam
        tdata = globus_sdk.TransferData(self.tc, GO_EP2_ID,
                                        GO_EP1_ID, **kwargs)
        # individual
        file_name = "file1.txt"
        dir_name = "godata"
        tdata.add_item(source_path + file_name, dest_path + file_name)
        # recursive into a new data dir
        tdata.add_item(source_path, dest_path + dir_name, recursive=True)
        # send the request
        transfer_doc = self.tc.submit_transfer(tdata)

        # validate results
        self.assertEqual(transfer_doc["DATA_TYPE"], "transfer_result")
        self.assertEqual(transfer_doc["code"], "Accepted")
        self.assertIn("task_id", transfer_doc)
        self.assertIn("submission_id", transfer_doc)

        # confirm the task completed and the files were transfered
        task_id = transfer_doc["task_id"]
        self.assertTrue(
            self.tc.task_wait(
                task_id, timeout=DEFAULT_TASK_WAIT_TIMEOUT,
                polling_interval=DEFAULT_TASK_WAIT_POLLING_INTERVAL))
        # confirm file and dir are visible by ls
        filter_string = "name:" + file_name + "," + dir_name
        params = {"path": dest_path, "filter": filter_string}
        ls_doc = self.tc.operation_ls(GO_EP1_ID, **params)
        self.assertEqual(len(ls_doc["DATA"]), 2)
        # confirm 3 .txt files are found in dir
        filter_string = "name:~*.txt"
        params = {"path": dest_path + dir_name, "filter": filter_string}
        ls_doc = self.tc.operation_ls(GO_EP1_ID, **params)
        self.assertEqual(len(ls_doc["DATA"]), 3)

        # test submission_id parameter
        sub_id = self.tc.get_submission_id()["value"]

        # confirm first submission is normal
        sub_tdata = globus_sdk.TransferData(self.tc, GO_EP2_ID, GO_EP1_ID,
                                            submission_id=sub_id, **kwargs)
        sub_tdata.add_item(source_path + file_name, dest_path + file_name)
        sub_transfer_doc = self.tc.submit_transfer(sub_tdata)
        # validate results
        self.assertEqual(sub_transfer_doc["DATA_TYPE"], "transfer_result")
        self.assertEqual(sub_transfer_doc["code"], "Accepted")
        self.assertEqual(sub_transfer_doc["submission_id"], sub_id)
        self.assertIn("task_id", sub_transfer_doc)
        sub_task_id = sub_transfer_doc["task_id"]

        # confirm re-using submission_id returns a Duplicate response
        resub_tdata = globus_sdk.TransferData(self.tc, GO_EP2_ID, GO_EP1_ID,
                                              submission_id=sub_id, **kwargs)
        resub_tdata.add_item(source_path + file_name, dest_path + file_name)
        resub_transfer_doc = self.tc.submit_transfer(resub_tdata)
        self.assertEqual(resub_transfer_doc["DATA_TYPE"], "transfer_result")
        self.assertEqual(resub_transfer_doc["code"], "Duplicate")
        self.assertEqual(resub_transfer_doc["submission_id"], sub_id)
        self.assertEqual(resub_transfer_doc["task_id"], sub_task_id)

        # wait for submission to finish before moving on to cleanup
        self.assertTrue(self.tc.task_wait(
            sub_transfer_doc["task_id"],
            timeout=DEFAULT_TASK_WAIT_TIMEOUT,
            polling_interval=DEFAULT_TASK_WAIT_POLLING_INTERVAL))

    def test_submit_transfer_keep_recursive_symlinks(self):
        """
        Submits transfer tasks from go#ep3:/share/symlinks/good/
        with recursive_symlinks set to "keep"
        Confirms symlinks are kept as symlinks at the destination.
        """
        # dir for testing transfers to, name randomized to prevent collision
        keep_dir = "keep_symlink_dest_dir-" + str(getrandbits(128))
        keep_path = "/~/" + keep_dir + "/"
        self.tc.operation_mkdir(GO_EP3_ID, keep_path)
        # track asset for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP3_ID, keep_path]})

        # transfer from /share/symlink/good to keep_dir
        tdata = globus_sdk.TransferData(self.tc, GO_EP3_ID, GO_EP3_ID,
                                        recursive_symlinks="keep")
        tdata.add_item("/share/symlinks/good/", keep_path, recursive=True)
        task_id = self.tc.submit_transfer(tdata)["task_id"]

        # confirm the symlinks are kept as symlinks
        self.assertTrue(
            self.tc.task_wait(
                task_id, timeout=DEFAULT_TASK_WAIT_TIMEOUT,
                polling_interval=DEFAULT_TASK_WAIT_POLLING_INTERVAL))
        ls_doc = self.tc.operation_ls(GO_EP3_ID, path=keep_path)
        self.assertEqual(len(ls_doc["DATA"]), 4)
        for item in ls_doc:
            self.assertIsNotNone(item["link_target"])

    def test_submit_transfer_copy_recursive_symlinks(self):
        """
        Submits transfer tasks from go#ep3:/share/symlinks/good/
        with recursive_symlinks set to "copy"
        Confirms symlinks are kept as symlinks at the destination.
        """
        # dir for testing transfers to, name randomized to prevent collision
        copy_dir = "copy_symlink_dest_dir-" + str(getrandbits(128))
        copy_path = "/~/" + copy_dir + "/"
        self.tc.operation_mkdir(GO_EP3_ID, copy_path)
        # track asset for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP3_ID, copy_path]})

        # transfer from /share/symlink/good to copy_dir
        tdata = globus_sdk.TransferData(self.tc, GO_EP3_ID, GO_EP3_ID,
                                        recursive_symlinks="copy")
        tdata.add_item("/share/symlinks/good/", copy_path, recursive=True)
        task_id = self.tc.submit_transfer(tdata)["task_id"]

        # confirm the symlinks have their targets copied
        self.assertTrue(
            self.tc.task_wait(
                task_id, timeout=DEFAULT_TASK_WAIT_TIMEOUT,
                polling_interval=DEFAULT_TASK_WAIT_POLLING_INTERVAL))
        ls_doc = self.tc.operation_ls(GO_EP3_ID, path=copy_path)
        self.assertEqual(len(ls_doc["DATA"]), 4)
        for item in ls_doc:
            self.assertIsNone(item["link_target"])

    def test_submit_transfer_ignore_recursive_symlinks(self):
        # dir for testing transfers to, name randomized to prevent collision
        ignore_dir = "ignore_symlink_dest_dir-" + str(getrandbits(128))
        ignore_path = "/~/" + ignore_dir + "/"
        self.tc.operation_mkdir(GO_EP3_ID, ignore_path)
        # track asset for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP3_ID, ignore_path]})

        # transfer from /share/symlink/good to ignore_dir
        tdata = globus_sdk.TransferData(self.tc, GO_EP3_ID, GO_EP3_ID,
                                        recursive_symlinks="ignore")
        tdata.add_item("/share/symlinks/good/", ignore_path, recursive=True)
        task_id = self.tc.submit_transfer(tdata)["task_id"]

        # confirm the symlinks have their targets copied
        self.assertTrue(
            self.tc.task_wait(
                task_id, timeout=DEFAULT_TASK_WAIT_TIMEOUT,
                polling_interval=DEFAULT_TASK_WAIT_POLLING_INTERVAL))
        ls_doc = self.tc.operation_ls(GO_EP3_ID, path=ignore_path)
        self.assertEqual(len(ls_doc["DATA"]), 0)

    def test_submit_transfer_symlink(self):
        """
        Transfers a symlink on go#ep3:/share/symlinks/good to go#ep3:~/
        As a transfer_symlink_item and as a transfer_item
        Confirms the symlink and the target are transfered as expected.
        """
        # transfer /share/symlink/good/file1.txt link \u2764
        tdata = globus_sdk.TransferData(self.tc, GO_EP3_ID, GO_EP3_ID)
        source_path = u"/share/symlinks/good/file1.txt link \u2764"

        # add a transfer_symlink_item
        link_name = "link-" + str(getrandbits(128))
        link_dest = "~/" + link_name
        tdata.add_symlink_item(source_path, link_dest)
        # add a transfer_item
        file_name = "file-" + str(getrandbits(128))
        file_dest = "~/" + file_name
        tdata.add_item(source_path, file_dest)

        # submit the task
        task_id = self.tc.submit_transfer(tdata)["task_id"]
        self.assertTrue(
            self.tc.task_wait(
                task_id, timeout=DEFAULT_TASK_WAIT_TIMEOUT,
                polling_interval=DEFAULT_TASK_WAIT_POLLING_INTERVAL))
        # track assets for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP1_ID, link_dest]})
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP1_ID, file_dest]})

        # confirm the transfer_symlink_item transfered the symlink
        ls_doc = self.tc.operation_ls(GO_EP3_ID, filter="name:" + link_name)
        self.assertEqual(ls_doc["DATA"][0]["link_target"],
                         "/share/godata/file1.txt")
        # confirm the transfer_item transfered the target
        ls_doc = self.tc.operation_ls(GO_EP3_ID, filter="name:" + file_name)
        self.assertIsNone(ls_doc["DATA"][0]["link_target"])

    def test_submit_delete(self):
        """
        Transfers a file and makes a dir in go#ep1, then deletes them,
        validates results and that the items are no longer visible by ls
        Confirms resubmission using the same data returns a Duplicate response
        """

        # dir for testing deletes in, name randomized to prevent collision
        dest_dir = "delete_dest_dir-" + str(getrandbits(128))
        dest_path = "/~/" + dest_dir + "/"
        self.tc.operation_mkdir(GO_EP1_ID, dest_path)
        # track asset for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP1_ID, dest_path]})

        # transfer file into go#ep1/~/dir_name
        source_path = "/share/godata/"
        kwargs = {"notify_on_succeeded": False}  # prevent email spam
        tdata = globus_sdk.TransferData(self.tc, GO_EP2_ID,
                                        GO_EP1_ID, **kwargs)
        file_name = "file1.txt"
        tdata.add_item(source_path + file_name, dest_path + file_name)
        transfer_doc = self.tc.submit_transfer(tdata)

        # make a dir to delete
        dir_name = "test_dir"
        path = dest_path + dir_name
        self.tc.operation_mkdir(GO_EP1_ID, path)

        # wait for transfer to complete
        self.assertTrue(self.tc.task_wait(
            transfer_doc["task_id"],
            timeout=DEFAULT_TASK_WAIT_TIMEOUT,
            polling_interval=DEFAULT_TASK_WAIT_POLLING_INTERVAL))

        # delete the items
        ddata = globus_sdk.DeleteData(self.tc, GO_EP1_ID,
                                      recursive=True, **kwargs)
        ddata.add_item(dest_path + file_name)
        ddata.add_item(dest_path + dir_name)
        delete_doc = self.tc.submit_delete(ddata)

        # validate results
        self.assertEqual(delete_doc["DATA_TYPE"], "delete_result")
        self.assertEqual(delete_doc["code"], "Accepted")
        self.assertIn("task_id", delete_doc)
        self.assertIn("submission_id", delete_doc)
        task_id = delete_doc["task_id"]
        sub_id = delete_doc["submission_id"]

        # confirm the task completed and the files were deleted
        # wait for transfer to complete
        self.assertTrue(self.tc.task_wait(
            task_id, timeout=DEFAULT_TASK_WAIT_TIMEOUT,
            polling_interval=DEFAULT_TASK_WAIT_POLLING_INTERVAL))
        # confirm file and dir are no longer visible by ls
        filter_string = "name:" + file_name + "," + dir_name
        params = {"path": dest_path, "filter": filter_string}
        ls_doc = self.tc.operation_ls(GO_EP1_ID, **params)
        self.assertEqual(ls_doc["DATA"], [])

        # confirm re-submission of ddata returns Duplicate response
        resub_delete_doc = self.tc.submit_delete(ddata)
        self.assertEqual(resub_delete_doc["DATA_TYPE"], "delete_result")
        self.assertEqual(resub_delete_doc["code"], "Duplicate")
        self.assertEqual(resub_delete_doc["submission_id"], sub_id)
        self.assertEqual(resub_delete_doc["task_id"], task_id)

    def test_task_list(self):
        """
        Gets task list, validates results, tests num_results and filter params
        """

        # get task list
        list_doc = self.tc.task_list()

        # validate results are in the right format
        self.assertIsInstance(list_doc, PaginatedResource)
        # validate tasks have some expected fields
        for task in list_doc:
            self.assertEqual(task["DATA_TYPE"], "task")
            self.assertEqual(task["owner_id"],
                             get_user_data()["sdktester1a"]["id"])
            self.assertIn("task_id", task)
            self.assertIn("type", task)
            self.assertIn("status", task)

        # test num_results param, assumes SDK tester has run at least 20 tasks
        cap = 20
        num_doc = self.tc.task_list(num_results=cap)
        # confirm results were capped
        count = 0
        for task in num_doc:
            count += 1
        self.assertEqual(count, cap)

        # test filter param
        params = {"filter": "type:DELETE/status:SUCCEEDED"}
        filter_doc = self.tc.task_list(**params)
        # validate only Successful Delete tasks were returned
        for task in filter_doc:
            self.assertEqual(task["type"], "DELETE")
            self.assertEqual(task["status"], "SUCCEEDED")

    def test_task_event_list(self):
        """
        Gets the task event list for a completed transfer,
        validates results, tests filter param
        """

        # get the task event list for a completed transfer
        task_id = self.test_get_task()
        list_doc = self.tc.task_event_list(task_id)

        # validate results
        self.assertIsInstance(list_doc, PaginatedResource)
        for event in list_doc:
            self.assertEqual(event["DATA_TYPE"], "event")
            self.assertIn("is_error", event)
            self.assertIn("code", event)
            self.assertIn("time", event)

        # test filter param
        params = {"filter": "is_error:1"}
        filter_doc = self.tc.task_event_list(task_id, **params)
        for event in filter_doc:
            self.assertEqual(event["is_error"], True)

    def test_get_task(self):
        """
        Submits a transfer, waits for transfer to complete, gets transfer task
        validates results
        returns the task_id for use in other test functions
        """

        # dir the test transfer, name randomized to prevent collision
        dest_dir = "get_task_dest_dir-" + str(getrandbits(128))
        dest_path = "/~/" + dest_dir + "/"
        self.tc.operation_mkdir(GO_EP1_ID, dest_path)
        # track asset for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP1_ID, dest_path]})

        # submit transfer task
        source_path = "/share/godata/"
        kwargs = {"notify_on_succeeded": False}  # prevent email spam
        tdata = globus_sdk.TransferData(self.tc, GO_EP2_ID,
                                        GO_EP1_ID, **kwargs)
        file_name = "file1.txt"
        tdata.add_item(source_path + file_name, dest_path + file_name)
        transfer_doc = self.tc.submit_transfer(tdata)

        # wait for task to complete
        task_id = transfer_doc["task_id"]
        self.assertTrue(self.tc.task_wait(
            task_id, timeout=DEFAULT_TASK_WAIT_TIMEOUT,
            polling_interval=DEFAULT_TASK_WAIT_POLLING_INTERVAL))

        # get the task by id
        get_doc = self.tc.get_task(task_id)
        self.assertEqual(get_doc["DATA_TYPE"], "task")
        self.assertEqual(get_doc["task_id"], task_id)
        self.assertEqual(get_doc["owner_id"],
                         get_user_data()["sdktester1a"]["id"])
        self.assertEqual(get_doc["type"], "TRANSFER")
        self.assertIn("status", get_doc)

        # return task_id
        return task_id

    def test_update_task(self):
        """
        Submits an un-allowed transfer task, updates task, validates results,
        confirms a conflict error when trying to update a completed task
        """

        # submit an un-allowed transfer task
        source_path = "/share/godata/"
        dest_path = "/share/godata/"
        kwargs = {"notify_on_succeeded": False, "notify_on_fail": False,
                  "notify_on_inactive": False}  # prevent email spam
        tdata = globus_sdk.TransferData(self.tc, GO_EP2_ID,
                                        GO_EP1_ID, **kwargs)
        file_name = "file1.txt"
        tdata.add_item(source_path + file_name, dest_path + file_name)
        transfer_doc = self.tc.submit_transfer(tdata)
        task_id = transfer_doc["task_id"]

        # update task, deadline is in the past for automatic cleanup
        update_data = {"DATA_TYPE": "task", "label": "updated",
                       "deadline": "2000-01-01 00:00:06+00:00"}
        update_doc = self.tc.update_task(task_id, update_data)

        # validate results
        self.assertEqual(update_doc["DATA_TYPE"], "result")
        self.assertEqual(update_doc["code"], "Updated")
        self.assertEqual(update_doc["message"],
                         "Updated task deadline and label successfully")

        # confirm a conflict error when updating a completed task
        completed_id = self.test_get_task()
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.update_task(completed_id, update_data)
        self.assertEqual(apiErr.exception.http_status, 409)
        self.assertEqual(apiErr.exception.code, "Conflict")

    def test_cancel_task(self):
        """
        Submits an un-allowed transfer task, cancels task, validates results,
        confirms a complete task is seen as such and returns correct code
        """

        # submit an un-allowed transfer task
        source_path = "/share/godata/"
        dest_path = "/share/godata/"
        kwargs = {"notify_on_succeeded": False, "notify_on_fail": False,
                  "notify_on_inactive": False}  # prevent email spam
        tdata = globus_sdk.TransferData(self.tc, GO_EP2_ID,
                                        GO_EP1_ID, **kwargs)
        file_name = "file1.txt"
        tdata.add_item(source_path + file_name, dest_path + file_name)
        transfer_doc = self.tc.submit_transfer(tdata)
        task_id = transfer_doc["task_id"]

        # cancel task
        cancel_doc = self.tc.cancel_task(task_id)

        # validate results
        self.assertEqual(cancel_doc["DATA_TYPE"], "result")
        self.assertEqual(cancel_doc["code"], "Canceled")
        self.assertEqual(cancel_doc["message"],
                         "The task has been cancelled successfully.")

        # confirm a conflict error when updating a completed task
        complete_id = self.test_get_task()
        complete_doc = self.tc.cancel_task(complete_id)
        self.assertEqual(complete_doc["DATA_TYPE"], "result")
        self.assertEqual(complete_doc["code"], "TaskComplete")
        self.assertEqual(
            complete_doc["message"],
            "The task completed before the cancel request was processed.")

    def test_task_wait(self):
        """
        Waits on complete, and never completing tasks, confirms results
        """

        # complete
        complete_id = self.test_get_task()
        self.assertTrue(self.tc.task_wait(complete_id, timeout=1))

        # never completing
        source_path = "/share/godata/"
        dest_path = "/share/godata/"
        kwargs = {"notify_on_succeeded": False, "notify_on_fail": False,
                  "notify_on_inactive": False}  # prevent email spam
        tdata = globus_sdk.TransferData(self.tc, GO_EP2_ID,
                                        GO_EP1_ID, **kwargs)
        file_name = "file1.txt"
        tdata.add_item(source_path + file_name, dest_path + file_name)
        transfer_doc = self.tc.submit_transfer(tdata)
        never_id = transfer_doc["task_id"]

        self.assertFalse(self.tc.task_wait(never_id, timeout=1))

        # track asset for cleanup
        self.asset_cleanup.append({"function": self.tc.cancel_task,
                                   "args": [never_id]})

    def test_task_successful_transfers(self):
        """
        Gets the successful transfers from a completed task, validates results
        """

        # get successful transfer info
        task_id = self.test_get_task()
        transfers_doc = self.tc.task_successful_transfers(task_id)

        # validate results
        self.assertIsInstance(transfers_doc, PaginatedResource)
        for success in transfers_doc:
            self.assertEqual(success["DATA_TYPE"], "successful_transfer")
            self.assertIn("source_path", success)
            self.assertIn("destination_path", success)

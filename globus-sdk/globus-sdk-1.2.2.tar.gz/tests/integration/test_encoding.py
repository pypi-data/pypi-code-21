# -*- coding: utf8 -*-
import unittest
import six
from random import getrandbits

import globus_sdk
from tests.framework import (
    TransferClientTestCase, GO_EP1_ID,
    DEFAULT_TASK_WAIT_TIMEOUT, DEFAULT_TASK_WAIT_POLLING_INTERVAL)


class EncodingTests(TransferClientTestCase):

    __test__ = True  # marks sub-class as having tests

    def dir_operations(self, input_name, expected_name=None):
        """
        Given an input directory name, makes, renames, and ls's that directory
        transfers files into that directory, and deletes the directory.
        If an expected_name is given, confirms output matches that name
        rather than the input_name.
        """
        # mkdir
        # name randomized to prevent collision
        rand = str(getrandbits(128))
        path = "/~/" + input_name + rand
        mkdir_doc = self.tc.operation_mkdir(GO_EP1_ID, path)
        self.assertEqual(mkdir_doc["code"], "DirectoryCreated")
        # confirm ls sees dir
        ls_doc = self.tc.operation_ls(GO_EP1_ID, path="/~/")
        expected = (expected_name or input_name) + rand
        self.assertIn(expected, [x["name"] for x in ls_doc])

        # rename
        new_rand = str(getrandbits(128))
        new_path = "/~/" + input_name + new_rand
        rename_doc = self.tc.operation_rename(GO_EP1_ID, path, new_path)
        self.assertEqual(rename_doc["code"], "FileRenamed")
        # confirm ls sees new dir name
        expected = (expected_name or input_name) + new_rand
        ls_doc = self.tc.operation_ls(GO_EP1_ID, path="/~/")
        self.assertIn(expected, [x["name"] for x in ls_doc])

        # transfer
        source_path = "/share/godata/"
        tdata = globus_sdk.TransferData(self.tc, GO_EP1_ID, GO_EP1_ID)
        tdata.add_item(source_path, new_path, recursive=True)
        transfer_id = self.tc.submit_transfer(tdata)["task_id"]
        self.assertTrue(
            self.tc.task_wait(
                transfer_id, timeout=DEFAULT_TASK_WAIT_TIMEOUT,
                polling_interval=DEFAULT_TASK_WAIT_POLLING_INTERVAL))
        # confirm ls sees files inside the directory
        ls_doc = self.tc.operation_ls(GO_EP1_ID, path=new_path)
        expected = ["file1.txt", "file2.txt", "file3.txt"]
        self.assertEqual(expected, [x["name"] for x in ls_doc])

        # delete
        ddata = globus_sdk.DeleteData(self.tc, GO_EP1_ID, recursive=True)
        ddata.add_item(new_path)
        delete_doc = self.tc.submit_delete(ddata)
        self.assertEqual(delete_doc["code"], "Accepted")

    def ep_operations(self, input_name, expected_name=None):
        """
        Given an input_name, creates, updates, gets, and deletes an endpoint
        using the input_name as a display_name. If an expected_name is given,
        confirms output matches that name rather than the input_name.
        """
        # create
        create_data = {"display_name": input_name}
        create_doc = self.tc.create_endpoint(create_data)
        self.assertEqual(create_doc["code"], "Created")
        ep_id = create_doc["id"]
        # confirm get sees ep
        get_doc = self.tc.get_endpoint(ep_id)
        self.assertEqual((expected_name or input_name),
                         get_doc["display_name"])

        # update
        update_data = {"description": input_name}
        update_doc = self.tc.update_endpoint(ep_id, update_data)
        self.assertEqual(update_doc["code"], "Updated")
        # confirm get sees updated description
        get_doc = self.tc.get_endpoint(ep_id)
        self.assertEqual((expected_name or input_name), get_doc["description"])

        # delete
        delete_doc = self.tc.delete_endpoint(ep_id)
        self.assertEqual(delete_doc["code"], "Deleted")

    def test_literal_str_encoding(self):
        """
        Sanity check that importing unicode_literals in the globus_sdk
        doesn't affect the encoding of literals in code that imports the sdk.
        """
        if (six.PY2):
            self.assertEqual(type("literal"), six.binary_type)
        else:
            self.assertEqual(type("literal"), six.text_type)

    def test_ascii_url_encoding(self):
        """
        Tests operations with an ASCII name that includes ' ' and '%"
        characters that will need to be encoded for use in a url.
        """
        name = "a% b"
        self.dir_operations(name)
        self.ep_operations(name)

    def test_non_ascii_utf8(self):
        """
        Tests operations with a UTF-8 name containing non ASCII characters with
        code points requiring multiple bytes.
        """
        name = u"テスト"
        self.dir_operations(name)
        self.ep_operations(name)

    @unittest.skipIf(six.PY3, "test run with Python 3")
    def test_non_ascii_utf8_bytes(self):
        """
        Tests operations with a byte string encoded from non ASCII UTF-8.
        This test is only run on Python 2 as bytes are not strings in Python 3.
        """
        uni_name = u"テスト"
        byte_name = uni_name.encode("utf8")
        # we expect uni_name back since the API returns unicode strings
        self.dir_operations(byte_name, expected_name=uni_name)
        self.ep_operations(byte_name, expected_name=uni_name)

    def test_latin1(self):
        """
        Tests operations with latin-1 name that is not valid UTF-8.
        """
        # the encoding for 'é' in latin-1 is a continuation byte in utf-8
        byte_name = b"\xe9"  # é's latin-1 encoding
        name = byte_name.decode("latin-1")
        with self.assertRaises(UnicodeDecodeError):
            byte_name.decode("utf-8")

        self.dir_operations(name)
        self.ep_operations(name)

    @unittest.skipIf(six.PY3, "test run with Python 3")
    def test_invalid_utf8_bytes(self):
        """
        Tests operations with byte string that can be decoded with
        latin-1 but not with UTF-8. Confirms that this raises a
        UnicodeDecodeError, as the SDK/APIs can't handle decoding non UTF-8.
        This test is only run on Python 2 as bytes are not strings in Python 3.
        """
        # the encoding for 'é' in latin-1 is a continuation byte in utf-8
        byte_name = b"\xe9"  # é's latin-1 encoding

        with self.assertRaises(UnicodeDecodeError):
            self.dir_operations(byte_name)
        with self.assertRaises(UnicodeDecodeError):
            self.ep_operations(byte_name)

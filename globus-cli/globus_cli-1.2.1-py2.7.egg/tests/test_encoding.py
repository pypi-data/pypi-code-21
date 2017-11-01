# -*- coding: utf8 -*-

from random import getrandbits
import unittest
import six
import json

from tests.framework.cli_testcase import CliTestCase
from tests.framework.constants import GO_EP1_ID


class EncodingTests(CliTestCase):

    def dir_operations(self, input_name, expected_name=None):
        """
        Given an input directory name, makes the directory to test inputs,
        ls's the directory to test outputs and output formats,
        attempts to remake the directory to test error outputs,
        and finally deletes the directory for cleanup.
        """
        # mkdir
        # name randomized to prevent collision
        rand = str(getrandbits(128))
        dir_name = input_name + rand
        expected = (expected_name or input_name) + rand
        # if given a unicode name, run a unicode string
        if isinstance(input_name, six.text_type):
            make_output = self.run_line(
                u"globus mkdir {}:~/{}".format(GO_EP1_ID, dir_name))
        # if given a byte string name, run a byte string
        else:
            make_output = self.run_line(
                b"globus mkdir {}:~/{}".format(GO_EP1_ID, dir_name))

        self.assertIn("The directory was created successfully", make_output)

        # confirm the dir can be seen. Confirms simple, long, verbose,
        # and json output all handle the encoding.
        ls_output = self.run_line(u"globus ls {}:~/".format(GO_EP1_ID))
        self.assertIn(expected, ls_output)

        long_output = self.run_line(
            u"globus ls -l {}:~/".format(GO_EP1_ID))
        self.assertIn(expected, long_output)
        self.assertIn("Filename", long_output)

        json_output = json.loads(
            self.run_line(
                u"globus ls -F json {}:~/".format(GO_EP1_ID)))
        self.assertIn(expected, [i["name"] for i in json_output["DATA"]])

        # attempt to make the dir again to test error output:
        # if given a unicode name, run a unicode string
        if isinstance(input_name, six.text_type):
            make2_output = self.run_line(
                u"globus mkdir {}:~/{}".format(GO_EP1_ID, dir_name),
                assert_exit_code=1)
        # if given a byte string name, run a byte string
        else:
            make2_output = self.run_line(
                b"globus mkdir {}:~/{}".format(GO_EP1_ID, dir_name),
                assert_exit_code=1)
        self.assertIn("Path already exists", make2_output)
        self.assertIn(expected, make2_output)

        # delete for cleanup:
        # if given a unicode name, run a unicode string
        if isinstance(input_name, six.text_type):
            delete_output = self.run_line(
                u"globus delete -r {}:~/{}".format(GO_EP1_ID, dir_name))
        # if given a byte string name, run a byte string
        else:
            delete_output = self.run_line(
                b"globus delete -r {}:~/{}".format(GO_EP1_ID, dir_name))

        self.assertIn("The delete has been accepted", delete_output)

    def ep_operations(self, input_name, expected_name=None):
        """
        Given an input_name, creates, updates, gets, and deletes an endpoint
        using the input_name as a display_name. If an expected_name is given,
        confirms output matches that name rather than the input_name.
        """
        # if given a unicode name, run a unicode string
        if isinstance(input_name, six.text_type):
            create_output = json.loads(self.run_line(
                u"globus endpoint create -F json --server {}".format(
                    input_name)))
        # if given a byte string name, run a byte string
        else:
            create_output = json.loads(self.run_line(
                b"globus endpoint create -F json --server {}".format(
                    input_name)))
        self.assertEqual(create_output["code"], "Created")
        self.assertEqual(create_output["code"], "Created")
        ep_id = create_output["id"]

        # confirm endpoint show sees ep
        show_output = self.run_line("globus endpoint show {}".format(ep_id))
        self.assertIn((expected_name or input_name), show_output)

        # update
        # if given a unicode name, run a unicode string
        if isinstance(input_name, six.text_type):
            update_output = self.run_line(
                u"globus endpoint update {} --description {}".format(
                    ep_id, input_name))
        # if given a byte string name, run a byte string
        else:
            update_output = self.run_line(
                b"globus endpoint update {} --description {}".format(
                    ep_id, input_name))
        self.assertIn("updated successfully", update_output)

        # confirm show sees updated description
        show_output = json.loads(self.run_line(
            "globus endpoint show {} -F json".format(ep_id)))
        self.assertEqual((expected_name or input_name),
                         show_output["description"])

        # delete
        delete_output = self.run_line(
            "globus endpoint delete {}".format(ep_id))
        self.assertIn("deleted successfully", delete_output)

    def test_quote_escaping(self):
        """
        Tests operations with an escaped quote inside quotes that should be
        seen as one literal quote character by the shell
        """
        name = r'"\""'
        self.dir_operations(name, expected_name='"')
        self.ep_operations(name, expected_name='"')

    def test_ascii_url_encoding(self):
        """
        Tests operations with an ASCII name that includes ' ' and '%"
        characters that will need to be encoded for use in a url.
        """
        name = '"a% b"'
        self.dir_operations(name, expected_name="a% b")
        self.ep_operations(name, expected_name="a% b")

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

        make_output = self.run_line("globus mkdir {}:~/{}".format(
            GO_EP1_ID, byte_name), assert_exit_code=1)
        self.assertIn("UnicodeDecodeError", make_output)

        create_output = self.run_line(
                "globus endpoint create --server {}".format(
                    byte_name), assert_exit_code=1)
        self.assertIn("UnicodeDecodeError", create_output)

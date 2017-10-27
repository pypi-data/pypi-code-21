# coding=utf-8

import unittest

from tcell_agent.appsensor import params


class ParamsTest(unittest.TestCase):
    def one_flatten_params_test(self):
        result = params.flatten_clean("utf-8", {
            "action": "index"
        })

        self.assertEqual(
            result,
            {("action",): "index"}
        )

    def two_flatten_params_test(self):
        result = params.flatten_clean("utf-8", {
            u"müller": "sadness"
        })

        self.assertEqual(
            result,
            {(u"müller",): "sadness"}
        )

    def three_flatten_params_test(self):
        result = params.flatten_clean("utf-8", {
            u"müller".encode("utf-8"): "sadnessdos"
        })

        self.assertEqual(
            result,
            {(u"müller",): "sadnessdos"}
        )

    def four_flatten_params_test(self):
        result = params.flatten_clean("utf-8", {
            "utf8-char": u"Müller",
        })

        self.assertEqual(
            result,
            {("utf8-char",): u"Müller"}
        )

    def five_flatten_params_test(self):
        result = params.flatten_clean("utf-8", {
            "waitlist_entries": {"email": "emailone", "preferences": {"email": "emaildos"}},
        })

        self.assertEqual(
            result,
            {
                ("waitlist_entries", "email",): "emailone",
                ("waitlist_entries", "preferences", "email",): "emaildos"
            }
        )

    def six_flatten_params_test(self):
        result = params.flatten_clean("utf-8", {
            "email_preferences": ["daily_digest", "reminders", u"Müller".encode("utf8")],
        })

        self.assertEqual(
            result,
            {
                ("0", "email_preferences",): "daily_digest",
                ("1", "email_preferences",): "reminders",
                ("2", "email_preferences"): u"Müller",
            }
        )

    def seven_flatten_params_test(self):
        result = params.flatten_clean("utf-8", {
            "users": [
                {"email": "one@email.com"},
                {"email": "dos@email.com"},
            ]
        })

        self.assertEqual(
            result,
            {
                ("0", "users", "email",): "one@email.com",
                ("1", "users", "email",): "dos@email.com"
            }
        )

    def eight_flatten_params_test(self):
        result = params.flatten_clean("latin-1", {
            "ISO-Latin1": u"Méller".encode("ISO-8859-1"),
        })

        self.assertEqual(
            result,
            {("ISO-Latin1",): u"Méller"}
        )

    def nine_flatten_params_test(self):
        result = params.flatten_clean("utf-8", {
            u"waitlist_entriés".encode("utf-8"): {
                u"émail".encode("utf-8"): u"émailone".encode("utf-8")
            }
        })

        self.assertEqual(
            result,
            {
                (u"waitlist_entriés", u"émail",): u"émailone"
            }
        )

    def ten_flatten_params_test(self):
        encoding = "latin-1"
        result = params.flatten_clean(encoding, {
            u"waitlist_entriés".encode(encoding): {
                u"émail".encode(encoding): u"émailone".encode(encoding)
            }
        })

        self.assertEqual(
            result,
            {
                (u"waitlist_entriés", u"émail",): u"émailone"
            }
        )

    def eleven_flatten_params_test(self):
        encoding = "utf-8"
        result = params.flatten_clean(encoding, {
            u"waitlist_entriés".encode(encoding): [
                u"émail".encode(encoding), u"émailone".encode(encoding)
            ]
        })

        self.assertEqual(
            result,
            {
                ("0", u"waitlist_entriés",): u"émail",
                ("1", u"waitlist_entriés",): u"émailone",
            }
        )

    def twelve_flatten_params_test(self):
        encoding = "latin-1"
        result = params.flatten_clean(encoding, {
            u"waitlist_entriés".encode(encoding): [
                u"émail".encode(encoding), u"émailone".encode(encoding)
            ]
        })

        self.assertEqual(
            result,
            {
                ("0", u"waitlist_entriés",): u"émail",
                ("1", u"waitlist_entriés",): u"émailone",
            }
        )

    def thirteenth_flatten_params_test(self):
        encoding = "utf-8"
        result = params.flatten_clean(encoding, {
            "body": ["first", "second"]
        })

        self.assertEqual(
            result,
            {
                ("0", u"body",): u"first",
                ("1", u"body",): u"second",
            }
        )

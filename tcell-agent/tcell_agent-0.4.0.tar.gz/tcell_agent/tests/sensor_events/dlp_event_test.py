import unittest

from ...sensor_events import DlpEvent


class DlpEventTest(unittest.TestCase):
    def test_dlp_event_create_framework(self):
        dlpe = DlpEvent("routeid", "/rawuri?y=z&d=f", DlpEvent.FOUND_IN_LOG).for_framework(
            DlpEvent.FRAMEWORK_VARIABLE_SESSION_ID)
        dlpe.post_process()

        self.assertEqual(dlpe["event_type"], "dlp")
        self.assertEqual(dlpe["type"], "framework")
        self.assertEqual(dlpe["variable"], DlpEvent.FRAMEWORK_VARIABLE_SESSION_ID)

    def test_dlp_event_create_request(self):
        dlpe = DlpEvent("routeid", "/rawuri?y=z&d=f", DlpEvent.FOUND_IN_LOG).for_request(DlpEvent.REQUEST_CONTEXT_FORM,
                                                                                         "passwd")
        dlpe.post_process()

        self.assertEqual(dlpe["event_type"], "dlp")
        self.assertEqual(dlpe["type"], "request")
        self.assertEqual(dlpe["context"], "form")
        self.assertEqual(dlpe["variable"], "passwd")

import unittest
import json

from mock import ANY, Mock, patch, call

from tcell_agent.agent import TCellAgent
from tcell_agent.appsensor.injections_reporter import report_and_log


class InjectionsReporterTest(unittest.TestCase):

    def none_events_test(self):
        mock_logger = Mock()
        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            with patch("tcell_agent.appsensor.injections_reporter.get_payloads_logger",
                       return_value=mock_logger):
                report_and_log(None)

                self.assertFalse(patched_send.called)
                self.assertFalse(mock_logger.info.called)

    def empty_events_test(self):
        mock_logger = Mock()
        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            with patch("tcell_agent.appsensor.injections_reporter.get_payloads_logger",
                       return_value=mock_logger):
                report_and_log([])

                self.assertFalse(patched_send.called)
                self.assertFalse(mock_logger.info.called)

    def no_log_payload_one_event_test(self):
        events = [{
            "cnt": 1,
            "event_type": "as",
            "pattern": "1",
            "m": "request_method",
            "uri": "abosolute_uri",
            "param": "avatar",
            "meta": {"l": "body"},
            "sid": "session_id",
            "rid": "route_id",
            "dp": "xss",
            "uid": "user_id"
        }]

        mock_logger = Mock()
        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            with patch("tcell_agent.appsensor.injections_reporter.get_payloads_logger",
                       return_value=mock_logger):
                report_and_log(events)

                self.assertFalse(mock_logger.info.called)
                patched_send.assert_has_calls([
                    call({
                        "event_type": "as",
                        "pattern": "1",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "param": "avatar",
                        "meta": {"l": "body"},
                        "sid": "session_id",
                        "rid": "route_id",
                        "dp": "xss",
                        "uid": "user_id"
                    })
                ])

    def log_payload_one_event_test(self):
        events = [{
            "cnt": 1,
            "event_type": "as",
            "pattern": "1",
            "m": "request_method",
            "uri": "abosolute_uri",
            "param": "avatar",
            "meta": {"l": "body"},
            "sid": "session_id",
            "rid": "route_id",
            "dp": "xss",
            "uid": "user_id",
            "log_payload": "<script>"
        }]

        mock_logger = Mock()
        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            with patch("tcell_agent.appsensor.injections_reporter.get_payloads_logger",
                       return_value=mock_logger):
                report_and_log(events)

                patched_send.assert_has_calls([
                    call({
                        "event_type": "as",
                        "pattern": "1",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "param": "avatar",
                        "meta": {"l": "body"},
                        "sid": "session_id",
                        "rid": "route_id",
                        "dp": "xss",
                        "uid": "user_id"
                    })
                ])

                mock_logger.info.assert_called_once_with(ANY)
                call_args, _ = mock_logger.info.call_args
                self.assertEqual(
                    sorted(json.loads(call_args[0])),
                    sorted({
                        "event_type": "as",
                        "pattern": "1",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "param": "avatar",
                        "meta": {"l": "body"},
                        "sid": "session_id",
                        "rid": "route_id",
                        "payload": "<script>",
                        "dp": "xss",
                        "uid": "user_id"
                    })
                )

    def payload_and_no_log_payload_one_event_test(self):
        events = [{
            "cnt": 1,
            "event_type": "as",
            "pattern": "1",
            "m": "request_method",
            "uri": "abosolute_uri",
            "param": "avatar",
            "meta": {"l": "body"},
            "sid": "session_id",
            "rid": "route_id",
            "dp": "xss",
            "uid": "user_id",
            "payload": "<script>"
        }]

        mock_logger = Mock()
        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            with patch("tcell_agent.appsensor.injections_reporter.get_payloads_logger",
                       return_value=mock_logger):
                report_and_log(events)

                self.assertFalse(mock_logger.info.called)
                patched_send.assert_has_calls([
                    call({
                        "event_type": "as",
                        "pattern": "1",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "param": "avatar",
                        "meta": {"l": "body"},
                        "sid": "session_id",
                        "rid": "route_id",
                        "payload": "<script>",
                        "dp": "xss",
                        "uid": "user_id"
                    })
                ])

    def log_payload_and_payload_one_event_test(self):
        events = [{
            "cnt": 1,
            "event_type": "as",
            "pattern": "1",
            "m": "request_method",
            "uri": "abosolute_uri",
            "param": "avatar",
            "meta": {"l": "body"},
            "sid": "session_id",
            "rid": "route_id",
            "dp": "xss",
            "uid": "user_id",
            "payload": "<script>",
            "log_payload": "<script>"
        }]

        mock_logger = Mock()
        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            with patch("tcell_agent.appsensor.injections_reporter.get_payloads_logger",
                       return_value=mock_logger):
                report_and_log(events)

                patched_send.assert_has_calls([
                    call({
                        "event_type": "as",
                        "pattern": "1",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "param": "avatar",
                        "meta": {"l": "body"},
                        "sid": "session_id",
                        "rid": "route_id",
                        "payload": "<script>",
                        "dp": "xss",
                        "uid": "user_id"
                    })
                ])

                mock_logger.info.assert_called_once_with(ANY)
                call_args, _ = mock_logger.info.call_args
                self.assertEqual(
                    sorted(json.loads(call_args[0])),
                    sorted({
                        "event_type": "as",
                        "pattern": "1",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "param": "avatar",
                        "meta": {"l": "body"},
                        "sid": "session_id",
                        "rid": "route_id",
                        "payload": "<script>",
                        "dp": "xss",
                        "uid": "user_id"
                    })
                )

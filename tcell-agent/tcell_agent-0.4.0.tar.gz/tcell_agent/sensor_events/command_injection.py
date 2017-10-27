from __future__ import unicode_literals

from . import SensorEvent


class CommandInjectionMatchEvent(dict):

    def __init__(self, rule_id, command):
        super(CommandInjectionMatchEvent, self).__init__()

        self["rule_id"] = rule_id
        if command:
            self["command"] = command


class CommandInjectionEvent(SensorEvent):
    def __init__(self,
                 commands,
                 blocked,
                 matches,
                 method=None,
                 remote_address=None,
                 route_id=None,
                 session_id=None,
                 user_id=None,
                 full_commandline=None):
        super(CommandInjectionEvent, self).__init__("cmdi")

        self["commands"] = commands
        self["blocked"] = blocked
        self["matches"] = matches

        if method:
            self["method"] = method

        if remote_address:
            self["remote_address"] = remote_address

        if route_id:
            self["route_id"] = route_id

        if session_id:
            self["session_id"] = session_id

        if user_id:
            self["user_id"] = user_id

        if full_commandline:
            self["full_commandline"] = full_commandline

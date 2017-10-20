from builtins import object
from ahqapiclient.http_client import HTTPClient

from ahqapiclient.resources.backendsettings import BackendSettings
from ahqapiclient.resources.action import Action
from ahqapiclient.resources.aggregation import Aggregation
from ahqapiclient.resources.case import Case
from ahqapiclient.resources.endpoint import Endpoint
from ahqapiclient.resources.inbound_filter import InboundFilter
from ahqapiclient.resources.incident import Incident
from ahqapiclient.resources.log import Log
from ahqapiclient.resources.mailbox import Mailbox
from ahqapiclient.resources.me import Me
from ahqapiclient.resources.network import Network
from ahqapiclient.resources.noop import Noop
from ahqapiclient.resources.setting import Settings
from ahqapiclient.resources.system import System
from ahqapiclient.resources.user import User
from ahqapiclient.resources.escalation import Escalation
from ahqapiclient.resources.client import Client as ClientEndpoint
from ahqapiclient.resources.reports import Reports
from ahqapiclient.resources.apisettings import ApiSettings


class Client(object):

    def __init__(self, endpoint, timeout=60):
        http_client = HTTPClient(endpoint, timeout)
        self._action = Action(http_client)
        self._aggregation = Aggregation(http_client)
        self._case = Case(http_client)
        self._client = ClientEndpoint(http_client)
        self._endpoint = Endpoint(http_client)
        self._escalation = Escalation(http_client)
        self._inbound_filter = InboundFilter(http_client)
        self._incident = Incident(http_client)
        self._log = Log(http_client)
        self._mailbox = Mailbox(http_client)
        self._me = Me(http_client)
        self._network = Network(http_client)
        self._noop = Noop(http_client)
        self._settings = Settings(http_client)
        self._backendsettings = BackendSettings(http_client)
        self._system = System(http_client)
        self._user = User(http_client)
        self._reports = Reports(http_client)
        self._apisettings = ApiSettings(http_client)

        self._apiendpoint = endpoint

    def get_endpoint(self):
        return self._apiendpoint

    @property
    def noop(self):
        return self._noop

    @property
    def user(self):
        return self._user

    @property
    def mailbox(self):
        return self._mailbox

    @property
    def incident(self):
        return self._incident

    @property
    def escalation(self):
        return self._escalation

    @property
    def client(self):
        return self._client

    @property
    def system(self):
        return self._system

    @property
    def inboundfilter(self):
        return self._inbound_filter

    @property
    def settings(self):
        return self._settings

    @property
    def backendsettings(self):
        return self._backendsettings

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def log(self):
        return self._log

    @property
    def action(self):
        return self._action

    @property
    def aggregation(self):
        return self._aggregation

    @property
    def network(self):
        return self._network

    @property
    def me(self):
        return self._me

    @property
    def case(self):
        return self._case

    @property
    def reports(self):
        return self._reports

    @property
    def apisettings(self):
        return self._apisettings


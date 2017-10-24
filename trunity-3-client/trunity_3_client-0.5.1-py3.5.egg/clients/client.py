from trunity_3_client.clients.auth import initialize_session_from_creds
from trunity_3_client.clients.endpoints import *


class Client(object):

    def __init__(self, login, password):

        self._session = initialize_session_from_creds(login, password)

        self.topics = TopicsClient(self._session)
        self.contents = ContentsClient(self._session)
        self.terms = TermsClient(self._session)
        self.sites = SitesClient(self._session)
        self.questions = QuestionsClient(self._session)




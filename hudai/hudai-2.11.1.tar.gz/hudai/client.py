"""
hudai.client
"""

from datetime import datetime, timedelta
import requests

from .error import HudAiError
from .resources import *
from .helpers.http_client import HttpClient


class Client(object):
    """
    API Client for HUD.ai that handles the API token injection and translation
    to/from Python objects
    """
    def __init__(self,
                 client_id=None,
                 client_secret=None,
                 base_url='https://api.hud.ai/v1',
                 auth_url='https://accounts.hud.ai',
                 redirect_uri=None,
                 debug=False):
        if not client_id:
            raise HudAiError('missing client_id', 'initialization_error')

        self._debug = debug

        self._client_id = client_id
        self._client_secret = client_secret
        self._auth_url = auth_url
        self._redirect_uri = redirect_uri

        self._auth_code = None
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None

        self._http_client = HttpClient(self, base_url)

        self.article_highlights = ArticleHighlightsResource(self._http_client)
        self.article_key_terms = ArticleKeyTermResource(self._http_client)
        self.article_tags = ArticleTagResource(self._http_client)
        self.articles = ArticleResource(self._http_client)
        self.collateral = CollateralResource(self._http_client)
        self.company_events = CompanyEventResource(self._http_client)
        self.company_key_terms = CompanyKeyTermResource(self._http_client)
        self.companies = CompanyResource(self._http_client)
        self.domains = DomainResource(self._http_client)
        self.key_terms = KeyTermResource(self._http_client)
        self.organizations = OrganizationResource(self._http_client)
        self.people = PersonResource(self._http_client)
        self.person_key_terms = PersonKeyTermResource(self._http_client)
        self.person_quotes = PersonQuoteResource(self._http_client)
        self.relevant_article_collateral = RelevantArticleCollateralResource(self._http_client)
        self.relevant_articles = RelevantArticlesResource(self._http_client)
        self.system_events = SystemEventResource(self._http_client)
        self.system_tasks = SystemTaskResource(self._http_client)
        self.text_corpora = TextCorpusResource(self._http_client)
        self.user_companies = UserCompanyResource(self._http_client)
        self.user_contacts = UserContactResource(self._http_client)
        self.user_digest_subscriptions = UserDigestSubscriptionResource(self._http_client)
        self.user_key_terms = UserKeyTermResource(self._http_client)
        self.users = UserResource(self._http_client)

        # Preserve backwards compatibility
        self._add_deprecated_attributes()

    def get_authorize_uri(self):
        """
        Builds authorization URL to send users to to grant access and return a
        `code` to the redirect_uri
        """
        if not self._redirect_uri:
            raise HudAiError('cannot generate authorization uri without redirect_uri')

        return (
            '{host}/oauth2/authorize' +
            '?response_type=code' +
            '&client_id={client_id}' +
            '&redirect_uri={redirect_uri}'
        ).format(
            host=self._auth_url,
            client_id=self._client_id,
            redirect_uri=self._redirect_uri
        )

    def refresh_tokens(self):
        """
        Refreshes the tokens (access and refresh) if required
        """
        if self.token_expires_at and self.token_expires_at > datetime.now():
            return

        if self._auth_code:
            return self._exchange_auth_code()

        if self.refresh_token:
            return self._refresh_tokens()

        if self._client_secret:
            return self._exchange_client_credentials()

    def set_auth_code(self, code):
        """
        Store the authorization code given back from the auth server for future
        exchange to get a user access token
        """
        self._auth_code = code

    # Private

    def _add_deprecated_attributes(self):
        self.article_highlight = self.article_highlights
        self.article_key_term = self.article_key_terms
        self.article = self.articles
        self.company_key_term = self.company_key_terms
        self.company = self.companies
        self.domain = self.domains
        self.key_term = self.key_terms
        self.relevant_article = self.relevant_articles
        self.system_event = self.system_events
        self.system_task = self.system_tasks
        self.text_corpus = self.text_corpora
        self.user_company = self.user_companies
        self.user_digest_subscription = self.user_digest_subscriptions
        self.user_key_term = self.user_key_terms
        self.user = self.users

    def _get_tokens(self, data):
        token_url = '{host}/oauth2/token'.format(host=self._auth_url)

        response = requests.post(token_url, json=data).json()

        self.access_token = response.get('access_token')

        if self._debug and not self.access_token:
            print "hudai.client error:get_token", response

        self.refresh_token = response.get('refresh_token', None)

        expires_in = response.get('expires_in', 0)
        self.token_expires_at = datetime.now() + timedelta(milliseconds=expires_in)

    def _exchange_auth_code(self):
        self._get_tokens({
            'grant_type':    'authorization_code',
            'client_id':     self._client_id,
            'client_secret': self._client_secret,
            'code':          self._auth_code,
            'redirect_uri':  self._redirect_uri,
        })

    def _exchange_client_credentials(self):
        self._get_tokens({
            'grant_type':    'client_credentials',
            'client_id':     self._client_id,
            'client_secret': self._client_secret,
        })

    def _refresh_tokens(self):
        self._get_tokens({
            'grant_type':    'refresh_grant',
            'client_id':     self._client_id,
            'client_secret': self._client_secret,
            'refresh_token': self.refresh_token,
        })

HudAi = Client

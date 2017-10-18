"""HUD.ai Client Specs

Makes sure that the client surfaces the right resources and performs the
required token exchanges
"""

from datetime import datetime, timedelta
import pytest
import requests

from hudai.client import Client
from hudai.error import HudAiError
from hudai.resources import *


MOCK_CLIENT_ID = '7fe475ee-aae1-4ff2-82f4-ab48948edad0'
MOCK_CLIENT_SECRET = '42202699-d526-4505-9218-28e2af284e70'
MOCK_REDIRECT_URI = 'https://app.example.com/auth/callbacks/hud-ai'

def test_initialization():
    client = Client(client_id=MOCK_CLIENT_ID)

    assert isinstance(client, Client)
    assert isinstance(client.article_highlights, ArticleHighlightsResource)
    assert isinstance(client.article_key_terms, ArticleKeyTermResource)
    assert isinstance(client.articles, ArticleResource)
    assert isinstance(client.company_key_terms, CompanyKeyTermResource)
    assert isinstance(client.companies, CompanyResource)
    assert isinstance(client.domains, DomainResource)
    assert isinstance(client.key_terms, KeyTermResource)
    assert isinstance(client.people, PersonResource)
    assert isinstance(client.person_key_terms, PersonKeyTermResource)
    assert isinstance(client.person_quotes, PersonQuoteResource)
    assert isinstance(client.relevant_articles, RelevantArticlesResource)
    assert isinstance(client.system_events, SystemEventResource)
    assert isinstance(client.system_tasks, SystemTaskResource)
    assert isinstance(client.text_corpora, TextCorpusResource)
    assert isinstance(client.user_companies, UserCompanyResource)
    assert isinstance(client.user_contacts, UserContactResource)
    assert isinstance(client.user_digest_subscriptions, UserDigestSubscriptionResource)
    assert isinstance(client.user_key_terms, UserKeyTermResource)
    assert isinstance(client.users, UserResource)

def test_deprecated_methods():
    client = Client(client_id=MOCK_CLIENT_ID)

    assert isinstance(client.article_highlights, ArticleHighlightsResource)
    assert isinstance(client.article_key_term, ArticleKeyTermResource)
    assert isinstance(client.article, ArticleResource)
    assert isinstance(client.company_key_term, CompanyKeyTermResource)
    assert isinstance(client.company, CompanyResource)
    assert isinstance(client.domain, DomainResource)
    assert isinstance(client.key_term, KeyTermResource)
    assert isinstance(client.system_event, SystemEventResource)
    assert isinstance(client.system_task, SystemTaskResource)
    assert isinstance(client.text_corpus, TextCorpusResource)
    assert isinstance(client.user_company, UserCompanyResource)
    assert isinstance(client.user_key_term, UserKeyTermResource)
    assert isinstance(client.user, UserResource)


def test_get_authorize_uri_without_redirect_uri():
    client = Client(client_id=MOCK_CLIENT_ID)

    with pytest.raises(HudAiError):
        client.get_authorize_uri()


def test_get_authorize_uri():
    redirect_uri = 'https://app.example.com/auth/callbacks/hud-ai'
    client = Client(client_id=MOCK_CLIENT_ID, redirect_uri=redirect_uri)

    expected_uri = (
        'https://accounts.hud.ai/oauth2/authorize' +
        '?response_type=code' +
        '&client_id={client_id}' +
        '&redirect_uri={redirect_uri}'
    ).format(client_id=MOCK_CLIENT_ID, redirect_uri=redirect_uri)

    assert client.get_authorize_uri() == expected_uri


def test_refresh_tokens_valid_token(mocker):
    client = Client(client_id=MOCK_CLIENT_ID)
    client.token_expires_at = datetime.now() + timedelta(hours=1)

    mocker.spy(client, '_refresh_tokens')

    client.refresh_tokens()

    assert client._refresh_tokens.call_count == 0


def test_refresh_tokens_expired_token(mocker):
    client = Client(client_id=MOCK_CLIENT_ID, client_secret=MOCK_CLIENT_SECRET)

    mock_refresh_token = 'mock-refresh-token'

    client.token_expires_at = datetime.now() - timedelta(hours=1)
    client.refresh_token = mock_refresh_token

    mock_response = mocker.Mock()
    mock_json = {
        'access_token': 'new-token',
        'refresh_token': 'new-refresh-token',
        'expires_in': 100000
    }
    mock_response.json.return_value = mock_json

    mocker.patch('requests.post', return_value=mock_response)

    client.refresh_tokens()

    request_args, request_kwargs = requests.post.call_args

    assert request_args[0] == 'https://accounts.hud.ai/oauth2/token'
    assert request_kwargs['json'] == {
        'client_id': MOCK_CLIENT_ID,
        'client_secret': MOCK_CLIENT_SECRET,
        'grant_type': 'refresh_grant',
        'refresh_token': mock_refresh_token
    }
    assert client.access_token == mock_json['access_token']
    assert client.refresh_token == mock_json['refresh_token']

    projected_expiration = datetime.now() + \
        timedelta(milliseconds=mock_json['expires_in'])

    assert (
        (projected_expiration - timedelta(seconds=1))
        < client.token_expires_at <
        (projected_expiration + timedelta(seconds=1))
    )


def test_refresh_tokens_auth_code(mocker):
    client = Client(
        client_id=MOCK_CLIENT_ID,
        client_secret=MOCK_CLIENT_SECRET,
        redirect_uri=MOCK_REDIRECT_URI
    )

    mock_auth_code = 'mock-auth-code'

    client.set_auth_code(mock_auth_code)

    mock_response = mocker.Mock()
    mock_json = {
        'access_token': 'new-token',
        'refresh_token': 'new-refresh-token',
        'expires_in': 100000
    }
    mock_response.json.return_value = mock_json

    mocker.patch('requests.post', return_value=mock_response)

    client.refresh_tokens()

    request_args, request_kwargs = requests.post.call_args

    assert request_args[0] == 'https://accounts.hud.ai/oauth2/token'
    assert request_kwargs['json'] == {
        'client_id': MOCK_CLIENT_ID,
        'client_secret': MOCK_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': mock_auth_code,
        'redirect_uri': MOCK_REDIRECT_URI
    }
    assert client.access_token == mock_json['access_token']
    assert client.refresh_token == mock_json['refresh_token']

    projected_expiration = datetime.now() + \
        timedelta(milliseconds=mock_json['expires_in'])

    assert (
        (projected_expiration - timedelta(seconds=1))
        < client.token_expires_at <
        (projected_expiration + timedelta(seconds=1))
    )


def test_refresh_tokens_client_credentials(mocker):
    client = Client(client_id=MOCK_CLIENT_ID, client_secret=MOCK_CLIENT_SECRET)

    mock_response = mocker.Mock()
    mock_json = {
        'access_token': 'new-token',
        'refresh_token': 'new-refresh-token',
        'expires_in': 100000
    }
    mock_response.json.return_value = mock_json

    mocker.patch('requests.post', return_value=mock_response)

    client.refresh_tokens()

    request_args, request_kwargs = requests.post.call_args

    assert request_args[0] == 'https://accounts.hud.ai/oauth2/token'
    assert request_kwargs['json'] == {
        'client_id': MOCK_CLIENT_ID,
        'client_secret': MOCK_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    assert client.access_token == mock_json['access_token']
    assert client.refresh_token == mock_json['refresh_token']

    projected_expiration = datetime.now() + \
        timedelta(milliseconds=mock_json['expires_in'])

    assert (
        (projected_expiration - timedelta(seconds=1))
        < client.token_expires_at <
        (projected_expiration + timedelta(seconds=1))
    )

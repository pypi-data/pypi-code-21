"""
NOTE: Trunity 3 API for Terms is very weird. You can find some information
about how to use it in this article (in Russian):
https://docs.google.com/document/d/14GhRKMfFVfpsHJCooUvMdET7DfnFwJLvxHIKYssmStc/edit#heading=h.cqv7zltqr37
"""
from trunity_3_client.utils.url import Url, API_ROOT


base_url = Url(API_ROOT)
base_url.tail = 'terms'


class TermsListClient(object):
    _url = base_url.list

    def __init__(self, session):
        self._session = session

    def post(self, site_id, term_title, term_text):
        data = {
            'site_id': site_id,
            'term[title]': term_title,
            'term[text]': term_text,
        }
        response = self._session.post(self._url, data)
        response.raise_for_status()
        return response.json()['term_id']


class ContentTermsClient(object):
    _url = base_url.list + '/content_term'

    def __init__(self, session):
        self._session = session

    def post(self, term_id, content_id, content_type):
        """
        Create a content term.
        You can add term in content like
        <term content-term-id="$id" > term_title </term>
        """
        data = {
            'term_id': term_id,
            'content[content_id]': content_id,
            'content[content_type]': content_type,
        }
        response = self._session.post(self._url, data)
        response.raise_for_status()
        return response.json()['content_term_id']


class TmpContentTermClient(object):
    _url = base_url.list + '/tmp_content_term'

    def __init__(self, session):
        self._session = session

    def post(self, term_id):
        data = {
            'term_id': term_id,
        }
        response = self._session.post(self._url, data)
        response.raise_for_status()
        return response.json()['content_term_id']


class UpdateTmpContentTermClient(object):
    _url = base_url.list + '/update_tmp_content_term/{id}'

    def __init__(self, session):
        self._session = session

    def put(self, tmp_content_term_id, content_id, content_type):
        data = {
            'content[content_id]': content_id,
            'content[content_type]': content_type,
        }
        url = self._url.format(id=tmp_content_term_id)
        response = self._session.put(url, data)
        response.raise_for_status()
        return response.json()['content_term_id']


class TermsClient(object):

    def __init__(self, session):
        self.list = TermsListClient(session)
        self.content_terms = ContentTermsClient(session)
        self.tmp_content_term = TmpContentTermClient(session)
        self.update_tmp_content_term = UpdateTmpContentTermClient(session)

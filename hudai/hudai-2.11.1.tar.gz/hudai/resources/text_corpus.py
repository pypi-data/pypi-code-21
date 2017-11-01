"""
hudai.resources.text_corpus
"""
from ..helpers.resource import Resource


class TextCorpusResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/text-corpora')
        self.resource_name = 'TextCorpus'

    def list(self, user_id=None, corpus_type=None, page=None):
        return self._list(user_id=user_id, type=corpus_type, page=page)

    def create(self, user_id=None, corpus_type=None, body=None):
        return self._create(user_id=user_id, type=corpus_type, body=body)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def update(self, entity_id, user_id=None, corpus_type=None, body=None):
        return self._update(entity_id,
                            user_id=user_id,
                            type=corpus_type,
                            body=body)

    def delete(self, entity_id):
        return self._delete(entity_id)

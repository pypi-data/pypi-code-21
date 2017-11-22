"""
kzconfig.couch
~~~~~

Kazoo config library.

"""

import json
from urllib.parse import urlparse, unquote

import couchdb

from . import util


class CouchDBDoc:
    def __init__(self, parent):
        self.parent = parent

    def create(self, db, doc):
        if isinstance(doc, str):
            doc = json.loads(doc)
        doc_id = doc['_id']

        db = self.parent.api[db]
        if doc_id in db:
            old_doc = db[doc_id]
            doc['_rev'] = old_doc.rev
        return db.save(doc)


class CouchDB:
    def __init__(self, context):
        env = context.configs['environment']
        creds = context.secrets['couchdb']

        p = urlparse(env['uri.couchdb'])
        self.api = couchdb.Server(util.join_url(
            p.scheme, creds['user'], creds['pass'], p.netloc
        ))
        self.doc = CouchDBDoc(self)

    def acct_db(self, acct_id):
        db = self.api['accounts']
        doc = db[acct_id]
        db_name = doc['pvt_account_db']
        print(db_name)
        return api[unquote(db_name)]


#
# def get_db_for(acct_id):
#     api = context.couchdb
#
#     db = api['accounts']
#     doc = db[acct_id]
#     db_name = doc['pvt_account_db']
#     print(db_name)
#     return api[unquote(db_name)]

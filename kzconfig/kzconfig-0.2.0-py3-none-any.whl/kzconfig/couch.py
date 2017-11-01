"""
kzconfig.couch
~~~~~

Kazoo config library.


"""

from urllib.parse import urlparse, unquote
import json
import couchdb

from . import util
from .context import context


p = urlparse(context.env['uri.couchdb'])
api = couchdb.Server(util.join_url(
    p.scheme, context.couch['user'], context.couch['pass'], p.netloc
))


def create_doc(db, doc):
    if isinstance(doc, str):
        doc = json.loads(doc)
    doc_id = doc['_id']

    db = api[db]
    if doc_id in db:
        old_doc = db[doc_id]
        doc['_rev'] = old_doc.rev
    return db.save(doc)


def get_db_for(acct_id):
    db = api['accounts']
    doc = db[acct_id]
    db_name = doc['pvt_account_db']
    print(db_name)
    return api[unquote(db_name)]

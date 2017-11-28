import connexion

from couchbase.bucket import Bucket
from couchbase.exceptions import CouchbaseError
from couchbase.n1ql import N1QLQuery

from swagger_server.models.label import Label

CONNSTR = 'couchbase://db/labeldata'
db = None      # global db connection

def get_db():
    global db
    if db == None:
        try:
            db = Bucket(CONNSTR)
        except:
            pass
    return db

def delete(label_id):
    """
    delete label with label id.
    """
    try:
        db = get_db()
        if isinstance(db, Bucket):
            result =  db.delete(str(label_id))
            return "Deleted", 200
        else:
            return "Can't establish database connection.", 404
    except:
        return "Label not found.", 404

    return 'do some magic!'


def get(label_id):
    """
    retrieve label with label id.
    """
    try:
        db = get_db()
        if isinstance(db, Bucket):
            result =  db.get(str(label_id))
            return result.value, 200
        else:
            return "Can't establish database connection.", 404
    except:
        return "Label not found.", 404

    return 'do some magic!'

def get_all_labels(doc_id):
    """
    retrieve all labels for given document id.
    """
    db = get_db()
    if isinstance(db, Bucket):
        try:
            db.n1ql_query("CREATE PRIMARY INDEX ON labeldata").execute()
        finally:
            q = N1QLQuery('SELECT * FROM `labeldata` WHERE doc_id = $doc_id', doc_id=str(doc_id))
            result = []
            for row in db.n1ql_query(q):
                result.append(row['labeldata'])
            return result, 200
    else:
        return "Can't establish database connection.", 404

def post(label):
    """
    upload label to database.
    """
    if connexion.request.is_json:
        label = connexion.request.get_json()
        # label = Label.from_dict(connexion.request.get_json())
        # label = label.to_dict()
    try:
        db = get_db()
        if isinstance(db, Bucket):
            upload = db.upsert(str(label['label_id']),label)
            return "OK", 200
        else:
            return "Can't establish connection to database.", 404
    except KeyError:
        return "Invalid input format. Missing field 'label_id'.", 404

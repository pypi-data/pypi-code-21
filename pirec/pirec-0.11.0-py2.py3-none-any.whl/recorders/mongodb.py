"""Exposes the MongoDB recorder class."""
try:
    from pymongo import MongoClient
except ImportError:
    pass


class MongoDB(object):
    """Records results to a MongoDB database.

    Args:
        uri (str): MongoDB server URI e.g. ``mongodb://localhost:27017``
        database (str): database name
        collection (str): collection name

    Note:
        Use of this class requires the installation of the `pymongo
        module <https://pypi.python.org/pypi/pymongo>`_.

    See Also:
        `MongoDB tutorial <https://api.mongodb.org/python/current/tutorial.html>`_
    """

    def __init__(self, uri, database, collection):
        """Initialize the recorder."""
        self.uri = uri
        self.database_name = database
        self.collection_name = collection

    def write(self, results):
        """Insert results into the database."""
        client = MongoClient(self.uri)
        db = client[self.database_name]
        collection = db[self.collection_name]
        collection.insert_one(results)

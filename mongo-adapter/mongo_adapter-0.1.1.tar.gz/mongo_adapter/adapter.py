import logging

LOG = logging.getLogger(__name__)

class MongoAdapter(object):
    """Adapter for communicating with a mongo database"""
    def __init__(self, client=None, db_name=None):
        """
        Args:
            client(MongoClient)
            db_name(str)
        """
        self.client = client
        self.db = None
        self.db_name = None
        if (db_name and client):
            self.setup(database)
    
    def init_app(self, app):
        """Setup via Flask"""
        host = app.config.get('MONGO_HOST', 'localhost')
        port = app.config.get('MONGO_PORT', 27017)
        db_name = app.config['MONGO_DBNAME']
        LOG.info("connecting to database: %s:%s/%s", host, port, db_name)
        self.setup(db_name=db_name, db=app.extensions['pymongo']['MONGO'][1])
        
    
    def setup(self, db_name, db=None):
        """Setup connection to a database
        
        Args:
            db_name(str)
            db(pymongo.Database)
        """
        if db:
            self.db = db
            self.db_name = db.name
        else:
            self.db = self.client[db_name]
            self.db_name = db_name
        LOG.info("Use database %s", self.db_name)
        # Specify collections that will be used here when overriding
        # eg self.food_collection = self.db.food etc
    
    def __str__(self):
        return "MongoAdapter(db={0})".format(self.db_name)
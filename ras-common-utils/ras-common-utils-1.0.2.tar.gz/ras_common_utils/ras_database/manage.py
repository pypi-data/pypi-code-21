from structlog import get_logger

logger = get_logger()


class Manage:
    def __init__(self, config, engine):
        self._config = config
        self._engine = engine

    def drop(self):
        db_connection = self._config['uri']
        db_schema = self._config['schema']

        # fix-up the postgres schema:
        from ras_common_utils.ras_database.base import Base
        Base.metadata.schema = db_schema if db_connection.startswith('postgres') else None

        logger.info("Dropping database tables.")
        if db_connection.startswith('postgres'):
            logger.info("Dropping schema {}.".format(db_schema))
            self._engine.execute("DROP SCHEMA IF EXISTS {} CASCADE".format(db_schema))
        else:
            Base.metadata.drop_all(self._engine)
        logger.info("Ok, done.")

    def create(self):
        db_connection = self._config['uri']
        db_schema = self._config['schema']

        # fix-up the postgres schema:
        from ras_common_utils.ras_database.base import Base
        if db_connection.startswith('postgres'):
            for t in Base.metadata.sorted_tables:
                t.schema = db_schema

        logger.info("Creating database with uri '{}'".format(db_connection))
        if db_connection.startswith('postgres'):
            logger.info("Creating schema {}.".format(db_schema))
            self._engine.execute("CREATE SCHEMA IF NOT EXISTS {}".format(db_schema))
        logger.info("Creating database tables.")
        Base.metadata.create_all(self._engine)
        logger.info("Ok, database tables have been created.")

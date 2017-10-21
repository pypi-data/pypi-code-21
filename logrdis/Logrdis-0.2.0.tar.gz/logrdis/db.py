import logging
from sqlalchemy import Column, create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, sessionmaker

LOGGER = logging.getLogger(__name__)


class Adapter(object):
    """General Database Adapter that allows dynamic store operations on data."""

    def __init__(self, engine):
        """Initialize the Adapter with an engine string.

        http://docs.sqlalchemy.org/en/latest/core/engines.html
        """
        self.engine = create_engine(engine)
        self.base = declarative_base()
        self.tables = dict()  # key = tablename
        self.__table_definitions = dict()  # key = tablename
        self.types = dict()  # key typename

    @property
    def definitions(self):
        """Provide table definitions."""
        return self.__table_definitions

    def declare(self, tablename, pk, mapping):
        """Declare a table dynamically using the mapping.

        :param tablename: str. the name of the table to be defined
        :param pk: str. the primary key column defined in mapping
        :param mapping: dict. descriptive dictionary with table schema definitions
        :raises: AttributeError. if the pk was not found in the mapping

        For an example, take a look at the below code block
        .. code-block:: python

            {
                'id': Column(Integer, primary_key=True), 
                'name': Column(String), 
                'fullname': Column(String), 
                'password': Column(String)
            }
        """
        self.__table_definitions[tablename] = dict()
        if pk not in mapping.keys():
            raise AttributeError('Invalid primary key defined')

        for column_name, column_declaration in mapping.items():
            if column_name not in self.types:
                # Cache column types for all declaration imports
                _import = __import__('sqlalchemy', fromlist=[str(column_declaration)])
                self.types[column_name] = getattr(_import, column_declaration)

            self.__table_definitions[tablename][column_name] = Column(column_name, self.types[column_name])
            LOGGER.debug('Declared {}:{}'.format(tablename, column_name))
            if pk == column_name:
                self.__table_definitions[tablename][column_name].primary_key=True

        metadata = MetaData(bind=self.engine)
        self.tables[tablename] = \
            Table(tablename, metadata, *self.__table_definitions[tablename].values(), extend_existing=True)
        metadata.create_all()
        LOGGER.info('Created {}'.format(tablename))

    def query(self, tablename, column_name):
        """Helper fn to query a specific table for column."""
        class Table(object):
            pass

        if tablename not in self.tables:
            raise AttributeError('No such table {}'.format(tablename))

        if column_name not in self.__table_definitions[tablename].keys():
            raise AttributeError('Column {} not found in Table {}'.format(column_name, tablename))

        Session = sessionmaker(bind=self.engine)
        session = Session()
        mapper(Table, self.tables[tablename])
        results = session.query(getattr(Table, column_name))
        session.close()

        return results

    def store(self, tablename, regex_match):
        """Store regex match in tablename.

        Iterates the table definition for each column and stores the results
        in the table.

        :param tablename: str. the name of the table in which to store the data
        :param regex_match: regular expresion object that represents a match as
        defined in the yaml.
        :raises: AttributeError
        """
        class Table(object):
            pass

        if tablename not in self.tables:
            raise AttributeError('No such table {}'.format(tablename))

        Session = sessionmaker(bind=self.engine)
        session = Session()
        mapper(Table, self.tables[tablename])

        if not regex_match:
            raise RuntimeError('No match was found')

        regex_dict = regex_match.groupdict()

        table_entry = Table()
        for column_name in self.__table_definitions[tablename].keys():
            setattr(table_entry, column_name, regex_dict[column_name])
        session.add(table_entry)
        LOGGER.debug('Stored: {}'.format(table_entry))

        session.commit()
        session.close()
from sqlalchemy.orm import sessionmaker

from recipe import SETTINGS
from recipe.oven.base import OvenBase
from recipe_caching import query_callable


class CachingOven(OvenBase):
    """An Oven for baking recipes with a cache backed query Session.
    """
    def init_engine(self, connection_string=None, **kwargs):
        """ Builds a SQLAlchemy engine appropiate for use in caching

        :param connection_string: the connection string required to connect
                                  to the database
        :type connection_string: str
        :param **kwargs: Any additional arguments to pass to create_engine
        :type connection_string: dict

        :return: a SQLAlchemy engine
        """
        return super(CachingOven, self).init_engine(connection_string,
                                                    **kwargs)

    def init_session(self):
        """Establishes a Sessionmaker thab supplies sessions with caching
        queries.

        :return: a SQLAlchemy Sessionmaker
        """
        if not self.engine:
            return

        SETTINGS.REGIONS = {}

        return sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False,
            query_cls=query_callable(SETTINGS.CACHE_REGIONS)
        )

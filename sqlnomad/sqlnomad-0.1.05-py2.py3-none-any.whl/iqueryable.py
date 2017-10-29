# coding=utf-8
from abc import abstractmethod, ABC
from typing import Sequence, Optional

from .custom_types import FieldDisplayName, SQL, SqlDialect
from .sql_field import SqlField


class IQueryable(ABC):
    """The object is a self-contained subquery with accompanying metadata.

    In practical terms, conforming to the IQueryable interface means
    that the object is capable of being transformed with the Query monad.
    """

    @property
    @abstractmethod
    def alias(self) -> FieldDisplayName:
        """Display name of the subquery"""
        raise NotImplementedError

    @property
    @abstractmethod
    def dialect(self) -> SqlDialect:
        """Flavor of SQL generated queries should conform to

        Options include the following:
            * SqlDialect.ACCESS
            * SqlDialect.MSSQL
            * SqlDialect.MYSQL
            * SqlDialect.ORACLE
            * SqlDialect.POSTGRES
            * SqlDialect.SQLITE
        """
        raise NotImplementedError

    @abstractmethod
    def field(self, field_alias: FieldDisplayName) -> SqlField:
        """Given a field alias, return a reference to the SqlField it represents"""
        raise NotImplementedError

    @property
    @abstractmethod
    def fields(self) -> Sequence[SqlField]:
        """Sequence of SQL fields accessible to the subquery"""
        raise NotImplementedError

    @property
    @abstractmethod
    def root_alias(self) -> str:
        """Display name of the original subquery ancestor"""
        raise NotImplementedError

    @property
    @abstractmethod
    def schema(self) -> Optional[str]:
        """Database schema of the StorageTable

        This attribute is optional, and should return None for d
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def sql(self) -> SQL:
        """SQL statement representation of the subquery

        The attribute respresents executable SQL code that can be run
        in a database conforming to the specified dialect.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def suffix(self) -> int:
        """THe suffix of the current subquery to distinguish it from its ancestors

        The default suffix is 1.
        """
        raise NotImplementedError

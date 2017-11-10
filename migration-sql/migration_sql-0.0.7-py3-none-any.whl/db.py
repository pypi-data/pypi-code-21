import logging
import subprocess
from contextlib import contextmanager
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import schema_version
from .schema_version import SchemaVersion
from .version import Version

l = logging.getLogger("ww.migration")


class DB(object):
    """

    Provides utility method to interact with the database server, including:

    - read/write the schema table in the *main* database (that is specified when instantiating the object)
    - drop other databases if necessary
    - kill process
    - use mysqldump to duplicate database

    The user and password used to instantiate this class should have enough rights to do all the above actions.

    """

    def __init__(self, host, port, username, password, name):
        """
        Instantiate the object given the database server information and
        the main database (i.e. object of the migration process)

        :param host: server host
        :param port: server port
        :param name: main database name
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.name = name

        self._create_schema_version_if_needed()

    @contextmanager
    def get_session(self):
        """
        to make sure to close the session
        """
        session = self._get_session()
        yield session
        session.close()

    def get_versions_to_apply(self, all_versions: [Version]) -> [Version]:
        """return what versions that should be applied to this db"""
        current_version = self._get_current_version()
        if not current_version:
            current_version_index = -1  # apply all versions
        else:
            current_version_indexes = [i for i in range(len(all_versions)) if
                                       all_versions[i].version_code == current_version]
            if len(current_version_indexes) != 1:
                raise Exception(
                    f"""the current version {current_version} must appear once and only 
                    once the schema version table. 
                    It appears {len(current_version_indexes)} times""")

            current_version_index = current_version_indexes[0]

        to_apply_versions = all_versions[current_version_index + 1:]
        return to_apply_versions

    def clean_dbs_with_names(self, names):
        """delete all the databases whose name match with names"""

        def match_name(db_name):
            for name in names:
                if name in db_name:
                    return True

            return False

        with self.get_session() as session:
            db_names = [_[0] for _ in session.execute("show databases").fetchall()]

            for db_name in db_names:
                if match_name(db_name):
                    l.info("drop db %s", db_name)
                    session.execute(f"drop database if EXISTS {db_name}")

    def duplicate(self, clone_name):
        """duplicate database content to another database using mysqldump"""
        db_connection = self.get_db_connection()

        with self.get_session() as session:
            session.execute(f"create database {clone_name} DEFAULT CHARACTER SET = utf8mb4")

        # copy data from original database to backup database
        duplicate_command = f"""mysqldump --routines --events --triggers --single-transaction \
        {db_connection} {self.name} \
        |mysql {db_connection} {clone_name}"""

        subprocess.check_output(duplicate_command, shell=True)

    def kill_all_process(self):
        """kill all the process except the current one (which is also closed at the end)"""
        with self.get_session() as session:
            current_process = session.execute("select CONNECTION_ID();").fetchone()[0]
            all_process = [_[0] for _ in session.execute("show processlist").fetchall()]

            l.debug("current process:%s", current_process)

            to_kill = [p for p in all_process if p != current_process]
            l.debug("gonna kill %s", to_kill)

            for process in to_kill:
                l.debug("kill process:%s", process)
                try:
                    session.execute(f"kill {process}")
                except Exception:
                    l.warning("cannot kill %s", process)

            l.debug("finish kill")

    def drop(self):
        self.kill_all_process()
        db_connection = self.get_db_connection()
        drop_db_command = f'mysqladmin {db_connection} -f drop {self.name}'
        subprocess.check_output(drop_db_command, shell=True)
        l.debug("drop %s success", self.name)

    def get_db_connection(self):
        """return the connection args to use with mysql command"""
        return f"-u{self.username} -p{self.password} -h{self.host} -P{self.port}"

    def _get_engine(self):
        return create_engine(
            f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}?charset=utf8mb4",
            pool_recycle=3600)

    def _get_session(self):

        session = sessionmaker(bind=self._get_engine())()

        return session

    def _create_schema_version_if_needed(self):
        schema_version.Base.metadata.create_all(self._get_engine())

    def _get_current_version(self) -> Optional[str]:
        with self.get_session() as session:
            schema_version = session.query(SchemaVersion).order_by(SchemaVersion.id.desc()).first()
            return schema_version.version_code if schema_version else None

    def __repr__(self):
        return f"<Database {self.host}:{self.port}/{self.name}>"

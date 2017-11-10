import logging
import subprocess
from datetime import datetime

from .db import DB
from .schema_version import SchemaVersion
from .version import Version

l = logging.getLogger("ww.migration")


def migrate(all_versions: [Version], dbs: [DB]) -> bool:
    """
    Migrate all versions on all the databases.

    Migrate only the versions that are not migrated yet.

    :param all_versions: list of `Version`
    :param dbs: list of `DB` objects
    :return: True if success, False otherwise
    """
    if not _check_command_exist():
        l.error("mysqldump and mysqladmin commands must be present")
        return False

    l.info("start migrate %s for %s", all_versions, dbs)
    clone_backup_dbs = []  # list of tuple (clone_db, backup_db, db)

    for db in dbs:
        db.clean_dbs_with_names([f"{db.name}_backup_", f"{db.name}_clone_"])

        versions = db.get_versions_to_apply(all_versions)
        if not versions:
            l.debug("db %s is already at the latest version", db)
            continue

        success, clone_db, backup_db = _clone_and_apply_migrations(db, versions)
        clone_backup_dbs.append((clone_db, backup_db, db))
        if not success:
            l.error("migration fails on %s", db)
            return False

    for clone_db, backup_db, db in clone_backup_dbs:
        if not _finish_migration(clone_db, backup_db, db):
            l.error("migration finish step fails on %s", db)
            return False

    return True


def _check_command_exist() -> bool:
    """return True if commands mysqldump, mysqladmin exist, otherwise False"""
    try:
        subprocess.check_output("mysqldump --version", shell=True)
        subprocess.check_output("mysqladmin --version", shell=True)
    except subprocess.CalledProcessError:
        return False
    else:
        return True


def _clone_and_apply_migrations(db: DB, versions) -> (bool, DB, DB):
    """
    1. Clone the current database, backup it.
    2. Apply migration on the clone database

    Return whether the migration is successful on the clone db and clone db, backup db if success
    """

    now = datetime.utcnow()
    now_str = now.strftime("%Y%m%d%H%M")  # 201701310233
    clone_db_name = f"{db.name}_clone_{now_str}"
    backup_db_name = f"{db.name}_backup_{now_str}"

    clone_db = _get_db(db)
    clone_db.name = clone_db_name

    backup_db = _get_db(db)
    backup_db.name = backup_db_name

    # clone db
    l.info("clone %s to %s", db.name, clone_db_name)
    db.duplicate(clone_db_name)

    # backup the duplicated db using the cloned database
    l.info("duplicate %s to %s", clone_db_name, backup_db_name)
    clone_db.duplicate(backup_db_name)

    l.info("start applying migration scripts on clone %s", clone_db_name)
    try:
        l.debug("apply versions:%s", versions)
        _apply_versions(versions, clone_db)
    except Exception:  # roll back in any event of exception
        l.exception("migrations failed on %s", clone_db.name)
        return False, None, None
    else:
        l.info("migration success on %s", clone_db.name)
        return True, clone_db, backup_db


def _get_db(other_db: DB):
    return DB(other_db.host, other_db.port, other_db.username, other_db.password, other_db.name)


def _apply_versions(versions: [Version], db: DB):
    with db.get_session() as session:
        for version in versions:
            l.debug("start apply version:%s", version)

            try:
                if version.before_migrate:
                    l.debug("run %s before %s", version.before_migrate, version)
                    version.before_migrate(session)

                if version.sql_text:
                    session.execute(version.sql_text)
                elif version.sql_file:
                    db_connection = db.get_db_connection()
                    bash_command = f'mysql {db_connection} {db.name} < {version.sql_file}'
                    subprocess.check_output(bash_command, shell=True)

                schema_version = SchemaVersion(version_code=version.version_code,
                                               comment=version.comment)

                session.add(schema_version)

                session.commit()

                if version.after_migrate:
                    l.debug("run %s after %s", version.after_migrate, version)
                    version.after_migrate(session)

            except:
                l.exception("fail to apply version:%s", version)
                session.rollback()
                raise
            else:
                l.debug("version %s applied successfully", version)


def _finish_migration(clone_db, backup_db, db) -> bool:
    """
    to be called when the migration is successful on clone_db
    Rename the clone db to actual db (should be fast)
    If failed, restore the backup db to the actual db (using mysqldump to be safe)
    """
    l.debug("drop %s", db.name)
    db.drop()

    try:
        l.debug("duplicate %s -> %s", clone_db.name, db.name)
        clone_db.duplicate(db.name)
        l.debug("finish_migration success")
        return True
    except Exception:
        l.exception("duplicate clone db to original db fail. Duplicate backup db to original db")
        backup_db.duplicate(db.name)
        return False

# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
from   contextlib import contextmanager
import logging
import os.path
import queue
import re
import shutil
import sqlite3
import sys
import time
from   typing import Iterable, Tuple

from abus.cornelib import schapp_upgrade
from abus.rebuild import find_index_files, find_compressed_backups

class connect:
   def __init__(self, database_path, archive_root_path, allow_create=False):
      """
      Returns an object for the index database.

      :param database_path:
      :param allow_create: whether blank database should be created if `database_path` does not exist.
      :rtype: Database
      """
      self.db= Database(database_path, archive_root_path, allow_create)
   def __enter__(self):
      return self.db
   def __exit__(self, exc_type, exc_val, exc_tb):
      self.db.close()

class Database(object):
   def __init__(self, database_path, archive_root_path, allow_create):
      self.dbpath= database_path
      existed= os.path.exists(database_path)
      if not existed and not allow_create:
         raise RuntimeError("could not find database "+database_path)
      self.connection_pool_size= 0
      self.connection_pool= queue.Queue()
      self._set_connection_pool_size(1)
      self._check_schema(archive_root_path)
   def close(self):
      self._set_connection_pool_size(0)

   def _set_connection_pool_size(self, n):
      while self.connection_pool_size < n:
         conn= sqlite3.connect(self.dbpath, timeout=60, check_same_thread=False)
         conn.isolation_level= None # autocommit
         conn.execute("PRAGMA synchronous=OFF")
         self.connection_pool.put(conn)
         self.connection_pool_size += 1
      while self.connection_pool_size > n:
         self.connection_pool.get().close()
         self.connection_pool_size -= 1

   @contextmanager
   def _get_connection(self):
      """
      Returns a connection object from the pool with context manager.

      :rtype:sqlite3.Connection
      """
      conn= self.connection_pool.get()
      try:
         yield conn
      finally:
         self.connection_pool.put(conn)

   def _check_schema(self, archive_root_path):
      abus_src_dir= os.path.dirname(__file__)
      schema_file_name_pattern= re.compile(r"schema-([0-9]+)[.]sql")
      matches= ((schema_file_name_pattern.match(direntry.name), direntry.path)
                for direntry in os.scandir(abus_src_dir))
      target_schema, schema_file_path = max((int(m.group(1)),p) for m,p in matches if m)
      abus_version_pattern= re.compile(r"v([0-9]+)$")
      with open(schema_file_path) as stream:
         first_line= stream.readline()
         abus_version= abus_version_pattern.search(first_line).group(1)
      target_version= "{}.{}".format(target_schema, abus_version)

      with self._get_connection() as conn:
         try:
            current_version= conn.execute("select current_version from _database_version").fetchall()[0][0]
         except sqlite3.OperationalError as e:
            # did not have version table in versions <= 2.4, finding out manually which one it is
            tables= set(conn.execute("select name from sqlite_master where type='table'").fetchall())
            if ("completed_run",) in tables:
               current_version= "2"
            elif ("run",) in tables:
               current_version= "1"
            else:
               current_version= "0"
      current_schema= int(current_version.split(".")[0])
      if current_version == target_version:
         return
      if current_schema > target_schema:
         raise RuntimeError("ABuS {} is an older version than index database {}".format(abus_version, current_version))
      if 0 < current_schema < target_schema:
         upgrade_script_path= "{}/upgrade-{}.sql".format(abus_src_dir, current_schema)
      else:
         upgrade_script_path= None

      with self._take_backup():
         with self._get_connection() as conn:
            logging.info("index database needs upgrading")
            print("index database needs upgrading - this may take a while", file=sys.stderr)
            schapp_upgrade(conn, target_version, schema_file_path, upgrade_script_path)
            if 0 < current_schema < 3:
               # need to fill-in new columns from archive directory scan
               logging.info("reconstructing new index data")
               print("reconstructing new index data", file=sys.stderr)
               data= ((archive_dir, run_name) for run_name,archive_dir in find_index_files(archive_root_path))
               conn.executemany("update run set archive_dir= ? where run_name = ?", data)
               data= ((checksum,) for checksum in find_compressed_backups(archive_root_path))
               conn.executemany("update location set is_compressed= 1 where checksum = ?", data)

   @contextmanager
   def _take_backup(self):
      """Context manager that creates a backup copy of the database and
      restores or deletes it on exit
      depending on whether an exception has been raised"""
      connection_pool_size= self.connection_pool_size
      self._set_connection_pool_size(0)
      backup= self.dbpath + ".backup"
      logging.info("taking backup of index database")
      shutil.copyfile(self.dbpath, backup)
      self._set_connection_pool_size(1)
      try:
         yield
      except:
         self._set_connection_pool_size(0)
         logging.info("index database upgrade failed, restoring backup")
         shutil.copyfile(backup, self.dbpath)
         os.unlink(backup)
         raise
      else:
         os.unlink(backup)
         self._set_connection_pool_size(connection_pool_size)

   def _make_runname(self, timestamp):
      tm= time.localtime(timestamp)
      # format chosen to make the run name a "word" in most editors:
      return time.strftime("%Y_%m_%d_%H%M", tm)

   def open_backup_run(self, archive_dir):
      run_name= self._make_runname(time.time())
      with self._get_connection() as conn:
         n= conn.execute("select count(*) from run where run_name=?", [run_name]).fetchall()[0][0]
      if n>0:
         raise RuntimeError("There is already a run with the current timestamp (minute granularity")
      conn.execute("insert into run(run_name, is_complete, archive_dir) values(?,0,?)", [run_name, archive_dir])
      return run_name

   def complete_backup_run(self, run_name):
      with self._get_connection() as conn:
         cur= conn.execute("update run set is_complete= 1 where run_name = ?", [run_name])
         if cur.rowcount!=1:
            raise RuntimeError("could not complete run "+run_name)

   def get_archivedir_usage(self):
      with self._get_connection() as conn:
         rows= conn.execute("select archive_dir, count(*) as n from location group by archive_dir")
         counts= {archive_dir:n for archive_dir,n in rows}
         rows= conn.execute("select archive_dir, count(*) as n from run group by archive_dir")
         for archive_dir, n in rows:
            counts[archive_dir]= counts.get(archive_dir, 0) + n
         return counts

   def lookup_checksum(self, st_dev, st_ino, timestamp):
      with self._get_connection() as conn:
         for (checksum,) in conn.execute("""
               select checksum
                  from checksum_cache
                  where dev=? and ino=? and timestamp=?""", (st_dev, st_ino, timestamp)):
            return checksum
         return None

   def remember_checksum(self, st_dev, st_ino, timestamp, checksum):
      with self._get_connection() as conn:
         dbg_existed= conn.execute("""select count(*) from checksum_cache
            where dev=? and ino=?""", (st_dev, st_ino)).fetchall()[0][0]
         cur= conn.execute("""
            update checksum_cache
            set timestamp= ?, checksum= ?
            where dev=? and ino=?""", (timestamp, checksum, st_dev, st_ino))
         if cur.rowcount==0:
            conn.execute("insert into checksum_cache(timestamp, checksum, dev, ino) values(?,?,?,?)",
               (timestamp, checksum, st_dev, st_ino))

   def have_checksum(self, checksum: str) -> bool:
      """whether there is an existing backup for the given checksum"""
      with self._get_connection() as conn:
         rs= conn.execute("select archive_dir from location where checksum=?", [checksum]).fetchall()
      return len(rs)==1

   def remember_archivedir(self, checksum, archive_dir_rel, is_compressed):
      with self._get_connection() as conn:
         conn.execute("insert into location(checksum, archive_dir, is_compressed) values(?,?,?)",
                      (checksum, archive_dir_rel, is_compressed))

   def add_backup_entry(self, run_name, path, timestamp, checksum):
      with self._get_connection() as conn:
         conn.execute("""insert into content(run_name, path, timestamp, checksum)
            values(?,?,?,?)""", (run_name, path, timestamp, checksum))

   def get_all_backup_files(self):
      """
      Returns list of all checksums in backup

      :rtype: ((checksum, archive_dir, is_compressed))
      """
      with self._get_connection() as conn:
         return conn.execute("select checksum, archive_dir, is_compressed from location")

   def get_all_runs(self):
      """
      Returns list of all runs in DB

      :rtype: ((run_name, archive_dir))
      """
      with self._get_connection() as conn:
         return conn.execute("select run_name, archive_dir from run")

   def get_archive_contents(self, patterns, cutoff_date, show_all: bool) -> Iterable[Tuple[str,float,str,str,int]]:
      """
      Returns content of archive for listing or restore.

      :param patterns: glob-operator patterns for path to match any of
      :type patterns: string list
      :param cutoff_date: time from which files are ignored or None
      :type cutoff_date: time.time() format
      :param show_all: whether all files should be returned rather than just those from the latest run
      :returns: (path, timestamp, archive_dir, checksum, is_compressed)s
      """
      with self._get_connection() as conn:
         sql= "select distinct path, min(timestamp), archive_dir, content.checksum, is_compressed from content"
         sql_args= []
         where_clauses= [] # to be built now but added later
         where_args= []

         if cutoff_date is None:
            if show_all:
               # show all without cutoff date is just everything
               pass
            else:
               # show one without cutoff means latest run
               where_clauses.append("run_name = (select max(run_name) from content)")
         else:
            if show_all:
               # show all with cutoff date
               where_clauses.append("timestamp <= ?")
               where_args.append(cutoff_date)
            else:
               # show one with cutoff date requires subquery for the latest
               sql += " join (select path as p, max(timestamp) as t from content "
               sql +=       " where timestamp <= ?"
               sql_args.append(cutoff_date)
               sql +=       " group by path) as latest"
               sql +=  " on path = latest.p and timestamp = latest.t"

         sql += " join location on location.checksum = content.checksum"

         if patterns:
            where_clauses.append("("
               +" or ".join("path glob ?" for x in patterns)
               +")")
            where_args.extend(patterns)

         if where_clauses:
            sql += " where " + " and ".join(where_clauses)
            sql_args.extend(where_args)

         sql += " group by path, archive_dir, content.checksum"
         sql += " order by path, min(timestamp) desc"
         yield from conn.execute(sql, sql_args)

   def rebuild_location_table(self, actual_content_list: Iterable[Tuple[str, str, bool]]) -> Tuple[int, int, int]:
      """
      Adjusts the location table to reflect data in dictionary.

      :param actual_content_list: (checksum, archive_dir, is_compressed)s of required state
      :type actual_content_list: iterable
      :returns: counts: (updates, inserts, deletes)
      """
      actual_content= {checksum:(archive_dir,is_compressed)
                       for checksum,archive_dir,is_compressed in actual_content_list}
      updates= []
      deletes= []
      with self._get_connection() as conn:
         for checksum,archive_dir,is_compressed in conn.execute("select checksum, archive_dir, is_compressed from location"):
            # leaving actual_content with all records that are not in database:
            actual_values= actual_content.get(checksum)
            if actual_values is None:
               deletes.append((checksum,))
            else:
               del actual_content[checksum]
               if actual_values!=(archive_dir,is_compressed!=0):
                  archive_dir, is_compressed= actual_values
                  updates.append((archive_dir, is_compressed, checksum))
         conn.executemany("delete from location where checksum = ?", deletes)
         conn.executemany("update location set archive_dir= ?, is_compressed= ? where checksum = ?", updates)
         data= ((k,a,b) for k,(a,b) in actual_content.items())
         conn.executemany("insert into location(checksum,archive_dir,is_compressed) values(?,?,?)", data)
      return len(updates), len(actual_content), len(deletes)

   def rebuild_content(self, run_name, run_archive_dir, checksum_timestamp_path_rows):
      """
      Replaces all rows in content table for a given run_name with the given values.

      :param run_name:Run whose content rows will all be deleted and then replaced.
      :type run_name: str
      :param checksum_timestamp_path_rows: New rows (without run_nam column itself)
      :type checksum_timestamp_path_rows: (str,str,str)
      :return: number of records changed, added, deleted
      :rtype: tuple
      """
      typed_ctp= ((c,float(t),p) for c,t,p in checksum_timestamp_path_rows)
      with self._get_connection() as conn:
         conn.execute("""create temp table if not exists required_content(
            path text not null primary key,
            timestamp float not null,
            checksum text not null)""")
         conn.execute("delete from required_content")
         conn.executemany("insert into required_content(checksum, timestamp, path) values(?,?,?)", typed_ctp)
         cur= conn.execute("delete from required_content where checksum='error'")
         run_is_complete= cur.rowcount==0
         changed= conn.execute("""select count(*)
            from content join required_content on content.path=required_content.path
               and (content.checksum!=required_content.checksum or content.timestamp!=required_content.timestamp)
            where content.run_name=?""", [run_name]).fetchall()[0][0]
         new= conn.execute("""select count(*)
            from required_content left join content on content.path=required_content.path and content.run_name=?
            where content.path is null""", [run_name]).fetchall()[0][0]
         removed= conn.execute("""select count(*)
            from content left join required_content on required_content.path = content.path
            where content.run_name=? and required_content.path is null""", [run_name]).fetchall()[0][0]
         conn.execute("delete from content where run_name=?", [run_name])
         conn.execute("""insert into content(run_name, path, timestamp, checksum)
            select ?, path, timestamp, checksum from required_content""", [run_name])
         exists= conn.execute("select archive_dir, is_complete from run where run_name=?", [run_name]).fetchall()
         if len(exists)==0:
            new += 1
            conn.execute("""insert into run(run_name, archive_dir, is_complete) values(?,?,?)""",
                         (run_name, run_archive_dir, run_is_complete))
         elif exists[0]!=(run_archive_dir, int(run_is_complete)):
            changed += 1
            conn.execute("""update run set archive_dir= ?, is_complete= ? where run_name=?""",
                         (run_archive_dir, run_is_complete, run_name))
      return changed, new, removed

   def remove_runs(self, other_than: Iterable[str]):
      """
      Removes all runs from content and completed_runs, whose run_name is not in `other_than`

      :return: number of deleted rows
      """
      other_than= list(other_than)
      place_holders= ",?" * len(other_than)
      n= 0
      with self._get_connection() as conn:
         for table in "run", "content":
            stmt= "delete from "+table+" where run_name not in("+place_holders[1:]+")"
            cur= conn.execute(stmt, other_than)
            n += cur.rowcount
      return n

   def remove_location_entry(self, checksum):
      """
      Reflects in DB that a backup file has been deleted

      :param checksum: of deleted location file
      """
      with self._get_connection() as conn:
         conn.execute("delete from location where checksum=?", [checksum])

   def get_purgeable_backups(self, rounders):
      """
      Returns list of backup files that are superfluous and to be deleted.

      :param: rounders: retention policy definition: (rounder,age)-list
      :return:  (checksum, archive_dir, path, timestamp)-list
      """
      case_clause= "case " +"when timestamp >= ? then round(timestamp/?)*? "*len(rounders) +"else 0 end"
      now= time.time()
      params= []
      for r,a in sorted(rounders):
         params.extend([now-a*86400, r*86400, r*86400])

      with self._get_connection() as conn:
         cur= conn.execute("""
            with SLOTTED as(
                  select distinct path, timestamp, """+case_clause+""" as slot
                  from content
                  )
               ,KEEP_VERSIONS as(
                  select path, max(timestamp) as timestamp
                  from SLOTTED
                  group by path, slot
                  )
               ,KEEP_CHECKSUMS as(
                  select distinct content.checksum
                  from content join KEEP_VERSIONS on content.path = KEEP_VERSIONS.path
                     and content.timestamp = KEEP_VERSIONS.timestamp
                  )
               ,PURGE as(
                  select distinct location.checksum, location.archive_dir, content.path, content.timestamp
                  from location
                     join content on content.checksum = location.checksum
                  where location.checksum not in(select checksum from KEEP_CHECKSUMS)
                  )
            select *
            from PURGE
            order by checksum, path, timestamp
            """, params)
         return cur.fetchall()

   def purge_runs(self, run_names: Iterable[str]) -> None:
      """
      Purges given runs after checking that they can be purged.
      """
      run_names= set(run_names)
      run_names.intersection_update(r for r,a in self.get_purgeable_runs())
      run_names= list(run_names)
      if run_names:
         place_holders= ",?" * len(run_names)
         with self._get_connection() as conn:
            for table in ("run", "content"):
               conn.execute("delete from {} where run_name in({})".format(table, place_holders[1:]), run_names)

   def get_purgeable_runs(self) -> Iterable[Tuple[str,str]]:
      """
      Returns runs that can be purged.

      :returns: (run_name, archive_dir)s
      """
      with self._get_connection() as conn:
         return conn.execute("""
            select run_name, archive_dir
            from run
            where run_name not in(select run_name
               from content join location on location.checksum = content.checksum)""")

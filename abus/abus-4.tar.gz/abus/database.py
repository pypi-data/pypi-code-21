# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import logging
import os.path
import queue
import sqlite3
import time
from contextlib import contextmanager

class connect:
   def __init__(self, database_path, allow_create=False):
      """
      Returns an object for the index database.

      :param database_path:
      :param allow_create: whether blank database should be created if `database_path` does not exist.
      :rtype: Database
      """
      self.db= Database(database_path, allow_create)
   def __enter__(self):
      return self.db
   def __exit__(self, exc_type, exc_val, exc_tb):
      self.db.close()

class Database(object):
   def __init__(self, database_path, allow_create):
      self.path= database_path
      self.connection_pool_size= 1
      self.connection_pool= queue.Queue()
      existed= os.path.exists(database_path)
      if not existed and not allow_create:
         raise RuntimeError("could not find database "+database_path)
      for _ in range(self.connection_pool_size):
         conn= sqlite3.connect(database_path, timeout=60, check_same_thread=False)
         conn.isolation_level= None # autocommit
         conn.execute("PRAGMA synchronous=OFF")
         self.connection_pool.put(conn)
      if not existed:
         self._create_tables()
   def close(self):
      for _ in range(self.connection_pool_size):
         self.connection_pool.get().close()

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

   def _create_tables(self):
      with self._get_connection() as conn:
         # An entry in completed_run indicates that the run completed without errors
         # and that `content` contains a complete list of files for the run, even
         # if some of the files have been purged since.
         conn.execute("create table completed_run(run_name text not null primary key)")

         conn.execute("""create table content(
            run_name text not null,
            path text not null,
            timestamp float not null,
            checksum text not null)""")
         conn.execute("create unique index content_pk on content(run_name, path)")

         conn.execute("""create table location(
            checksum text not null primary key,
            archive_dir text not null)""")
         conn.execute("create index location_archivedir on location(archive_dir)")

         conn.execute("""create table checksum_cache(
            dev int not null,
            ino int not null,
            timestamp float not null,
            checksum text not null)""")
         conn.execute("create unique index checksum_cache_pk on checksum_cache(dev, ino)")

   def _make_runname(self, timestamp):
      tm= time.localtime(timestamp)
      # format chosen to make the run name a "word" in most editors:
      return time.strftime("%Y_%m_%d_%H%M", tm)

   def open_backup_run(self):
      run_name= self._make_runname(time.time())
      with self._get_connection() as conn:
         n= conn.execute("select count(*) from content where run_name=?", [run_name]).fetchall()[0][0]
      if n>0:
         raise RuntimeError("There is already a run with the current timestamp (minute granularity")
      return run_name

   def complete_backup_run(self, run_name):
      with self._get_connection() as conn:
         cur= conn.execute("insert into completed_run values(?)", [run_name])
         if cur.rowcount!=1:
            raise RuntimeError("could not complete run "+run_name)

   def get_archivedir_usage(self):
      with self._get_connection() as conn:
         rows= conn.execute("select archive_dir, count(*) as n from location group by archive_dir")
         return {archive_dir:n for archive_dir,n in rows}

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

   def lookup_archivedir(self, checksum):
      with self._get_connection() as conn:
         for (archive_dir,) in conn.execute("select archive_dir from location where checksum=?", [checksum]):
            return archive_dir
         return None

   def remember_archivedir(self, checksum, archive_dir_rel):
      with self._get_connection() as conn:
         conn.execute("insert into location(checksum, archive_dir) values(?,?)", (checksum, archive_dir_rel))

   def add_backup_entry(self, run_name, path, timestamp, checksum):
      with self._get_connection() as conn:
         conn.execute("""insert into content(run_name, path, timestamp, checksum)
            values(?,?,?,?)""", (run_name, path, timestamp, checksum))

   def get_archive_contents(self, patterns, cutoff_date, show_all):
      """

      :param patterns: like-operator patterns for path to match any of
      :type patterns: string list
      :param cutoff_date: time after which files are ignored or None
      :type cutoff_date: time.time() format
      :param show_all: whether all files should be returned rather than just those from the latest run
      :type show_all: bool
      :return: iterable of (path, timestamp, archive_dir, checksum)
      :rtype:
      """
      with self._get_connection() as conn:
         sql= "select distinct path, min(timestamp), archive_dir, content.checksum from content"
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

   def reconstruct_location(self, actual_content):
      """
      Adjusts the location table to reflect data in dictionary.

      :param actual_content: checksum -> archive_dir dict of required state. The contents will be changed.
      :type actual_content: dict
      """
      updates= []
      deletes= []
      with self._get_connection() as conn:
         for checksum,archive_dir in conn.execute("select checksum, archive_dir from location"):
            # leaving actual_content with all chacksums that are not in database:
            actual_value= actual_content.get(checksum)
            if actual_value is None:
               deletes.append((checksum,))
            else:
               del actual_content[checksum]
               if actual_value!=archive_dir:
                  updates.append((actual_value,checksum))
         conn.executemany("delete from location where checksum = ?", deletes)
         conn.executemany("update location set archive_dir= ? where checksum = ?", updates)
         conn.executemany("insert into location(checksum,archive_dir) values(?,?)", actual_content.items())
      return len(actual_content), len(deletes), len(updates)

   def reconstruct_content(self, run_name, checksum_timestamp_path_rows):
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
         conn.execute("""create temp table if not exists reconstruct(
            path text not null primary key,
            timestamp float not null,
            checksum text not null)""")
         conn.execute("delete from reconstruct")
         conn.executemany("insert into reconstruct(checksum, timestamp, path) values(?,?,?)", typed_ctp)
         cur= conn.execute("delete from reconstruct where checksum='error'")
         run_is_complete= cur.rowcount==0
         changed= conn.execute("""select count(*)
            from content join reconstruct on content.path=reconstruct.path
               and (content.checksum!=reconstruct.checksum or content.timestamp!=reconstruct.timestamp)
            where content.run_name=?""", [run_name]).fetchall()[0][0]
         new= conn.execute("""select count(*)
            from reconstruct left join content on content.path=reconstruct.path and content.run_name=?
            where content.path is null""", [run_name]).fetchall()[0][0]
         removed= conn.execute("""select count(*)
            from content left join reconstruct on reconstruct.path = content.path
            where content.run_name=? and reconstruct.path is null""", [run_name]).fetchall()[0][0]
         conn.execute("delete from content where run_name=?", [run_name])
         conn.execute("""insert into content(run_name, path, timestamp, checksum)
            select ?, path, timestamp, checksum from reconstruct""", [run_name])
         exists= len(conn.execute("select * from completed_run where run_name=?", [run_name]).fetchall())>0
         if run_is_complete and not exists:
            new += 1
            conn.execute("""insert into completed_run(run_name) values(?)""", [run_name])
         elif not run_is_complete and exists:
            removed += 1
            conn.execute("""delete from completed_run where run_name=?""", [run_name])
      return changed, new, removed

   def remove_runs(self, other_than):
      """
      Removes all runs from content and completed_runs, whose run_name is not in `other_than`

      :return: number of deleted rows
      """
      place_holders= ",?" * len(other_than)
      n= 0
      with self._get_connection() as conn:
         for table in "completed_run", "content":
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

   def try_purge_run(self, run_name):
      """
      Purges given run after checking that it can be purged.

      :return: whether run has been purged
      """
      with self._get_connection() as conn:
         n= conn.execute("""select count(*)
            from content join location on location.checksum=content.checksum
            where content.run_name=?""", [run_name]).fetchall()[0][0]
         if n==0:
            conn.execute("""delete from completed_run where run_name=?""", [run_name])
            conn.execute("""delete from content where run_name=?""", [run_name])
            return True
         return False

# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import logging
import os
from abus.testbase import AbusTestBase
from abus import backup
from abus import database
from abus import main

class UpgradeTests(AbusTestBase):
   def check_tables_and_columns(self):
      tables= self.executesql("select name,sql from sqlite_master where type='table'")
      schema= {}
      for (name,sql) in tables:
         joined= sql.replace("\n", " ")
         create,bar,column_defs_string= joined.partition("(")
         column_defs= column_defs_string.split(",")
         columns= set(s.split()[0] for s in column_defs)
         columns.difference_update({"constraint"}) # not a proper column
         schema[name]= columns
      expected_schema= {
         "run": {"run_name", "is_complete", "archive_dir"},
         "content": {"run_name", "path", "timestamp", "checksum"},
         "location": {"checksum", "archive_dir", "is_compressed"},
         "checksum_cache": {"dev", "ino", "timestamp", "checksum"},
         "_database_version": {"current_version"},
      }
      self.assertDictEqual(schema, expected_schema)
      tbl= self.executesql("select * from _database_version")
      self.assertEqual(tbl, [("3.6",)])

   def test_create(self):
      self.setup_directories()
      self.check_tables_and_columns()

   def upgrade_and_check_tables_columns_and_rebuilt_data(self):
      """For upgrades from schema <3, generates a few archive files, whose names must match data
      created by caller, then upgrades and checks that is_compressed and run.archive_dir are
      reconstructed from the filesnames."""
      for f in ["/47/11/2017_10_27_0810.lst",
                "/34/15/2015_06_08_1200.lst",
                "/08/15/32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2",
                "/13/22/f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa.z",
               ]:
         abspath= self.archivedir+f
         os.makedirs(os.path.dirname(abspath), exist_ok=True)
         with open(abspath, "w"): pass
      with database.connect(self.databasepath, self.archivedir):
         pass
      self.check_tables_and_columns()
      tbl= self.executesql("select run_name, archive_dir, is_complete from run")
      self.assertEqual(set(tbl), {("2017_10_27_0810","47/11",1),("2015_06_08_1200","34/15",0)})
      tbl= self.executesql("select checksum, is_compressed from location")
      self.assertEqual(set(tbl), {("32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2", 0),
                                  ("f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa", 1),})

   def test_upgrade_v1(self):
      self.setup_directories()
      os.unlink(self.databasepath)
      with open(os.path.dirname(__file__)+"/schema-1.sql") as stream:
         schema_str= stream.read()
      with self.get_direct_db_connection() as conn:
         for sql in schema_str.split(";"):
            conn.execute(sql)
         conn.executemany("insert into run(run_name, timestamp)values(?,?)",
                          [("2017_10_27_0810", 56), ("2015_06_08_1200", None)])
         conn.executemany("insert into location(checksum,archive_dir) values(?,?)",
                          [("32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2", "08/15"),
                           ("f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa", "13/22")])
      self.upgrade_and_check_tables_columns_and_rebuilt_data()

   def _create_v2_db(self):
      self.setup_directories()
      os.unlink(self.databasepath)
      with self.get_direct_db_connection() as conn:
         conn.execute("""
            create table content(
               run_name text not null,
               path text not null,
               timestamp float not null,
               checksum text not null)""")
         conn.execute("""
            create table location(
               checksum text not null primary key,
               archive_dir text not null)""")
         conn.execute("""
            create table checksum_cache(
               dev int not null,
               ino int not null,
               timestamp float not null,
               checksum text not null)""")
         conn.execute("""
            create table completed_run(
               run_name text not null primary key)""")
         conn.execute("insert into completed_run(run_name) values(?)", ("2017_10_27_0810",))
         conn.executemany("insert into content(run_name, path, timestamp, checksum) values(?,?,?,?)",
                          [("2017_10_27_0810", "c:/some/path", 56, "32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2"),
                           ("2015_06_08_1200", "C:/bla/bla",   97, "f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa"),
                           ])
         conn.executemany("insert into location(checksum,archive_dir) values(?,?)",
                          [("32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2", "08/15"),
                           ("f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa", "13/22")])

   def test_upgrade_v2(self):
      self._create_v2_db()
      self.upgrade_and_check_tables_columns_and_rebuilt_data()

   def test_recover_from_upgrade_error(self):
      self._create_v2_db()
      with self.get_direct_db_connection() as conn:
         conn.execute("""alter table location rename to ex_location""")
         conn.execute("""
            create table location(
               checksum text not null,
               archive_dir text not null)""")
         conn.execute("""insert into location select checksum, archive_dir from ex_location""")
         # introducing unique constraint violation after upgrade:
         conn.execute("""insert into location select checksum, archive_dir from ex_location""")

      checksum_before= backup.calculate_checksum(self.databasepath)
      with self.assertLogs() as logs:
         rc= main.main(["test", "-f", self.configfile])
         self.assertEqual(rc, 4)
         self.assertTrue(any(r.levelno==logging.ERROR and "sqlite3.IntegrityError" in r.msg
                             for r in logs.records))
         self.assertTrue(any("index database upgrade failed, restoring backup" in r.msg
                             for r in logs.records))
      checksum_after= backup.calculate_checksum(self.databasepath)
      self.assertEqual(checksum_after, checksum_before)

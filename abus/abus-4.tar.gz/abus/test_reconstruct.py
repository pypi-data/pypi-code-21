# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import os
import sqlite3
import unittest
from abus import config
from abus import crypto
from abus import database
from abus import main
from abus import reconstruct
from abus.testbase import AbusTestBase

class ReconstructionTests(AbusTestBase):
   def _get_database_contents(self):
      """
      reads DB into sets

      :return: set with completed_run, content, and location rows (distinguishable by their lengths)
      """
      queries= ["select run_name from completed_run",
                "select run_name, path, timestamp, checksum from content",
                "select checksum, archive_dir from location",
                ]
      result= set()
      with self.get_direct_db_connection() as conn:
         for q in queries:
            result.update(conn.execute(q))
      return result

   def test_reconstruct_e2e(self):
      self.setup_multiple_backups()
      before= self._get_database_contents()
      os.unlink(self.databasepath)
      with database.connect(self.databasepath, allow_create=True):
         pass
      rc= main.main(["test", "-f", self.configfile, "--reconstruct"])
      self.assertEqual(rc, 0)
      after= self._get_database_contents()
      self.assertEqual(after, before)

   def test_timestamp_string_gets_converted_properly(self):
      # timestamp stores as 1508532089.993785 if you let sqlite3 convert
      self.setup_directories()
      with database.connect(self.databasepath) as db:
         db.reconstruct_content("name", [['checksum', '1508532089.9937847', 'path']])
      t= self.executesql("select timestamp from content")
      self.assertEqual(len(t), 1)
      self.assertEqual(t[0][0], 1508532089.9937847)

   records= [
         ("good",),
         ("good", "/home/somepath", 1507934953.0, "f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa"),
         ("good", "/home/other.path", 1507934453.0, "bcf1a11950d1a1dd1bbe6f3b97cbeb431653e2ad43e1ab42c9ea13f4153764a8"),
         ("incomplete",),
         ("incomplete", "/home/somepath", 1290000000.0, "32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2"),
         ("incomplete", "/home/path", 1290003000.0, "498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f"),
         ("error", "/home/somepath", 1507934953.0, "f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa"),
         ("32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2", "47/11"),
         ("f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa", "47/11"),
         ("bcf1a11950d1a1dd1bbe6f3b97cbeb431653e2ad43e1ab42c9ea13f4153764a8", "47/11"),
      ]
   def run_reconstruction(self, records, expected_entry_stats, expected_location_stats):
      """
      Performs a complete reconstruction run, filling the database from the parameters first.

      :param records: records to for initialising database
      :type records: iterable
      :param expected_entry_stats: (n_changed, n_added, n_deleted) for content/run
      :param expected_location_stats: (n_changed, n_added, n_deleted) for location
      """
      self.setup_directories()
      d= self.archivedir + "/47/11"
      os.makedirs(d)
      with crypto.open_txt(d+"/incomplete.lst", "w", self.password) as f:
         print("32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2 1290000000.0 /home/somepath", file=f)
         print("498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f 1290003000.0 /home/path", file=f)
      with crypto.open_txt(d+"/error.lst", "w", self.password) as f:
         print("f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa 1507934953.0 /home/somepath", file=f)
         print("error 0 /home/other.path", file=f)
      with crypto.open_txt(d+"/good.lst", "w", self.password) as f:
         print("f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa 1507934953.0 /home/somepath", file=f)
         print("bcf1a11950d1a1dd1bbe6f3b97cbeb431653e2ad43e1ab42c9ea13f4153764a8 1507934453.0 /home/other.path", file=f)
      with crypto.open_txt(d+"/32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2", "w", self.password) as f:
         f.write("data")
      with crypto.open_txt(d+"/f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa", "w", self.password) as f:
         f.write("data")
      with crypto.open_txt(d+"/bcf1a11950d1a1dd1bbe6f3b97cbeb431653e2ad43e1ab42c9ea13f4153764a8.z", "w", self.password) as f:
         f.write("compressed data")
      with self.get_direct_db_connection() as conn:
         run_records= [t for t in records if len(t)==1]
         conn.executemany("insert into completed_run(run_name) values(?)", run_records)
         content_records= (t for t in records if len(t)==4)
         conn.executemany("insert into content(run_name, path, timestamp, checksum) values(?,?,?,?)", content_records)
         location_records= (t for t in records if len(t)==2)
         conn.executemany("insert into location(checksum, archive_dir) values(?,?)", location_records)
      cfg= config.Configuration(["test", "-f", self.configfile])
      entry_stats= reconstruct.reconstruct_entries(cfg)
      location_stats= reconstruct.reconstruct_location(cfg)
      expected_db= set(self.records)
      actual= self._get_database_contents()
      self.assertEqual(actual, expected_db)
      self.assertEqual(entry_stats, expected_entry_stats)
      self.assertEqual(location_stats, expected_location_stats)

   def test_reconstruction_no_changes(self):
      r= self.records
      self.run_reconstruction(r, expected_entry_stats=(0,0,0), expected_location_stats=(0,0,0))

   def test_reconstruction_missing_record(self):
      for i in range(8):
         with self.subTest(i=i):
            r= self.records[:i] + self.records[i+1:]
            self.run_reconstruction(r,
                                    expected_entry_stats=(0,1 if i<7 else 0,0),
                                    expected_location_stats=(0,0 if i<7 else 1,0))

   def test_reconstruction_changed_record(self):
      changes= [
         (1, "good", "/home/somepath", 1111111111.0, "f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa"),
         (1, "good", "/home/somepath", 1507934953.0, "caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5"),
         (2, "good", "/home/other.path", 1111111111.0, "bcf1a11950d1a1dd1bbe6f3b97cbeb431653e2ad43e1ab42c9ea13f4153764a8"),
         (2, "good", "/home/other.path", 1507934453.0, "caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5"),
         (4, "incomplete", "/home/somepath", 1111111111.0, "32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2"),
         (4, "incomplete", "/home/somepath", 1290000000.0, "caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5"),
         (5, "incomplete", "/home/path", 1111111111.0, "498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f"),
         (5, "incomplete", "/home/path", 1290003000.0, "caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5"),
         (6, "error", "/home/somepath", 1111111111.0, "f8e920545e99cdc9bbc2650eb8282344e8971a7ff0c397c91355d0fcaf6c61fa"),
         (6, "error", "/home/somepath", 1507934953.0, "caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5"),
         (7, "32b772fb46ad237546d030bfd880d48220c57c555912f24873debfe8d0505ba2", "08/15"),
         ]
      for iteration, change in enumerate(changes):
         with self.subTest(i=iteration):
            r= list(self.records)
            i= change[0]
            r[i]= change[1:]
            self.run_reconstruction(r,
                                    expected_entry_stats=(1 if i<7 else 0,0,0),
                                    expected_location_stats=(0 if i<7 else 1,0,0))

   def test_reconstruction_extra_location(self):
      r= self.records + [
            ("caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5", "08/15"),
         ]
      self.run_reconstruction(r, expected_entry_stats=(0,0,0), expected_location_stats=(0,0,1))

   def test_reconstruction_extra_enry(self):
      r= self.records + [
            ("good", "/home/completely.different", 1507934453.0, "caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5"),
         ]
      self.run_reconstruction(r, expected_entry_stats=(0,0,1), expected_location_stats=(0,0,0))

   def test_reconstruction_extra_run(self):
      r= self.records + [
            ("extra",),
            ("extra", "/home/completely.different", 1507934453.0, "caf956254790e0f71ad80e57b5a69a61183ab2cf9f5b75c406a02d29d6ba3eb5"),
         ]
      self.run_reconstruction(r, expected_entry_stats=(0,0,2), expected_location_stats=(0,0,0))


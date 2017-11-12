# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import gzip
import logging
import os
import shutil
import sqlite3
import unittest.mock
from abus import backup
from abus import crypto
from abus import main
from abus.testbase import AbusTestBase

class BackedUpHomedirTests(AbusTestBase):
   def test_simple_end_to_end_backup(self):
      self.setup_backup_with_well_known_checksums()

      # checking archive contents matches DB
      subdir,run_name = self.executesql("select archive_dir, run_name from run")[0]
      index_file_path_rel= subdir+"/"+run_name+".lst"
      expected_backupfiles= {"index.sl3", index_file_path_rel, run_name+".gz"}
      entries= self.executesql("""
         select path, archive_dir, location.checksum, is_compressed
         from content
            join location on location.checksum = content.checksum""")
      expected_backupfiles.update(a+"/"+c+(".z" if z else "") for p,a,c,z in entries)
      expected_backupfiles_abs= {self.archivedir+"/"+rel for rel in expected_backupfiles}
      actual= set(direntry.path.replace("\\","/")
                  for direntry in self.find_files(self.archivedir))
      self.assertEqual(actual, expected_backupfiles_abs)

      # checking archive contents matches what has been backed up
      # rs= e.g. ('C:/tmp/abushome/my_little_file', '40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880', 0)
      from_db= {(p, c+".z" if z else c) for p,a,c,z in entries}
      from_test= {(self.homedir+"/"+p, f) for p,f in self.expected_backups}
      self.assertEqual(from_db, from_test)

      # checking that index files matches
      with crypto.open_txt(self.archivedir+"/"+index_file_path_rel, "r", self.password) as f:
         index_entries= set(l.strip() for l in f)
      dbentries= set("{} {} {}".format(*row)
                     for row in self.executesql("select checksum, timestamp, path from content"))
      self.assertEqual(index_entries, dbentries)

      # checking that contents file matches
      with gzip.open(self.archivedir+"/"+run_name+".gz", "rt", encoding="UTF-8") as stream:
         lines= {l.strip() for l in stream}
      self.assertEqual(lines, expected_backupfiles)

      # decrypting backup
      my_litte_backup= [e for e in expected_backupfiles_abs if "/40aff2e" in e]
      self.assertEqual(len(my_litte_backup), 1)
      self.assertEqual(os.stat(my_litte_backup[0]).st_size, 256+80) # 80 for salt, init vector, and checksum
      with crypto.open_bin(my_litte_backup[0], "r", self.password) as f:
         blk= f.read(8192)
         self.assertEqual(len(blk), 256)
         self.assertEqual(blk, bytearray(range(256)))

   def test_error_prevents_closing_backup_run(self):
      self.setup_directories()
      self.create_homedir_file("unreadable",23)
      with unittest.mock.patch('abus.backup.make_backup_copy', side_effect=RuntimeError):
         rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 1)
      rs= self.executesql("select run_name, archive_dir, is_complete from run")
      self.assertEqual(len(rs), 1)
      run_name, archive_dir, is_complete = rs[0]
      self.assertEqual(is_complete, 0)
      index_file_path= self.archivedir+"/"+rs[0][1]+"/"+rs[0][0]+".lst"
      with crypto.open_txt(index_file_path, "r", self.password) as stream:
         contents= set(stream)
      error_line= "error 0 {}/unreadable\n".format(self.homedir)
      self.assertIn(error_line, contents)
      self.assertTrue(os.path.isfile(self.archivedir+"/"+run_name+".gz"))

   def test_changing_file_gets_backed_up_after_retry(self):
      self.setup_directories()
      self.create_homedir_file("myfile",23)
      def make_backup_copy_sideeffect(path, expected_checksum, backup_path, open_dst_function, password):
         self.create_homedir_file("myfile",97) # 1244d0711c6534ee79a6d3b82cea33b76e766e46cbca75791ac9fa3a30e365f3
      with unittest.mock.patch('time.sleep'):
         with unittest.mock.patch('abus.backup.make_backup_copy',
                                  wraps=backup.make_backup_copy,
                                  side_effect=make_backup_copy_sideeffect):
            rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)
      rs= self.executesql("select run_name, archive_dir, is_complete from run")
      self.assertEqual(len(rs), 1)
      _run_name, _archive_dir, is_complete = rs[0]
      self.assertEqual(is_complete, 1)
      rs= self.executesql("""select location.checksum
         from content join location on location.checksum = content.checksum""")
      self.assertEqual(len(rs), 1)
      self.assertEqual(rs[0][0], "1244d0711c6534ee79a6d3b82cea33b76e766e46cbca75791ac9fa3a30e365f3")

   def test_always_changing_file_causes_error_after_5_attempts(self):
      self.setup_directories()
      primes= iter([17,19,23,29,31,37,41])
      self.create_homedir_file("myfile", next(primes))
      def make_backup_copy_sideeffect(path, expected_checksum, backup_path, open_dst_function, password):
         self.create_homedir_file("myfile", next(primes))
      with unittest.mock.patch('time.sleep'):
         with unittest.mock.patch('abus.backup.make_backup_copy',
                                  wraps=backup.make_backup_copy,
                                  side_effect=make_backup_copy_sideeffect) as mock:
            rc= main.main(["test", "-f", self.configfile, "--backup"])
            self.assertEqual(mock.call_count, 5)
      self.assertEqual(rc, 1)
      rs= self.executesql("select is_complete from run")
      self.assertEqual(rs, [(0,)])
      rs= self.executesql("select * from location")
      self.assertEqual(rs, [])

   def test_bad_include_entry_does_not_stop_other_backups(self):
      """bug: read error on c:/users/*/documents causes unhandled exception and aborts whole backup"""
      self.setup_directories()
      # Appending bad [include]-entry happens to run it first and used to prevent homedir from being backed up
      with open(self.configfile, "a") as stream:
         stream.write("C:/Users/*/Desktop\n")
      self.create_homedir_file("a_file",23)
      rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 1)
      with self.get_direct_db_connection() as conn:
         rows= [conn.execute("select * from "+t).fetchall() for t in("content", "run", "location", "run where is_complete")]
      self.assertEqual(len(rows[0]), 1)
      self.assertEqual(len(rows[1]), 1)
      self.assertEqual(len(rows[2]), 1)
      self.assertEqual(len(rows[3]), 0)

   def test_archive_dirs_to_use(self):
      def go(initial_usage: dict, expected_result: list):
         i= iter(backup.archive_dirs_to_use(initial_usage))
         for archive_dir, n, skip in expected_result:
            actual= [next(i) for _ in range(n)]
            expect= [archive_dir]*n
            self.assertEqual(actual, expect)
            for _ in range(skip):
               next(i)
      go({},
         [("00", 100, 0), ("01", 100, 9800), ("00/01", 100, 0), ("01/01", 100, 9800), ("00/02", 100, 979800),
          ("99/99", 100, 0),
          ("00/00/01", 100, 0)])
      go({"00": 100, "45": 30},
         [("45", 70, 0), ("01", 100, 9700), ("00/01", 100, 0), ("01/01", 100, 9800), ("00/02", 100, 0)])

   def test_indexdb_in_different_location(self):
      self.setup_directories()
      self.create_homedir_file("hello.txt", 79)
      db_path= self.otherdir+"/index_database"
      shutil.move(self.databasepath, db_path)
      self.write_config_file("indexdb " +db_path)
      rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)
      with sqlite3.connect(db_path) as conn:
         content= conn.execute("select * from content").fetchall()
         subdir,run_name = conn.execute("select archive_dir, run_name from run").fetchall()[0]
      self.assertEqual(len(content), 1)
      self.assertFalse(os.path.exists(self.databasepath))

      with gzip.open(self.archivedir+"/"+run_name+".gz", "rt", encoding="UTF-8") as stream:
         lines= {l.strip() for l in stream}
      lines.remove(run_name+".gz")
      lines.remove(subdir+"/"+run_name+".lst")
      self.assertEqual(len(lines), 1)
      self.assertRegex(lines.pop(), "[a-z0-9]{64}")

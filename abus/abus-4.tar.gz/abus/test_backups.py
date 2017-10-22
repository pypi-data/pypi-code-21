# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import unittest.mock
from abus import crypto
from abus import main
from abus.testbase import AbusTestBase

class BackedUpHomedirTests(AbusTestBase):
   def test_simple_end_to_end_backup(self):
      self.setup_backup_with_well_known_checksums()
      index_filename= self.executesql("select distinct run_name from content")[0][0] +".lst"
      expect= {"index.sl3", index_filename}
      expect.update(s for p,s in self.expected_backups)
      result= set(direntry.name for direntry in self.find_files(self.archivedir))
      self.assertEqual(result, expect)

      # decrypting backup
      my_litte_backup= [e for e in self.find_files(self.archivedir) if e.name.startswith("40aff2e")]
      self.assertEqual(len(my_litte_backup), 1)
      self.assertEqual(my_litte_backup[0].stat().st_size, 256+80) # 80 for salt, init vector, and checksum
      with crypto.open_bin(my_litte_backup[0], "r", self.password) as f:
         blk= f.read(8192)
         self.assertEqual(len(blk), 256)
         self.assertEqual(blk, bytearray(range(256)))

      # checking that index file agrees with db entries
      index_file_path= [direntry.path for direntry in self.find_files(self.archivedir) if direntry.name==index_filename]
      with crypto.open_txt(index_file_path[0], "r", self.password) as f:
         index_entries= set(l.strip() for l in f)
      dbentries= set("{} {} {}".format(*row)
                     for row in self.executesql("select checksum, timestamp, path from content"))
      self.assertEqual(index_entries, dbentries)

   def test_error_prevents_closing_backup_run(self):
      self.setup_directories()
      self.create_homedir_file("unreadable",23)
      class mock_make_backup_copy(object):
         def __call__(self, path, expected_checksum, backup_path, open_dst_function, password):
            raise RuntimeError("file changed while reading: "+path)
      with unittest.mock.patch('abus.backup.make_backup_copy', new_callable=mock_make_backup_copy):
         rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 1)
      rs= self.executesql("select * from completed_run")
      self.assertEqual(len(rs), 0)

      # checks that index file contains error
      for d in self.find_files(self.archivedir):
         if d.name.endswith(".lst"):
            index_file_path= d.path
            break
      else:
         self.fail("no .lst file encountered")
      with crypto.open_txt(index_file_path, "r", self.password) as stream:
         contents= stream.read()
      self.assertEqual(contents, "error 0 {}/unreadable\n".format(self.homedir))

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
         rows= [conn.execute("select * from "+t).fetchall() for t in("content", "completed_run", "location")]
      self.assertEqual(len(rows[0]), 1)
      self.assertEqual(len(rows[1]), 0)
      self.assertEqual(len(rows[2]), 1)

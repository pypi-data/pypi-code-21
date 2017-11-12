# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import itertools
import os
import sqlite3
from typing import Iterable, Tuple
from abus import backup
from abus import crypto
from abus import database
from abus import main
from abus.testbase import AbusTestBase

class RestoreTests(AbusTestBase):
   def test_database_get_archive(self):
      """Writes various rundata to DB and checks that Database returns the right listings.
      No actual restoring or backing up takes place"""
      self.setup_directories()
      checksums= ("e{:03}".format(i) for i in itertools.count()).__iter__()
      timestamps= itertools.count(1506159900, 50).__iter__()
      all_files= ["c:/home/file_{}.txt".format(c) for c in "abcdefghxy"]
      file_states= {}
      data= [] # (run_name, timestamp, path, checksum, archive_dir) list
      for run,files in [("2017-09-22 12:45","abcdefghxy"),
                        ("2017-09-23 12:45","xy"),
                        ("2017-09-24 12:45","bcdefghx"),
                        ("2017-09-25 12:45","abcfghy"),
                       ]:
         for c in files:
            file_states[c]= timestamps.__next__(), checksums.__next__()
         # this sometimes "touches" b, tests that some content is not listed twice:
         file_states["b"]= timestamps.__next__(), file_states["b"][1]
         data.extend((run,ts,"c:/home/file_{}.txt".format(c),cs,cs[:2]+"/"+cs[2:])
                     for c,(ts,cs) in file_states.items())
      with sqlite3.connect(self.databasepath) as conn:
         conn.executemany("insert into location(checksum, archive_dir, is_compressed) values(?,?,1)", set(t[3:5] for t in data))
         conn.executemany("insert into content(run_name, timestamp, path, checksum) values(?,?,?,?)", (t[0:4] for t in data))
         conn.execute("insert into run(run_name,archive_dir,is_complete) select distinct run_name, '', 1 from content")

      with database.connect(self.databasepath, self.archivedir) as db:
         def test_one(cutoff_date,
                      show_all,
                      nearly_expect: Iterable[Tuple[str,float,str,str,int]]):
            # nearly_expect may still contain duplicate (file,content) with different timestamps
            pac_set= set((p,a,c)for p,t,a,c,z in nearly_expect)
            ptacz_list= [min(ptacz for ptacz in nearly_expect if ptacz[0]==p and ptacz[2]==a and ptacz[3]==c)
                         for p,a,c in pac_set]
            expect= sorted(ptacz_list, key= lambda ptacz: (ptacz[0],-ptacz[1]))
            result= list(db.get_archive_contents([], cutoff_date, show_all))
            self.assertEqual(result, expect)

            expect= [ptac for ptac in expect if ptac[0][-5] in "ab"]
            result= list(db.get_archive_contents(['*a.txt','*b.txt'], cutoff_date, show_all))
            self.assertEqual(result, expect)

            expect= [ptac for ptac in expect if ptac[0][-5]=="a"]
            result= list(db.get_archive_contents(['*a.txt'], cutoff_date, show_all))
            self.assertEqual(result, expect)

         test_one(cutoff_date=None, show_all=False,
                  nearly_expect= [(p,t,a,c,1) for r,t,p,c,a in data if r=="2017-09-25 12:45"],
                  )
         test_one(cutoff_date=None, show_all=True,
                  nearly_expect= [(p,t,a,c,1) for r,t,p,c,a in data],
                  )

         by_path= {}
         for cutoff in sorted(set(t for r,t,p,c,a in data)):
            with self.subTest(cutoff=cutoff):
               test_one(cutoff_date=cutoff, show_all=True,
                        nearly_expect= [(p,t,a,c,1) for r,t,p,c,a in data if t<=cutoff],
                        )
               by_path.update({p:(p,t,a,c,1) for r,t,p,c,a in data if t==cutoff})
               test_one(cutoff_date=cutoff, show_all=False,
                        nearly_expect= by_path.values(),
                        )

   def test_simple_restore(self):
      self.setup_backup_with_well_known_checksums()
      self.remove_dir_contents(self.restoredir)
      rc= main.main(["test", "-f", self.configfile, "-r"])
      self.assertEqual(rc, 0)
      self.assertEqual(sum(1 for _ in self.find_files(self.restoredir)), len(self.expected_backups))
      for relpath, archive_name in self.expected_backups:
         actual= backup.calculate_checksum(self.restoredir+"/"+relpath)
         expected= archive_name[:64]
         self.assertEqual(actual, expected)

   def test_restore_does_not_overwrite(self):
      self.setup_backup_with_well_known_checksums()
      self.remove_dir_contents(self.restoredir)
      filenames= [path.partition("/")[0] for path,_ in self.expected_backups]
      for filename in filenames:
         with open(filename,"w",newline='\n') as f: f.write("Hello World\n")
      rc= main.main(["test", "-f", self.configfile, "-r"])
      self.assertEqual(rc, 0)
      for filename in filenames:
         actual= backup.calculate_checksum(filename)
         self.assertEqual(actual, "d2a84f4b8b650937ec8f73cd8be2c74add5a911ba64df27458ed8229da804a26")

   def test_no_partial_backupfile_is_left(self):
      self.setup_backup_with_well_known_checksums()
      relpath, archivename= max(self.expected_backups)
      path= self.homedir+"/"+relpath
      expected_checksum= "42" # causes Exception which is expected not to leave file behind
      password= "Would you like to buy some air?"
      open_dst_function= crypto.open_lzma
      backup_path= self.archivedir+"/42"
      with self.assertRaises(backup.FileChangedWhileReadingError):
         backup.make_backup_copy(path, expected_checksum, backup_path, open_dst_function, password)
      self.assertFalse(os.path.exists(backup_path))
      self.assertFalse(os.path.exists(backup_path+".part"))
      # making doubly sure the file would normally have been created (the source path might just be wrong, for example):
      backup.make_backup_copy(path, archivename[:64], backup_path, open_dst_function, password)
      self.assertTrue(os.path.exists(backup_path))
      self.assertFalse(os.path.exists(backup_path+".part"))

   def test_allversions_restore(self):
      self.setup_multiple_backups()
      n_versions= sum(1 for direntry in self.find_files(self.archivedir)
                        if len(direntry.name) in(64,66))
      rc= main.main(["test", "-f", self.configfile, "-r", "-a"])
      self.assertEqual(rc, 0)
      self.find_files(self.restoredir)
      n_restored= sum(1 for _ in self.find_files(self.restoredir))
      self.assertEqual(n_restored, n_versions)

   def test_bug_index_error_if_no_files_match(self):
      self.setup_backup_with_well_known_checksums()
      self.remove_dir_contents(self.restoredir)
      rc= main.main(["test", "-f", self.configfile, "-r", self.homedir])
      self.assertEqual(rc, 0)
      self.assertEqual(list(self.find_files(self.restoredir)), [])

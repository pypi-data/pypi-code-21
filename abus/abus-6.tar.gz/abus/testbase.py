# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import itertools
import logging
import os
import shutil
import sqlite3
import time
import unittest

from abus import database
from abus import main

class AbusTestBase(unittest.TestCase):
   def change_latest_runname(self, offset):
      """
      Adds `offset` to the latest run_name to simulate backup happening earlier.

      :type db: database.Database
      :param offset: seconds to be added to all timestamps
      """
      with database.connect(self.databasepath, self.archivedir) as db:
         with db._get_connection() as conn:
            latest, archive_dir= conn.execute("""
               select run_name, archive_dir
               from run
               order by run_name desc
               limit 1""").fetchall()[0]
            new_name= db._make_runname(time.mktime(time.strptime(latest, "%Y_%m_%d_%H%M"))+offset)
            for table in "content", "run":
               conn.execute("update "+table+" set run_name= ? where run_name = ?", [new_name, latest])

      # renaming index file and content file
      for relpath in archive_dir +"/" +latest +".lst", latest +".gz":
         path= self.archivedir + "/" +relpath
         os.rename(path, path.replace(latest, new_name))

   def create_homedir_file(self, relative_path, prime, timestamp=None):
      path= self.homedir+"/"+relative_path
      os.makedirs(os.path.dirname(path), exist_ok=True)
      with open(path,"wb") as f:
         f.write(bytes(n*prime%256 for n in range(8192)))
      if timestamp:
         os.utime(path, times=(timestamp,timestamp))

   @property
   def databasepath(self):
      return self.archivedir+"/index.sl3"

   def executesql(self, sql):
      """Runs sql statement on the index database and returns all rows.
      """
      with self.get_direct_db_connection() as conn:
         return conn.execute(sql).fetchall()

   def find_files(self, start):
      """Returns direntries for all files in `start`, recursively"""
      q= [start]
      while q:
         entries= list(os.scandir(q.pop())) # prevents iterator leakage
         yield from (e for e in entries if e.is_file())
         q.extend(e.path for e in entries if e.is_dir())

   def get_direct_db_connection(self):
      conn= sqlite3.connect(self.databasepath)
      conn.isolation_level= None # autocommit
      conn.execute("PRAGMA synchronous=OFF")
      return conn

   def remove_dir_contents(self, path):
      for direntry in os.scandir(path):
         if direntry.is_dir():
            shutil.rmtree(direntry.path)
         elif direntry.is_file():
            os.unlink(direntry.path)

   def setup_directories(self):
      """
      Sets up empty home, archive, and restore dirs, config file and empty database.

      :rtype: None
      """
      logging.basicConfig(level=logging.DEBUG)
      candidates_for_tmp= ["C:/tmp", "C:/temp"]
      if "TEMP" in os.environ: candidates_for_tmp.append(os.environ["TEMP"])
      for tempdir in candidates_for_tmp:
         if os.path.isdir(tempdir):
            break
      else:
         raise Exception("Could not find a temporary directory for tests")

      self.password= "Sesam, öffne dich!"
      self.homedir= tempdir + "/abushome"
      self.otherdir= tempdir + "/abusother"
      self.archivedir= tempdir + "/abusarchive"
      self.restoredir= tempdir + "/abusrestore"
      os.makedirs(self.homedir, exist_ok=True)
      os.makedirs(self.archivedir, exist_ok=True)
      os.makedirs(self.restoredir, exist_ok=True)
      os.makedirs(self.otherdir, exist_ok=True)
      os.chdir(self.restoredir)

      # empty them
      self.remove_dir_contents(self.homedir)
      self.remove_dir_contents(self.archivedir)
      self.remove_dir_contents(self.restoredir)
      self.remove_dir_contents(self.otherdir)

      self.configfile= self.otherdir + "/abusconfig.cfg"
      self.write_config_file()

      with database.connect(self.databasepath, self.archivedir, allow_create=True):
         pass

   def write_config_file(self, *extra_param_lines):
      with open(self.configfile, "w", encoding="utf-8") as f:
         print("logfile", self.otherdir + "/abuslog.txt", file=f)
         print("archive", self.archivedir, file=f)
         print("password", self.password, file=f)
         print("\n".join(extra_param_lines), file=f)
         print("[include]", file=f)
         print(self.homedir, file=f)

   def setup_backup_with_well_known_checksums(self):
      self.setup_directories()
      self.expected_backups= set() # contains (path rel to homedir, backup filename) pairs

      path= "my_valueable_file"
      with open(self.homedir+"/"+path, "w", encoding="utf-8") as f:
         for n in range(400):
            for p in range(10):
               print(n**p, file=f, end="")
            print(file=f)
      self.expected_backups.add((path,"73672933c00ab3cd730c8715a392ee6dee9ba2c0a8e5e5d07170b6544b0113ef.z"))

      path= "my_little_file"
      with open(self.homedir+"/"+path, "wb") as f:
         f.write(bytearray(range(256)))
      self.expected_backups.add((path,"40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880"))

      path= "subdir_a/I_am_in_a.tif"
      self.create_homedir_file(path, 31)
      self.expected_backups.add((path,"498630374d56ea4c53c5baaee00b630be09ca5dbe678b11b1a81b37f1058635f"))

      path= "subdir_b/I_am_in_b.bin"
      self.create_homedir_file(path, 97)
      self.expected_backups.add((path,"1244d0711c6534ee79a6d3b82cea33b76e766e46cbca75791ac9fa3a30e365f3.z"))

      rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)

   def setup_multiple_backups(self):
      self.setup_directories()
      def primes():
         prev= [2]
         for c in itertools.count(3,2):
            for p in prev:
               if p*p>c:
                  yield c
                  prev.append(c)
                  break
               if c%p==0: break
      primes= primes().__iter__()

      all_paths= ["a", "b", "s/a", "s/b", "t/a", "t/b"]
      n= len(all_paths)*3//4
      for i in range(3):
         change_paths= all_paths if i==0 else all_paths[:n] if i==1 else all_paths[-n:]
         offset= (i-2)*86000 -3000
         timestamp= time.time() + offset
         for path in change_paths:
            self.create_homedir_file(path, next(primes), timestamp)
         rc= main.main(["test", "-f", self.configfile, "--backup"])
         self.assertEqual(rc, 0)
         if i<2:
            self.change_latest_runname(offset+1000)

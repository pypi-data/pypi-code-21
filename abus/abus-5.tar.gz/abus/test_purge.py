# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import os
import time
import unittest
from abus import config
from abus import crypto
from abus import database
from abus import main
from abus.testbase import AbusTestBase

class PurgeTests(AbusTestBase):
   def test_purge_e2e(self):
      self.setup_directories()
      def checkdb(n_runs):
         data= self.executesql("""
            select run_name, content.checksum, location.checksum
            from content
               left join location on location.checksum = content.checksum""")
         self.assertEqual(len(set(r for r,c,l in data)), n_runs)
         self.assertEqual(len(data), n_runs*2)
         # test always keeps 2 files current:
         self.assertEqual(len(set(l for r,c,l in data if l is not None)), 2)
      def contents_runs(expected_content_size, expected_runs_size):
         """Checks that there are as many backup files and runs in archivedir as expected

         :return: Pair with sets with names of backup files and run files respectively.
         """
         all_files= set(direntry.name for direntry in self.find_files(self.archivedir))
         runs= set(n for n in all_files if n.endswith(".lst"))
         content_file= max(runs).replace(".lst", ".gz")
         backups= all_files -runs -{"index.sl3", content_file}
         self.assertEqual(len(backups), expected_content_size)
         self.assertEqual(len(runs), expected_runs_size)
         return backups, runs
      def elt(s):
         """returns the only element from set"""
         self.assertEqual(len(s), 1)
         for e in s: return e
      self.create_homedir_file("file_a", 23, time.time()-365*86400)
      self.create_homedir_file("file_b.gz", 11, time.time()-365*86400)
      rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)
      print("cornie",45)
      self.change_latest_runname(-365*86400)
      content, runs= contents_runs(2, 1) # file_a0, file_b0, run0
      compressed= {n for n in content if n.endswith(".z")}
      file_a0= elt(compressed)
      file_b0= elt(content - compressed)
      run0= elt(runs)
      checkdb(n_runs=1)

      self.create_homedir_file("file_a", 17, time.time()-335*86400)
      rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)
      self.change_latest_runname(-335*86400)
      # file_a0 has been purged
      content, runs= contents_runs(2, 2) # file_a1, file_b0, run0, run1
      file_a1= elt(content - {file_b0})
      run1= elt(runs - {run0})
      checkdb(n_runs=2)

      self.create_homedir_file("file_b.gz", 59, time.time()-305*86400)
      rc= main.main(["test", "-f", self.configfile, "--backup"])
      self.assertEqual(rc, 0)
      self.change_latest_runname(-305*86400)
      content, runs= contents_runs(2, 2) # file_a1, file_b1, run1, run2
      file_b1= elt(content - {file_a1})
      run2= elt(runs - {run1})
      checkdb(n_runs=2)

   def test_db_get_purgeable_backups(self):
      self.setup_directories()
      rounders= [(1, 3), (4, 9)]
      aged_based_data= [
         # rounders:    0   0   0    0    4    4    4  4  4    4    4    4    1   1    1    1    1    1    1 <-- matches era calculation below
         ("file_a", (1000,20  ,  10, 9.1, 8.9, 8.1, 7.9,   6,   5, 4.1, 3.9, 3.1, 2.9,1.9, 1.5, 1.1, 0.9, 0.4, 0.2)),
         ("file_b", (None,19.5)),
         ("file_c", (1001,30  ,None,None,None,None,None,None,None,None,None,None,None,2  )),
         ("file_1d",(1002,31)), # shared checksums
         ("file_2d",(1002,32)),
         ("file_1e",(1003,33)), # shared checksums
         ("file_2e",(1003,None,None,None,None,None,   8)),
      ]
      now= time.time()
      timestamp_lists= {path:[None if age is None else now-age*86400 for age in ages] for path,ages in aged_based_data}
      checksum_lists= {path:[None if t is None else path[-1] +("0"*64 +str(t))[-63:] for t in timestamps]
                       for path,timestamps in timestamp_lists.items()}
      # maps checksums to 3 periods defined by rounders. Period id is maximum number of slots in that period (depending on time of day)
      eras= {}
      for path in timestamp_lists:
         for i, checksum in enumerate(checksum_lists[path]):
            if not checksum: continue
            eras[checksum]= 1 if i<4 else 3 if i<12 else 4
      with database.connect(self.databasepath, self.archivedir) as db:
         runs= [db._make_runname(t+65) for t in timestamp_lists["file_a"]]
         all_checksums= set()
         for path in timestamp_lists:
            for run_name, timestamp, checksum in zip(runs, timestamp_lists[path], checksum_lists[path]):
               if not timestamp: continue
               db.add_backup_entry(run_name, path, timestamp, checksum)
               all_checksums.add(checksum)
         for checksum in all_checksums:
               db.remember_archivedir(checksum, checksum[-2:], True)
         del all_checksums

         result= db.get_purgeable_backups(rounders)
         self.assertTrue(all(a==c[-2:] for c,a,p,t in result)) # correct checksum

         result_checksums= set(c for c,a,p,t in result)

         # the latest versions must never be purged
         latest= set(cl[-1] for cl in checksum_lists.values())
         self.assertEqual(latest & result_checksums, set())

         # file_a
         keep= set(checksum_lists["file_a"]) - result_checksums
         # grouping by era, there must be at most as many versions to keep as slots in era.
         # cannot check "one per slot" directly because slot boundaries depend on time of day
         keep_by_era= {era: set() for era in eras.values()}
         for checksum in keep:
            keep_by_era[eras[checksum]].add(checksum)
         for era in keep_by_era:
            with self.subTest(contents=keep_by_era[era]):
               self.assertLessEqual(len(keep_by_era[era]), era)

         # file_c - one backup in oldest slot is always kept
         purged= [c for c in result_checksums if c.startswith("c")]
         self.assertEqual(purged, [checksum_lists["file_c"][0]]) # 30 and 2 stay

         # file_?d - oldest gets deleted because both paths don't need it any more
         purged= [c for c in result_checksums if c.startswith("d")]
         self.assertEqual(purged, [checksum_lists["file_1d"][0]])
         self.assertEqual(purged, [checksum_lists["file_2d"][0]])

         # file_?e - no deletion because the other still needs it
         purged= [c for c in result_checksums if c.startswith("e")]
         self.assertEqual(purged, [])

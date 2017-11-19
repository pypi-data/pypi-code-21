# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import os
import time
from abus import config
from abus import main
from abus.testbase import AbusTestBase

class ConfigTestser(AbusTestBase):
   def test_parse_date(self):
      def str2sec(s):
         return time.mktime(time.strptime(s, "%Y%m%d%H%M%S"))
      now= str2sec("20170912150000")
      for d in range(1,9):
         for t in range(8):
            for future_date in True, False:
               for future_time in True, False:
                  d_str= "20171003" if future_date else "20170912"
                  t_str= "-160723" if future_time else "-130905"
                  test_str= d_str[-d:] + t_str[:t]

                  if d in (4,6,8) and t in (0,5,7):
                     expect_str= "2016"+d_str[-4:] if future_date and d==4 else d_str
                     expect_str += (t_str[1:t]+"000000")[:6]
                     try:
                        self.assertEqual(config._parse_date(test_str, now), str2sec(expect_str))
                     except:
                        print("test string:", test_str)
                        raise
                  else:
                     with self.assertRaises(ValueError):
                        print("test string:", test_str, "result:", config._parse_date(test_str, now))

   def test_conflicting_cmdline_actions(self):
      self.setup_directories()
      with self.assertRaisesRegex(config.ConfigurationError, "conflicting command line actions"):
         config.Configuration(["test", "-f", self.configfile, "--backup", "--restore"])

   def test_init_creates_directory(self):
      self.setup_directories()
      os.unlink(self.databasepath)
      os.rmdir(self.archivedir)
      rc= main.main(["test", "-f", self.configfile, "--init"])
      self.assertEqual(rc, 0)
      self.assertTrue(os.path.isfile(self.databasepath))
      # non-standard database file:
      db_path= self.otherdir+"/index_database"
      self.write_config_file("indexdb " +db_path)
      os.unlink(self.databasepath)
      os.rmdir(self.archivedir)
      rc= main.main(["test", "-f", self.configfile, "--init"])
      self.assertEqual(rc, 0)
      self.assertTrue(os.path.isfile(db_path))
      self.assertFalse(os.path.exists(self.databasepath))

   def test_retention_parsing(self):
      self.setup_directories()
      def get_cfg_for_retention(*retention_strings):
         self.write_config_file(*retention_strings)
         return config.Configuration(["test", "-f", self.configfile])

      # default
      cfg= get_cfg_for_retention()
      self.assertEqual(cfg.retention, [(1,7), (56,150)])
      # std
      cfg= get_cfg_for_retention("retain 7 20  1 10  .25 2  28 182")
      self.assertEqual(cfg.retention, [(.25,2), (1,10), (7,20), (28,182)])
      # non-numbers
      with self.assertRaises(config.ConfigurationError):
         get_cfg_for_retention("retain 7 28  56 b")
      # missing arguments
      with self.assertRaises(config.ConfigurationError):
         get_cfg_for_retention("retain 7 28  14 56 28")
      with self.assertRaises(config.ConfigurationError):
         get_cfg_for_retention("retain")
      # duplicates
      with self.assertRaises(config.ConfigurationError):
         get_cfg_for_retention("retain 1 10  7 10")
      # non-factors
      with self.assertRaises(config.ConfigurationError):
         get_cfg_for_retention("retain 4 10  7 20")

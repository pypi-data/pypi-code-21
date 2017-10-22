# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import logging
import os
import sys
import time
import queue
import concurrent.futures
import threading
from contextlib import contextmanager

from abus import config
from abus import database
from abus import reconstruct

def do_purge(cfg):
   """
   Removes all purgeable backup files.

   :type cfg: config.Configuration
   """
   logging.info("starting purge")
   with database.connect(cfg.database_path) as db:
      purgeable= db.get_purgeable_backups(cfg.retention)
      previous= None
      for checksum, archive_dir, path, timestamp in purgeable:
         time_str= time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp))
         if checksum==previous:
            logging.info("     == %s from %s", path, time_str)
         else:
            logging.info("Purging %s from %s", path, time_str)
            previous= checksum
            base= cfg.archive_root_path+"/"+archive_dir+"/"+checksum
            if os.path.exists(base+".z"): os.unlink(base+".z")
            if os.path.exists(base): os.unlink(base)
            db.remove_location_entry(checksum)
      for run_name, index_file_path in reconstruct.find_index_files(db, cfg.archive_root_path):
         if db.try_purge_run(run_name):
            os.unlink(index_file_path)

   logging.info("completed purge")

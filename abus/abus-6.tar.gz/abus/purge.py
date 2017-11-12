# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import gzip
import logging
import os
from   pprint import pprint
import time

from abus.cornelib import partial_write_guard
from abus import config
from abus import database

def do_purge(cfg: config.Configuration, db: database.Database):
   """
   Removes all purgeable backup files.
   """
   logging.info("starting purge")
   purgeable_backups= db.get_purgeable_backups(cfg.retention)
   previous= None
   for checksum, archive_dir, path, timestamp in purgeable_backups:
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
   purgeable_runs= list(db.get_purgeable_runs())
   for run_name, archive_dir in purgeable_runs:
      index_file_path= cfg.mk_archive_path(run_name, archive_dir, ".lst")
      logging.info("Purging run %s", run_name)
      os.unlink(index_file_path)
   db.purge_runs(r for r,a in purgeable_runs)
   logging.info("completed purge")

def write_content_file(cfg: config.Configuration, db: database.Database) -> None:
   """
   Writes a new content file listing all files in backup directory, removing any previous such file.
   """
   all_runs= list(db.get_all_runs())
   contentfile_name= max(run_name for run_name, subdir in all_runs)+".gz"
   contentfile_path= cfg.archive_root_path+"/"+contentfile_name
   with partial_write_guard(contentfile_path) as partial_path:
      with gzip.open(partial_path, "wt", encoding="UTF=8", newline="\n") as stream:
         indexdb_rel= os.path.relpath(cfg.database_path, cfg.archive_root_path).replace('\\','/')
         if not indexdb_rel.startswith("../"):
            print(indexdb_rel, file=stream)
         print(contentfile_name, file=stream)
         for run_name, subdir in all_runs:
            print(subdir+"/"+run_name+".lst", file=stream)
         for checksum, subdir, is_compressed in db.get_all_backup_files():
            print(subdir+"/"+checksum+(".z" if is_compressed else ""), file=stream)
   doomed= [
      direntry.path
      for direntry in os.scandir(cfg.archive_root_path)
      if direntry.is_file() and direntry.name.endswith(".gz") and direntry.name != contentfile_name]
   for p in doomed:
      os.unlink(p)
   logging.info("wrote content file "+contentfile_path)

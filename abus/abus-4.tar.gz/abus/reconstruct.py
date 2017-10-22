import logging
import os
import re

from abus import config
from abus import crypto
from abus import database

def reconstruct_location(cfg):
   """
   Reconstructs the location table from scanning the archive dir

   :type cfg: config.Configuration
   """
   logging.info("starting location index reconstruction")
   re_archive_filename= re.compile(r"[0-9a-f]{64}")
   result= {}
   dirqueue= [cfg.archive_root_path]
   while dirqueue:
      dirpath= dirqueue.pop()
      archive_dir= os.path.relpath(dirpath, start=cfg.archive_root_path).replace("\\","/")
      for direntry in os.scandir(dirpath):
         if direntry.is_dir():
            dirqueue.append(direntry.path)
         elif direntry.is_file():
            m= re_archive_filename.match(direntry.name)
            if m:
               checksum= m.group(0)
               result[checksum]= archive_dir
   with database.connect(cfg.database_path) as db:
      inserts, deletes, updates = db.reconstruct_location(result)

   logging.info("location index reconstruction added %d, removed %d, changed %d entries", inserts, deletes, updates)
   return updates, inserts, deletes

def find_index_files(db, archive_root_path):
   """
   returns iterable of .lst files

   :param archive_root_path: from cfg
   :type db: database.Database
   :return: (run name, full path) list
   """
   dirqueue= [archive_root_path]
   while dirqueue:
      dirpath= dirqueue.pop()
      for direntry in os.scandir(dirpath):
         if direntry.is_dir():
            dirqueue.append(direntry.path)
         elif direntry.is_file():
            run_name, ext = os.path.splitext(direntry.name)
            if ext==".lst":
               yield run_name, direntry.path

def reconstruct_entries(cfg):
   """
   Reconstructs the content table from index files.

   :type cfg: config.Configuration
   :return:
   :rtype:
   """
   logging.info("starting content index reconstruction")
   changed, added, deleted = 0,0,0
   runs= []
   with database.connect(cfg.database_path) as db:
      for run_name, index_file_path in find_index_files(db, cfg.archive_root_path):
         runs.append(run_name)
         with crypto.open_txt(index_file_path, "r", cfg.password) as index_file:
            splut_lines= (line.strip().split() for line in index_file)
            c,a,d = db.reconstruct_content(run_name, splut_lines)
         changed += c
         added += a
         deleted += d
      deleted += db.remove_runs(other_than=runs)
   logging.info("content index reconstruction added %d, removed %d, changed %d entries", added, deleted, changed)
   return changed, added, deleted

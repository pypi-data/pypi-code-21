# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import gzip
import logging
import os
import re
from pprint import pprint
from typing import Iterable,Optional,Set,Tuple

from abus import config
from abus import crypto
from abus import database

def rebuild_index_db(cfg):
   """
   Reconstructs the location table from scanning the archive dir

   :type cfg: config.Configuration
   """
   logging.info("rebuilding index database")
   with database.connect(cfg.database_path, cfg.archive_root_path) as db:
      actual_backup_files= set(_find_archive_files(cfg.archive_root_path))
      _validate_against_content_file(cfg, actual_backup_files)
      location_data= _filter_backup_files(actual_backup_files)
      updates, inserts, deletes = db.rebuild_location_table(location_data)

      runs= list(_filter_run_files(actual_backup_files))
      for run_name, archive_dir in runs:
         index_file_path= cfg.mk_archive_path(run_name, archive_dir, ".lst")
         with crypto.open_txt(index_file_path, "r", cfg.password) as index_file:
            splut_lines= (line.strip().split(maxsplit=2) for line in index_file)
            u,i,d = db.rebuild_content(run_name, archive_dir, splut_lines)
         updates += u; inserts += i; deletes += d
      deletes += db.remove_runs(other_than=(r[0] for r in runs))
   logging.info("index rebuild added %d, removed %d, changed %d entries", inserts, deletes, updates)
   return updates, inserts, deletes

def _validate_against_content_file(cfg: config.Configuration, actual_backup_files: Set[Tuple[str,str]]):
   """
   Checks that all path from latest content file are actually in backup archive.

   :param actual_backup_files: Paths (filename, archive_dir) that are actually in the backup archive."""
   content_files= sorted(filename for filename,archive_dir in actual_backup_files
                         if filename.endswith(".gz") and archive_dir=="")
   if len(content_files)<1:
      raise RuntimeError("Could not find a content file.")
   with gzip.open(cfg.mk_archive_path(content_files[-1]), "rt") as stream:
      for line in stream:
         archivedir, sep, filename = line[:-1].rpartition('/')
         if (filename,archivedir) not in actual_backup_files:
            raise RuntimeError("Path {} missing from backup archive".format(line[:-1]))

def _filter_run_files(archive_contents: Iterable[Tuple[str, str]]) -> Iterable[Tuple[str, str]]:
   """
   Filters run-files from all paths in backup archive.

   :param archive_contents: all (filename, archive_dir)s in backup archive.
   :return: (run_name, archive_dir)s
   """
   for filename, archive_dir in archive_contents:
      run_name, ext = os.path.splitext(filename)
      if ext==".lst":
         yield run_name, archive_dir

def find_index_files(archive_root_path: str) -> Iterable[Tuple[str,str]]:
   """
   returns iterable of .lst files

   :param archive_root_path: from cfg
   :type db: database.Database
   :return: (run_name, archive_dir)s
   """
   return _filter_run_files(_find_archive_files(archive_root_path))

def _find_archive_files(archive_root_path: str) -> Iterable[Tuple[str, str]]:
   """
   Returns list of files in archive dir.

   :param archive_root_path: from cfg
   :return: (filename, archive_dir)s
   """
   dirqueue= []
   dirpath, archive_dir = archive_root_path, ""
   while True:
      for direntry in os.scandir(dirpath):
         if direntry.is_dir():
            sepd= "" if archive_dir=="" else archive_dir+"/"
            dirqueue.append((direntry.path, sepd + direntry.name))
         elif direntry.is_file():
            yield direntry.name, archive_dir
      if not dirqueue: break
      dirpath, archive_dir = dirqueue.pop()

def _filter_backup_files(archive_contents: Iterable[Tuple[str, str]]) -> Iterable[Tuple[str, str, bool]]:
   """
   Filters backup files from all paths in backup archive.

   :param archive_contents: all (filename, archive_dir)s in backup archive.
   :return: (checksum, archive_dir, is_compressed)s
   """
   re_archive_filename= re.compile(r"[0-9a-f]{64}")
   for filename, archive_dir in archive_contents:
      m= re_archive_filename.match(filename)
      if m:
         checksum= m.group(0)
         yield checksum, archive_dir, filename.endswith(".z")

def find_compressed_backups(archive_root_path) -> Iterable[str]:
   """
   Returns list of backup files that are compressed.

   :param archive_root_path: from cfg
   :return: checksums
   """
   for checksum,archive_dir,is_compressed in _filter_backup_files(_find_archive_files(archive_root_path)):
      if is_compressed:
         yield checksum

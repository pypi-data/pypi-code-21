# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import concurrent.futures
import enum
import hashlib
import logging
import os
import sys
import threading
import traceback
from contextlib import contextmanager
from fnmatch import fnmatch

from abus import config
from abus import crypto
from abus import database
from abus import synchronisation

class Counters(enum.Enum):
   DIRS= "directories"
   UNTOUCHED= "untouched files"
   CHECKSUMMED_ONLY= "already backed up"
   COMPRESSED= "compressed"
   UNCOMPRESSED= "copied"
   ERROR= "errors"

class IndexFile(object):
   def __init__(self, stream):
      self.lock= threading.Lock()
      self.stream= stream
   def add_entry(self, checksum, timestamp, path):
      with self.lock:
         print(checksum, timestamp, path, file=self.stream)

@contextmanager
def open_index_file(run_name, cfg, iter_archivedirs_to_use):
   d= cfg.archive_root_path+ "/"+next(iter_archivedirs_to_use)
   index_file_path= d+ "/"+run_name+".lst"
   partial_path= index_file_path+".part"
   os.makedirs(d, exist_ok=True)
   try:
      with crypto.open_txt(partial_path, "w", cfg.password) as stream:
         yield IndexFile(stream)
   except:
      os.unlink(partial_path)
      raise
   else:
      os.rename(partial_path, index_file_path)

def do_backup(cfg):
   """Performs a backup run with given configuration.

   :type cfg: config.Configuration
   """
   with database.connect(cfg.database_path) as db:
      run_name= db.open_backup_run()
      logging.info("starting backup run %s", run_name)
      iter_archivedirs_to_use= iter(archive_dirs_to_use(db))
      stats= {c:0 for c in Counters}
      n_threads= 20
      with concurrent.futures.ThreadPoolExecutor(n_threads) as executor, \
            open_index_file(run_name, cfg, iter_archivedirs_to_use) as index_file:
         # This thread walks the directories, runs do_one_file in the background for each file
         # and then waits for all the background tasks.
         futures= []
         dir_queue= list(cfg.include)
         while dir_queue:
            p= dir_queue.pop()
            try:
               direntries= os.scandir(p)
            except (PermissionError, OSError) as e:
               msg= str(e)
               displaydir= "" if p in msg else " "+p
               logging.error("Error reading directory%s: %s", displaydir, msg)
               stats[Counters.ERROR] += 1
               continue
            else:
               stats[Counters.DIRS] += 1
            for direntry in direntries:
               path= direntry.path.replace('\\', '/')
               if any(fnmatch(path, p) for p in cfg.exclude):
                  pass
               elif direntry.is_file(follow_symlinks=False):
                  # restricts number of simultaneous single-file backups:
                  if len(futures)>=n_threads*2:
                     wait_for_one(futures, stats)
                  f= executor.submit(do_one_file, direntry, run_name, iter_archivedirs_to_use, cfg, db, index_file)
                  futures.append(f)
               elif direntry.is_dir(follow_symlinks=False):
                  dir_queue.append(path)
         while futures:
            wait_for_one(futures, stats)
      logging.info(", ".join("{}: {}".format(c.value, n) for c,n in stats.items()))
      n_errors= stats[Counters.ERROR]
      if n_errors==0:
         db.complete_backup_run(run_name)
         logging.info("completed backup run %s without errors", run_name)
      else:
         logging.warning("completed backup run %s with errors", run_name)
         raise RuntimeError("some files failed to be backed up")

def wait_for_one(futures, stats):
   done,not_done = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
   for f in done:
      stats[f.result()] += 1
   futures[:]= not_done

def archive_dirs_to_use(db):
   """
   Returns sequence of archive subdirectories (relative to root) to be used for each single new file in turn.
   The dirs return will exist.

   :type db: database.Database
   """
   subdir_usage= {"{:02}/{:02}".format(i//100, i%100):0 for i in range(10000)}
   subdir_usage.update(db.get_archivedir_usage())
   for a,n in subdir_usage.items():
      for _ in range(n, 100):
         yield a
   while True:
      yield from subdir_usage

def calculate_checksum(path):
   partially_calculated_checksum= hashlib.sha256()
   with open(path, "rb") as fd:
      while True:
         blk= fd.read(8192)
         if len(blk)==0: break
         partially_calculated_checksum.update(blk)
   return partially_calculated_checksum.hexdigest()

def do_one_file(direntry, run_name, iter_archivedirs_to_use, cfg, db, index_file):
   """
   Processes a single file, making appropriate database entries for it and creating the
   backup copy if necessary.

   :param direntry: a direntry with the file information as returned by os.scandir()
   :param run_name: the backup run to which the file should be added
   :param iter_archivedirs_to_use: iterator over archive dirs (relative to archive root) into which new backup copies
                                   should be placed.
   :type cfg: config.Configuration
   :type db: database.Database
   :param index_file: Open file descriptor for writing the index entry
   :type index_file: IndexFile
   """
   result= Counters.UNTOUCHED
   path= direntry.path.replace("\\", "/")
   try:
      ext= os.path.splitext(path)[-1]
      stat= direntry.stat()
      timestamp= stat.st_mtime
      size= stat.st_size
      if stat.st_dev==0 and stat.st_ino==0:
         # this means this is windows and the direntry does not have the relevant information
         stat= os.stat(path)
      with synchronisation.global_data_lock(stat.st_dev, stat.st_ino, timestamp):
         checksum= db.lookup_checksum(stat.st_dev, stat.st_ino, timestamp)
         if checksum is None:
            checksum= calculate_checksum(path)
            db.remember_checksum(stat.st_dev, stat.st_ino, timestamp, checksum)
            result= Counters.CHECKSUMMED_ONLY

      db.add_backup_entry(run_name, path, timestamp, checksum)

      with synchronisation.global_data_lock(checksum):
         archive_dir_rel= db.lookup_archivedir(checksum)
         if archive_dir_rel is None:
            with synchronisation.global_data_lock():
               archive_dir_rel= next(iter_archivedirs_to_use)
            backup_path= cfg.backup_path_abs(archive_dir_rel, checksum)
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            if size < cfg.minimum_size_for_compression or ext in cfg.compressed_extensions:
               make_backup_copy(path, checksum, backup_path, crypto.open_bin, cfg.password)
               result= Counters.UNCOMPRESSED
            else:
               backup_path += ".z"
               make_backup_copy(path, checksum, backup_path, crypto.open_lzma, cfg.password)
               result= Counters.COMPRESSED
            db.remember_archivedir(checksum, archive_dir_rel)

      index_file.add_entry(checksum, timestamp, path)
   except Exception as e:
      index_file.add_entry("error", 0, path)
      log_error(e, direntry)
      result= Counters.ERROR
   return result

def log_error(e, direntry):
   """
   Issues as pretty an error message as possible

   :type e: Exception
   :param direntry: of file that we tried to back up when exception occurred
   """
   #logging.debug("%s", "".join(traceback.format_exception(type(e), e, e.__traceback__)))
   error_msg= str(e)
   if direntry.path.replace("\\","/").lower() not in error_msg.replace("\\","/").lower():
      error_msg= "Backing up {}: {}".format(direntry.path, error_msg)
   logging.error(error_msg)
   print(error_msg, file=sys.stderr)

def make_backup_copy(path, expected_checksum, backup_path, open_dst_function, password):
   """
   Creates the encrypted backup copy of a file, taking care not to leave a partial backup file in case of errors.

   :param path: Path of file to be backed up.
   :param expected_checksum: Known checksum of the file, which is verified while copying; if different an exception
                             will be raised.
   :param backup_path: absolute filename of the destination file
   :param open_dst_function: function from crypto module to open the destination file, i.e. either open_lzma or open_bin according to whether
                             compression is required.
   :param password: to be used for encryption
   """
   partially_calculated_checksum= hashlib.sha256()
   try:
      with open(path,"rb") as src, open_dst_function(backup_path+".part", "w", password) as dst:
         while True:
            blk= src.read(8192)
            if len(blk)==0: break
            partially_calculated_checksum.update(blk)
            dst.write(blk)
      if partially_calculated_checksum.hexdigest() != expected_checksum:
         raise RuntimeError("file changed while reading: "+path)
   except:
      os.unlink(backup_path+".part")
      raise
   else:
      os.rename(backup_path+".part", backup_path)


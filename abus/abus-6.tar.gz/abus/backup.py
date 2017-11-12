# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import concurrent.futures
import enum
import hashlib
import logging
import math
import os
import sys
import threading
import time
import traceback
from   typing import Optional
from contextlib import contextmanager
from fnmatch import fnmatch

from abus.cornelib import partial_write_guard
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
def open_index_file(run_name, cfg, archive_dir):
   d= cfg.archive_root_path+ "/"+archive_dir
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

def read_blocks(stream):
   """returns contents of binary files as list of byte-blocks"""
   block_size= 8192
   while True:
      block= stream.read(block_size)
      yield block
      if len(block) < block_size:
         break

def do_backup(cfg: config.Configuration, db: database.Database) -> None:
   """Performs a backup run with given configuration.
   """
   initial_subdir_usage= db.get_archivedir_usage()
   iter_archivedirs_to_use= iter(archive_dirs_to_use(initial_subdir_usage))
   run_file_archive_dir= next(iter_archivedirs_to_use)
   run_name= db.open_backup_run(run_file_archive_dir)
   logging.info("starting backup run %s", run_name)
   stats= {c:0 for c in Counters}
   n_threads= 20
   with concurrent.futures.ThreadPoolExecutor(n_threads) as executor, \
         open_index_file(run_name, cfg, run_file_archive_dir) as index_file:
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

def archive_dirs_to_use(initial_subdir_usage):
   """
   Returns sequence of archive subdirectories (relative to root) to be used for each single new file in turn.
   The dirs returned may or may not exist.

   :param initial_subdir_usage: dict existing archive_dir -> n files therein
   """
   files_per_dir= 100
   for archive_dir, n in initial_subdir_usage.items():
      for _ in range(n, files_per_dir):
         yield archive_dir
   def infrange():
      n= 0
      while True:
         yield n
         n += 1
   def mkdirname(n):
      least= "{:02}".format(n%100)
      return least if n<100 else least + "/" + mkdirname(n//100)
   for n in infrange():
      archive_dir= mkdirname(n)
      if archive_dir not in initial_subdir_usage:
         for _ in range(files_per_dir):
            yield archive_dir

def calculate_checksum(path: str) -> str:
   """Calculates SHA256 sum of a file"""
   partially_calculated_checksum= hashlib.sha256()
   with open(path, "rb") as fd:
      for blk in read_blocks(fd):
         partially_calculated_checksum.update(blk)
   return partially_calculated_checksum.hexdigest()

class FileChangedWhileReadingError(Exception):
   pass

class Cache:
   def __init__(self, fun):
      self.f= fun
      self.v= None
   def __call__(self):
      if self.v is None:
         self.v= self.f()
      return self.v

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
   path= direntry.path.replace("\\", "/")
   try:
      stat= direntry.stat()
      if stat.st_dev==0 and stat.st_ino==0:
         # this means this is windows and the direntry does not have the relevant information
         stat= os.stat(path)

      archive_dir_fun= Cache(lambda:next(iter_archivedirs_to_use))
      failed_attempts= 0
      while True: # retry loop
         try:
            result= do_one_file_no_retry(run_name, path, stat, cfg, db, archive_dir_fun, index_file)
         except FileChangedWhileReadingError:
            failed_attempts += 1
            if failed_attempts==5:
               raise RuntimeError("file changed while reading")
            time.sleep(failed_attempts)
            stat= os.stat(path)
         else:
            return result
   except Exception as e:
      index_file.add_entry("error", 0, path)
      log_error(e, direntry)
      return Counters.ERROR

def do_one_file_no_retry(run_name, path, stat, cfg, db, archive_dir_fun, index_file):
   result= Counters.UNTOUCHED
   with synchronisation.global_data_lock(stat.st_dev, stat.st_ino, stat.st_mtime):
      checksum= db.lookup_checksum(stat.st_dev, stat.st_ino, stat.st_mtime)
      if checksum is None:
         checksum= calculate_checksum(path)
         db.remember_checksum(stat.st_dev, stat.st_ino, stat.st_mtime, checksum)
         result= Counters.CHECKSUMMED_ONLY

   with synchronisation.global_data_lock(checksum):
      if not db.have_checksum(checksum):
         backup_path= cfg.backup_path_abs(archive_dir_fun(), checksum)
         if stat.st_size < cfg.minimum_size_for_compression or os.path.splitext(path)[-1] in cfg.compressed_extensions:
            open_dst_function= crypto.open_bin
            result= Counters.UNCOMPRESSED
            is_compressed= False
         else:
            backup_path += ".z"
            open_dst_function= crypto.open_lzma
            result= Counters.COMPRESSED
            is_compressed= True
         make_backup_copy(path, checksum, backup_path, open_dst_function, cfg.password)
         db.remember_archivedir(checksum, archive_dir_fun(), is_compressed)
   db.add_backup_entry(run_name, path, stat.st_mtime, checksum)
   index_file.add_entry(checksum, stat.st_mtime, path)
   return result

def log_error(e: Exception, direntry: os.DirEntry) -> None:
   """
   Issues as pretty an error message as possible

   :param direntry: of file that we tried to back up when exception occurred
   """
   #logging.debug("%s", "".join(traceback.format_exception(type(e), e, e.__traceback__)))
   if isinstance(e, RuntimeError):
      error_msg= str(e)
   else:
      error_msg= "".join(traceback.format_exception(type(e), e, e.__traceback__))
   path= direntry.path.replace("\\","/")
   if path.lower() not in error_msg.replace("\\","/").lower():
      error_msg= "While backing up {}: {}".format(path, error_msg)
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
   os.makedirs(os.path.dirname(backup_path), exist_ok=True)
   partially_calculated_checksum= hashlib.sha256()
   with partial_write_guard(backup_path) as partial_path:
      with open(path,"rb") as src, open_dst_function(partial_path, "w", password) as dst:
         for blk in read_blocks(src):
            partially_calculated_checksum.update(blk)
            dst.write(blk)
      if partially_calculated_checksum.hexdigest() != expected_checksum:
         raise FileChangedWhileReadingError()

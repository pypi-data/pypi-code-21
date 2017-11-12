# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import concurrent.futures
import os
import time
import traceback

from abus.backup import read_blocks
from abus import crypto
from abus import database
from abus.synchronisation import global_data_lock

def list_archive(config):
   with database.connect(config.database_path, config.archive_root_path) as db:
      results= db.get_archive_contents(patterns=config.patterns,
                                       cutoff_date=config.cutoff,
                                       show_all=config.list_all)
      for path, timestamp, archive_dir, checksum, _is_compressed in results:
         time_str= time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp))
         print("{}  {}".format(time_str, path))

def restore(config):
   with database.connect(config.database_path, config.archive_root_path) as db:
      results= db.get_archive_contents(patterns=config.patterns,
                                       cutoff_date=config.cutoff,
                                       show_all=config.list_all)
      results= list(results) # path, timestamp, archive_dir, checksum
      if len(results)==0:
         return # have to check because empty generator breaks commonpath()
      common= os.path.commonpath(ptacc[0] for ptacc in results)
      n_threads= 4
      futures= []
      progress= Progress(len(results))
      with concurrent.futures.ThreadPoolExecutor(n_threads) as executor:
         for ptacc in results:
            if len(futures)>=n_threads*2:
               progress.wait_for_one(futures)
            f= executor.submit(restore_one, ptacc, config, common)
            futures.append(f)
         while futures:
            progress.wait_for_one(futures)
   progress.give_summary()

class CannotOverwriteError(RuntimeError):
   pass

def restore_one(ptacc, config, common):
   path, timestamp, archive_dir, checksum, is_compressed = ptacc
   target= os.path.relpath(path, start=common)
   if config.list_all:
      sansext, ext= target= os.path.splitext(target)
      target= sansext +time.strftime("-%Y%m%d-%H%M", time.localtime(timestamp)) +ext
   with global_data_lock(target):
      if os.path.exists(target):
         raise CannotOverwriteError("Cannot overwrite " + target)

      parent= os.path.dirname(target)
      with global_data_lock(parent):
         if parent=="" or os.path.isdir(parent):
            pass # good
         elif os.path.exists(parent):
            raise CannotOverwriteError("Cannot overwrite {} for {}".format(parent, target))
         else:
            os.makedirs(parent)
      source= config.archive_root_path +"/" +archive_dir +"/" +checksum
      if is_compressed:
         src_cm= crypto.open_lzma(source+".z", "r", config.password)
      else:
         src_cm= crypto.open_bin(source, "r", config.password)
      with src_cm as src, open(target, "wb") as dstfd:
         for blk in read_blocks(src):
            dstfd.write(blk)
   return path

class Progress:
   def __init__(self, n_files):
      self.n_files= n_files
      self.t0= time.time()
      self.times= []   # (t,n)s where n files have completed in the time up to t
      self.t= self.t0  # the t before self.times[0].t
      self.min_width_for_next_message= 0
      self.n_done= 0
      self.n_error= 0
      self.n_no_overwrite= 0

   def wait_for_one(self, futures):
      done, not_done = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
      futures[:]= not_done
      n= len(done)
      self.n_done += n
      self.times.append((time.time(), n))
      path_done= None
      for future in done:
         try:
            path_done= future.result()
         except Exception as e:
            self.n_error += 1
            if isinstance(e, RuntimeError):
               if isinstance(e, CannotOverwriteError):
                  self.n_no_overwrite += 1
               msg= str(e)
            else:
               msg= "".join(traceback.format_exception(type(e), e, e.__traceback__))
            self.message(msg)
      if path_done is None:
         return
      t= self.times[-1][0]
      while len(self.times)>1 and t - self.t > 5:
         self.t= self.times.pop(0)[0]
      average_speed= sum(n for t,n in self.times) / (t - self.t)
      eta= (self.n_files - self.n_done) / average_speed / 60
      message= "{}/{} {}% {}/s ETA:{}min {}".format(
              self.n_done,
              self.n_files,
              round(self.n_done*100/self.n_files),
              round(average_speed,1),
              round(eta),
              path_done)
      self.message(message, overwriteable=True)

   def message(self, msg, overwriteable=False):
      msg= msg.split("\n")
      l= len(msg[0])
      if l<self.min_width_for_next_message:
         msg[0] += ' '*(self.min_width_for_next_message - l)
      self.min_width_for_next_message= len(msg[-1]) if overwriteable else 0
      print("\n".join(msg), end= "\r" if overwriteable else "\n")

   def give_summary(self):
      msg= "Restored {}/{} files in {}min, {} errors, {} could not be overwritten".format(
         self.n_done - self.n_error,
         self.n_files,
         round((time.time()-self.t0)/60),
         self.n_error - self.n_no_overwrite,
         self.n_no_overwrite,
         )
      self.message(msg)

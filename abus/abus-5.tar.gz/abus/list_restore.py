# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import os
import sys
import time

from abus.backup import read_blocks
from abus import crypto
from abus import database

def list_archive(config):
   with database.connect(config.database_path, config.archive_root_path) as db:
      results= db.get_archive_contents(patterns=config.patterns,
                                       cutoff_date=config.cutoff,
                                       show_all=config.list_all)
      for path, timestamp, archive_dir, checksum in results:
         time_str= time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp))
         print("{}  {}".format(time_str, path))

def restore(config):
   with database.connect(config.database_path, config.archive_root_path) as db:
      results= db.get_archive_contents(patterns=config.patterns,
                                       cutoff_date=config.cutoff,
                                       show_all=config.list_all)
      results= list(results) # path, timestamp, archive_dir, checksum
      common= os.path.commonpath(ptac[0] for ptac in results)
      for path, timestamp, archive_dir, checksum in results:
         target= os.path.relpath(path, start=common)
         if config.list_all:
            sansext, ext= target= os.path.splitext(target)
            target= sansext +time.strftime("-%Y%m%d-%H%M", time.localtime(timestamp)) +ext
         if os.path.exists(target):
            print("Cannot overwrite", target, file=sys.stderr)
            continue

         parent= os.path.dirname(target)
         if parent=="" or os.path.isdir(parent):
            pass # good
         elif os.path.exists(parent):
            print("Cannot overwrite {} for {}".format(parent,target), file=sys.stderr)
            continue
         else:
            os.makedirs(parent)
         source= config.archive_root_path +"/" +archive_dir +"/" +checksum
         if os.path.exists(source+".z"):
            src_cm= crypto.open_lzma(source+".z", "r", config.password)
         else:
            src_cm= crypto.open_bin(source, "r", config.password)
         with src_cm as src, open(target, "wb") as dstfd:
            for blk in read_blocks(src):
               dstfd.write(blk)

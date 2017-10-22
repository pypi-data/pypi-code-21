# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import logging
import os
import sys
import traceback

from abus import config
from abus import backup
from abus import database
from abus import purge
from abus import reconstruct
from abus import list_restore

def main(argv):
   try:
      cfg= config.Configuration(argv)
      if cfg.is_backup:
         backup.do_backup(cfg)
         purge.do_purge(cfg)
      elif cfg.is_restore:
         list_restore.restore(cfg)
      elif cfg.is_init:
         if os.path.exists(cfg.database_path):
            raise config.ConfigurationError(cfg.database_path+" exists already")
         os.makedirs(cfg.archive_root_path, exist_ok=True)
         with database.connect(cfg.database_path, allow_create=True):
            print("created", cfg.database_path)
      elif cfg.is_full_reconstruction:
         # is_full_reconstruction implies is_location_reconstruction
         reconstruct.reconstruct_entries(cfg)
         reconstruct.reconstruct_location(cfg)
      elif cfg.is_location_reconstruction:
         reconstruct.reconstruct_location(cfg)
      else:
         list_restore.list_archive(cfg)
   except config.ConfigurationError as e:
      error_message= str(e)
      rc= 2
   except RuntimeError as e:
      error_message= str(e)
      rc= 1
   except Exception as e:
      error_message= "".join(traceback.format_exception(type(e), e, e.__traceback__))
      rc= 4
   else:
      logging.shutdown()
      return 0

   print("Error:", error_message, file=sys.stderr)
   if logging.root.handlers: # tests that logging could be initialised before error occurred
      logging.error(error_message)

   logging.shutdown()
   return rc

# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import argparse
import logging
import os
import time
from   typing import Optional

class ConfigurationError(Exception):
   pass

class Configuration(object):
   """Combined backup configuration options from command line, environment, and config file"""
   def __init__(self, argv):
      """
      Combined backup configuration options from command line, environment, and config file (determined
      by command line or environment.

      :param argv: command line arguments (`sys.argv`).
      """

      # Default values
      self.archive_root_path= None
      self.database_path= None
      self.logfile_path= None
      self.include= []
      self.exclude= []
      self.password= None
      self.minimum_size_for_compression= 4096
      self.compressed_extensions= set([".jpg", ".tif", ".gz", ".tgz",])
      self.retention= [(1,7), (56,150)]

      # Command line
      args= self._get_command_line_options(argv)
      if args.f is not None:
         config_path= args.f
      elif "ABUS_CONFIG" in os.environ:
         config_path= os.environ["ABUS_CONFIG"]
      else:
         raise ConfigurationError("Missing config file path (-f option or ABUS_CONFIG environment variable)")
      is_list= args.list
      self.is_backup= args.backup
      self.is_restore= args.restore
      self.is_init= args.init
      self.is_rebuild= args.rebuild_index
      self.list_all= args.a
      self.patterns= args.glob
      self.cutoff= args.d

      # Config file
      with open(config_path, encoding="utf-8") as f:
         try:
            self._parse_config_file(f)
         finally:
            # Initialising log file now because it might be possible despite a subsequent
            # error during parsing.
            if self.logfile_path:
               logging.basicConfig(filename=self.logfile_path,
                                   level=logging.DEBUG,
                                   format='%(asctime)s %(levelname)-7s %(message)s',
                                   datefmt='%Y-%m-%d %H:%M:%S',
                                   )

      actions= is_list, self.is_backup, self.is_restore, self.is_init, self.is_rebuild
      n_actions= sum(1 for a in actions if a)
      if n_actions>1:
         raise ConfigurationError("conflicting command line actions")
      if n_actions==0:
         is_list= True
      if (self.list_all or self.cutoff) and not (self.is_restore or is_list):
         raise ConfigurationError("conflicting command line options (-a/-d without -r/-l)")
      if not self.archive_root_path:
         raise ConfigurationError("archive directory option not set")
      if not os.path.isdir(self.archive_root_path) and not self.is_init:
         raise ConfigurationError("missing archive directory ({})".format(self.archive_root_path))
      if not self.password:
         raise ConfigurationError("password directory option not set")
      if not self.include:
         raise ConfigurationError("missing or empty [include] section")
      if not self.logfile_path:
         raise ConfigurationError("logfile path option not set")

      if not self.database_path:
         self.database_path= self.archive_root_path+"/index.sl3"

   def _parse_config_file(self, lines):
      self.include= []
      self.exclude= []
      section= None
      for line in lines:
         line= line.strip()
         if not line or line.startswith('#'):
            pass
         elif line.lower().startswith("[incl"):
            section= self.include
         elif line.lower().startswith("[excl"):
            section= self.exclude
         elif line.lower().startswith("["):
            raise ConfigurationError("unknown section name: "+line)
         elif section is not None:
            line= line.replace("\\", "/")
            if line.endswith("/"): line= line[:-1]
            section.append(line)
         else:
            splut= line.split(maxsplit=1)
            if len(splut)!=2:
               raise ConfigurationError("missing value: "+line)
            keyword, args = splut
            if keyword=="archive":
               self.archive_root_path= args
            elif keyword=="indexdb":
               self.database_path= args
            elif keyword=="logfile":
               self.logfile_path= args
            elif keyword=="password":
               self.password= args
            elif keyword=="retain":
               self.retention= _parse_retention_args(args)
            else:
               raise ConfigurationError("unknown option: "+keyword)

   def _get_command_line_options(self, argv):
      parser= argparse.ArgumentParser(
         prog=os.path.basename(argv[0]),
         description="""
            The Abingdon BackUp Script makes copies of files to a backup location on a local filesystem.
            For documentation, read the accompanying README or the project front page on PyPi.
            """,
         )
      parser.add_argument('-f',
         action='store',
         metavar='path',
         help="""Path to config file required for defining backup location etc.
                 Defaults to value of the ABUS_CONFIG environment variable.""")
      parser.add_argument('--list', '-l',
         action='store_true',
         help='Lists the contens of the backup directory. This is the default action.')
      parser.add_argument('--backup',
         action='store_true',
         help="Backs up files to the backup directory.")
      parser.add_argument('--restore', '-r',
         action='store_true',
         help="Restores files from the backup directory to the current directory.")
      parser.add_argument('-a',
         action='store_true',
         help="""Includes all matching file versions when listing or restoring
            rather than only the latest matching version of each file.""")
      parser.add_argument('-d',
                          action='store',
                          type=_parse_date,
                          metavar="datetime",
                          help="""
            Cut-off time (format [[cc]yy]mmdd[-HHMM[SS]]) from which files are not included in listing or restore.
            The year defaults to the current year or the previous year if date (without time) would be in the future.
            The time defaults to midnight.
            Note that to show all files in May, say, the argument must be 0601.
            """)
      parser.add_argument('--init',
         action='store_true',
         help='Creates an empty index database and the backup directory.')
      parser.add_argument('--rebuild-index',
         action='store_true',
         help="""Reconstructs the index database from static backup files. N.B.: You must convince yourself of the
            integrity of the content file <date>.gz first.""")
      parser.add_argument('glob',
         nargs='*',
         help="""File path pattern (* matches /) of file to be included in listing or restore.
            '/' must be used as a path separator.""")
      return parser.parse_args(argv[1:])


   def backup_path_abs(self, archive_dir_rel, checksum):
      return self.archive_root_path +"/" +archive_dir_rel +"/" +checksum

   def mk_archive_path(self, relpath:str, archive_dir: Optional[str]= None, ext: Optional[str]= None) -> str:
      """
      Makes absolute path from relpath relative to archive root.

      :param archive_dir: will be prepended to path if given
      :param ext: will be appended to relpath if given
      """
      return (self.archive_root_path
              +("/"+archive_dir if archive_dir else "")
              +"/" +relpath
              +(ext if ext else "")
              )

def _parse_date(string, now=None):
   today_str= time.strftime("%Y%m%d", time.localtime(now))
   d_str, minus, t_str = string.partition("-")
   if (t_str=="") == (minus==""):
      if len(d_str) in(4,6,8) and len(t_str) in(0,4,6):
         if d_str.isdigit():
            if t_str=="" or t_str.isdigit():
               full_t_str= t_str + "000000"[len(t_str):]
               full_d_str= today_str[:8-len(d_str)] + d_str
               if len(d_str)==4 and full_d_str > today_str:
                  last_year= int(today_str[:4])-1
                  full_d_str= str(last_year) + d_str
               tm= time.strptime(full_d_str + full_t_str, "%Y%m%d%H%M%S")
               return time.mktime(tm)
   raise ValueError()

def _parse_retention_args(arg_string):
   try:
      values= tuple(float(a) for a in arg_string.split())
   except ValueError:
      raise ConfigurationError("expected numeric arguments: "+arg_string)
   n= len(values)
   if n==0 or n%2==1:
      raise ConfigurationError("expected pairs of numbers: "+arg_string)
   paired= ((values[i],values[i+1]) for i in range(0,n,2))
   retention= sorted(paired, key=lambda ra:ra[1])
   if len(set(age for _,age in retention)) < len(retention):
      raise ConfigurationError("duplicate retention age")
   rounders= [r for r,a in retention]
   for a,b in zip(rounders, rounders[1:]):
      if b % a != 0:
         raise ConfigurationError("retention frequencies {} and {} are not multiples".format(a,b))
   return retention

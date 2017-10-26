####
# bomail.cli.chstate
#
# Change state of files (open/closed/scheduled/trash).
####

import sys
import shutil
import os, subprocess, datetime
import tempfile
import dateutil.parser
from dateutil import tz
from dateutil.relativedelta import relativedelta
from subprocess import Popen, PIPE

import bomail.config.config as config
import bomail.cli.mailfile as mailfile
import bomail.util.remove_lines as remove_lines
import bomail.util.merge_lines as merge_lines
import bomail.util.util as util
import bomail.util.datestr as datestr

usage_str = """
Change the state of an email to open, closed, or scheduled.
Reads a list of filenames from stdin, one per line, and applies the operation.
Call with no args or -h to print this help.

  bomail chstate -o           # make filenames open
  bomail chstate -c           # make filenames closed
  bomail chstate -t           # trash filenames
  bomail chstate -ut          # untrash filenames
  bomail chstate -s datestr   # schedule filename for datestr (e.g. yyyy-mm-dd)
"""


# remove files from open and scheduled lists
def remove_from_lists(filelist):
  if os.path.exists(config.openlist_file):
    remove_lines.do_sorted(config.openlist_file, sorted(filelist))
  if os.path.exists(config.scheduledlist_file):
    remove_lines.do_sched(config.scheduledlist_file, set(filelist))


# change all files' state to open
def make_open(filelist, mgr, remove_old=True):
  if remove_old:
    remove_from_lists(filelist)
  # sort openlist by lexicographic
  merge_lines.do(config.openlist_file, sorted(filelist))
  for f in filelist:
    mgr.set(f, mailfile.STATE_L, "open")


# change all files' state to closed
def make_closed(filelist, mgr):
  remove_from_lists(filelist)
  for f in filelist:
    mgr.set(f, mailfile.STATE_L, "closed")


def scheduled_list_str(filename, sched_datestr):
  return sched_datestr + " " + filename


# schedule all files for sched
# sched is a datetime object
def schedule(filelist, sched, mgr):
  remove_from_lists(filelist)
  # round down to the minute
  rounded_date = sched - relativedelta(seconds=sched.second, microseconds=sched.microsecond)
  datestr = rounded_date.strftime("%Y-%m-%dT%H:%M")
  # sort scheduledlist
  lines = [scheduled_list_str(f, datestr) for f in filelist]
  merge_lines.do(config.scheduledlist_file, lines)
  for f in filelist:
    mgr.set(f, mailfile.STATE_L, "scheduled " + datestr)


# trash all files, including remove them from msg_ids_file
# return corresponding list of new filenames (in trash folder)
def trash(filelist, mgr):
  remove_from_lists(filelist)
  if not os.path.exists(config.trash_dir):
    os.makedirs(config.trash_dir)
  newnames = []
  for f in filelist:
    d = mgr.get_all(f)
    new_dir,new_ext = mailfile.get_trashfilepath(f, d)
    new_name = new_dir + new_ext
    os.makedirs(new_dir, exist_ok=True)
    if os.path.exists(f):
      util.mv_file(f, new_name)
    else:
      mailfile.write_to_file(new_name, d)
    if len(d[mailfile.ATTACH_L].strip()) > 0:
      attach_dir = mailfile.get_attach_dir(d)
      if os.path.exists(attach_dir):
        trash_attach_dir = mailfile.get_trash_attach_dir(f, d)
        os.makedirs(trash_attach_dir, exist_ok=True)
        for attach_f in os.listdir(attach_dir):
          util.mv_file(attach_dir + attach_f, trash_attach_dir + attach_f)
    newnames.append(new_name)
  mgr.trash(filelist)
  return newnames


def do_untrash(trashed_filenames, mgr):
  datalist = [mailfile.file_to_data(f) for f in trashed_filenames]
  create_filelist = ["".join(mailfile.get_mailfilepath(d)) if f[-4:] == "mail" else "".join(mailfile.get_draftfilepath(d)) for d,f in zip(datalist, trashed_filenames)]
  untrash(create_filelist, datalist, mgr)


# given list of new filenames and data to put in them
def untrash(create_filelist, datalist, mgr):
  # 1) create mailfiles
  create(create_filelist, datalist, mgr)
  # 2) move attachments back if needed
  for fname,d in zip(create_filelist,datalist):
    if len(d[mailfile.ATTACH_L].strip()) > 0:
      trash_attach_path = mailfile.get_trash_attach_dir(fname, d)
      dest_path = mailfile.get_attach_dir(d)
      if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
      util.mv_file(trash_attach_path, dest_path)
    

# the opposite of trash basically
def create(filelist, datalist, mgr):
  for fname,d in zip(filelist, datalist):
    if os.path.exists(fname):
      with open(config.error_log_file, "a") as f:
        f.write("Creating file, already exists: " + fname + "\n")
        d2 = mailfile.file_to_data(fname)
        for i in range(len(d)):
          if d2[i] != d[i]:
            f.write(">>>> old version " + mailfile.fields[i] + ":\n")
            f.write(d2[i] + "\n")
            f.write(">>>> new version:\n")
            f.write(d[i] + "\n")
        f.write("\n")
    elif d[mailfile.MSG_ID_L] in mgr.ids.ids_to_filenames:
      with open(config.error_log_file, "a") as f:
        f.write("Creating file, non-identical file with same message ID already exists: " + mgr.ids.get(d[mailfile.MSG_ID_L]) + "\n")
        f.write("New data:\n  ")
        f.write("\n  ".join(d) + "\n")
    else:
      mailfile.write_to_file(fname, d)
  mgr.create(filelist, datalist)
  make_open(filelist, mgr, False)  # False == don't try to remove old ones from list
 

def main(args, filelist, mgr):
  filelist.sort()
  if args[0] == "-o":
    make_open(filelist, mgr)
  elif args[0] == "-c":
    make_closed(filelist, mgr)
  elif args[0] == "-t":
    trash(filelist, mgr)
  elif args[0] == "-ut":
    do_untrash(filelist, mgr)  # filelist are all currently in trash
  elif args[0] == "-s":
    sched = datestr.get_datetime(args[1])
    if sched is None:
      print("Could not parse scheduling date string!")
      exit(0)
    schedule(filelist, sched, mgr)


def main_cli():
  if len(sys.argv) < 2 or "-h" in sys.argv:
    print(usage_str)
    exit(0)
  mgr = mailfile.MailMgr()
  # remove each trailing newline
  main(sys.argv[1:], [s[:-1] for s in sys.stdin.readlines()], mgr)


if __name__ == "__main__":
  main_cli()


####
# bomail.cli.search
#
# Command-line interface to search.
####

import sys
import os, subprocess, shlex
import dateutil.parser
from dateutil import tz
import textwrap

import bomail.config.config as config
import bomail.cli.mailfile as mailfile
import bomail.cli.chstate as chstate
import bomail.util.listmail as listmail
import bomail.util.search_opts as search_opts

my_usage_str = """
Searches through mail for files matching given arguments.

High-level options:
    search.py -h            # print this help
    search.py -num ...      # only print the number of matches
    search.py -sum ...      # print summaries along with filenames
"""
usage_str = my_usage_str + search_opts.options_str

default_max_results = -1  # no max


# given filelist which already matches and is sorted,
# filter 'addlist' and merge into filelist in sorted order
def merge(filelist, addlist, mgr, arg_str):
  # note: shlex.split is quite slow
  query = search_opts.SQ_from_str(arg_str)
  new_addlist = [addlist[i] for i in query.filter(addlist, mgr)]
  filelist += new_addlist  # todo: smarter merge by assuming both are sorted
  filelist.sort(reverse = query.sort_new)


# return list of filenames
def main_argstr(arg_str, mgr, filelist=None):
  # note: shlex.split is quite slow, avoid calling it many times per second
  return main_arglist(shlex.split(arg_str), mgr, filelist=filelist)


# return list of filenames
def main_arglist(args, mgr, filelist=None):
  query = search_opts.SearchQuery(args)
  if filelist is None:
    filelist = listmail.do_list(query, mgr)
  new_filelist = [filelist[i] for i in query.filter(filelist, mgr, listmailed=(filelist is None))]
  new_filelist.sort(reverse = query.sort_new)
  return new_filelist


def main_cli():
  args = sys.argv[1:]
  if "-h" in args:
    print(usage_str)
    exit()
  printout = True
  if "-num" in args:
    printout = False
    i = args.index("-num")
    args = args[:i] + ([] if i+1 >= len(args) else args[i+1:])
  summaries = False
  if "-sum" in args:
    summaries = True
    i = args.index("-sum")
    args = args[:i] + ([] if i+1 >= len(args) else args[i+1:])
  filelist = main_arglist(args, mailfile.MailMgr())
  if printout:
    if summaries:
      mgr = mailfile.MailMgr()
      for fname in filelist:
        print(fname)
        is_sent = bool(mgr.get(fname, mailfile.SENT_L))
        print("    " + mgr.get(fname, mailfile.DATE_L)[:10] + "  " + mgr.get(fname, mailfile.FROM_L if is_sent else mailfile.TO_L)[:64])
        print("    " + mgr.get(fname, mailfile.SUBJ_L)[:76])
        split_lists = [textwrap.wrap(s, 76, replace_whitespace=False) for s in mgr.get(fname, mailfile.BODY_L).split("\n")]
        lines = ["    " + l for splitter in split_lists for l in splitter][:4]
        print("\n".join(lines))
        print()
    else:
      print("\n".join(filelist))
  else:
    print(str(len(filelist)) + " matching messages")


if __name__ == "__main__":
  main_cli()


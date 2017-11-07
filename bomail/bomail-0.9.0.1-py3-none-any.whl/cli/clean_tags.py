####
# bomail.cli.clean_tags
#
# A little utility to read through all emails, find any tags
# that are unused, and remove them from the tag list.
####

import os,sys

import bomail.cli.mailfile as mailfile
import bomail.cli.search as search
from bomail.util.tags import TagMgr

usage_str = """Scans all email for saved tags that aren't being used,
and deletes them."""

# maximum messages to hold in memory before releasing them
MAX_MSGS_IN_MEM = 10000


def main_cli():
  if "-h" in sys.argv:
    print(usage_str)
    exit()

  mgr = mailfile.MailMgr()
  all_fnames = search.main_argstr("", mgr)
  used_tagset = set()
  msgs_in_mem = 0
  for fname in all_fnames:
    my_tagset = mgr.get_tagset(fname)
    if "" in my_tagset:
      print(fname)
    used_tagset.update(my_tagset)
    msgs_in_mem += 1
    if msgs_in_mem >= MAX_MSGS_IN_MEM:
      mgr = mailfile.MailMgr()  # release memory of older messages

  tagmgr = TagMgr()
  tagmgr.reset_tags_to(list(used_tagset))


if __name__ == "__main__":
  main_cli()


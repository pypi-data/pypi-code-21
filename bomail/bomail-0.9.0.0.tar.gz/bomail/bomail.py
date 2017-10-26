
import os, sys

import bomail.config.config as config
from bomail.cli import gui,process,check_sched,search,chstate,mailfile,compose,clean_tags,send,stats
import bomail.util.datestr

usage_str = """
Usage:
Use bomail <command> -h for help on that command.

Commands:
  bomail gui         Launch interface (if in doubt, run this)

  bomail process     Check for and process new emails
  bomail check_sched Check 'scheduled' emails and unschedule them
  bomail search      Search
  bomail chstate     Change state of emails (open/closed/scheduled/trash)
  bomail compose     Compose new emails as blank, reply, forward
  bomail mailfile    See fields of an email or add/remove tags
  bomail send        Send drafts
  bomail stats       See some stats about email

  bomail help datestr  Print help about using relative dates
  bomail help tags     Print help about 'dirlike' tags

Configuration file: ~/.bomailrc
Data location: """ + config.bomail_data_base + """

"""

extra_info = """
Note many commands read a list of filenames from stdin,
so for example to tag a set of emails 'food', you can use:
  bomail search chocolate | bomail mailfile -add-tags food

"""

taghelp_str = """
Using tags:

An email can have unlimited tags.
Searching for emails with a given tag must match
exactly (so "bomail search -t happy" does not match
emails tagged happydays, but does match emails tagged happy.)

Twist: 'directory-like' tags.
Whenever your tag has a / character, it matches searches
for tags of a prefix up to a /.

Example: anything tagged social/twitter, social/facebook,
or social/mastodon will match "bomail search -t social".
However, none of those will match "bomail search -t facebook".
(Use "bomail search -t social/facebook" instead.)

"""


def main():
  if len(sys.argv) <= 1:
    print(usage_str)
    exit(0)

  if sys.argv[1] == "help":
    if len(sys.argv) < 2:
      print(usage_str)
    elif sys.argv[2] == "datestr":
      print(bomail.util.datestr.datestr_str)
    elif sys.argv[2] == "tags":
      print(taghelp_str)
    else:
      print(usage_str)
    exit(0)

  # hacky but simple: make programs act like they were
  # invoked from command line
  sys.argv = sys.argv[1:]

  if sys.argv[0] == "gui":
    gui.main_cli()
  elif sys.argv[0] == "process":
    process.main_cli()
  elif sys.argv[0] == "check_sched":
    check_sched.main_cli()
  elif sys.argv[0] == "search":
    search.main_cli()
  elif sys.argv[0] == "chstate":
    chstate.main_cli()
  elif sys.argv[0] == "mailfile":
    mailfile.main_cli()
  elif sys.argv[0] == "compose":
    compose.main_cli()
  elif sys.argv[0] == "clean_tags":
    clean_tags.main_cli()
  elif sys.argv[0] == "send":
    send.main_cli()
  elif sys.argv[0] == "stats":
    stats.main_cli()

  else:
    print(usage_str)

if __name__ == "__main__":
  main()


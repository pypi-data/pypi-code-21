####
# bomail.config.config
#
# Main configuration file.
####

import os, sys

bomailrc_filename = ".bomailrc"


#--------------------------------------------------------------
setup_success_str = """
Basic setup successful! Please edit ~/.bomailrc for:
 * SMTP server information, in order to send email
 * location to find new emails (~/mail/new by default)
 * location to put processed emails (~/mail/cur by default)
 * other options.

Run bomail to begin...
"""


#--------------------------------------------------------------
bomail_tabcomplete_str = """

_bomail()
{
    local cur=${COMP_WORDS[COMP_CWORD]}
    COMPREPLY=( $(compgen -W "gui process check_sched search chstate compose mailfile send stats clean_tags" -- $cur) )
}
complete -F _bomail bomail

"""


#--------------------------------------------------------------
sample_mailhandlers_str = """## This file controls handling of new emails in bomail.
## In this file, lines starting with '#' are comments.

## ------------------------------------------------------
## Section 1: Special options
##
## Comment each option out by prepending '#' to turn if off.
## ------------------------------------------------------

## Tag replies to a thread with parent message's tags
-autotagreplies

## Use tags from last line of email if of the form "tags: tag1, ..."
-lastlinetags

## Automatically close any sent mail
-close-sent


## ---------------------------------------------------
## Section 2: Custom handlers
##
## You write these.
## ---------------------------
##
## Format of each handler (blank line between handlers):
##
## search_string
## action_string
##
## search_string1
## OR search_string2
## OR search_string3
## action_string1
## AND action_string2
## AND action_string3
##
## search_string is a command-line argument to search
## actions are (for 'schedstr' see bomail chstate -h):
##   open
##   close
##   schedule schedstr
##   tag tag1, tag2
## ---------------------------------------------------



"""

#--------------------------------------------------------------
sample_config_str = """## bomail configuration file
##
## All lines beginning with # are comments.
## To 'uncomment' a line, delete the initial #.



## ============================================================
## User info: must edit everything in this section!

name = YOUR NAME
email_addr = USER@DOMAIN.COM

#alias_addresses = ALSO_ME@DOMAIN.COM, ALSO_METOO@DOMAIN.COM

smtp_servername = smtp.gmail.com
smtp_port = 587

## If commented, tries to read password from ~/.getmail/getmailrc
#smtp_password = PASSWORD_FOR_email_addr



## ============================================================
## Organization options: should confirm these are okay

bomail_location = ~/bomail
new_rawmail_location = ~/mail/new
processed_rawmail_location = ~/mail/cur



## ============================================================
## Important UI options

## Comment next line to turn off threading (conversations)
threads_on

read_program = less
edit_program = vim

## Comment next line to use vim-style navigation (hjkl for left/down/up/right)
#arrowkey_navigation

## Options are light1, light2, dark1, dark2
colorscheme = dark1



## ============================================================
## Other UI options

## Options are none, some, all
strip_newlines_in_msg_preview = some

## Num lines (including subject/author/date and preview lines) per message
total_lines_per_msg = 5
threadview_total_lines_per_msg = 10

## Number of characters to use ("len") and for spacing ("pad")
date_len = 20
date_pad = 2
author_len = 24
author_pad = 2

## Comment (uncomment) to turn off (on)
#hline_between_msgs
skipline_between_msgs
show_tags
tags_on_topline


"""
#--------------------------------------------------------------


home = os.getenv("HOME")
config_file = os.path.join(home, bomailrc_filename)


# Initial setup!
if not os.path.exists(config_file):
  print("\nWelcome to bomail!")
  sys.stdout.write("Name (as it will appear in From line): ")
  sys.stdout.flush()
  myname = sys.stdin.readline().strip()
  sys.stdout.write("Email address (primary, i.e. send email from): ")
  sys.stdout.flush()
  myaddr = sys.stdin.readline().strip()
  sys.stdout.write("Data files location? (leave blank for default of ~/bomail/): ")
  sys.stdout.flush()
  datadir = sys.stdin.readline().strip()
  if len(datadir) == 0:
    datadir = "~/bomail"
  sys.stdout.write("Add bomail command tab-completion to your ~/.bashrc file? (y/n): ")
  sys.stdout.flush()
  tabcomplete = sys.stdin.readline().strip()

  if len(tabcomplete) > 0 and tabcomplete[0] in ["y", "Y"]:
    with open(os.path.join(home, ".bashrc"), "a") as f:
      f.write(bomail_tabcomplete_str)

  # this is not ideal because it doesn't change if the configuration at
  # the bottom of the file changes
  metadata_dir  = os.path.join(datadir, "metadata/")
  handlers_file = os.path.join(metadata_dir, "mail-handlers.txt")
  if not os.path.exists(handlers_file):
    os.makedirs(metadata_dir, exist_ok=True)
    with open(handlers_file, "w") as f:
      f.write(sample_mailhandlers_str)

  with open(config_file, "w") as f:
    f.write(sample_config_str.replace("YOUR NAME", myname).replace("USER@DOMAIN.COM", myaddr).replace("~/bomail", datadir))

  print(setup_success_str)
  exit(0)


# Function to open and parse config file
def parse_config_file():
  options_dict = {}
  def parse_line(line):
    line = line.strip()
    if len(line) > 0 and line[0] != "#":
      if "=" in line:
        left, right = line.split("=")
        options_dict[left.strip()] = right.strip()
      else:
        options_dict[line.strip()] = True
  
  with open(config_file) as f:
    for line in f:
      parse_line(line)
  return options_dict


# Actually do it
options_dict = parse_config_file()


# --------------------------------------------------------------
# User info

name = options_dict["name"]
email_addr = options_dict["email_addr"]
my_aliases = []
if "alias_addresses" in options_dict:
  my_aliases = [s.strip() for s in options_dict["alias_addresses"].split(",")]

smtp_servername = options_dict["smtp_servername"]
smtp_port = int(options_dict["smtp_port"])
password = ""
if "smtp_password" in options_dict:
  password = options_dict["smtp_password"]
else:
  try:
    with open(os.path.join(home, ".getmail/getmailrc")) as f:
      for line in f:
        if line.startswith("password ="):
          password = line[len("password ="):].strip()
          break
  except:
    pass


# --------------------------------------------------------------
# Organization locations

def add_slash(s):
  return s if s[-1] == "/" else s + "/"
bomail_data_base = add_slash(options_dict["bomail_location"].replace("~", home))
new_rawmail_dir = add_slash(options_dict["new_rawmail_location"].replace("~", home))
old_rawmail_dir = add_slash(options_dict["processed_rawmail_location"].replace("~", home))


# --------------------------------------------------------------
# Options not in bomailrc (may edit)

# how many new emails to process at a time, -1 for no limit
process_new_limit = -1

# how many new emails to process in a batch, decrease to save memory
# for very large imports
process_batch_size = 20000

# tag drafts with same tags as parent
autotag_draft_replies = True

# Replying to emails
# will replace %from, %to, %date, %time, %body
# with the corresponding text from the quoted email
quote_format = """\n
%from wrote on %date at %time:
%body"""

# %a is day of week; %Y,%m,%d are year/month/date
# %H,%M are hour/minute
quote_date_fmt = "%a, %Y-%m-%d"  
quote_time_fmt = "%H:%M"         
quote_line_prefix = "> "


# --------------------------------------------------------------
# File locations: suggested not to edit

# Locations of directories
email_dir     = os.path.join(bomail_data_base, "email/")
attach_dir    = os.path.join(bomail_data_base, "attachments/")
drafts_dir    = os.path.join(bomail_data_base, "drafts/")
trash_dir     = os.path.join(bomail_data_base, "trash/")
metadata_dir  = os.path.join(bomail_data_base, "metadata/")

# Locations of files that must be edited by hand
handlers_file      = os.path.join(metadata_dir, "mail-handlers.txt")
addr_alias_file    = os.path.join(metadata_dir, "aliases.txt")

# Locations of files that may be edited by hand
tags_file          = os.path.join(metadata_dir, "tags.txt")
addr_book_file     = os.path.join(metadata_dir, "addr_book.txt")

# Locations of files that should not be hand-edited
openlist_file      = os.path.join(metadata_dir, "openlist.txt")
scheduledlist_file = os.path.join(metadata_dir, "scheduledlist.txt")
msg_ids_file       = os.path.join(metadata_dir, "msg_ids.txt")
tab_config_file    = os.path.join(metadata_dir, "tab_config.py")

# Locations of logs, these can be deleted whenever
acts_log_file      = os.path.join(metadata_dir, "acts_log.txt")
error_log_file     = os.path.join(metadata_dir, "error_log.txt")

for d in [email_dir, attach_dir, drafts_dir, trash_dir, metadata_dir]:
  if not os.path.exists(d):
    os.makedirs(d)


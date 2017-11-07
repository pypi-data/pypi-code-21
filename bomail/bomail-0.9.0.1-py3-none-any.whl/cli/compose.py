####
# bomail.cli.compose
#
# Compose new emails as blank, reply, forward.
####

import sys
import string
import traceback
import os, random
import dateutil
import email, email.utils, uuid

import bomail.config.config as config
import bomail.cli.mailfile as mailfile
import bomail.cli.chstate as chstate
import bomail.util.addr as addr
import bomail.util.util as util

usage_str = """Use with option -h to print this help.
There are two forms of usage.

1. To compose a new email from scratch, use no options or any combination of:
  -to "example here"              add "example string" to recips (may be comma-sep list)
  -subj "example here"            set subject line to "example here"
  -cc "example here"              add "example here" to cc (may be comma-sep list)
  -bcc "example here"             ditto for bcc

2. To compose based on an existing email, use one of:
  -ro yyyy/mm-dd/msgid            reply-one to msgid
  -ra yyyy/mm-dd/msgid            reply-all to msgid
  -rr yyyy/mm-dd/msgid            reply-recipients to msgid
  -f yyyy/mm-dd/msgid "example"   forward msgid to "example"

(Both 1 and 2.) Optional, add:
  -body "body of email here"        
"""


def create(data, mgr):
  nowstr = util.utc_timestr()
  draft_dir, ext = mailfile.get_draftfilepath(data)
  filename = draft_dir + ext
  os.makedirs(draft_dir, exist_ok=True)
  chstate.create([filename], [data], mgr)
  chstate.make_open([filename], mgr)
  mgr.ensure_loaded(filename)
  return filename


def get_blank_draft_data():
  new_data = [""]*len(mailfile.fields)
  new_data[mailfile.FROM_L] = config.name + " <" + config.email_addr + ">"
  new_data[mailfile.DATE_L] = util.local_now_isostr()
  new_data[mailfile.SENT_L] = "True"
  new_data[mailfile.STATE_L] = "open"
  # create a message id, at least for now
  new_data[mailfile.MSG_ID_L] = email.utils.make_msgid(uuid.uuid4().hex)
  return new_data


# if quote, include previous email message as quoted text
def get_old_and_new_data(msg_file, quote):
  old_data = mailfile.file_to_data(msg_file)
  new_data = get_blank_draft_data()
  new_data[mailfile.REFS_L] = old_data[mailfile.MSG_ID_L] + ", " + old_data[mailfile.REFS_L]
  new_data[mailfile.TAGS_L] = old_data[mailfile.TAGS_L] if config.autotag_draft_replies else ""
  prev_date_obj = dateutil.parser.parse(old_data[mailfile.DATE_L])
  prev_date_str = prev_date_obj.strftime(config.quote_date_fmt)
  prev_time_str = prev_date_obj.strftime(config.quote_time_fmt)
  if quote:
    body_lines = old_data[mailfile.BODY_L].split("\n")
    body_str = config.quote_line_prefix + ("\n" + config.quote_line_prefix).join(body_lines)
    new_data[mailfile.BODY_L] = config.quote_format.replace("%date", prev_date_str).replace("%time", prev_time_str).replace("%from", old_data[mailfile.FROM_L]).replace("%body", body_str)
  return old_data, new_data
  

def get_subject_with(old_sub, prefix):
  return old_sub if old_sub.startswith(prefix) else prefix + old_sub


def reply_one(msg_file, mgr, quote):
  old_data, new_data = get_old_and_new_data(msg_file, quote)
  new_data[mailfile.SUBJ_L] = get_subject_with(old_data[mailfile.SUBJ_L], "Re: ")
  new_data[mailfile.TO_L] = old_data[mailfile.FROM_L]
  return create(new_data, mgr)


def reply_all(msg_file, mgr, quote, include_sender=True):
  old_data, new_data = get_old_and_new_data(msg_file, quote)
  new_data[mailfile.SUBJ_L] = get_subject_with(old_data[mailfile.SUBJ_L], "Re: ")
  to_list = [s for s in old_data[mailfile.TO_L].split(", ") if not addr.is_str_me(s)]
  to_list += [s for s in old_data[mailfile.CC_L].split(", ") if not addr.is_str_me(s)]
  if include_sender:
    to_list = old_data[mailfile.FROM_L].split(", ") + to_list
  new_data[mailfile.TO_L] = ", ".join(to_list)
  return create(new_data, mgr)


def forward(msg_file, to_str, mgr):
  old_data, new_data = get_old_and_new_data(msg_file)
  new_data[mailfile.SUBJ_L] = get_subject_with(old_data[mailfile.SUBJ_L], "Fwd: ")
  new_data[mailfile.TO_L] = to_str
  return create(new_data, mgr)


def new_compose(subj_str, to_str, cc_str, bcc_str, bodystr, mgr):
  d = get_blank_draft_data()
  d[mailfile.TO_L] = to_str
  d[mailfile.CC_L] = cc_str
  d[mailfile.BCC_L] = bcc_str
  d[mailfile.SUBJ_L] = subj_str
  d[mailfile.BODY_L] = bodystr
  return create(d, mgr)


def main_cli():
  if "-h" in sys.argv:
    print(usage_str)
    exit(0)
  try:
    args = sys.argv
    bodystr = ""
    mgr = mailfile.MailMgr()
    if len(args) <= 1:
      print(new_compose("", "", "", "", mgr))
      sys.exit(0)

    if "-body" in args:
      ind = args.index("-body")
      if ind < len(args) - 1:
        bodystr = args[ind+1]
        args = args[:ind] + args[ind+2:]

    if args[1] == "-ro":
      print(reply_one(args[2], bodystr, mgr))
    elif args[1] == "-ra":
      print(reply_all(args[2], bodystr, mgr))
    elif args[1] == "-rr":
      print(reply_all(args[2], bodystr, mgr, include_sender=False))
    elif args[1] == "-f":
      print(forward(args[2], args[3], bodystr, mgr))
    else:
      to_str_list = []
      cc_str_list = []
      bcc_str_list = []
      subj_str = ""
      i = 1
      while i < len(args):
        if args[i] == "-to":
          to_str_list.append(args[i+1])
          i += 1
        elif args[i] == "-subj":
          subj_str = args[i+1]
          i += 1
        elif args[i] == "-cc":
          cc_str_list.append(args[i+1])
          i += 1
        elif args[i] == "-bcc":
          bcc_str_list.append(args[i+1])
          i += 1
        i += 1
      print(new_compose(subj_str, ", ".join(to_str_list), ", ".join(cc_str), ", ".join(bcc_str), bodystr, mgr))
  except Exception:
    traceback.print_exc()
    print("")
    print(usage_str)


if __name__ == "__main__":
  main_cli()


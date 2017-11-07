####
# bomail.cli.mailfile
#
# Specifies the bomail file format, called 'mailfile',
# and mail manager object, and some commands to view/edit
# metadata of emails.
####

import sys
import os, bisect
import email.utils, uuid

import datetime
import dateutil, dateutil.parser

import bomail.config.config as config
import bomail.util.tags as tags
import bomail.util.msgids as msgids

####
# This file specifies
# (1) the mailfile format and interface
# (2) MailMgr, the mail manager object

# Emails are stored in "mailfiles".
# A mailfile is of the form:
#   field_name: field_value
#   ...
#   field_name: field_value
#   =================
#   body_of_email

# Formats of specific entries:
# "addr" can be either of these:
#    name@domain.com
#    Longer Name Here <name@domain.com>
#
# "msg_id" is an email message id enclosed in < >
#
# "date" is an ISO8061 date string in UTC time, i.e. yyyy-mm-ddTHH:MM:SS or some prefix
#
# no newlines except in the body
#
# all lists are comma-and-space separated, implying that their
# elements shouldn't have either commas or spaces in them
####

fields = ["from","to","cc","bcc","subject","date","sent","msg-id","references","referenced_by","attachments","state","tags","body"]
FROM_L   = 0    # addr
TO_L     = 1    # addr_list
CC_L     = 2    # addr_list
BCC_L    = 3    # addr_list
SUBJ_L   = 4    # string with no newline
DATE_L   = 5    # datestr
SENT_L   = 6    # "True" if sent from me, "False" otherwise
MSG_ID_L = 7    # msg_id
REFS_L   = 8    # list of msg_ids
REF_BY_L = 9    # list of msg_ids
ATTACH_L = 10   # list of attachment files
STATE_L  = 11   # "open", "closed", or "scheduled datestr"
TAGS_L   = 12   # list of tags
BODY_L   = 13   # arbitrary string

sep = "================\n"  # between headers and body

usage_str = """
Usage: reads a list of filenames from stdin and does the action for each one.
Options: -g (get the indicated fields), -add-tags, -rm-tags

  mailfile.py -h                  # print this help
  mailfile.py -g all              # get and print all fields
  mailfile.py -g from bcc date    # get and print the fields 'from', 'bcc', and 'date'
  mailfile.py -add-tags tag1 tag2 # add the tags 'tag1' and 'tag2'
  mailfile.py -rm-tags tag1 tag2  # remove the tags 'tag1' and 'tag2'
"""


error_data = [
  "error file not found <>",
  "", "", "", "", "9999-12-28", "True", email.utils.make_msgid(uuid.uuid4().hex),
  "", "", "", "open", "", "error file not found"]


def msgid_as_path(msg_id):
#  return msg_id.replace("<","").replace(">","").replace("/","-")
  return msg_id.replace("/","-")


# input date in isoformat
# output directory, prefix
def get_datepath(datestr):
  s = dateutil.parser.parse(datestr).astimezone(datetime.timezone.utc).strftime("%Y/%m-%d/T%H:%M:%S")
  return s[:-9], s[-9:]


def wrong_get_datepath(datestr):
  s = dateutil.parser.parse(datestr).astimezone(datetime.timezone.utc).strftime("%Y/%m-%d/T%H:%S")
  return s[:-6], s[-6:]
def wrong_get_rel_idpath(datestr, msgid):
  mydir, ext = wrong_get_datepath(datestr)
  return mydir, ext + "-" + msgid_as_path(msgid)
def wrong_get_attachdir(data):
  mydir, ext = wrong_get_rel_idpath(data[DATE_L], data[MSG_ID_L])
  return config.attach_dir + mydir + ext + "/"


def get_rel_idpath(datestr, msgid):
  mydir, ext = get_datepath(datestr)
  return mydir, ext + "-" + msgid_as_path(msgid)


# assumes it's not a draft
# return dir, filename
def get_mailfilepath(data):
  mydir, ext = get_rel_idpath(data[DATE_L], data[MSG_ID_L])
  return config.email_dir + mydir, ext + ".mail"


def get_attach_dir(data):
  mydir, ext = get_rel_idpath(data[DATE_L], data[MSG_ID_L])
  return config.attach_dir + mydir + ext + "/"


def get_trash_attach_dir(filename, data):
  mydir, ext = get_rel_idpath(data[DATE_L], data[MSG_ID_L])
  return config.trash_dir + "attach/" + mydir + ext + "/"


def get_trashfilepath(filename, data):
  mydir, ext = get_rel_idpath(data[DATE_L], data[MSG_ID_L])
  return config.trash_dir + mydir, ext + filename[filename.rfind("."):]


def get_draftfilepath(data):
  mydir, ext = get_rel_idpath(data[DATE_L], data[MSG_ID_L])
  return config.drafts_dir + mydir, ext + ".draft"


def get_rawfilepath(data):
  mydir, ext = get_rel_idpath(data[DATE_L], data[MSG_ID_L])
  return config.old_rawmail_dir + mydir, ext + ".mime"
  

def do_get_referencelist(my_id, refstr):
  reflist = []
  for r in refstr.split(", "):
    rs = r.strip()
    if len(rs) > 0 and rs != my_id:
      reflist.append(rs)
  return reflist


def do_get_parent_id(my_id, reflist):
  if len(reflist) == 0 or reflist[-1] == my_id:
   return None
  return reflist[-1]


def data_to_str(data):
  a = []
  for i,field in enumerate(fields[:-1]):
    a.append(field)
    a.append(": ")
    a.append(data[i])
    a.append("\n")
  a.append(sep)
  a.append(data[BODY_L])
  return "".join(a)


def file_to_data(filename):
  data = []
  try:
    with open(filename) as f:
      for i in range(len(fields)-1):
        line = f.readline()
        data.append(line[len(fields[i]) + 2 : -1])  # erase "field: " and trailing "\n"
      f.readline()  # separator
      data.append(f.read())
  except:
    with open(config.error_log_file, "a") as f:
      f.write("mailfile: could not find " + str(filename) + "\n")
    return list(error_data)
  return data


def write_to_file(filename, data):
  if "/" in filename:  # hopefully!?!
    os.makedirs(filename[:filename.rfind("/")], exist_ok=True)
  with open(filename, "w") as f:
    f.write(data_to_str(data))


# lazily loaded mailfiles
class MailMgr:
  def __init__(self):
    self.ids = msgids.Ids()
    self.datas = {}   # None or not present if unloaded
    
  def ensure_loaded(self, filename):
    if filename not in self.datas or self.datas[filename] is None:
      self.datas[filename] = file_to_data(filename)

  def get(self, filename, ind):
    self.ensure_loaded(filename)
    return self.datas[filename][ind]

  def get_all(self, filename):
    self.ensure_loaded(filename)
    return self.datas[filename]

  def set(self, filename, ind, val):
    self.ensure_loaded(filename)
    self.datas[filename][ind] = val
    write_to_file(filename, self.datas[filename])

  def get_references(self, filename):
    my_id = self.get(filename, MSG_ID_L).strip()
    refstr = self.get(filename, REFS_L)
    return do_get_referencelist(my_id, refstr)

  def get_refby(self, filename):
    s = self.get(filename, REF_BY_L)
    return s.split(", ") if len(s) > 0 else []

  def add_refby(self, filename, msg_id):
    prev_refbys = self.get_refby(filename)
    prev_refbys.append(msg_id)
    self.set(filename, REF_BY_L, ", ".join(prev_refbys))

  # get the mailfile of the message that 'filename' replies to, or None
  def get_parent_id(self, filename):
    return do_get_parent_id(self.get(filename, MSG_ID_L), self.get_references(filename))

  def get_parent(self, filename, ids_to_filenames):
    ref = self.get_parent_id(filename)
    return ids_to_filenames[ref] if ref in ids_to_filenames else None

  def get_tags(self, filename, include_folders=False):
    return tags.get_taglist_from_str(self.get(filename, TAGS_L), include_folders=include_folders)

  def get_tagset(self, filename, include_folders=False):
    return tags.get_tagset_from_str(self.get(filename, TAGS_L), include_folders=include_folders)

  def add_tags(self, filelist, my_taglist):
    taglist = tags.get_taglist_from_list(my_taglist)  # clean, sort tags
    if len(taglist) > 0:
      for filename in filelist:
        new_taglist = tags.join(taglist, self.get_tags(filename))
        self.set(filename, TAGS_L, tags.get_str_from_clean_taglist(new_taglist))

  def remove_tags(self, filelist, my_taglist):
    taglist = tags.get_taglist_from_list(my_taglist)  # clean, sort tags
    if len(taglist) > 0:
      for filename in filelist:
        new_taglist = tags.get_nonmatching(self.get_tags(filename), taglist)
        self.set(filename, TAGS_L, tags.get_str_from_clean_taglist(new_taglist))

  def set_tags(self, filelist, taglist):
    tagstr = tags.get_str_from_taglist(taglist)  # clean tags
    for filename in filelist:
      self.set(filename, TAGS_L, tagstr)

  # if there was an update to these files (added, changed, or deleted),
  # just remove them and re-load at next request
  def updated_filelist(self, filelist):
    for f in filelist:
      if f in self.datas:
        del self.datas[f]

  def create(self, filelist, datalist):
    for f,d in zip(filelist, datalist):
      self.datas[f] = d
    self.ids.add([d[MSG_ID_L] for d in datalist], filelist)
    for f,d in zip(filelist, datalist):
      p_id = do_get_parent_id(d[MSG_ID_L], do_get_referencelist(d[MSG_ID_L], d[REFS_L]))
      if p_id is not None and p_id in self.ids.ids_to_filenames:
        self.add_refby(self.ids.get(p_id), d[MSG_ID_L])

  # when files are deleted
  def trash(self, filelist):
    msg_ids = []
    for f in filelist:
      msg_ids.append(self.get(f, MSG_ID_L))
      if f in self.datas:  # which it should be...
        del self.datas[f]
    self.ids.remove(msg_ids, filelist)


def main_cli():
  if len(sys.argv) <= 1 or "-h" in sys.argv:
    print(usage_str)
    exit(0)
  #filenames = sys.stdin.readlines()
  filenames = [f[:-1] for f in sys.stdin.readlines()]
  mgr = MailMgr()
  if sys.argv[1] == "-g":
    if len(sys.argv) <= 2:
      print(usage_str)
      exit(0)
    if sys.argv[2] == "all":
      print("\n\n".join([data_to_str(mgr.get_all(f)) for f in filenames]))
    else:
      inds = [fields.index(s) for s in sys.argv[2:]]
      print("\n\n".join(["\n".join([mgr.get(f, i) for i in inds]) for f in filenames]))
  elif sys.argv[1] == "-add-tags":
    taglist = sys.argv[2:]
    mgr.add_tags(filenames, taglist)
  elif sys.argv[1] == "-rm-tags":
    taglist = sys.argv[2:]
    mgr.remove_tags(filenames, taglist)
  else:
    print(usage_str)


if __name__ == "__main__":
  main_cli()


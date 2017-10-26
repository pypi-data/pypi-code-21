####
# bomail.util.msgids
#
# Given a message-id, look up if we have an email file for it.
# Basically a wrapper for reading and writing to plain text file
# config.ids_to_filenames.
####

import os, sys

import bomail.config.config as config
import bomail.util.merge_lines as merge_lines
import bomail.util.remove_lines as remove_lines


def msgid_file_line(msgid, filename):
  return msgid.strip() + " " + filename


def get_idfile_lines(msg_id_list, filename_list):
  return sorted([msgid_file_line(m, f) for m,f in zip(msg_id_list,filename_list)])


class Ids:
  def __init__(self):
    self.ids_to_filenames = {}
    if os.path.exists(config.msg_ids_file):
      with open(config.msg_ids_file) as f:
        for line in f:
          prs = line.split()
          if len(prs) != 2:
            continue
          self.ids_to_filenames[prs[0].strip()] = prs[1].strip()

  def get(self, msg_id):
    return self.ids_to_filenames[msg_id]

  def add(self, msg_id_list, filename_list):
    for m,f in zip(msg_id_list, filename_list):
      self.ids_to_filenames[m] = f
    merge_lines.do(config.msg_ids_file, get_idfile_lines(msg_id_list, filename_list))

  def remove(self, msg_id_list, filename_list):
    for m in msg_id_list:
      del self.ids_to_filenames[m]
    remove_lines.do_sorted(config.msg_ids_file, get_idfile_lines(msg_id_list, filename_list))



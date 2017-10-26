####
# bomail.util.tags
#
# Each message can have a list of descriptive "tags"
# (see cli/mailfile.py).
# A list of tags is stored in config.tags_file.
# This file:
#  - utilities for dealing with the "tags" line of mailfiles
#  - the "Tag Manager" object that interacts with the tags file
####

import sys
import bisect
import os

import bomail.config.config as config
import bomail.util.merge_lines as merge_lines
import bomail.util.remove_lines as remove_lines


def clean_tag(t):
  return t.strip().replace(" ","-").replace(",","-")


def get_str_from_clean_taglist(taglist):
  return ", ".join(taglist)


def get_tagset(unclean_taglist, include_folders=False):
  new = set()
  if not include_folders:
    redundant = set()
  for t in unclean_taglist:
    w = clean_tag(t)
    if len(w) > 0:
      new.add(w)
      for i,s in enumerate(w):
        if s == "/":
          if include_folders:
            new.add(w[:i])
          else:
            redundant.add(w[:i])
  if not include_folders:
    for w in redundant:
      new.discard(w)
  return new


def get_taglist_from_list(unclean_taglist):
  return sorted(list(get_tagset(unclean_taglist, include_folders=False)))


def get_tagset_from_str(unclean_taglist_str, include_folders=False):
  return get_tagset(unclean_taglist_str.split(", "), include_folders=include_folders)


def get_taglist_from_str(unclean_taglist_str, include_folders=False):
  return sorted(list(get_tagset_from_str(unclean_taglist_str, include_folders=include_folders)))


def get_str_from_taglist(taglist):
  return get_str_from_clean_taglist(get_taglist_from_list(taglist))


# return True if search_str is equal to tag or
# is a "folder containing tag", i.e. a prefix of tag
# preceding a forward-slash
def matches(tag, search_str):
  if not tag.startswith(search_str):
    return False
  return len(tag) == len(search_str) or tag[len(search_str)] == "/"


# get all tags from taglist that match searchlist
def get_matching(taglist, searchlist):
  # TODO: better than quadratic implementation (usually doesn't matter though...)
  mylist = []
  for t in taglist:
    for s in searchlist:
      if matches(t, s):
        mylist.append(t)
  return mylist


def get_nonmatching(taglist, searchlist):
  res = []
  for t in taglist:
    if len(searchlist) == 0 or not any([matches(t,s) for s in searchlist]):
      res.append(t)
  return res


# remove all folder-prefixes from list
def remove_redundant(taglist):
  res = []
  for i,t in enumerate(taglist):
    if i < len(taglist)-1 and matches(taglist[i+1], t):
      continue
    else:
      res.append(t)
  return res


# get all tags from both lists
# but remove redundancies created by folders
def join(taglist_1, taglist_2):
  longlist = sorted(taglist_1 + taglist_2)
  return remove_redundant(longlist)


# to read from this, just use tag_mgr.tags
class TagMgr:
  def __init__(self):
    self.tags = []
    if not os.path.exists(config.tags_file):
      with open(config.tags_file, "w") as f:
        pass
    else:
      with open(config.tags_file) as f:
        for line in f.readlines():
          w = clean_tag(line)
          if len(w) > 0:
            self.tags.append(w)

  def check_and_add_tags(self, taglist):
    taglist = [t for t in taglist if t not in self.tags]
    if len(taglist) > 0:
      self.add_tags(taglist)

  def add_tags(self, taglist):
    tagset = get_tagset(taglist, include_folders=True)
    if len(tagset) > 0:
      self.tags = sorted(list(tagset.union(set(self.tags))))
      with open(config.tags_file, "w") as f:
        f.write("\n".join(self.tags))

  def remove_tags(self, taglist):
    tagset = set(taglist)
    self.tags = [t for t in self.tags if t not in tagset]
    remove_lines.do_sorted(config.tags_file, sorted(list(tagset)))

  # remove all tags except these
  def reset_tags_to(self, taglist):
    self.tags = []
    self.check_and_add_tags(taglist)



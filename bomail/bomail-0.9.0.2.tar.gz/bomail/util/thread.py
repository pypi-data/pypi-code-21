####
# bomail.util.thread
#
# Manages EMAIL threads (not multithreading), a.k.a. conversations.
####

import sys
import os
import bisect

import bomail.config.config as config
import bomail.cli.mailfile as mailfile
import bomail.util.util as util
import bomail.util.listmail as listmail
import bomail.util.msgids as msgids
import bomail.guistuff.display_fmt as display_fmt

####
# source of algorithm:
# http://www.jwz.org/doc/threading.html 

# Every possible email has a unique msg_id;
# some of them also have filenames present.
# For every msg_id we hear about that is relevant, we have a "container"
# and entry in id_to_cntr.
# Each thread is a tree of containers with some root.
# Threads also have "pruned" versions that remove containers for which
# we don't have filenames.
####

usage_str = """
Usage:
    python3 thread.py -h     # print this help
    python3 thread.py

Reads a list of files from stdin, one per line.
Prints a representation of each thread those files belong to.
"""

class ThreadMgr:
  def __init__(self):
    self.id_to_cntr = {}         # msg_id to its Container
    self.id_to_pruned_root = {}  # msg_id to its root's Container

  def update_for_add(self, filelist, mail_mgr):
    touched_cntrs = build_id_to_cntr(filelist, mail_mgr, self.id_to_cntr)
    self.do_pruning(touched_cntrs, mail_mgr)

  def do_pruning(self, touched_cntrs, mail_mgr):
    touched_rootset = set()
    for c in touched_cntrs:
      while c.parent is not None:
        c = c.parent
      touched_rootset.add(c)
    pruned_roots = prune_empty(list(touched_rootset), mail_mgr, is_root_list=True)
    for r in pruned_roots:
      r.point_to_pruned_root(r, self.id_to_pruned_root)
      r.recount()

  # don't remove container, because its msg_id may be part of a useful chain
  # and don't look up any of these files in mail_mgr, as they don't exist anymore!
  def update_for_trash(self, filelist, data_list, mail_mgr):
    msg_id_list = [d[mailfile.MSG_ID_L] for d in data_list]
    touched_cntrs = []
    for msg_id in msg_id_list:
      if msg_id in self.id_to_cntr:
        c = self.id_to_cntr[msg_id]
        c.remove_self()
        touched_cntrs.append(c)
    self.do_pruning(touched_cntrs, mail_mgr)


  # given a "base" filelist
  # Return a list of triples (matching_files, root_cntr, all_files) where:
  #  - each triple corresponds to one thread
  #  - matching_files are those from the *base* list that are in this thread
  #  - root_cntr is the Container of the root of the thread
  #  - all_files is a list in some order of *all* files in thread
  # sort order of matching_files and the returned list is according to filelist
  def get_threads_for(self, filelist, mail_mgr):
    if len(filelist) == 0:
      return []
    msg_id_list = [mail_mgr.get(f, mailfile.MSG_ID_L) for f in filelist]
    new_flist = [f for m,f in zip(msg_id_list,filelist) if m not in self.id_to_pruned_root]
    self.update_for_add(new_flist, mail_mgr)
    return self.get_the_threads(filelist, msg_id_list)


  # this is pretty slow with many threads...
  # return list of triples (matching_files_in_thread, root, all_files_in_thread)
  def get_the_threads(self, filelist, msg_id_list):
    results = []        # list of pairs [files_in_this_thread, root_container]
    results_roots = {}  # map container to int, its index in results
    for msg_id,f in zip(msg_id_list, filelist):
      if msg_id not in self.id_to_pruned_root:
        with open(config.error_log_file, "a") as f_err:
          f_err.write(util.local_now_timestr() + "\n")
          f_err.write("Thread error: message id not in self.id_to_pruned_root.\n" + str(msg_id) + "\n" + str(f) + "\nIs in id_to_cntr: " + str(msg_id in self.id_to_cntr) + "\n\n")
        continue
      r = self.id_to_pruned_root[msg_id]
      if r in results_roots:
        results[results_roots[r]][0].append(f)
      else:
        temp = []
        r.build_fname_list(temp)
        results_roots[r] = len(results)
        results.append(([f], r, [t[1] for t in temp]))
    return results


# actually seems never necessary to do this
#def sort_msgs(container_list, mgr):
#  def cntr_to_val(c):
#    return (("9999-12-31" if c.filename is None else mgr.get(c.filename, mailfile.DATE_L)) , c.msg_id)
#  container_list.sort(key=cntr_to_val)


# MAIN THREAD-BUILDING ALGORITHM
# build all message Containers and put in the table id_to_cntr
# return list of all files touched
def build_id_to_cntr(orig_filelist, mgr, id_to_cntr):
  filelist = list(orig_filelist)
  fileset = set(filelist)
  file_i = 0
  touched_cntrs = []

  # go through files creating containers for all msg_ids encountered
  # and setting their parent-child relationships
  while file_i < len(filelist):  # note filelist gets lengthened dynamically
    filename = filelist[file_i]
    msg_id = mgr.get(filename, mailfile.MSG_ID_L)

    # A. get this message's container
    if msg_id in id_to_cntr:
      cntr = id_to_cntr[msg_id]
    else:
      cntr = Container(msg_id)
      id_to_cntr[msg_id] = cntr
    cntr.filename = filename
    touched_cntrs.append(cntr)

    # A.5 (Bo's modification) append my "children" messages to filelist if not there
    children_ids = mgr.get_refby(filename)
    for c_id in children_ids:
      if c_id in mgr.ids.ids_to_filenames and c_id not in id_to_cntr:
        c_fname = mgr.ids.get(c_id)
        if c_fname not in fileset:
          fileset.add(c_fname)
          filelist.append(c_fname)

    # B. link its references list together as "parent of parent of ... of this"
    # First create containers for any of them if necessary
    # Also, add their files to filelist if not present
    ref_ids = mgr.get_references(filename)
    ref_containers = []
    for ref_id in ref_ids:
      if ref_id == mgr.get(filename, mailfile.MSG_ID_L):  # this happens sometimes
        continue

      # add its containers to table if not present
      if ref_id in id_to_cntr:
        ref_cntr = id_to_cntr[ref_id]
      else:
        ref_cntr = Container(ref_id)
        id_to_cntr[ref_id] = ref_cntr
      ref_containers.append(ref_cntr)
      # also append ref_id's file onto filelist if it exists
      if ref_id in mgr.ids.ids_to_filenames:
        ref_filename = mgr.ids.ids_to_filenames[ref_id]
        if ref_filename not in fileset:
          filelist.append(ref_filename)
          fileset.add(ref_filename)
    # Second, link the containers, but don't overwrite existing parent-child links
    for i in range(len(ref_containers)-1):
      # do the linking
      a,b = ref_containers[i], ref_containers[i+1]
      if b.parent is None and not a.has_descendant(b.msg_id) and not b.has_descendant(a.msg_id):
        a.add_child(b, mgr)

    # C. definitively set the parent of this message, overwriting existing relationships
    if cntr.parent is not None:
      cntr.parent.children.remove(cntr)
      cntr.parent = None
    if len(ref_containers) > 0:
      # This if-condition failing would be very bizarre, but it's happened to me
      if not cntr.has_descendant(ref_containers[-1].msg_id):
        ref_containers[-1].add_child(cntr, mgr)

    # D. increment file_i
    file_i += 1
  return touched_cntrs


# Prune empty containers (those with no file) where possible.
# Originally given list of root containers, recursively works down.
# If given container is empty, prune it if:
#  - it's a root with only one child - the child takes its place.
#  - it's a non-root - all its children get "spliced" in at its level.
# Return the pruned list (do not modify original)
def prune_empty(cntr_list, mail_mgr, is_root_list=False):
  if len(cntr_list) == 0:
    return []

  # A. prune all children of containers in this list
  for c in cntr_list:
    c.pruned_children = prune_empty(c.children, mail_mgr)

  # B. prune empty containers from this list and promote their children
  new_cntr_list = []
  for c in cntr_list:
    if c.filename is None and (not is_root_list or len(c.pruned_children) == 1):
      new_cntr_list += c.pruned_children
    else:
      new_cntr_list.append(c)

#  sort_msgs(new_cntr_list, mail_mgr)
  return new_cntr_list
  

class Container:
  def __init__(self, msg_id):
    self.msg_id = msg_id
    self.parent = None  # Container
    self.children = []
    self.pruned_children = []   # prunes msg_ids with no associated file
    self.filename = None
    self.count = 0  # number in descendents (including self) who have a filename


  def __str__(self):
    return "Container " + self.msg_id + " : " + str(self.filename) + " : " + str(self.children)

  def __repr__(self):
    return str(self)

  def __hash__(self):
    return hash(self.msg_id)

  def __eq__(self, other):
    return self.msg_id == other.msg_id

  def __ne__(self, other):
    return self.msg_id != other.msg_id


  def add_child(self, child, mgr):
    self.children.append(child)
    child.parent = self
#    sort_msgs(self.children, mgr)


  def get_root(self):
    return self if self.parent is None else self.parent.get_root()


  # Do NOT use pruned_children for this, or we might miss a relationship
  # that has been pruned
  def has_descendant(self, mid):
    if self.msg_id == mid:
      return True
    for c in self.children:
      if c.has_descendant(mid):
        return True
    return False

  def remove_self(self):
    self.filename = None


  # point pruned msg_ids to roots
  def point_to_pruned_root(self, r, id_to_pruned_root):
    id_to_pruned_root[self.msg_id] = r
    for c in self.pruned_children:
      c.point_to_pruned_root(r, id_to_pruned_root)


  def recount(self):
    num = 0 if self.filename is None else 1
    for c in self.pruned_children:
      num += c.recount()
    self.count = num
    return num


  # add (level, filename) to list in preorder depth-first order:
  # me, first child and all descendants, second child and all descendants, ....
  def build_fname_list(self, a, level=0):
    if self.filename is not None:
      a.append((level, self.filename))
    for c in self.pruned_children:
      c.build_fname_list(a, level+1)


if __name__ == "__main__":
  if "-h" in sys.argv:
    print(usage_str)
    exit(0)
  width = 100  # TODO command-line option

  mail_mgr = mailfile.MailMgr()
  thread_mgr = ThreadMgr()
  filelist = [f.strip() for f in sys.stdin.readlines()]
  thread_trips = thread_mgr.get_threads_for(filelist, mail_mgr)
  for trip in thread_trips:
    print("================")
    for f in trip[2]:  # all files in thread
      print(("--> " if f in trip[0] else "    ") + f)
      # TODO: sort and indent according to thread replies, depending on command-line option
      lines, blank_attr_data = display_fmt.get_msg_lines_nothread(mail_mgr, f, width, use_curses=False)
      for l in lines:
        print("    " + l)
      print()
    print()



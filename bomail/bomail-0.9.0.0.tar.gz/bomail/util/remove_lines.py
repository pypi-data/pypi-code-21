####
# bomail.util.remove_lines
#
# Removes matching lines from a file.
####

import sys
import os
import tempfile

import bomail.util.util as util

usage_str = """
Usage:
    remove_lines.py -h         # print this help
    remove_lines.py filename

Reads line "s1" from stdin and removes first line in file containing s1.
Then reads line "s2" from stdin and removes next line in file containing s2.
Etc.

So s1, s2, ... should be in the same sorted order as lines in the file.
"""


# remove from filename all lines containing a string in the set s_set
# scheduled list style: check if second part of line is in s_set, if so remove it
def do_sched(list_filename, s_set):
  if not os.path.exists(list_filename):
    return
  made_change = False

  # write to a new temp file "tof"
  with open(list_filename) as fromf, tempfile.NamedTemporaryFile(dir=".", mode="w", delete=False) as tof:
    for temp in fromf:
      pr = temp.split()
      if len(pr) >= 2 and pr[1] in s_set:
        s_set.remove(pr[1])
        made_change = True
        continue
      tof.write(temp)
  if made_change:  # otherwise, no need to rewrite file
    util.mv_file(tof.name, list_filename) 
  else:
    os.remove(tof.name)


def do_sorted(list_filename, s_list):
  if not os.path.exists(list_filename):
    return
  made_change = False
  curr_i = 0

  # write to a new temp file "tof"
  with open(list_filename) as fromf, tempfile.NamedTemporaryFile(dir=".", mode="w", delete=False) as tof:
    for temp in fromf:
      while curr_i < len(s_list) and s_list[curr_i] < temp[:-1]:
        curr_i += 1
      if curr_i < len(s_list) and s_list[curr_i] == temp[:-1]:
        made_change = True
        curr_i += 1 # assume no duplicates
        continue
      tof.write(temp)
  if made_change:  # otherwise, no need to rewrite file
    util.mv_file(tof.name, list_filename) 
  else:
    os.remove(tof.name)


if __name__ == "__main__":
  if len(sys.argv) != 2 or "-h" in sys.argv:
    print(usage_str)
    exit(0)

  # could be more efficient by reading as needed...
  # also remove trailing newlines
  slist = [s[:-1] for s in sys.stdin.readlines()]
  do_sorted(sys.argv[1], sorted(slist))


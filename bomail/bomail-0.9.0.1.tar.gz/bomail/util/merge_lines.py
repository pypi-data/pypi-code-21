####
# bomail.util.merge_lines
#
# Merges sorted lines into a sorted file.
####

import sys, os, subprocess
import tempfile
from subprocess import PIPE, Popen

import bomail.util.util as util

usage_str = """
Reads a list of lines from stdin (one per line) and merges them into the file.
Assumes the file and input lines are sorted.

Use:
    merge_lines.py listfile         # sort in lexicographic order
    merge_lines.py -r listfile      # sort in reverse order
    merge_lines.py -h               # print this help
"""


def do(filename, lines, reverse=False):
  if reverse:
    comp = lambda a,b: a > b
  else:
    comp = lambda a,b: a <= b
  if not os.path.exists(filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "a"):
      pass

  if len(lines) == 0:
    return
  
  with open(filename) as fromf, tempfile.NamedTemporaryFile(dir=".", mode="w", delete=False) as tof:
    lines_ind = 0
    next_fileline = fromf.readline()
    while True:
      if len(next_fileline) == 0 and lines_ind >= len(lines):
        break
      elif lines_ind >= len(lines) or (len(next_fileline) > 0 and comp(next_fileline, lines[lines_ind])):
        tof.write(next_fileline)
        next_fileline = fromf.readline()
      else:
        tof.write(lines[lines_ind])
        tof.write("\n")
        lines_ind += 1
  util.mv_file(tof.name, filename)


if __name__ == "__main__":
  if len(sys.argv) <= 1 or "-h" in sys.argv:
    print(usage_str)
    exit(0)
  lines = [l[:-1] for l in sys.stdin.readlines()]  # remove newlines
  if sys.argv[1] == "-r":
    if len(sys.argv) <= 2:
      print(usage_str)
      exit(0)
    do(sys.argv[2], lines, reverse=True)
  else:
    do(sys.argv[1], lines)


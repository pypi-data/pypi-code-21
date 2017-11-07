####
# bomail.util.addr
#
# Utilities for dealing with email addresses
# and the "address book", which is stored in config.addr_book_file.
####

import sys
import os
from bisect import bisect_left

import bomail.config.config as config
import bomail.cli.mailfile as mailfile
import bomail.util.merge_lines as merge_lines

####
# Python 'types' used:
# pr      A pair of the form ("Person Name", "local@domain")
# prlist  A list of the form [pr, pr, ...]
#
# Plain text stuff:
#
# email_addr  Assumes no commas or quotes!
#             An email address string of the form
#             "Person Name <local@domain>"
#             or "local@domain"
#
# Address book file format: each line is
#    email_addr, N M
# where N and M are integers for num emails sent and received respectively.
####

# Ideally: each email string we can parse should be a recipient from a MIME
# email (RFC5322).
# Currently: each string in raw_str_list should be a comma-separated list
# of recipients each readable by str_to_pair()
# and with the given send and receive counts



# canonical version that ignores case, dots, and +stuff in
# email address
# input is the second part of a pair (e.g. "local@domain")
def canon(s):
  if "@" not in s:
    return s  # no idea what's going on
  local, domain = s.split("@")
  local = local.lower()
  if "+" not in local and "." not in local:
    return s
  if "+" in local:
    local = local[:local.index("+")]
  if "." in local:
    local = local.replace(".","")
  return local + "@" + domain


# GLOBAL VARIABLE
# the user's list of email addresses
my_addr_list = [canon(a) for a in config.my_aliases + [config.email_addr]]


# given a string describing possibly a list of email names and addresses
# take out everything in quotes and replace it with non-quoted names
# e.g. inside namestr, "Stuff Here" and "Here, Stuff" both get changed
# to Stuff Here
def convert_quoted_names(namestr):
  slist = []
  old_quote_ind = -1
  while True:
    new_quote_ind = namestr.find('"', old_quote_ind+1)
    if new_quote_ind == -1:
      slist.append(namestr[old_quote_ind+1:])
      break
    next_ind = namestr.find('"', new_quote_ind+1)
    if next_ind == -1:
      slist.append(namestr[old_quote_ind+1:])
      break
    # everything between last quoted sequence and this one
    slist.append(namestr[old_quote_ind+1: new_quote_ind])
    name = namestr[new_quote_ind+1:next_ind]
    if "," in name:
      namelist = [r.strip() for r in name.split(",")]
      namelist.reverse()
      name = ' '.join(namelist)
    slist.append(name)
    old_quote_ind = next_ind
  return ''.join(slist)


# given plain-text comma-separated list of email addresses,
# return list of pairs
def str_to_pairlist(auth_str):
  if '"' in auth_str:
    auth_str = convert_quoted_names(auth_str)
  str_list = [s.strip() for s in auth_str.split(",") if len(s.strip()) > 0]
  return list(map(str_to_pair, str_list))


# opposite direction
def pairlist_to_str(pair_list):
  return ", ".join([pair_to_str(*r) for r in pair_list])


# return author_name, email_addr
def str_to_pair(auth_str):
  try:  # Author Name <email@addr.domain>
    ind = auth_str.index("<")
    name = auth_str[:ind].strip().strip('"').strip()
    addr = auth_str[ind+1:auth_str.index(">")].strip()
    if "," in name:
      name = " ".join(reversed([s.strip() for s in name.split(",")]))
    return name, addr
  except:  # email@addr.domain
    return "", auth_str.strip()


def pair_to_str(auth, addr):
  if auth == "":
    return addr
  else:
    return auth + " <" + addr + ">"

# given a line from address book,
# return email pair and N, M
def str_to_quad(s):
  if "," not in s:
    p = str_to_pair(s)
    return (p[0], p[1], 0, 0)
  l = s.split(",")
  p = str_to_pair(l[0].strip())
  try:
    counts = l[1].split()
    return (p[0], p[1], int(counts[0].strip()), int(counts[1].strip()))
  except:
    return (p[0], p[1], 0, 0)


# given email pair and two counts,
# return a line for the address book
def quad_to_str(q):
  return pair_to_str(q[0], q[1]) + " , " + str(q[2]) + " " + str(q[3])


# check if the emails go to the same place
def is_recip_eq(p1, p2):
  return canon(p1) == canon(p2)

def is_pair_me(pr):
  return canon(pr[1]) in my_addr_list

def is_str_me(s):
  return is_pair_me(str_to_pair(s))



# Mostly, this class is just used to read the list of addresses
# and to write new ones into the text file
class AddrBook:
  def __init__(self):
    self.pair_to_count = {}    # map (name, email_addr) to (send_count, recv_count)
    self.address_to_pair = {}    # map email_addr to (name, email_addr)
    self.load()


  def load(self):
    if not os.path.exists(config.addr_book_file):
      with open(config.addr_book_file, "w") as f:
        pass
    else:
      with open(config.addr_book_file) as f:
        lines = f.readlines()
      for l in [ll for ll in lines if ll.strip() != ""]:
        q = str_to_quad(l)
        self.pair_to_count[(q[0], q[1])] = (q[2], q[3])
        self.address_to_pair[q[1]] = (q[0], q[1])


  def check_for_new(self, prlist):
    added = False
    for pr in prlist:
      tuple_pr = (pr[0], pr[1])
      if tuple_pr not in self.pair_to_count:
        self.pair_to_count[tuple_pr] = (0, 0)
        self.address_to_pair[pr[1]] = tuple_pr
        added = True
    if added:
      self.rewrite_file()


  # delete all addresses in pairlist
  def remove_addresses(self, pairlist):
    rmlist = [p for p in pairlist if p in self.pair_to_count]
    if len(rmlist) != 0:
      for p in rmlist:
        del self.pair_to_count[p]
        if p[1] in self.address_to_pair:
          del self.address_to_pair[p[1]]
      self.rewrite_file()


  # delete all addresses in pairlist and add their
  # send/receive counts to merge_to
  def merge_addresses(self, merge_to, pairlist):
    c1, c2 = self.pair_to_count[merge_to]
    for pr in pairlist:
      t1, t2 = self.pair_to_count[pr]
      c1 += t1
      c2 += t2
      del self.pair_to_count[pr]
      del self.address_to_pair[pr[1]]
    self.pair_to_count[merge_to] = (c1, c2)
    self.rewrite_file()


  # look up pr in the book
  # if not present, but pr only contains an address
  # that is present, then change to that address
  def lookup_and_change(self, pr):
    if pr in self.pair_to_count:
      return pr
    if pr[0] == "" and pr[1] in self.address_to_pair:
      return self.address_to_pair[pr[1]]
    return pr


  # update our data to include any new addresses and new
  # send/receive counts
  def update_for_new(self, maildatas):
    for data in maildatas:
      fromlist = str_to_pairlist(data[mailfile.FROM_L])
      tolist = str_to_pairlist(data[mailfile.TO_L]) + str_to_pairlist(data[mailfile.CC_L]) + str_to_pairlist(data[mailfile.BCC_L])
      fromlist = [self.lookup_and_change(pr) for pr in fromlist]
      tolist = [self.lookup_and_change(pr) for pr in tolist]
      # increment counts depending on if sent or received
      if data[mailfile.SENT_L] == "True":
        for p in tolist:
          cnt = self.pair_to_count[p] if p in self.pair_to_count else (0, 0)
          self.pair_to_count[p] = (cnt[0] + 1, cnt[1])
        for p in [pr for pr in fromlist if pr not in self.pair_to_count]:
          self.pair_to_count[p] = (0, 0)
          self.address_to_pair[p[1]] = p
      else:
        for p in [pr for pr in tolist if pr not in self.pair_to_count]:
          self.pair_to_count[p] = (0, 0)
          self.address_to_pair[p[1]] = p
        for p in fromlist:
          cnt = self.pair_to_count[p] if p in self.pair_to_count else (0, 0)
          self.pair_to_count[p] = (cnt[0], cnt[1] + 1)
    self.rewrite_file()

 
  # save our address book to the text file
  def rewrite_file(self):
    # add my entry_quads to the dict, then flatten it to a list and write to disk
    entry_quads = [(p[0], p[1], c[0], c[1]) for p,c in self.pair_to_count.items()]
    entry_quads.sort()
    s = "\n".join([quad_to_str(q) for q in entry_quads])
    with open(config.addr_book_file, "w") as f:
      f.write(s)


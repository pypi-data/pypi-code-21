####
# bomail.util.search_opts
#
# The main 'search' code.
####

import os
import shlex

import bomail.cli.mailfile as mailfile
import bomail.util.tags as tags
import bomail.util.datestr as datestr

####
# The code tries to be a bit fancy -- given a search string,
# generate and compile a short python program that conducts
# the search using only the options in the query.
####

options_str = """
All arguments are optional:
 -h               [print this help]

 -not             not satisfying the next option
 -OR              matching everything before OR everything after
 
 -a datestr       after date. datestr can be e.g. yyyy-mm-dd
 -b datestr       before date

 -open            state is open
 -scheduled       state is scheduled
 -closed          state is closed
 -draft           is a draft
 -sent            is sent from me
 -attach          has an attachment

 -t str           has str as a tag. Use multiple times to match any
 -t "tag1, tag2"  has all these tags
 -nt str          does not have str as a tag
 -nt "tag1, tag2" does not have *all* of these tags
 -notags          has no tags

 -to str          str is in to, cc, or bcc field
 -to "s1, s2"     s1, s2, ... all in to, cc, or bcc field
 -from str        str is in from field
 -subject str     str is in subject field

 query            query is in email somewhere
 "long query"     long query is in email somewhere
 quer1 quer2      all queries are in email somewhere

 -n 200           only return first 200 results
 -sortold         list by oldest (default is by newest)
"""


# used when constructing the search code
break_str = "      break\n"


# dumb helper function: when producing python code from an object
# that is either None or a string
def mystr(s):
  if s is None:
    return "None"
  else:
    return "\"" + s + "\""


# filename is ...email/yyyy/mm-dd/x.email
# or .../yyyy/mm-dd/x.draft
def get_date_from_filename(filename):
  # filedir = os.path.dirname(filename)  # too slow
  slashind = filename.rfind("/")  # assume x does not contain a slash!!
  return filename[slashind-10:slashind].replace("/","-")


def datestr_matches(datestr, after, before, not_after=None, not_before=None):
  return ((after is None or datestr[:len(after)] >= after)
          and (before is None or datestr[:len(before)] <= before)
          and (not_after is None or datestr < not_after)
          and (not_before is None or datestr > not_before))


# given a 'datestr' like yyyy-mm or m3.0d,
# turn it into an absolute date string yyyy-mm-dd
# throw an exception if unable
def get_absstr_from_datestr(schedstr):
  dateobj = datestr.get_datetime(schedstr)
  if dateobj is None:
    dateobj = datetime.datetim.now()  # what else to do?
  return dateobj.isoformat()[:10]


# A query that does not contain an OR
class OneQuery:
  def __init__(self, copy=None):
    if copy is None:
      self.after = None
      self.not_after = None
      self.before = None
      self.not_before = None
  
      self.open = None
      self.scheduled = None
      self.closed = None
      self.draft_only = None
      self.sent_only = None
      self.attachonly = None
  
      self.tagset_list = None
      self.nottagset_list = None
      self.notags = None  # or bool
  
      self.tolist = None
      self.not_tolist = None
      self.fromlist = None
      self.not_fromlist = None
  
      self.subject_str = None
      self.not_subject_str = None
  
      self.querylist = None
      self.not_querylist = None
  
      self.need_data = False
      self.need_date = False
    else:
      self.after = copy.after
      self.not_after = copy.not_after
      self.before = copy.before
      self.not_before = copy.not_before
  
      self.open = copy.open
      self.scheduled = copy.scheduled
      self.closed = copy.closed
      self.draft_only = copy.draft_only
      self.sent_only = copy.sent_only
      self.attachonly = copy.attachonly
  
      self.tagset_list = copy.tagset_list
      self.nottagset_list = copy.nottagset_list
      self.notags = copy.notags
  
      self.tolist = copy.tolist
      self.not_tolist = copy.not_tolist
      self.fromlist = copy.fromlist
      self.not_fromlist = copy.not_fromlist
  
      self.subject_str = copy.subject_str
      self.not_subject_str = copy.not_subject_str
  
      self.querylist = copy.querylist
      self.not_querylist = copy.not_querylist
  
      self.need_data = copy.need_data
      self.need_date = copy.need_date
      

  def parse(self, args):
    i = 0
    while i < len(args):
      same_as_current = True
      if args[i] == "-nt":
        # "hack" to make this equivalent to -not -t
        same_as_current = False
        args[i] = "-t"
      
      # NOT elif!
      if args[i] == "-not":
        same_as_current = False
        i += 1
        if i >= len(args):
          break
      
      if args[i] == "-a":
        if i+1 < len(args):
          try:
            self.need_date = True
            if same_as_current:
              res = get_absstr_from_datestr(args[i+1])
              self.after = res
            else:
              res = get_absstr_from_datestr(args[i+1])
              self.not_after = res
          except:
            self.need_date = False
            raise
        i += 1
      elif args[i] == "-b":
        if i+1 < len(args):
          try:
            self.need_date = True
            if same_as_current:
              res = get_absstr_from_datestr(args[i+1])
              self.before = res
            else:
              res = get_absstr_from_datestr(args[i+1])
              self.not_before = res
          except:
            self.need_date = False
            raise
        i += 1

      elif args[i] == "-open":
        self.need_data = True
        self.open = same_as_current
      elif args[i] == "-closed":
        self.need_data = True
        self.closed = same_as_current
      elif args[i] == "-scheduled":
        self.need_data = True
        self.scheduled = same_as_current
      elif args[i] == "-draft":
        self.need_data = True
        self.draft_only = same_as_current
      elif args[i] == "-sent":
        self.need_data = True
        self.sent_only = same_as_current
      elif args[i] == "-attach":
        self.need_data = True
        self.attachonly = same_as_current

      elif args[i] == "-t":
        if i+1 < len(args):
          # don't split query tags into folders, only search for the exact query
          the_tagset = tags.get_tagset_from_str(args[i+1], include_folders=False)
          if len(the_tagset) > 0:
            self.need_data = True
            if same_as_current:
              if self.tagset_list is None:
                self.tagset_list = [the_tagset]
              else:
                self.tagset_list.append(the_tagset)
            else:
              if self.nottagset_list is None:
                self.nottagset_list = [the_tagset]
              else:
                self.nottagset_list.append(the_tagset)
        i += 1
      elif args[i] == "-notags":
        self.need_data = True
        self.notags = same_as_current

      elif args[i] == "-to":
        if i+1 < len(args):
          self.need_data = True
          the_tolist = [s.strip() for s in args[i+1].split(",")]
          if same_as_current:
            self.tolist = the_tolist
          else:
            self.not_tolist = the_tolist
        i += 1
      elif args[i] == "-from":
        if i+1 < len(args):
          self.need_data = True
          the_fromlist = [s.strip() for s in args[i+1].split(",")]
          if same_as_current:
            self.fromlist = the_fromlist
          else:
            self.not_fromlist = the_fromlist
        i += 1

      elif args[i] == "-subject":
        if i+1 < len(args):
          self.need_data = True
          if same_as_current:
            self.subject_str = args[i+1]
          else:
            self.not_subject_str = args[i+1]
        i += 1

      else:
        self.need_data = True
        if same_as_current:
          if self.querylist is None:
            self.querylist = []
          self.querylist.append(args[i])
        else:
          if self.not_querylist is None:
            self.not_querylist = []
          self.not_querylist.append(args[i])

      i += 1

  # append a list of strings of commands to slist
  # a 4-indented block that checks f based on self, mailfile, mgr, tags, data (if needed), datestr (if needed), datestr_matches (if needed)
  # if a check fails, break
  def compile_slist(self, slist):
    if self.draft_only is not None:
      slist.append("    if f[-5:] ")
      slist.append("!" if self.draft_only else "=")
      slist.append("= \"draft\":\n")
      slist.append(break_str)
    if any([o is not None for o in [self.after, self.not_after, self.before, self.not_before]]):
      slist += ["    if not datestr_matches(datestr, ", mystr(self.after), ", ", mystr(self.before), ", ", mystr(self.not_after), ", ", mystr(self.not_before), "):\n"]
      slist.append(break_str)

    if self.open is not None:
      slist.append("    if data[mailfile.STATE_L].startswith(\"open\") != ")
      slist.append(str(self.open))
      slist.append(":\n")
      slist.append(break_str)
    if self.closed is not None:
      slist.append("    if data[mailfile.STATE_L].startswith(\"closed\") != ")
      slist.append(str(self.closed))
      slist.append(":\n")
      slist.append(break_str)
    if self.scheduled is not None:
      slist.append("    if data[mailfile.STATE_L].startswith(\"scheduled\") != ")
      slist.append(str(self.scheduled))
      slist.append(":\n")
      slist.append(break_str)
    if self.sent_only is not None:
      slist.append("    if (data[mailfile.SENT_L] == \"True\") != ")
      slist.append(str(self.sent_only))
      slist.append(":\n")
      slist.append(break_str)
    if self.attachonly is not None:
      slist.append("    if (len(data[mailfile.ATTACH_L]) > 0) != ")
      slist.append(str(self.attachonly))
      slist.append(":\n")
      slist.append(break_str)

    if self.notags is not None:
      slist.append("    if len(data[mailfile.TAGS_L]) ")
      slist.append("!" if self.notags else "=")
      slist.append("= 0:\n")
      slist.append(break_str)

    # TODO: speed these up by manually embedding the tags we've already parsed? maybe not, set is fast lookup..
    got_tagset = False
    if self.tagset_list is not None:
      # if the search includes a folder, make sure to match it
      slist.append("    data_tagset = tags.get_tagset_from_str(data[mailfile.TAGS_L], include_folders=True)\n")
      slist.append("    if not any([ts.issubset(data_tagset) for ts in q.tagset_list]):\n")
      slist.append(break_str)
      got_tagset = True
    if self.nottagset_list is not None:
      if not got_tagset:
        slist.append("    data_tagset = tags.get_tagset_from_str(data[mailfile.TAGS_L], include_folders=True)\n")
        got_tagset = True
      slist.append("    if any([nts.issubset(data_tagset) for nts in q.nottagset_list]):\n")
      slist.append(break_str)

    if self.tolist is not None:
      for tostr in self.tolist:
        dec = "\"" + tostr.encode().decode('unicode_escape') + "\""
        slist += ["    if ", dec, " not in data[mailfile.TO_L] and ", dec, " not in data[mailfile.CC_L] and ", dec, " not in data[mailfile.BCC_L]:\n", break_str]
    if self.not_tolist is not None:
      for tostr in self.not_tolist:
        dec = "\"" + tostr.encode().decode('unicode_escape') + "\""
        slist += ["    if ", dec, " in data[mailfile.TO_L] or ", dec, " in data[mailfile.CC_L] or ", dec, " in mailfile.BCC_L:\n"]
      slist.append(break_str)
    if self.fromlist is not None:
      for fromstr in self.fromlist:
        slist += ["    if \"", fromstr.encode().decode('unicode_escape'), "\" not in data[mailfile.FROM_L]:\n"]
      slist.append(break_str)
    if self.not_fromlist is not None:
      for fromstr in self.not_fromlist:
        slist += ["    if \"", fromstr.encode().decode('unicode_escape'), "\" in data[mailfile.FROM_L]:\n"]
        slist.append(break_str)

    if self.subject_str is not None:
      slist += ["    if \"", self.subject_str.encode().decode('unicode_escape'), "\" not in data[mailfile.SUBJ_L]:\n"]
      slist.append(break_str)
    if self.not_subject_str is not None:
      slist += ["    if \"", self.not_subject_str.encode().decode('unicode_escape'), "\" in data[mailfile.SUBJ_L]:\n"]
      slist.append(break_str)

    if self.querylist is not None:
      for q in self.querylist:
        slist += ["    if not any([\"", q.encode().decode('unicode_escape'), "\" in l for l in data]):\n"]
        slist.append(break_str)
    if self.not_querylist is not None:
      for q in self.not_querylist:
        slist += ["    if any([\"", q.encode().decode('unicode_escape'), "\" in l for l in data]):\n"]
        slist.append(break_str)


def list_indic(l):
  return False if len(l) == 0 else all(l)


def do_compile(q_list, need_data, need_date):
  slist = ["matched_list = []\nfor i,f in enumerate(filelist):\n"]
  if need_data:
    slist.append("  data = mgr.get_all(f) if datalist is None else datalist[i]\n")
    if need_date:
      slist.append("  datestr = data[mailfile.DATE_L]\n")
  elif need_date:
    slist.append('  slashind = f.rfind("/")\n  datestr = f[slashind-10:slashind].replace("/","-")\n')

  slist.append("  matched_result = False\n")
  for i,q in enumerate(q_list):
    slist.append("  q = self.q_list[" + str(i) + "]\n")
    # if any q sets matched_result True, it's a match (logical OR)
    slist.append("  while True:\n")
    # a 4-indented block that breaks if not a match
    q.compile_slist(slist)
    slist.append("    matched_result = True\n    break\n")  # if all tests pass, match!
    slist.append("  if matched_result:\n    matched_list.append(i)\n    continue\n")

  slist = slist
#  with open("compile_log.txt", "w") as f:
#    f.write("".join(slist))
  return compile("".join(slist), '<string>', 'exec')


# A full search query
class SearchQuery:
  # if include_listmailed, then we can assume listmail
  # has already filtered the list of filenames for us
  def __init__(self, arglist, include_listmailed=True):
    self.max_results = -1  # no limit
    self.sort_new = True
    self.q_list = []
    self.compiled_obj = None
    self.compiled_listmailed_obj = None
    self.need_data = False
    self.need_date = False

    if len(arglist) == 0:
      return

    if "-n" in arglist:
      ind = arglist.index("-n")
      if ind+1 < len(arglist):
        self.max_results = int(arglist[ind+1])
      arglist = arglist[:ind] + ([] if len(arglist) <= ind+2 else arglist[ind+2:])

    if "-sortold" in arglist:
      self.sort_new = False
      ind = arglist.index("-sortold")
      arglist = arglist[:ind] + ([] if len(arglist) <= ind+1 else arglist[ind+1:])

    i = 0
    while i < len(arglist) and "-OR" in arglist[i:]:
      or_i = arglist.index("-OR", i)
      q = OneQuery()
      q.parse(arglist[i:or_i])
      self.q_list.append(q)
      i = or_i + 1
    if i < len(arglist):
      q = OneQuery()
      q.parse(arglist[i:])
      self.q_list.append(q)

    if len(self.q_list) > 0:
      self.need_data = any([q.need_data for q in self.q_list])
      self.need_date = any([q.need_date for q in self.q_list])

    self.compiled_obj = do_compile(self.q_list, self.need_data, self.need_date)

    if include_listmailed:
      # TODO! (complicated)
      # produce the version that assumes listmail has been run before
      # calling this to filter it
      # important that order or draft, open, scheduled, attach
      # matches the order that listmail uses to break ties in which query to address
      # this could speed up some searches a lot...
      self.compiled_listmailed_obj = self.compiled_obj
        
        

  # return list of indices of matching files in filelist
  # if listmailed, don't need to repeat work...
  def filter(self, filelist, mgr, datalist=None, listmailed=False):
    if len(self.q_list) == 0:
      return range(len(filelist))
    namespace ={"self": self, "datestr_matches": datestr_matches, "mailfile": mailfile, "mgr": mgr, "tags": tags, "filelist": filelist, "datalist": datalist}
    if listmailed:
      exec(self.compiled_obj, namespace)
    else:
      exec(self.compiled_listmailed_obj, namespace)
    return namespace["matched_list"]


  # get options for listmail
  # it's ok to return too many results, but not to leave some out
  # (although the queries may conflict...)
  # after and before are None or strings
  # others are bool
  def get_list_opts(self):
    if len(self.q_list) == 0:
      return None, None, False, False, False, False

    after_list = [q.after for q in self.q_list if q.after is not None]
    after = None if len(after_list) == 0 else min(after_list)
    before_list = [q.before for q in self.q_list if q.before is not None]
    before = None if len(before_list) == 0 else max(before_list)

    draft = list_indic([q.draft_only for q in self.q_list if q.draft_only is not None])
    is_open = list_indic([q.open for q in self.q_list if q.open is not None])
    scheduled = list_indic([q.scheduled for q in self.q_list if q.scheduled is not None])
    attachonly = list_indic([q.attachonly for q in self.q_list if q.attachonly is not None])
    return after, before, draft, is_open, scheduled, attachonly


def SQ_from_str(s):
  return SearchQuery(shlex.split(s))



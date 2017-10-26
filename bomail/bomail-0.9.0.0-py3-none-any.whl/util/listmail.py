####
# bomail.util.listmail
#
# (Quickly) list emails matching date range or simple state queries.
# The idea is it's fast because it doesn't have to open the files.
####

import sys
import os.path

import bomail.config.config as config
import bomail.cli.mailfile as mailfile
import bomail.util.search_opts as search_opts

usage_str = """
Prints a list of filenames of emails matching some basic filters.
All arguments are optional.
 -h              print this help

Use either, both or neither:
 -a datestr   after date (e.g. yyyy-mm-dd)
 -b datestr   before date

Use at most one:
 -open           restrict to open
 -scheduled      restrict to scheduled
 -draft          drafts only
 -attach         only those having attachments
"""

# after and before may be none
# if f_out is None, return a list of strings,
# otherwise print them to f_out
def list_all(after, before, f_out, mgr, dirname=config.email_dir):
  if not os.path.exists(dirname):
    return []
  all_years = os.listdir(dirname)
  if len(all_years) == 0:
    return []
  output = []
  for year_str in all_years:
    if after is not None and year_str < after[:4]:   continue
    if before is not None and year_str > before[:4]: continue
    year_prefix = year_str + "-"
    year_dir = dirname + year_str + "/"
    all_days = os.listdir(year_dir)
    for day_str in all_days:
      date_str = year_prefix + day_str
      if after is not None and date_str[:len(after)] < after:   continue
      if before is not None and date_str[:len(before)] > before: continue
      day_dir = year_dir + day_str + "/" 
      for s in os.listdir(day_dir):
        if len(s) >= 5 and (s[-4:] == "mail" or s[-5:] == "draft"):
          if f_out is None:
            output.append(day_dir + s)
          else:
            print(day_dir + s, file=f_out)
  return output

# openlist is sorted by reverse lexicographic order
def list_open(after, before, f_out, mgr):
  if not os.path.exists(config.openlist_file):
    return []
  output = []
  with open(config.openlist_file) as f:
    for line in f:
      filename = line[:-1] if (len(line) > 0 and line[-1] == "\n") else line
      if search_opts.datestr_matches(search_opts.get_date_from_filename(filename), after, before):
        if f_out is None: 
          output.append(filename)
        else:
          print(filename, file=f_out)
  return output

# scheduledlist is sorted by schedule date, not file date!
# have to check date of file!
# lines have the form "scheduledate emailfilename"
def list_scheduled(after, before, f_out, mgr):
  if not os.path.exists(config.scheduledlist_file):
    return []
  output = []
  with open(config.scheduledlist_file) as f:
    for line in f:
      if len(line.strip()) == 0:
        continue
      filename = line.split()[1]
      if filename[-1] == "\n":
        filename = filename[:-1]
      datestr = search_opts.get_date_from_filename(filename)
      if search_opts.datestr_matches(datestr, after, before):
        if f_out is None:
          output.append(filename)
        else:
          print(filename, file=f_out)
  return output

def list_drafts(after, before, f_out, mgr):
  return list_all(after, before, f_out, mgr, config.drafts_dir)

# similar to list_all, but use the attach directories (only the ones that exist)
def list_attachonly(after, before, f_out, mgr):
  if not os.path.exists(config.attach_dir):
    return []
  all_years = os.listdir(config.attach_dir)
  if len(all_years) == 0:
    return []
  output = []
  for year_str in all_years:
    if after is not None and year_str < after[:4]:   continue
    if before is not None and year_str > before[:4]: continue
    year_prefix = year_str + "-"
    year_dir = config.attach_dir + year_str + "/"
    all_days = os.listdir(year_dir)
    for day_str in all_days:
      date_str = year_prefix + day_str
      if after is not None and date_str[:len(after)] < after:   continue
      if before is not None and date_str[:len(before)] > before: continue
      day_dir = year_dir + day_str + "/" 
      for s in os.listdir(day_dir):
        if s[-1] == "/":
          s = s[:-1]
        mailfile_path = config.email_dir + year_str + "/" + day_str + "/" + s
        if f_out is None:
          output.append(mailfile_path)
        else:
          print(mailfile_path, file=f_out)
  return output
   


# query is a search_opts.SearchQuery
def do_list(query, mgr, f_out=None):
  after, before, draft_only, is_open, scheduled, attachonly = query.get_list_opts()

  # pick an order over these options and just use one of them
  if draft_only:
    return list_drafts(after, before, f_out, mgr)
  elif is_open:
    return list_open(after, before, f_out, mgr)
  elif scheduled:
    return list_scheduled(after, before, f_out, mgr)
  elif attachonly:
    return list_attachonly(after, before, f_out, mgr)
  else:
    return list_all(after, before, f_out, mgr)


# f_out is a writable buffer-like object or None
# if None, return a list of filenames
def main(args, mgr, f_out=None):
  query = search_opts.SearchQuery(args)
  return do_list(query, mgr, f_out=f_out)


if __name__ == "__main__":
  if "-h" in sys.argv:
    print(usage_str)
  else:
    main(sys.argv[1:], mailfile.MailMgr(), f_out=sys.stdout)


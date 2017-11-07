####
# bomail.cli.stats
#
# Report some stats about a set of mail filenames.
####

import sys
import string
import datetime
import dateutil.parser
from dateutil.relativedelta import relativedelta
import os
import shlex
import io
import math

import bomail.cli.mailfile as mailfile
import bomail.cli.search as search
import bomail.util.addr as addr
import time

# TODO: implement line wrapping for all printing

iso_wkdays = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

max_items = 25
max_cols = 100  # width to print

usage_str = """
Reads a list of files from stdin, e.g.
    bomail search | bomail stats

If called with no arguments, prints some default stats and top lists.


Global options:
    bomail stats -max_items n  # print at most n items per list (default """ + str(max_items) + """)
    bomail stats -max_cols n   # wrap lines at n characters


1. Printing basic stats:
    bomail stats all [list]       # print top entries from list, aggregated
    bomail stats num [list]       # print statistics about length of list

Lists you can use:
  - addresses
  - authors
  - recipients
  - tags
  - words
  - attach

Examples:
    bomail stats all authors     # get most common authors
    bomail stats num recipients  # get stats about num of recips per message
    bomail stats num words       # get wordcount stats


2. Filters:
    bomail stats matching [search_str]           # print default stats for matching files
    bomail stats total matching [search_str]     # how many match the query
    bomail stats fraction matching [search_str]  # what fraction of all messages match the query
    bomail stats [basic_part] matching [search_str]

Examples:
    bomail stats matching -subject "Hungry"        # default stats for matching files
    bomail stats num words matching -sent          # how long are emails I write?
    bomail stats all authors matching "chocolate"  # list those who write about it most
    bomail stats fraction matching -sent           # fraction of emails sent by me


3a. Slicing into bins:
    bomail stats slice [basic_part] into [bin_units]
    bomail stats slice [filter_part] into [bin_units]

Bin units:
  - years
  - months
  - weeks
  - days
  - hours

Examples:
    bomail stats slice into years                 # stats about number of messages each year
    bomail stats slice addresses into months      # list top addresses each month
    bomail stats slice num addresses into months  # plot avg num addresses/message, each month
    bomail stats slice fraction matching -sent into months
    bomail stats slice num tags matching -attach into weeks


3b. Slicing across time:
    bomail stats slice [basic_part] into [bin_units] of the [slice_unit]
    bomail stats slice [filter+part] into [bin_units] of the [slice_unit]

Same thing, but group together bins across different slice_units:
  - year
  - month
  - week
  - day

Examples:
    bomail stats slice total into days of the month
    bomail stats slice fraction matching -from me -to "Name" into days of the week

The first gave how many emails I get on the 1st, 2nd, 3rd, ... of each month.
The second gave what fraction of all emails I send on Mon, Tue, ... go to "Name".


"""


def datestr_to_week_of_year(datestr):
  return datetime.date(int(datestr[:4]), int(datestr[5:7]), int(datestr[8:10])).isocalendar()[1]


def itemlist_to_strlist(itemlist, item_to_str):
  res = []
  for i,pr in enumerate(itemlist[:max_items]):
    res.append("    ")
    res.append(item_to_str(pr[0]))
    res.append(" (")
    res.append(str(pr[1]))
    res.append(")")
    if i < len(itemlist) - 1:
      res.append("\n")
  return res


# given a sorted list of numbers
def compute_stats(counts):
  n = len(counts)
  if n == 0:
    return 0, 0, 0, 0, 0
  avg = sum(counts) / n
  std_dev = -1 if n==1 else math.sqrt(sum([(c-avg)**2 for c in counts]) / (n-1))
  counts.sort()
  quant_05 = counts[int(n/20)]
  quant_25 = counts[int(n/4)]
  median = counts[int(n/2)]
  quant_75 = counts[int(3*n/4)]
  quant_95 = counts[int(19*n/20)]
  return sum(counts), len(counts), avg, std_dev, quant_05, quant_25, median, quant_75, quant_95


def get_stats_strlist_from_counts(counts):
  return get_stats_strlist(compute_stats(counts))


def get_stats_strlist(stats):
  total, num_unique, avg, std_dev, quant_05, quant_25, median, quant_75, quant_95 = stats
  return ["    total:   ", str(total), "\n",
          "    unique:  ", str(num_unique), "\n",
          "    average: ", str(avg), "\n",
          "    std dev: ", str(std_dev), "\n",
          "     5 %:    ", str(quant_05), "\n",
          "    25 %:    ", str(quant_25), "\n",
          "    median:  ", str(median), "\n",
          "    75 %:    ", str(quant_75), "\n",
          "    95 %:    ", str(quant_95), "\n"]


# helper functions for slicing over dates
# get the endpoint of the bin this date is in
def round_up(date_obj, bin_unit):
  if bin_unit.startswith("hour"):
    upper = date_obj + datetime.timedelta(hours = 1)
    return datetime.datetime(year=upper.year, month=upper.month, day=upper.day, hour=upper.hour, tzinfo=upper.tzinfo)
  elif bin_unit.startswith("day"):
    upper = date_obj + datetime.timedelta(days = 1)
    return datetime.datetime(year=upper.year, month=upper.month, day=upper.day, tzinfo=upper.tzinfo)
  elif bin_unit.startswith("week"):
    wkday = date_obj.isocalendar()[2]
    upper = date_obj + datetime.timedelta(days = 7 - wkday)
    return datetime.datetime(year=upper.year, month=upper.month, day=upper.day, tzinfo=upper.tzinfo)
  elif bin_unit.startswith("month"):
    lower = datetime.datetime(year=date_obj.year, month=date_obj.month, day=1, tzinfo=date_obj.tzinfo)
    return lower + relativedelta(months=+1)
  elif bin_unit.startswith("year"):
    return datetime.datetime(year=date_obj.year+1, month=1, day=1, tzinfo=date_obj.tzinfo)


def datestr_to_bin_id(datestr, bin_unit, slice_unit):
  if slice_unit is not None and slice_unit.startswith("week"):
    day_num = dateutil.parser.parse(datestr).isocalendar()[2] - 1
    wkday = iso_wkdays[day_num]
    if bin_unit.startswith("day"):
      return wkday
    # assume it's hours
    return wkday + " " + datestr[11:13]
  if bin_unit.startswith("week"):
    if slice_unit is None:
      return datestr[:4] + " " + str(datestr_to_week_of_year(datestr))
    if slice_unit.startswith("year"):
      return str(datestr_to_week_of_year(datestr))
    # assume it's month, and break the weeks of the month into these sets of days
    return ["01-07","08-14","15-21","22-28","29-31"][int(int(datestr[8:10]) / 7)]

  max_len = 13
  if bin_unit.startswith("day"):
    max_len = 10
  elif bin_unit.startswith("month"):
    if slice_unit is not None and slice_unit.startswith("year"):
      return month_names[int(datestr[5:7])-1]
    max_len = 7
  elif bin_unit.startswith("year"):
    max_len = 4

  if slice_unit is None:
    return datestr[:max_len].replace("T"," ")
  elif slice_unit.startswith("year"):
    return datestr[5:max_len].replace("T"," ")
  elif slice_unit.startswith("month"):
    return datestr[8:max_len].replace("T"," ")
  else:
    return datestr[11:max_len].replace("T"," ")


# return two functions which give the name of a date's bin and its slice
def get_date_maps(bin_unit, slice_unit):
  date_to_sliceind = lambda x: x  # map date to the name of the slice it's in
  date_to_binname = lambda x: x   # map date to the name of the bin it's in

  if slice_unit.startswith("year"):
    date_to_sliceind = lambda datestr: datestr[:4]
    if bin_unit.startswith("month"):
      date_to_binname = lambda datestr: datestr[5:7]
    elif bin_unit.startswith("week"):
      date_to_binname = datestr_to_week_of_year
    elif bin_unit.startswith("day"):
      date_to_binname = lambda datestr: datestr[5:10]
    else:  # hour
      date_to_binname = lambda datestr: datestr[5:]

  elif slice_unit.startswith("month"):
    date_to_sliceind = lambda datestr: datestr[:7]
    if bin_unit.startswith("week"):
      date_to_binname = lambda datestr: int(int(datestr[8:10]) / 7)
    elif bin_unit.startswith("day"):
      date_to_binname = lambda datestr: datestr[8:10]
    else:  # hour
      date_to_binname = lambda datestr: datestr[8:]

  elif slice_unit.startswith("week"):
    # (year, week of the year)
    date_to_sliceind = lambda datestr: (datestr[:4], dateutil.parser.parse(datestr).isocalendar()[1])
    get_wkday = lambda datestr: str(datetime.date(int(datestr[:4]), int(datestr[5:7]), int(datestr[8:10])).weekday())
    if bin_unit.startswith("day"):
      date_to_binname = get_wkday
    else:  # hour
      date_to_binname = lambda datestr: get_wkday(datestr) + " " + datestr[11:]

  else:  # day: assume hours
    date_to_sliceind = lambda datestr: datestr[:10]
    date_to_binname = lambda datestr: int(datestr[11:])

  return date_to_sliceind, date_to_binname


# binstr_to_flist: a dict mapping each binstr to list of files that fall in that bin
#   binstr is a rounded date representing a bin
# return list of tuples: (bin_identifier, bin_filelist, num_sliced_over)
# sorted by bins chronologically
# e.g. if we bin into months and slice across two years 1994-1995, then return a list of 12 tuples, each
# of the form e.g. ('Jan', [filelist], 2)
def do_slice(binstr_to_flist, bin_unit, slice_unit):
  if slice_unit is None:
    mylist = sorted(binstr_to_flist.items())
    return [(datestr_to_bin_id(d, bin_unit, slice_unit), flist, 1) for d,flist in mylist]

  date_to_sliceind, date_to_binname = get_date_maps(bin_unit, slice_unit)
  bins = {}  # map slice_ind to tuple (bin_id, [filelist], set(unique_slices)) 
  for datestr,flist in binstr_to_flist.items():
    k = date_to_binname(datestr)
    if k in bins:
      bins[k][1] += flist
      bins[k][2].add(date_to_sliceind(datestr))
    else:
      bins[k] = [datestr_to_bin_id(datestr, bin_unit, slice_unit), list(flist), set([date_to_sliceind(datestr)])]
  result = [(pr[1][0], pr[1][1], len(pr[1][2])) for pr in sorted(bins.items())]

  return result


# totals is a list of numbers
def get_bar_plot(labels, totals):
  s_nums = ['%s' % float('%.4g' % t) for t in totals]
  max_numlen = max(map(len,s_nums))
  max_lablen = max(map(len,labels))
  cols = max(1, max_cols - max_numlen - max_lablen - 4)
  m = max(totals)
  col_list = [round(b*cols/m) for b in totals]
  slist = []
  for i in range(len(totals)):
    slist.append(labels[i].ljust(max_lablen) + " (" + (s_nums[i] + ")").ljust(max_numlen+1) + " " + ("="*col_list[i]))
    slist.append("\n")
  return slist


def get_list_plot(labels, attrs, listname):
  max_lablen = max(map(len,labels))
  slist = []
  for i in range(len(attrs)):
    slist.append(labels[i].ljust(max_lablen) + "\n")
    slist += itemlist_to_strlist(attrs[i], get_strfunc(listname))
  return slist


def get_mean_plot(labels, stats):
  avgs = [s[2] for s in stats]
  std_devs = [s[3] for s in stats]
  s_nums = list(map(str, avgs))
  max_numlen = max(map(len,s_nums))
  max_lablen = max(map(len,labels))
  cols = max(1, max_cols - max_numlen - max_lablen - 4)
  m = max([a+s for a,s in zip(avgs,std_devs)])
  avg_list = [round(b*cols/m) for b in avgs]
  low_list = [max(0,round((a-s)*cols/m)) for a,s in zip(avgs,std_devs)]
  hi_list = [min(cols-1, round((a+s)*cols/m)) for a,s in zip(avgs,std_devs)]
  numstrs = [" "*l + "-"*(a-l) + "=" + "-"*(h-a) for a,l,h in zip(avg_list, low_list, hi_list)]
  slist = []
  for i in range(len(stats)):
    avg_str = '%s' % float('%.4g' % avgs[i])
    sd_str  = '%s' % float('%.4g' % std_devs[i])
    slist.append(labels[i].ljust(max_lablen) + " (" + (avg_str + " ± " + sd_str + ")").ljust(max_numlen+1) + " " + numstrs[i])
    slist.append("\n")
  return slist


# persistent, re-usable
punct_trans = str.maketrans("","", string.punctuation)


# a summary of a message
class MsgSum:
  def __init__(self, filename, mail_mgr):
    self.authlist = addr.str_to_pairlist(mail_mgr.get(filename, mailfile.FROM_L))
    self.reciplist = addr.str_to_pairlist(mail_mgr.get(filename, mailfile.TO_L))
    self.reciplist += addr.str_to_pairlist(mail_mgr.get(filename, mailfile.CC_L))
    self.reciplist += addr.str_to_pairlist(mail_mgr.get(filename, mailfile.BCC_L))

    self.tags = mail_mgr.get_tags(filename)

    temp = mail_mgr.get(filename, mailfile.BODY_L).split()
    self.words = [t.translate(punct_trans).lower() for t in temp]

    attach_s = mail_mgr.get(filename, mailfile.ATTACH_L).strip()
    self.num_attach = 0 if len(attach_s) == 0 else len(attach_s.split(", "))

    self.from_me = mail_mgr.get(filename, mailfile.SENT_L) == "True"

    self.datestr = mail_mgr.get(filename, mailfile.DATE_L)
    self.date_obj = None
    try:
      self.date_obj = dateutil.parser.parse(self.datestr)
    except:
      self.date_obj = datetime.datetime(year=9999,month=12,day=1)


def listname_to_getter(ln):
  if ln == "addresses":
    return lambda ms: ms.authlist + ms.reciplist
  elif ln == "authors":
    return lambda ms: ms.authlist
  elif ln == "recipients":
    return lambda ms: ms.reciplist
  elif ln == "tags":
    return lambda ms: ms.tags
  elif ln == "words":
    return lambda ms: ms.words
  else:  # shouldn't happen
    return lambda ms: [1]


def get_strfunc(ln):
  if ln in ["addresses", "authors", "recipients"]:
    return lambda pr: addr.pair_to_str(*pr)
  elif ln == "tags":
    return lambda tag: tag
  elif ln == "words":
    return lambda word: word
  else:  # shouldn't happen
    return lambda s: str(s)


# we need to count, sort, combine list of lists
def get_count_list(list_lists):
  counts = {}  # map x to number of occurrences
  for xs in list_lists:
    for x in xs:
      counts[x] = counts.get(x, 0) + 1
  return sorted(counts.items(), key = lambda pr: (-pr[1], pr[0]))


class MailStats:
  def __init__(self, mail_mgr):
    self.mail_mgr = mail_mgr
    self.msg_sums = {}       # map filename to summary

  # get message summary object
  def get_msg_sum(self, filename):
    if filename not in self.msg_sums:
      self.msg_sums[filename] = MsgSum(filename, self.mail_mgr)
    return self.msg_sums[filename]

  def get_all(self, listname, filelist):
    if len(filelist) == 0:
      return []
    getter = listname_to_getter(listname)
    return get_count_list([getter(self.get_msg_sum(f)) for f in filelist])

  def get_stats(self, listname, filelist):
    count_list = self.get_all(listname, filelist)
    counts = [c[1] for c in count_list]
    return compute_stats(counts)

  # return filenames sorted into each [bin_unit] in [slice_unit], over all slice_units
  # bin_unit can be hour, day, week, month, or year
  # slice_unit can be day, week, month, year, or None
  #
  # return list of bins sorted chronologically
  # each bin is a tuple (identifier, list of files, num_sliced_over)
  def get_time_slice(self, filenames, bin_unit, slice_unit=None):
    now = datetime.datetime.now()
    last_bin_obj = round_up(now, bin_unit)
    binstr_to_flist = {}
    for f in filenames:
      bound_str = round_up(self.get_msg_sum(f).date_obj, bin_unit).isoformat()[:13]
      if bound_str in binstr_to_flist:
        binstr_to_flist[bound_str].append(f)
      else:
        binstr_to_flist[bound_str] = [f]
    return do_slice(binstr_to_flist, bin_unit, slice_unit)

  # So the kinds of stats seem to be:
  # indicators (print total and fraction)
  # numbers, including length of lists (print general stats)
  # aggregations of lists, e.g. all authors (print top members and indicators)
  # lengths of *aggregations* of lists (print general stats)

  def get_summary(self, filenames):
    if len(filenames) == 0:
      return "No messages.\n"
    l = []
    l.append("Summary:\n\n")
    l.append("Number of messages: ")
    l.append(str(len(filenames)))
    l.append("\n\n")

    l.append("Popular tags: \n")
    l += itemlist_to_strlist(self.get_all("tags", filenames), lambda tag: tag)
    l.append("\n\n")

    for s in ["addresses", "authors", "recipients"]:
      l.append("All ")
      l.append(s)
      l.append(" by number of emails:\n")
      count_list = self.get_all(s, filenames)
      l += get_stats_strlist_from_counts([p[1] for p in count_list])
      l.append("Most common ")
      l.append(s)
      l.append(":\n")
      l += itemlist_to_strlist(count_list, lambda pr: addr.pair_to_str(*pr))
      l.append("\n\n")
    
    l.append("Word count:\n")
    l += get_stats_strlist(self.get_stats("words", filenames))
    l.append("\n")
    l.append("Popular words:\n")
    l += itemlist_to_strlist(self.get_all("words", filenames), lambda word: word)
    return "".join(l)


def parse_args(args):
  if len(args) == 0:
    return "default", None, None, None, None
  if args[0] == "slice":
    into_i = args.index("into")
    attr, listname, filt_args = parse_filt_args([] if into_i == 1 else args[1:into_i])
    bin_units = args[into_i+1]
    if not any([bin_units.startswith(s) for s in ["hour","day","week","month","year"]]):
      raise Exception("unrecognized bin unit in slice: " + bin_units)
    if len(args) > into_i+2:
      slice_units = args[-1]
      if not any([slice_units.startswith(s) for s in ["day","week","month","year"]]):
        raise Exception("unrecognized slice unit: " + slice_units)
    else:
      slice_units = None
  else:
    bin_units = None
    slice_units = None
    attr, listname, filt_args = parse_filt_args(args)
  return attr, listname, filt_args, bin_units, slice_units


def parse_filt_args(args):
  attr, listname, filt_args = "default", None, None
  if len(args) == 0:
    return attr, listname, filt_args

  if "matching" in args:
    i = args.index("matching")
    filt_args = args[i+1:]
    args = args[:i]
  if len(args) > 0:
    attr = args[0]
    if attr not in ["total", "fraction", "all", "num"]:
      raise Exception("Unrecognized attribute type: " + attr)
  if len(args) > 1 or attr == "all" or attr == "num":
    # if all or num, expect there to be another arg
    # (raise an exception if not)
    listname = args[1]
    if listname not in ["addresses","authors","recipients","tags","words"]:
      raise Exception("Unrecognized list: " + listname)
  return attr, listname, filt_args


def main(filelist, mail_mgr, attr, listname, filt_args, bin_units, slice_units):
  ms = MailStats(mail_mgr)
  match_list = filelist if filt_args is None else search.main_arglist(filt_args, mail_mgr, filelist)
  if bin_units is None:
    if attr == "default":
      return ms.get_summary(match_list)   # matching ...
    elif attr == "total":
      return [str(len(match_list))]
    elif attr == "fraction":
      return [str(len(match_list) / len(filelist))]
    elif attr == "all":
      return itemlist_to_strlist(ms.get_all(listname, match_list), get_strfunc(listname))
    elif attr == "num":
      return get_stats_strlist(ms.get_stats(listname, match_list))
  else:  # SLICE
    binlist = ms.get_time_slice(match_list, bin_units, slice_units)
    labels = [b[0] for b in binlist]
    if attr == "default" or attr == "total":
      totals = [len(b[1]) for b in binlist]
      return get_bar_plot(labels, totals)
    elif attr == "fraction":
      all_binlist = ms.get_time_slice(filelist, bin_units, slice_units)
      fracs = [len(b[1]) / len(a[1]) for b,a in zip(binlist, all_binlist)]
      return get_bar_plot(labels, fracs)
    elif attr == "all":
      attrs = [ms.get_all(listname, b[1]) for b in binlist]
      return get_list_plot(labels, attrs, listname)
    elif attr == "num":
      stats = [ms.get_stats(listname, b[1]) for b in binlist]
      return get_mean_plot(labels, stats)
  return ["error\n"]


def main_cli():
  args = sys.argv[1:]
  if "-h" in args:
    print(usage_str)
    exit()

  if "-max_items" in args:
    ind = args.index("-max_items")
    if len(args) <= ind+1:
      print(usage_str)
      exit()
    max_items = max(int(args[ind+1]), 5)
    args = args[:ind] + ([] if len(args) <= ind+2 else args[ind+2:])

  if "-max_cols" in args:
    ind = args.index("-max_cols")
    if len(args) <= ind+1:
      print(usage_str)
      exit()
    max_cols = max(int(args[ind+1]), 5)
    args = args[:ind] + ([] if len(args) <= ind+2 else args[ind+2:])
  
  try:
    attr, listname, filt_args, bin_units, slice_units = parse_args(args)
  except Exception as e:
    print("Error parsing: " + str(e))
    print(usage_str)
    exit()
  filenames = [f[:-1] for f in sys.stdin.readlines()]

  result_strlist = main(filenames, mailfile.MailMgr(), attr, listname, filt_args, bin_units, slice_units)

  print()
  print("".join(result_strlist))


if __name__ == "__main__":
  main_cli()



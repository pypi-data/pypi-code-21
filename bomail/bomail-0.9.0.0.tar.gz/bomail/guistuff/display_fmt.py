####
# bomail.guistuff.display_fmt
#
# Format messages or threads for display.
####

import sys
import time
import curses
import curses.textpad
import re
import time
import textwrap, dateutil.parser, time
from dateutil import tz

import bomail.config.config as config
import bomail.config.guiconfig as guicfg
import bomail.cli.mailfile as mailfile
import bomail.util.addr as addr
import bomail.util.tags as tags

ATTACH_STR = " + "
MARKING_STR = " [ ]"

#---------------------------------------------------------------
# utility stuff, getting display-formatted versions of things

def get_disp_author_from_pair(pair):
  return pair[0] if pair[0] != "" else pair[1]
  
def get_disp_author_from_str(s):
  return get_disp_author_from_pair(addr.str_to_pair(s))

def get_disp_author(data, is_draft=False):
  if is_draft:
    to_strs = [data[l] for l in [mailfile.TO_L, mailfile.CC_L, mailfile.BCC_L]]
    tolists = [addr.str_to_pairlist(s) for s in to_strs]
    return "[DRAFT] " + ", ".join([get_disp_author_from_pair(p) for l in tolists for p in l])
  else:
    return get_disp_author_from_str(data[mailfile.FROM_L])

def get_disp_datestr(data):
  return dateutil.parser.parse(data[mailfile.DATE_L]).astimezone(tz.tzlocal()).strftime(guicfg.datefmt)

indic = lambda x: 1 if x else 0


#---------------------------------------------------------------
# formatting messages / threads into displayable chunks

# return a shortened string describing the email
def get_shortened(filename, mgr):
  data = mgr.get_all(filename)
  author = get_disp_author(data)[:guicfg.short_authorlen]
  subject = data[mailfile.SUBJ_L][:guicfg.short_subjectlen]
  return "[" + subject + "] by " + author

def get_shortened_list(filelist, mail_mgr):
  return "(" + str(len(filelist)) + " messages) " + ", ".join([get_shortened(f, mail_mgr) for f in filelist])


### These routines format a message or thread for display
# They return a pair (msg_lines, attr_data)
# where msg_lines is a list of text lines
# and attr_data is a list of quads (y, x, width, attr)


# get lines, attr_data for standard inbox view
# if use_curses is false, don't fill out attr_data
def format_msg_lines(mail_mgr, screen_width, authorstr, subj, tagstr, datestr, has_attach, is_draft, orig_body, thread_num, thread_total, use_curses=True):
  top_line, attr_data = format_msg_top_line(
      screen_width,
      authorstr,
      subj,
      tagstr if guicfg.show_tags and guicfg.inline_tags else None,
      datestr,
      has_attach,
      is_draft,
      thread_num,
      thread_total,
      use_curses=use_curses)
     
  max_lines = guicfg.lines_per_msg
  msg_lines = [top_line]
  if max_lines == 1:
    return msg_lines, attr_data

  tag_lines = 0
  if guicfg.show_tags and not guicfg.inline_tags:
    # tags get their own line
    tag_lines = 1
    s = " "*(guicfg.authorlen + guicfg.authorpad) + tagstr
    s = s[:screen_width]
    msg_lines.append(s)
    if use_curses:
      attr_data.append((1, guicfg.authorlen + guicfg.authorpad, len(tagstr), curses.color_pair(guicfg.TAGS_CLR_PAIR)))

  bodywidth  = screen_width - guicfg.authorlen - guicfg.authorpad - 1
  indent_len = guicfg.authorlen + guicfg.authorpad
  new_lines, new_data = get_indented_bodylines(orig_body, bodywidth, indent_len, guicfg.remove_newlines, len(msg_lines), use_curses=use_curses)
  msg_lines += new_lines
  attr_data += new_data
  
  # trim msg_lines if needed
  if max_lines >= 1:
    stop_at = max(1, max_lines - indic(guicfg.horiz_line) - indic(guicfg.skip_line) - tag_lines)
    if guicfg.pad_msg_lines:
      while len(msg_lines) < stop_at:
        msg_lines.append("")
    msg_lines = msg_lines[:stop_at]

  if guicfg.horiz_line:
    msg_lines.append("-"*screen_width)
  if guicfg.skip_line:
    msg_lines.append(" "*screen_width)

  return msg_lines, attr_data


# get lines for the standard inbox view with threads off
def get_msg_lines_nothread(mail_mgr, filename, screen_width, use_curses=True):
  data = mail_mgr.get_all(filename)
  return format_msg_lines(
      mail_mgr,
      screen_width,
      get_disp_author(data, filename[-5:] == "draft"),
      data[mailfile.SUBJ_L],
      data[mailfile.TAGS_L],
      get_disp_datestr(data),
      len(data[mailfile.ATTACH_L].strip()) > 0,
      filename[-5:] == "draft",
      data[mailfile.BODY_L],
      None,
      None,
      use_curses)

# get lines for the standard inbox view with threads on
# get data for a thread, formatted as a single displayed set of lines
# current approach: display *oldest NEW message* in thread
#   (that is, the *last* one matching the tab search query)
# plus (num_new / total_in_thread)
# plus display multiple authors and ellipsis if appropriate
def get_msg_lines_thread(mail_mgr, thread_view, screen_width):
  fnames = thread_view.all_files
  datas = [mail_mgr.get_all(f) for f in fnames]
  datas.reverse()  # newest to oldest?
  is_draft_list = [f[-5:] == "draft" for f in fnames]
  is_draft = any(is_draft_list)
  has_attach = any([len(d[mailfile.ATTACH_L].strip()) > 0 for d in datas])
  authors = []
  for i,d in enumerate(datas):
    auth = get_disp_author(d, is_draft_list[i])
    if auth not in authors:
      authors.append(auth)
  authorstr = ", ".join(authors)
  subject = mail_mgr.get(thread_view.repr_file, mailfile.SUBJ_L)
  datestr = get_disp_datestr(mail_mgr.get_all(thread_view.repr_file))
  body = mail_mgr.get(thread_view.repr_file, mailfile.BODY_L)
  tagset = set()
  for d in datas:
    tagset.update(tags.get_tagset_from_str(d[mailfile.TAGS_L], include_folders=False))
  tagstr = ", ".join(sorted(list(tagset)))

  return format_msg_lines(
      mail_mgr,
      screen_width,
      authorstr,
      subject,
      tagstr,
      datestr,
      has_attach,
      is_draft,
      body,
      len(thread_view.matching_set),
      len(thread_view.all_files))


# get format data for a single message to be shown in a thread view
# (linear or tree view)
# here orig_data is the data of the root of the message tree
# return pair lines, attribute_data
def get_thread_view_lines(data, orig_data, is_draft, screen_width, is_collapsed, thread_num, thread_total, level):
  tagstr = data[mailfile.TAGS_L]

  # In the future with tree view, this will be  level * guicfg.thread_indent
  indent_amt = 0
  top_line, attr_data = format_msg_top_line(
      screen_width - indent_amt, 
      get_disp_author(data, is_draft),
      data[mailfile.SUBJ_L],
      tagstr if guicfg.thread_show_tags and guicfg.thread_inline_tags else None,
      get_disp_datestr(data),
      len(data[mailfile.ATTACH_L].strip()) > 0,
      is_draft,
      thread_num,
      thread_total)
     
  max_lines = guicfg.thread_lines_per_collapsed_msg if is_collapsed else -1
  msg_lines = [" "*indent_amt + str(top_line)]

  tag_lines = 0
  if guicfg.thread_show_tags and not guicfg.thread_inline_tags:
    tag_lines = 1
    s = " "*(guicfg.authorlen + guicfg.authorpad) + tagstr
    s = s[:screen_width]
    msg_lines.append(s)
    attr_data.append((1, guicfg.authorlen + guicfg.authorpad, len(tagstr), curses.color_pair(guicfg.TAGS_CLR_PAIR)))

  bodywidth  = screen_width - guicfg.authorlen - guicfg.authorpad - 1
  indent_len = guicfg.authorlen + guicfg.authorpad + indent_amt
  new_lines, new_data = get_indented_bodylines(data[mailfile.BODY_L], bodywidth, indent_len, guicfg.thread_remove_newlines, len(msg_lines))
  msg_lines += new_lines
  attr_data += new_data
  
  # trim msg_lines if needed
  max_lines = guicfg.thread_lines_per_collapsed_msg if is_collapsed else -1
  if max_lines >= 1:
    stop_at = max(1, max_lines - indic(guicfg.thread_horiz_line) - indic(guicfg.thread_skip_line) - tag_lines)
    if guicfg.pad_msg_lines:
      while len(msg_lines) < stop_at:
        msg_lines.append("")
    msg_lines = msg_lines[:stop_at]

  if guicfg.thread_horiz_line:
    msg_lines.append("-"*screen_width)
  if guicfg.thread_skip_line:
    msg_lines.append(" "*screen_width)

  return msg_lines, attr_data


# remove_newlines_type is "all", "some", or "none"
# return (lines_of_text, attr_data)
def get_indented_bodylines(orig_body, bodywidth, indent_len, remove_newlines_type, y_offset, use_curses=True):
  attr_data = []
  indent = " " * indent_len
  if remove_newlines_type == "all":
    return [indent + l for l in textwrap.wrap(orig_body, bodywidth, replace_whitespace=True)], []

  if remove_newlines_type == "some":
    orig_bodylines = [s for s in orig_body.splitlines() if len(s.strip()) > 0]
  else:  # none
    orig_bodylines = [s for s in orig_body.splitlines()]
  wrapped_lines_lst = [textwrap.wrap(line, bodywidth) for line in orig_bodylines]
  y_coord = y_offset
  lines = [indent + l for linelst in wrapped_lines_lst for l in linelst]
  if use_curses:
    for ind,line in enumerate(lines):
      attr_data.append((y_coord+ind, indent_len, bodywidth, curses.color_pair(guicfg.DEFAULT_CLR_PAIR)))
  for orig_ind,line in enumerate(orig_bodylines):
    if len(line) > 0 and line[0] == ">":
      for i in range(len(wrapped_lines_lst[orig_ind])):
        if use_curses:
          attr_data.append((y_coord+i, indent_len, bodywidth, guicfg.quote_attr))
    y_coord += len(wrapped_lines_lst[orig_ind])
  return lines, attr_data


# format given data into a line
# return msg_line (a string) and attr_data (a list of quads (y, x, width, attr))
# tagstr: None if no tags, else a string of tags
# is_draft: Bool
# if thread_num and thread_total are None, ignore
# else display [thread_num of thread_total]
def format_msg_top_line(screen_width, authorstr, subj, tagstr, datestr, has_attach, is_draft, thread_num, thread_total, use_curses=True):
  attr_data = []
  line_lst = []  # join these strings together at the end
  line_len = 0

  # AUTHOR and attachment
  author = authorstr[:guicfg.authorlen]
  line_len = guicfg.authorlen + guicfg.authorpad
  if has_attach:
    line_lst.append(author[:line_len - len(ATTACH_STR)])
    line_lst.append(" "*(line_len - len(ATTACH_STR) - len(author)))
    line_lst.append(ATTACH_STR)
  else:
    line_lst.append(author)
    line_lst.append(" "*(line_len - len(author)))

  if use_curses:
    attr = curses.color_pair(guicfg.AUTHOR_CLR_PAIR) | guicfg.author_attr
    attr_data.append((0, 0, line_len, attr))

  # SUBJECT [X of Y]
  pre_date_width = screen_width - guicfg.datelen - guicfg.datepad - len(MARKING_STR)
  subject = re.sub(r'\s+', " ", subj)
  if thread_total is None:
    subject = subject[:pre_date_width - line_len]
    line_lst.append(subject)
    line_len += len(subject)
    if use_curses:
      attr_data.append((0, guicfg.authorlen + guicfg.authorpad, len(subject), attr))
  else:
    countstr_list = [" ["]
    if thread_num is not None:
      countstr_list.append(str(thread_num))
      countstr_list.append(" of ")
    countstr_list.append(str(thread_total))
    countstr_list.append("]")
    countstr_len = sum(map(len,countstr_list))
    subject = subject[:pre_date_width - line_len - countstr_len]
    line_lst.append(subject)
    line_len += len(subject)
    if use_curses:
      attr_data.append((0, guicfg.authorlen + guicfg.authorpad, len(subject)+1, attr))
    for cs in countstr_list:
      line_lst.append(cs)
    line_len += countstr_len
    if use_curses:
      attr_data.append((0, line_len - countstr_len + 1, countstr_len - 1, curses.color_pair(guicfg.THREAD_CLR_PAIR) | guicfg.author_attr))
  
  # TAGS
  if tagstr is not None:
    # right-align tags, so we get:
    #  ---spaces---tag1, tag2  DATE
    tag_pad = 2
    min_tag_len = 3
    min_tagstart = line_len + tag_pad
    tagspace_avail = pre_date_width - min_tagstart
    if tagspace_avail >= min_tag_len:  # else give up on tags
      tagstr = tagstr[:tagspace_avail]
      tagstart = pre_date_width - len(tagstr)
      num_spaces = tagstart - line_len
      line_lst.append(" "*num_spaces)
      line_lst.append(tagstr)
      if use_curses:
        attr_data.append((0, line_len, num_spaces, attr))
      line_len += num_spaces
      if use_curses:
        attr_data.append((0, line_len, len(tagstr), curses.color_pair(guicfg.TAGS_CLR_PAIR)))
      line_len += len(tagstr)

  # DATE
  num_spaces = screen_width - guicfg.datelen - line_len - len(MARKING_STR)
  if use_curses:
    attr_data.append((0, line_len, num_spaces, attr))
  line_lst.append(" "*num_spaces)
  line_len += num_spaces

  datestr = datestr[:guicfg.datelen]
  if use_curses:
    attr_data.append((0, line_len, len(datestr), attr))
  line_lst.append(datestr)
  line_len += len(datestr)

  # MARKING BOX
  num_spaces = screen_width - len(MARKING_STR) - line_len
  line_lst.append(" "*num_spaces)
  line_lst.append(MARKING_STR)
  if use_curses:
    attr_data.append((0, screen_width - num_spaces - len(MARKING_STR), num_spaces + len(MARKING_STR), attr))

  return ''.join(line_lst), attr_data


####
# bomail.guistuff.get_text
#
# Getting input text for specific tasks.
####

import sys
import os
import time
import curses
import curses.textpad
import time
import textwrap, dateutil.parser, time
from dateutil import tz

import bomail.config.config as config
import bomail.config.guiconfig as guicfg
import bomail.cli.mailfile as mailfile
import bomail.util.addr as addr
import bomail.util.search_opts as search_opts
import bomail.util.tags as tags
import bomail.util.search_opts as search_opts
import bomail.guistuff.display as display

LIST_INSTR_LINES = [
    "Type or use up/down arrows to navigate.",
    "Tab: accept current line and go to next entry.",
    "Enter: accept current line and return list.",
    "Escape: cancel current line and return list.",
    "Ctrl-x: cancel entire process."]


#---------------------------------------------------------------------
# mini-screens to get input for specific tasks

def get_subj_line(gui, init_str):
  display.draw_bottom_text(gui, ["Enter subject line (ESC=cancel)."])
  height,width = gui.note_area.getmaxyx()
  return get_txt_line(gui.note_area, 0, 0, width, "", gui.attr)


sched_instructions = [
      "format: yyyy-mm-dd-HH:MM   (or any prefix)",
      "        p10d               (plus 10 days from now at 00:00)",
      "        p3.5w              (plus exactly 3.5 weeks from now)",
      "ESC=cancel.  units are y (year), w (week), d (day), H (hour), M (minute)."]


def get_sched_txt(gui):
  display.draw_bottom_text(gui, sched_instructions)
  display.redraw_note(gui, "")
  height, width = gui.note_area.getmaxyx()
  return get_txt_line(gui.note_area, 0, 0, width, "", gui.attr)

def get_tab_search_txt(gui, init_str):
  height,width = gui.tab_area.getmaxyx()
  gui.tab_area.clear()
  gui.tab_area.addstr(0, 0, "Enter to accept, ESC to cancel", gui.attr)
  for i,s in enumerate(search_opts.options_str.split("\n")):
    if i+2 >= height:
      break
    gui.tab_area.addstr(i + 2, 0, s[:width], gui.attr)
  gui.tab_area.refresh()
  height, width = gui.note_area.getmaxyx()
  display.draw_bottom_text(gui, "")
  return get_txt_line(gui.note_area, 0, 0, width, init_str, gui.attr)


def get_decoded(key):
  try:
    res = curses.unctrl(key).decode("utf-8")
  except:
    res = key
  return res


# return None if ESC is pressed
def get_txt_line(window, y, x, width, initstr, attr):
  s = initstr
  blankstr = " "*(width - x - 1)
  window.keypad(True)
  x_ind = len(s)
  while True:
    window.addstr(y, x, blankstr)
    window.addstr(y, x, s[:width-1], attr)
    window.chgat(y, x+x_ind, 1, curses.A_STANDOUT)  # cursor
    window.refresh()
    
    # read input and react
    key = window.getkey()
    code = get_decoded(key)
    if key == "KEY_ESC" or code == "^[":
      return None
    elif key in ["KEY_ENTER", "\r", "\n", "\n\r"]:
      return s
    elif key in ["KEY_TAB", "\t"]:
      x_ind = len(s)
    elif key == "KEY_BACKSPACE" or code == "^?":
      if x_ind > 0:
        s = s[:x_ind-1] + ("" if x_ind >= len(s) else s[x_ind:])
        x_ind -= 1
    elif key == "KEY_LEFT":
      if x_ind > 0:
        x_ind -= 1
    elif key == "KEY_RIGHT":
      if x_ind < len(s):
        x_ind += 1
    else:
      s = s[:x_ind] + key + ("" if x_ind >= len(s) else s[x_ind:])
      x_ind += 1
  

# return window for editing, window for results, height, width (of editing window)
def draw_list_top_and_instr(window, instr_lines):
  height, width = window.getmaxyx()
  toplines = len(instr_lines) + 3
  height -= toplines
  window.clear()
  for i,line in enumerate(instr_lines):
    window.addstr(i, 0, line[:width-1])
  window.hline(toplines-3, 0, "-", width)
  window.hline(toplines-1, 0, "-", width)
  window.refresh()
  new_window = curses.newwin(height, width, toplines + display.TOPLINES, 0)
  new_window.bkgd(" ", curses.color_pair(guicfg.DEFAULT_CLR_PAIR))
  new_window.keypad(1)

  results_win = curses.newwin(1, width, toplines + display.TOPLINES - 2, 0)
  results_win.bkgd(" ", curses.color_pair(guicfg.DEFAULT_CLR_PAIR))
  return new_window, results_win, height, width


# get_bold_location(elem_str, curr_str) gets the index in elem_str to start bolding
def draw_list(curr_index, height, width, results_win, window, curr_str, curr_list, result_str, elem_tostr, get_bold_location):
  offset = 0
  if curr_index >= height:
    offset = curr_index - height + 1
  results_win.clear()
  results_win.addstr(0, 0, result_str)
  results_win.refresh()
  window.clear()
  if len(curr_list) > 0:
    for j in range(min(len(curr_list)-offset, height)):
      elem_str = elem_tostr(curr_list[j + offset])
      window.addstr(j, 0, elem_str[:width-1])
      bld_start = get_bold_location(elem_str, curr_str)
      if bld_start < width:
        window.chgat(j, bld_start, min(len(curr_str), width-bld_start-1), curses.A_BOLD)
    window.chgat(curr_index-offset, 0, width, curses.A_STANDOUT)
    elem_str = elem_tostr(curr_list[curr_index])
    bld_start = get_bold_location(elem_str, curr_str)
    if bld_start < width:
      window.chgat(curr_index-offset, bld_start, min(len(curr_str), width-bld_start-1), curses.A_STANDOUT | curses.A_BOLD)
  else:
    # element not in the list
    window.addstr(0, 0, curr_str[:width-1], curses.A_BOLD)
  window.refresh()


def get_bold_start(addrstr, substr):
  if addrstr.startswith(substr):
    return 0
  else:
    return addrstr.index("<")


# return a list of recipient pairs [name, addr]
# Choose from the list of recip_pairs, or the whole address book if it is None.
# Do not allow choosing from already_recip_pairs.
def get_recips(window, addr_book, recip_pairs=None, already_recip_pairs=None, allow_new=True):
  # recips is a list of (count_pair, str, name_pair)
  # where str is the display version of name and email_addr
  # and count_pair is negated (so that sorting ascending gives highest count first)
  if recip_pairs is None:
    if already_recip_pairs is None:
      recips = [((-cnt[0], -cnt[1]), addr.pair_to_str(*pr), pr) for pr,cnt in addr_book.pair_to_count.items()]
    else:
      recips = [((-cnt[0], -cnt[1]), addr.pair_to_str(*pr), pr) for pr,cnt in addr_book.pair_to_count.items() if pr not in already_recip_pairs]
    # TODO: aliases!

  else: # given a list of recip_pairs
    if already_recip_pairs is None:
      recips = [((0, 0), addr.pair_to_str(*r), r) for r in recip_pairs]
    else:                
      recips = [((0, 0), addr.pair_to_str(*r), r) for r in recip_pairs if r not in already_recip_pairs]

  if len(recips) == 0:
    return []

  instr = [
    "New recipients must be either:",
    "    Person Possibly-Full Name <email@addr.domain>",
    "    email@addr.domain"]
  window, results_win, height, width = draw_list_top_and_instr(window, instr)

  result_pairs = []

  # sort by send count, then receive count, then alphabetically
  recips.sort()
  eligible_cips = recips    # will narrow to exclude those already-entered
  curr_cips = eligible_cips
  curr_str = ""
  curr_index = 0
  while True:
    results_str = ", ".join([addr.pair_to_str(*r) for r in result_pairs])
    draw_list(curr_index, height, width, results_win, window, curr_str, curr_cips, results_str, lambda cip: cip[1], get_bold_start)

    # read input and react
#    key = window.getkey()
    key = window.getkey() #curses.keyname(ch).decode("utf-8")
    code = get_decoded(key)
    if key in ["\n", "\t"]:
      if len(curr_cips) == 0:
        if allow_new and len(curr_str) > 0:
          result_pairs.append(addr.str_to_pair(curr_str))
      else:
        result_pairs.append(curr_cips[curr_index][2])
      if key == "\n":
        break
      # reset, get next recipient
      curr_str = ""
      eligible_cips = [r for r in recips if r[2] not in result_pairs]
      curr_cips = eligible_cips
      curr_index = 0
    elif key == "KEY_ESC" or code == "^[":
      window.nodelay(True)    # a hack needed to detect ESC
      newch = window.getch()
      window.nodelay(False)
      if newch == -1: # it was ESC
        break
    elif len(key) <= 1 and code == "^X":
      return None
    elif key == "KEY_BACKSPACE" or key == "KEY_DELETE" or code == "^?":
      if len(curr_str) > 0:
        curr_str = curr_str[:-1]
        if curr_index > 0:
          prev_entry = curr_cips[curr_index]
        # keep a recip if curr_str is a prefix of either the long str or the email addr
        curr_cips = [r for r in eligible_cips if r[1].startswith(curr_str) or r[2][1].startswith(curr_str)]
        if curr_index > 0:
          curr_index = curr_cips.index(prev_entry)
    elif key == "KEY_UP":#ch == curses.KEY_UP:
      if curr_index > 0:
        curr_index -= 1
    elif key == "KEY_DOWN":#ch == curses.KEY_DOWN:
      if curr_index < len(curr_poss) - 1:
        curr_index += 1
    else:
      try:
        new_str = curr_str + key
        if not allow_new and itertools.none(new_str in cip[1] for cip in eligible_cips):
          continue
        curr_str = new_str
        if len(curr_cips) > 0:
          prev_highlight = curr_cips[curr_index]
        curr_cips = [r for r in curr_cips if r[1].startswith(curr_str) or r[2][1].startswith(curr_str)]
        if len(curr_cips) > 0 and prev_highlight in curr_cips:
          curr_index = curr_cips.index(prev_highlight)
        else:
          curr_index = 0
      except ValueError:
        pass
   
  addr_book.check_for_new(result_pairs)
  return result_pairs




# given a path, get a list of pairs (file, is_directory)
# for everything in the same directory and starting with path
def get_curr_poss(s):
    try:
      curr_dir = os.path.dirname(s)
      if curr_dir[-1] != "/":
        curr_dir += "/"
      res = []
      if curr_dir == s:
        res.append((s, True))
      for f in os.listdir(curr_dir):
        full = curr_dir + f
        if full.startswith(s):
          is_dir = os.path.isdir(full)
          res.append((full + "/" if is_dir else full, is_dir))
      res.sort()
      return res
    except:
      return []


# Global variable
most_recent_path = "/"

def get_path(window, mail_mgr):
  curr_str = most_recent_path
  
  instr_lines = [
    "Type or use up/down arrows.",
    "TAB: auto-complete.",
    "ENTER: accept current line and continue.",
    "ESC: cancel current line and return.",
    "Ctrl-x: cancel entire process."]
  window, results_win, height, width = draw_list_top_and_instr(window, instr_lines)

  curr_poss = get_curr_poss(curr_str)
  if len(curr_poss) == 0:
    curr_str = "/"
    curr_poss = get_curr_poss(curr_str)

  results = []
  curr_index = 0
  while True:
    draw_list(curr_index, height, width, results_win, window, curr_str, [p[0] for p in curr_poss], ", ".join(results), lambda s: s, lambda a,b: 0)
    key = window.getkey()
    code = get_decoded(key)
    if key in ["\n", "\t"]:
      if (key == "\n" or (len(curr_poss) == 1 and curr_str == curr_poss[curr_index][0])) and not curr_poss[curr_index][1]:
        # "autocomplete"
        results.append(curr_poss[curr_index][0])
      elif key == "\t":
        curr_str = os.path.commonprefix([p[0] for p in curr_poss])
        curr_poss = get_curr_poss(curr_str)
        cursor_ind = 0
        display_ind = 0
        continue
        ## autocomplete up to the next slash or end of current item
        ## then continue editing loop
        #try:
        #  i = curr_list[curr_index].index("/", len(curr_str))
        #  curr_str = curr_list[curr_index][:i] + "/"
        #except ValueError:
        #  curr_str = curr_list[curr_index] + "/"
        #continue
      # we just added a new result, continue
      curr_poss = get_curr_poss(os.path.dirname(curr_str))
      curr_str = curr_poss[0][0]
      curr_index = 0
    elif key == "KEY_ESC" or code == "^[":
      window.nodelay(True)    # a hack needed to detect ESC
      newch = window.getch()
      window.nodelay(False)
      if newch == -1: # it was ESC
        break
    elif len(key) <= 1 and code == "^X":
      return None
    elif key == "KEY_BACKSPACE" or key == "KEY_DELETE" or code == "^?":
      if len(curr_str) > 0:
        curr_str = curr_str[:-1]
        if curr_index > 0:
          prev_highlight = curr_poss[curr_index][0]
        curr_poss = get_curr_poss(curr_str)
        if curr_index > 0:
          strlist = [p[0] for p in curr_poss]
          curr_index = strlist.index(prev_highlight)
    elif key == "KEY_UP":#ch == curses.KEY_UP:
      if curr_index > 0:
        curr_index -= 1
    elif key == "KEY_DOWN":#ch == curses.KEY_DOWN:
      if curr_index < len(curr_poss) - 1:
        curr_index += 1
    else:
      try:
        if not any([p[0].startswith(curr_str + key) for p in curr_poss]):
          continue
        curr_str += key
        prev_highlight = curr_poss[curr_index][0] if len(curr_poss) > 0 else ""
        curr_poss = get_curr_poss(curr_str)
        strlist = [p[0] for p in curr_poss]
        if len(curr_poss) > 0 and prev_highlight in strlist:
          curr_index = strlist.index(prev_highlight)
        else:
          curr_index = 0
      except ValueError:
        pass
  return results



# returns None if cancelled, else a list of elements
# each selected from mainlist
# (or newly entered, if allow_new)
def get_sublist_from_list(window, mainlist, instr_lines, allow_new=True, taboo_chars=[]):
  instr_lines = instr_lines + LIST_INSTR_LINES
  window, results_win, height, width = draw_list_top_and_instr(window, instr_lines)

  results = []
  curr_str = ""
  curr_index = 0
  eligible_list = mainlist
  curr_list = mainlist
  while True:
    draw_list(curr_index, height, width, results_win, window, curr_str, curr_list, ", ".join(results), lambda s: s, lambda a,b: 0)
    key = window.getkey()
    code = get_decoded(key)
    if key in taboo_chars:
      continue
    elif key in ["\n", "\t"]:
      if len(curr_list) == 0:
        if allow_new and len(curr_str) > 0:
          results.append(curr_str[:-1] if curr_str[-1] == "/" else curr_str)
      elif key == "\n" or (len(curr_list) == 1 and curr_str == curr_list[curr_index]):
        # "autocomplete"
        results.append(curr_list[curr_index])
      elif key == "\t":
        # autocomplete up to the next slash or end of current item
        # then continue editing loop
        try:
          i = curr_list[curr_index].index("/", len(curr_str))
          curr_str = curr_list[curr_index][:i] + "/"
        except ValueError:
          curr_str = curr_list[curr_index] + "/"
        continue
      # we just added a new result, continue
      curr_str = ""
      eligible_list = [t for t in mainlist if t not in results]
      curr_list = eligible_list
      curr_index = 0
    elif key == "KEY_ESC" or code == "^[":
      window.nodelay(True)    # a hack needed to detect ESC
      newch = window.getch()
      window.nodelay(False)
      if newch == -1: # it was ESC
        break
    elif len(key) <= 1 and code == "^X":
      return None
    elif key == "KEY_BACKSPACE" or key == "KEY_DELETE" or code == "^?":
      if len(curr_str) > 0:
        curr_str = curr_str[:-1]
        if curr_index > 0:
          prev_highlight = curr_list[curr_index]
        curr_list = [s for s in eligible_list if s.startswith(curr_str)]
        if curr_index > 0:
          curr_index = curr_list.index(prev_highlight)
    elif key == "KEY_UP":#ch == curses.KEY_UP:
      if curr_index > 0:
        curr_index -= 1
    elif key == "KEY_DOWN":#ch == curses.KEY_DOWN:
      if curr_index < len(curr_list) - 1:
        curr_index += 1
    else:
      try:
        if not allow_new and not any([e.startswith(curr_str + key) for e in eligible_list]):
          continue
        curr_str += key
        prev_highlight = curr_list[curr_index] if len(curr_list) > 0 else ""
        curr_list = [s for s in curr_list if s.startswith(curr_str)]
        if len(curr_list) > 0 and prev_highlight in curr_list:
          curr_index = curr_list.index(prev_highlight)
        else:
          curr_index = 0
      except ValueError:
        pass
  return results


def build_disp_list(curr_list, curr_str):
  # only display "first level", i.e. if we have dirname, then skip dirname/subname, etc.
  # UNLESS curr_str is that level (i.e. we are only getting subfolders of that level)
  disp_list = []
  for l in curr_list:
    if len(disp_list) > 0 and l.startswith(disp_list[-1]) and disp_list[-1] != curr_str:
      continue  # don't display this one
    disp_list.append(l)
  return disp_list


# returns None if cancelled, else a list of tags
# selected from taglist
# (or newly entered, if allow_new)
# This is a customized version of get_sublist_from_list
def get_tags(window, taglist, allow_new=True):
  instr_lines = [
    "Type to narrow list or create new; navigate with up/down arrows.",
    "Tab: auto-complete.",
    "Space: accept current line and move to next item.",
    "Enter: accept current line and return list.",
    "Escape: cancel current line and return list.",
    "Ctrl-x: cancel entire process."]

  mainlist = [t + "/" for t in taglist]
  taboo_chars = [","]
  window, results_win, height, width = draw_list_top_and_instr(window, instr_lines)

  results = []
  curr_str = ""
  curr_index = 0
  eligible_list = mainlist
  curr_list = mainlist
  disp_list = build_disp_list(curr_list, curr_str)
  while True:
    draw_list(curr_index, height, width, results_win, window, curr_str, disp_list, ", ".join(results), lambda s: s, lambda a,b: 0)
    key = window.getkey()
    code = get_decoded(key)
    if key in taboo_chars:
      pass
    elif key in ["\n", " "]:
      # add new entry to results
      if len(disp_list) == 0:
        if allow_new and len(curr_str) > 0:
          results.append(curr_str[:-1] if curr_str[-1] == "/" else curr_str)
      else:
        # use current line, but without trailing "/"
        results.append(disp_list[curr_index][:-1])
      if key == "\n":
        break
      # we just added a new result, continue
      curr_str = ""
      eligible_list = [t for t in mainlist if t not in results]
      curr_list = eligible_list
      disp_list = build_disp_list(curr_list, curr_str)
      curr_index = 0
    elif key == "\t":
      # autocomplete up to the next slash or end of current item
      try:
        if len(disp_list) > 0:
          i = disp_list[curr_index].index("/", len(curr_str))
          curr_str = disp_list[curr_index][:i] + "/"
      except:
        curr_str = disp_list[curr_index]
      prev_highlight = disp_list[curr_index] if len(disp_list) > 0 else ""
      curr_list = [s for s in curr_list if s.startswith(curr_str)]
      disp_list = build_disp_list(curr_list, curr_str)
      if len(disp_list) > 0 and prev_highlight in disp_list:
        curr_index = disp_list.index(prev_highlight)
      else:
        curr_index = 0
    elif key == "KEY_ESC" or code == "^[":
      window.nodelay(True)    # a hack needed to detect ESC
      newch = window.getch()
      window.nodelay(False)
      if newch == -1: # it was ESC
        break
    elif len(key) <= 1 and code == "^X":
      return None
    elif key == "KEY_BACKSPACE" or key == "KEY_DELETE" or code == "^?":
      if len(curr_str) > 0:
        curr_str = curr_str[:-1]
        if curr_index > 0:
          prev_highlight = disp_list[curr_index]
        curr_list = [s for s in eligible_list if s.startswith(curr_str)]
        disp_list = build_disp_list(curr_list, curr_str)
        if curr_index > 0:
          curr_index = disp_list.index(prev_highlight)
    elif key == "KEY_UP":#ch == curses.KEY_UP:
      if curr_index > 0:
        curr_index -= 1
    elif key == "KEY_DOWN":#ch == curses.KEY_DOWN:
      if curr_index < len(disp_list) - 1:
        curr_index += 1
    else:
      try:
        if not allow_new and not any([e.startswith(curr_str + key) for e in eligible_list]):
          continue
        curr_str += key
        prev_highlight = disp_list[curr_index] if len(disp_list) > 0 else ""
        curr_list = [s for s in curr_list if s.startswith(curr_str)]
        disp_list = build_disp_list(curr_list, curr_str)
        if len(disp_list) > 0 and prev_highlight in disp_list:
          curr_index = disp_list.index(prev_highlight)
        else:
          curr_index = 0
      except ValueError:
        pass
  return results


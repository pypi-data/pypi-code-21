####
# bomail.guistuff.display
#
# Displaying various stuff on screen.
####

import sys
import time
import curses
import curses.textpad
import subprocess
import runpy
import tempfile
import os
import re
import time
import textwrap, dateutil.parser, time
from dateutil import tz

import bomail.config.config as config
import bomail.config.guiconfig as guicfg
import bomail.cli.chstate as chstate
import bomail.cli.mailfile as mailfile
import bomail.cli.compose as compose
import bomail.cli.search as search
import bomail.util.addr as addr
import bomail.util.tags as tags
import bomail.util.search_opts as search_opts


ldur_chars = guicfg.LEFT_KEY + guicfg.DOWN_KEY + guicfg.UP_KEY + guicfg.RIGHT_KEY
way_ldur_chars = guicfg.WAY_LEFT_KEY + guicfg.WAY_DOWN_KEY + guicfg.WAY_UP_KEY + guicfg.WAY_RIGHT_KEY
page_options = "  page left/down/up/right"
if guicfg.arrowkey_nav:
  ldur_chars = "←↓↑→" 
  way_ldur_chars = "Shf↔"  # shift+arrows
  page_options = "  page left/right"


ldur_str  = ldur_chars + "  left/down/up/right"
page_str  = way_ldur_chars + page_options
quit_str  = guicfg.QUIT_KEY + "  quit"
tab_str1  = guicfg.TAB_LEFT_KEY + guicfg.TAB_RIGHT_KEY + "  go tab left/right"
tab_str2  = guicfg.MOVE_TAB_LEFT_KEY + guicfg.MOVE_TAB_RIGHT_KEY + "  shift tab left/right"
tab_str3  = guicfg.EDIT_TAB_KEY + guicfg.ADD_TAB_KEY + guicfg.REMOVE_TAB_KEY + "  edit/add/remove tab"
state_str = guicfg.OPEN_KEY + guicfg.CLOSE_KEY + guicfg.SCHEDULE_KEY + guicfg.TRASH_KEY + "  open/close/schedule/trash"
tags_str  = guicfg.ADD_TAGS_KEY + guicfg.REMOVE_TAGS_KEY + "  add/delete tags"
undo_str  = guicfg.UNDO_KEY + guicfg.REDO_KEY + "  undo/redo"
get_str   = guicfg.GET_KEY + "  get updates"
write_str = guicfg.WRITE_KEY + "  write"
send_str  = guicfg.SEND_KEY + "  send"
view_str  = guicfg.VIEW_KEY + "  view"
mark_str  = guicfg.MARK_KEY + guicfg.MARK_ALL_KEY + "  mark/all"
TAB_MSG_INSTR_STR = [
    ldur_str         + "  "        + ""    + page_str  + "    "                     + " "  + undo_str + "             " + quit_str,
    "  "  + tab_str1 + "   "       + "  "  + tab_str2  + "       "                + ""   + tab_str3 + "  "            + mark_str,
    "   " + get_str  + "         " + "   " + write_str + "                      " + "  " + send_str,
    "  "  + tags_str + "     "     + ""    + state_str + "  "                     + "  " + view_str]

TOPLINES = 3
BOTTOMLINES = 7


#--------------------------------------------------------------
# drawing to screen

# write the array of msg_lines to screen,
# then set all the attributes for each (y, x, width, attr) in attr_data
def write_lines(window, y_min, y_max, y_start, x_start, msg_lines, attr_data):
  h,w = window.getmaxyx()
  for j,line in enumerate(msg_lines):
    if y_start + j >= y_min and y_start + j < y_max:
      try:
        window.insstr(y_start+j, x_start, line.encode("utf-8"))
      except:  # length problem?
        window.insstr(y_start+j, x_start, line[:w])
  for y,x,width,attr in attr_data:
    if y_start + y >= y_min and y_start + y < y_max:
      window.chgat(y_start+y, x_start+x, width, attr)


def draw_loading_screen(gui):
  height, width = gui.screen.getmaxyx()
  gui.screen.clear()
  gui.screen.refresh()  # this needs to be here, no idea why
  toptabs = "[1]"
  gui.screen.addstr(0, 0, toptabs, gui.attr)
  gui.screen.addstr(2, 0, "-"*curses.COLS, gui.attr)
  gui.screen.chgat(0, 0, 3, curses.A_STANDOUT | gui.attr)
  gui.screen.hline(height-BOTTOMLINES, 0, "-", width, gui.attr)
  gui.screen.hline(height-BOTTOMLINES+2, 0, "-", width, gui.attr)
  redraw_note(gui, "Loading (please wait)...")
  

# mode is all, tab, or note
def redraw(gui, mode, note=""):
  if mode == "all":
    redraw_overlay(gui)
  # note this is not an elif
  if mode in ["all", "tab"]:
    redraw_tab(gui)
  note = mod_note(gui, note)
  redraw_note(gui, note)  # refreshes screen


# top lines
def redraw_overlay(gui):
  height, width = gui.screen.getmaxyx()
  gui.screen.clear()
  gui.screen.refresh()  # this needs to be here, no idea why
  toptabs = "[1]  [2]  [3]  [4]  [5]  [6]  [7]  [8]  [9]  [0]"
  if len(gui.tabs) <= 10:
    len_tt = len(gui.tabs)*5 - 2
    toptabs = toptabs[:len_tt]
  else:
    toptabs = toptabs + "  [ ]" * (len(gui.tabs) - 10)
  gui.screen.addstr(0, 0, toptabs[:width], gui.attr)
  gui.screen.addstr(1, 0, gui.tabs[gui.tab_ind].search_str, gui.attr)
  gui.screen.addstr(2, 0, "-"*curses.COLS, gui.attr)
  if 5*gui.tab_ind + 3 <= width:
    gui.screen.chgat(0, 5*gui.tab_ind, 3, curses.A_STANDOUT | gui.attr)  # highlight tab number
  gui.screen.hline(height-BOTTOMLINES, 0, "-", width, gui.attr)
  gui.screen.hline(height-BOTTOMLINES+2, 0, "-", width, gui.attr)


# tab section and commands
def redraw_tab(gui):
  gui.tab_area.clear()
  tab = gui.tabs[gui.tab_ind]
  if not tab.is_loaded:
    tab.load()
    redraw_overlay(gui)
  if guicfg.threads_on:
    if tab.mode == "thread list":
      redraw_tab_msg(tab, gui)
    elif guicfg.thread_view == "tree":
      redraw_tab_tree(tab.file_data[tab.cursor_ind][0], gui)
    else:
      redraw_tab_lin(tab.file_data[tab.cursor_ind][0], gui)
  else:
    redraw_tab_msg(tab, gui)


# choose refresh_display=False to just draw the messages
# and get the y-coordinates without refreshing the screen yet
def redraw_tab_msg(mytab, gui, refresh_display=True):
  height,screen_width = gui.tab_area.getmaxyx()

  # draw messages, updating msg_ys and num_displayed
  i = mytab.display_ind
  mytab.num_displayed = 0
  curr_y = 0
  while curr_y < height and i < len(mytab.file_data):
    display_data, is_unread, is_marked = mytab.get_display_data(i)
    mytab.file_data[i][2][0] = curr_y  # set its y-coordinate
    mytab.num_displayed += 1
    msg_lines = display_data[1]
    orig_attr_data = display_data[2] 
    attr_data = list(orig_attr_data)
    if is_unread:
      attr_data = [(y, x, w, a | curses.A_BOLD if y==0 else a) for y,x,w,a in attr_data]
    if i == mytab.cursor_ind:
      # highlight the first line
      attr_data = [(y, x, w, a | guicfg.cursor_attr if y==0 else a) for y,x,w,a in attr_data]
    write_lines(gui.tab_area, 0, height, curr_y, 0, msg_lines, attr_data)
    if is_marked:
      attr = curses.A_BOLD | gui.attr
      if i == mytab.cursor_ind:
        attr |= guicfg.cursor_attr
      gui.tab_area.addstr(curr_y, screen_width - 2, "X", attr)

    curr_y += len(msg_lines)
    i += 1

  if refresh_display:
    gui.tab_area.refresh()
    draw_bottom_text(gui, TAB_MSG_INSTR_STR)


def redraw_tab_lin(thread_view, gui):
  thread_view.ensure_display_loaded()
  height, screen_width = gui.tab_area.getmaxyx()

  # can assume we have > 0 files
  subj_str = gui.mail_mgr.get(thread_view.repr_file, mailfile.SUBJ_L)[:screen_width]
  try:
    gui.tab_area.addstr(0, 0, subj_str.encode("uft-8"), curses.A_BOLD)
  except:
    gui.tab_area.addstr(0, 0, subj_str, curses.A_BOLD)
  gui.tab_area.hline(1, 0, "-", screen_width)
  offset = 2

  curr_y = thread_view.top_y_coord + offset
  for ind,tup in enumerate(thread_view.file_data):
    if tup[2]:  # is collapsed
      msg_lines, orig_attr_data = tup[3]  # collapsed disp_data
    else:
      msg_lines, orig_attr_data = tup[4]  # expanded disp data
    attr_data = list(orig_attr_data)
    if tup[0] in gui.unread_set:  # is_unread
      attr_data = [(y, x, w, a | curses.A_BOLD if y==0 else a) for y,x,w,a in attr_data]
    if ind == thread_view.cursor_ind:
      attr_data = [(y,x,screen_width,(attr if y>0 else attr|guicfg.cursor_attr)) for y,x,screen_width,attr in attr_data]
    write_lines(gui.tab_area, offset, height, curr_y, 0, msg_lines, attr_data)
    if curr_y >= 0 and curr_y < height and tup[1]:  # is marked
      attr = curses.A_BOLD | gui.attr
      if ind == thread_view.cursor_ind:
        attr |= guicfg.cursor_attr
      gui.tab_area.addch(curr_y, screen_width - 2, "X", attr)
    if curr_y-1 >= 0 and curr_y+1 < height and tup[2]:  # collapsed
      gui.tab_area.addstr(curr_y+1, 1, "<--")

    curr_y += len(msg_lines)

  gui.tab_area.refresh()
  draw_bottom_text(gui, TAB_MSG_INSTR_STR)


# TODO - implement!
def redraw_tab_tree(thread_view, gui):
  return redraw_tab_lin(thread_view, gui)


def draw_bottom_text(gui, lines):
  height, width = gui.commands_area.getmaxyx()
  gui.commands_area.clear()
  for i,line in enumerate(lines):
    if i >= height:
      break
    gui.commands_area.addstr(i, 0, lines[i][:width-1], gui.attr)
  gui.commands_area.refresh()


# add "message x of y" to end of note
# return new note
def mod_note(gui, note):
  mytab = gui.tabs[gui.tab_ind]
  if guicfg.threads_on:
    if mytab.mode == "thread list":
      num_msgs = len(mytab.file_data)
      ind = mytab.cursor_ind
      count_note = "No threads" if num_msgs == 0 else "Thread " + str(ind+1) + " of " + str(num_msgs)
    elif mytab.mode == "one thread":
      num_msgs = len(mytab.file_data[mytab.cursor_ind][0].all_files)
      ind = mytab.file_data[mytab.cursor_ind][0].cursor_ind
      count_note = "No messages" if num_msgs == 0 else "Message " + str(ind+1) + " of " + str(num_msgs)
  else:
    num_msgs = len(mytab.file_data)
    ind = mytab.cursor_ind
    count_note = "No messages" if num_msgs == 0 else "Message " + str(ind+1) + " of " + str(num_msgs)
  height, width = gui.screen.getmaxyx()
  gap = width - (len(note) + len(count_note) + 4)
  if gap >= 0:
    note += " "*(gap + 3) + count_note
  return note


def redraw_note(gui, note):
  height, width = gui.note_area.getmaxyx()
  gui.note_area.clear()
  gui.note_area.addstr(0, 0, note[:width-1], gui.attr)
  gui.note_area.refresh()
  gui.screen.refresh()


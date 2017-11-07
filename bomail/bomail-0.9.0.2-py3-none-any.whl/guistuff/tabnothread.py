####
# bomail.guistuff.tabnothread
#
# Tabs when configuration turns off threading, i.e.
# each email gets its own line.
####

import os
import sys
import subprocess
import curses
import shlex
import functools

import bomail.config.config as config
import bomail.config.guiconfig as guicfg

import bomail.cli.mailfile as mailfile
import bomail.cli.search as search
import bomail.cli.chstate as chstate
import bomail.cli.send as send
import bomail.cli.compose as compose

import bomail.util.addr as addr
import bomail.util.util as util

import bomail.guistuff.display as display
import bomail.guistuff.display_fmt as display_fmt
import bomail.guistuff.gui_util as gui_util


class TabNoThread:
  def __init__(self, search_str, gui):
    self.search_str = search_str
    self.gui = gui
    self.is_loaded = False
    self.cursor_ind = 0
    self.display_ind = 0
    self.num_marked = 0
    self.num_displayed = 0

    # list of lists (filename, is_marked, display_data)
    # where display_data is either None or (y_coord, lines_to_display, attr_data)
    self.file_data = []

    # for sorting filenames and tuples
    self.sort_new = not "-sortold" in shlex.split(self.search_str)
    self.file_key = lambda a: self.gui.mail_mgr.get(a, mailfile.DATE_L)
    self.tup_key  = lambda t: self.file_key(t[0])


  # get all the filenames matching our search_str
  def load(self):
    display.draw_loading_screen(self.gui)
    filenames = search.main_argstr(self.search_str, self.gui.mail_mgr)
    self.cursor_ind = 0
    self.display_ind = 0
    self.num_marked = 0
    self.num_displayed = 0
    self.file_data = [[f, False, None] for f in filenames]
    self.file_data.sort(key=self.tup_key, reverse=self.sort_new)
    self.is_loaded = True


  # like load, but try to keep all current settings if possible
  # all possibly-important files are: those currently in our list and those matching our search string
  def recheck(self, old_disp_info):
    if not self.is_loaded:
      return
    display.draw_loading_screen(self.gui)
    new_filenames = search.main_argstr(self.search_str, self.gui.mail_mgr)
    new_fileset = set(new_filenames)
    self.remove_files([t[0] for t in self.file_data if t[0] not in new_fileset], old_disp_info)
    # assume, worst-case, that all matching files have changed/added
    self.update_for_change(new_fileset, old_disp_info)

 
  # lazily load display data and return disp_data, is_unread, is_marked
  # where disp_data = (msg_y, lines, attr_data)
  # implements memo-ization: the data is None until requested, then is loaded
  def get_display_data(self, ind):
    if self.file_data[ind][2] is None:
      height, width = self.gui.tab_area.getmaxyx()
      lines, attr_data = display_fmt.get_msg_lines_nothread(self.gui.mail_mgr, self.file_data[ind][0], width)
      self.file_data[ind][2] = [0, lines, attr_data]
    is_unread = self.file_data[ind][0] in self.gui.unread_set
    is_marked = self.file_data[ind][1]
    return self.file_data[ind][2], is_unread, is_marked


  # get these two values
  def get_old_display_info(self):
    if not self.is_loaded:
      return (None, 0)
    old_cursor_key = None if len(self.file_data) == 0 else self.tup_key(self.file_data[self.cursor_ind])
    old_display_ind = self.display_ind
    return (old_cursor_key, old_display_ind)

  # re-set display and cursor indices and display data
  def update_display(self, disp_info):
    old_cursor_key, old_display_ind = disp_info
    self.cursor_ind = 0
    self.display_ind = old_display_ind
    if old_cursor_key is not None:
      self.cursor_ind = util.bisect_left_key(self.file_data, old_cursor_key, key=self.tup_key, reverse=self.sort_new)
    display.redraw_tab_msg(self, self.gui, refresh_display=False)  # set msg_ys
    self.scroll_up(amt=0)    # if cursor and display ind are too far apart, fix them
    self.scroll_down(amt=0)


  # update this view based on the fact that these new files have been added
  # to the database
  def update_for_add(self, add_list, old_disp_info):
    if not self.is_loaded or len(add_list) == 0:
      return
    add_match_list = search.main_argstr(self.search_str, self.gui.mail_mgr, filelist=add_list)
    if len(add_match_list) == 0:
      return
    add_tup_list = [[f, False, None] for f in add_match_list]
    add_tup_list.sort(key=self.tup_key, reverse=self.sort_new)
    self.file_data = util.merge_lists(self.file_data, add_tup_list, key=self.tup_key, reverse=self.sort_new)
    # num_marked does not need to change
    self.update_display(old_disp_info)


  # make it so that none of these files are in our view any more
  # do NOT ask mail_mgr for data of rm_list; they may not exist anymore!
  def remove_files(self, rm_list, old_disp_info):
    if not self.is_loaded or len(rm_list) == 0:
      return
    rm_set = set(rm_list)
    self.file_data = [t for t in self.file_data if t[0] not in rm_set]
    self.num_marked = sum([1 if t[1] else 0 for t in self.file_data])
    self.update_display(old_disp_info)


  # these files were deleted
  def update_for_trash(self, trash_list, data_list, old_disp_info):
    self.remove_files(trash_list, old_disp_info)


  # update based on the fact that these files have changed, or possibly
  # have been added
  def update_for_change(self, ch_list, old_disp_info):
    if not self.is_loaded or len(ch_list) == 0:
      return
    ch_set = set(ch_list)
    ch_match_set = set(search.main_argstr(self.search_str, self.gui.mail_mgr, filelist=ch_list))
    new_file_data = []
    changed_present_set = set()
    for tup in self.file_data:
      if tup[0] in ch_match_set:
        # present and matched: reset display data
        new_file_data.append([tup[0], tup[1], None])
        changed_present_set.add(tup[0])
      elif tup[0] not in ch_set:
        # present but not changed: keep
        new_file_data.append(tup)
      # else, present, but not matched: remove
    self.file_data = new_file_data
    # add all matched, but not previously present
    add_file_list = list(ch_match_set.difference(changed_present_set))
    add_tup_list = [[f, False, None] for f in add_file_list]
    add_tup_list.sort(key=self.tup_key, reverse=self.sort_new)
    self.file_data = util.merge_lists(self.file_data, add_tup_list, key=self.tup_key, reverse=self.sort_new)
    self.num_marked = sum([1 if t[1] else 0 for t in self.file_data])
    self.update_display(old_disp_info)


  # return all filenames to be affected by the current action
  def get_curr_filenames(self):
    if not self.is_loaded:
      self.load()
    if len(self.file_data) == 0:
      return []
    elif self.num_marked == 0:
      return [self.file_data[self.cursor_ind][0]]
    else:
      return [t[0] for t in self.file_data if t[1]]  # marked


  def scroll_up(self, amt=1):
    self.cursor_ind -= amt
    if self.cursor_ind < 0:
      self.cursor_ind = 0
    if self.display_ind > self.cursor_ind:
      self.display_ind = self.cursor_ind

  def scroll_down(self, amt=1):
    self.cursor_ind += amt
    if self.cursor_ind >= len(self.file_data):
      self.cursor_ind = len(self.file_data) - 1
    if self.cursor_ind >= self.display_ind + self.num_displayed:
      self.display_ind = self.cursor_ind - int(self.num_displayed / 2)

  def scroll_down_page(self):
    self.scroll_down(self.display_ind + self.num_displayed - self.cursor_ind)

  # attempt to scroll up until the previous cursor message leaves the screen
  def scroll_up_page(self):
    old_cursor_ind = self.cursor_ind
    while self.cursor_ind > 0:
      self.cursor_ind -= 1
      display.redraw_tab_msg(self, self.gui, refresh_display=False)  # set msg_ys
      if self.cursor_ind + self.num_displayed <= old_cursor_ind:
        break
    self.display_ind = self.cursor_ind


  # return mode, note
  def process_key(self, key):
    if not self.is_loaded:
      self.load()
    mode, note = "all", ""
    curr_filelist = self.get_curr_filenames()
    
    # if no files, only allowable action is new draft
    if len(curr_filelist) == 0:
      if key == guicfg.WRITE_KEY:
        return gui_util.go_compose_draft(self.gui, "n", None)  # new blank draft
      return "note", "Key not recognized / nothing to do"

    # Now assume len(curr_filelist) > 0

    # changing state
    if key == guicfg.OPEN_KEY:
      mode, note = self.gui.acts.do(("open", curr_filelist, [self.gui.mail_mgr.get(f, mailfile.STATE_L) for f in curr_filelist]))
    elif key == guicfg.CLOSE_KEY:
      mode, note = self.gui.acts.do(("closed", curr_filelist, [self.gui.mail_mgr.get(f, mailfile.STATE_L) for f in curr_filelist]))
    elif key == guicfg.SCHEDULE_KEY:
      mode, note = gui_util.go_schedule(self.gui, curr_filelist)
    elif key == guicfg.TRASH_KEY:
      mode, note = self.gui.acts.do(("trash", curr_filelist, [self.gui.mail_mgr.get_all(f) for f in curr_filelist]))

    # tags
    elif key == guicfg.ADD_TAGS_KEY:
      mode, note = gui_util.go_add_tags(self.gui, curr_filelist)
    elif key == guicfg.REMOVE_TAGS_KEY:
      mode, note = gui_util.go_remove_tags(self.gui, curr_filelist)

    # navgation type keys
    elif key == guicfg.DOWN_KEY:
      self.scroll_down()
      mode, note = "tab", ""
    elif key == guicfg.UP_KEY:
      self.scroll_up()
      mode, note = "tab", ""
    elif key == guicfg.WAY_DOWN_KEY:
      self.scroll_down_page()
      mode, note = "tab", ""
    elif key == guicfg.WAY_UP_KEY:
      self.scroll_up_page()
      mode, note = "tab", ""

    elif (guicfg.arrowkey_nav and key == "KEY_RIGHT") or (not guicfg.arrowkey_nav and key == guicfg.RIGHT_KEY):
      # TODO: view mode
      mode, note = "tab", ""

    # mark/unmark messages
    elif key == guicfg.MARK_KEY:
      name = display_fmt.get_shortened(self.file_data[self.cursor_ind][0], self.gui.mail_mgr)
      if self.file_data[self.cursor_ind][1]:  # is marked
        self.file_data[self.cursor_ind][1] = False
        self.num_marked -= 1
        mode, note = "tab", "Un-marked " + name
      else:
        self.file_data[self.cursor_ind][1] = True
        self.num_marked += 1
      mode, note = "tab", "Marked " + name

    elif key == guicfg.MARK_ALL_KEY:
      if self.num_marked == len(self.file_data):  # unmark all
        for i in range(len(self.file_data)):
          self.file_data[i][1] = False
        self.num_marked = 0
        mode, note = "tab", "Marked none"
      else:
        for i in range(len(self.file_data)):
          self.file_data[i][1] = True
        self.num_marked = len(self.file_data)
        mode, note = "tab", "Marked all"

    # writing and viewing
    elif key == guicfg.WRITE_KEY:
      filename = curr_filelist[0]
      mode, note = gui_util.go_write_key(self.gui, filename)

    elif key == guicfg.VIEW_KEY:
      self.gui.mark_read([self.file_data[self.cursor_ind][0]])
      subprocess.call(guicfg.read_prog + " '" + self.file_data[self.cursor_ind][0] + "'", shell=True)
      curses.curs_set(False)
      return "all", ""

    # sending
    elif key == guicfg.SEND_KEY:
      filename = curr_filelist[0]
      if filename[-5:] == "draft":
        return gui_util.go_send(self.gui, filename)
      else:
        return "note", "Cannot send: not a draft"
    else:
      return "note", "Input key not recognized"
    return mode, note



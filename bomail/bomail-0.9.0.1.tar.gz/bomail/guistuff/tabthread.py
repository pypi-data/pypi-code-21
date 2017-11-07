####
# bomail.guistuff.tabthread
#
# Tabs when threading is turned on, i.e.
# emails are grouped into conversations.
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
import bomail.util.thread as thread

import bomail.guistuff.display as display
import bomail.guistuff.display_fmt as display_fmt
import bomail.guistuff.gui_util as gui_util

from bomail.guistuff.tabthreadview import ThreadView


class TabThread:
  def __init__(self, search_str, gui):
    self.search_str = search_str
    self.gui = gui
    self.cursor_ind = 0
    self.display_ind = 0
    self.num_marked = 0
    self.num_displayed = 0

    # list of lists, each of the form:
    #   [threadview_obj, is_marked, disp_data]
    #   where disp_data is either None or (y_coord, lines_to_display, attr_data)
    self.file_data = []

    # list of filenames in this tab
    self.filenames = []
    self.fileset = set()

    # for sorting filenames and tuples
    self.sort_new = not "-sortold" in shlex.split(self.search_str)
    self.file_key = lambda a: self.gui.mail_mgr.get(a, mailfile.DATE_L)
    self.tup_key  = lambda t: self.file_key(self.__get_repres_file_tup(t))
   
    self.is_loaded = False


  # get all the filenames matching our search_str
  def load(self, draw_loading=True, filelist=None):
    self.mode = "thread list"  # or "one thread"
    self.cursor_ind = 0
    self.display_ind = 0
    self.num_marked = 0
    self.num_displayed = 0
    if draw_loading:
      display.draw_loading_screen(self.gui)
    if filelist is None:
      self.filenames = search.main_argstr(self.search_str, self.gui.mail_mgr)
    else:
      self.filenames = filelist
      self.filenames.sort(key=self.file_key, reverse=self.sort_new)
    self.fileset = set(self.filenames)
    thread_data = self.gui.thread_mgr.get_threads_for(self.filenames, self.gui.mail_mgr)
    self.file_data = [[ThreadView(trip, self, self.gui), False, None] for trip in thread_data]
    self.file_data.sort(key=self.tup_key, reverse=self.sort_new)
    self.is_loaded = True


  # get one filename to "represent" a thread
  def __get_repres_file_tup(self, tup):
    return tup[0].repr_file

  def __get_repres_file(self, ind):
    assert(ind >= 0)
    if ind >= len(self.file_data):
      return None
    return self.__get_repres_file_tup(self.file_data[ind])

  
  # Call if we don't know what has changed, but want to try to keep all
  # current settings if possible
  # just consider files currently in our list and/or matching our search string
  def recheck(self, old_disp_info):
    if not self.is_loaded:
      return
    self.__update_all(old_disp_info)
    #display.draw_loading_screen(self.gui)
    #new_filenames = search.main_argstr(self.search_str, self.gui.mail_mgr)
    #new_fileset = set(new_filenames)
    #self.update_for_rm([f for t in self.file_data for f in t[0].all_files if f not in new_fileset], old_disp_info)
    ## assume, worst-case, that all matching files have changed
    #self.update_for_change(new_fileset, old_disp_info)

 
  # lazily load display data and return disp_data, is_unread, is_marked
  # where disp_data = (msg_y, lines, attr_data)
  def get_display_data(self, ind):
    if self.file_data[ind][2] is None:
      height, width = self.gui.tab_area.getmaxyx()
      lines, attr_data = display_fmt.get_msg_lines_thread(self.gui.mail_mgr, self.file_data[ind][0], width)
      self.file_data[ind][2] = [0, lines, attr_data]
    is_unread = any([f in self.gui.unread_set for f in self.file_data[ind][0].all_files])
    is_marked = self.file_data[ind][1]
    return self.file_data[ind][2], is_unread, is_marked


  # get info about current cursor and scrolling settings
  # return tuple (filenames_under_cursor, sort_key_of_cursor, display_index)
  def get_old_display_info(self):
    if not self.is_loaded:
      return (None, None, 0)
    elif len(self.file_data) == 0:
      return (None, None, 0)
    old_cursor_tup = self.file_data[self.cursor_ind]
    old_cursor_fnames = set(old_cursor_tup[0].all_files)
    old_cursor_key = self.tup_key(old_cursor_tup)
    old_display_ind = self.display_ind
    return (old_cursor_fnames, old_cursor_key, old_display_ind)


  # given the same tuple returned by get_old_display_info
  # but now that files are updated,
  # attempt to set the display similar to how it was
  def __update_display(self, disp_info):
    self.cursor_ind, self.display_ind = 0, 0
    if len(self.file_data) == 0:
      return

    old_cursor_fnames, old_cursor_key, old_display_ind = disp_info
    if old_cursor_key is None:
      return
    self.display_ind = old_display_ind

    found_thread = False
    for ind,tup in enumerate(self.file_data):
      for new_f in tup[0].all_files:
        if new_f in old_cursor_fnames:
          self.cursor_ind = ind
          found_thread = True
          break
    if not found_thread:
      self.cursor_ind = util.bisect_left_key(self.file_data, old_cursor_key, key=self.tup_key, reverse=self.sort_new)
      if self.cursor_ind >= len(self.file_data):
        self.cursor_ind = len(self.file_data) - 1
    display.redraw_tab_msg(self, self.gui, refresh_display=False)  # set msg_ys
    self.__scroll_up(amt=0)
    self.__scroll_down(amt=0)


  # save some info that we'll use to reload
  def __save_file_stuff(self):
    old_mode = self.mode
    old_disp_file = self.__get_repres_file(self.cursor_ind)
    oldfile_to_threaddata = {}
    for thread_data, marked, disp_data in self.file_data:
      for f in thread_data.matching_set:
        oldfile_to_threaddata[f] = thread_data
    num_old_files = len(self.file_data)
    return (old_mode, old_disp_file, oldfile_to_threaddata, num_old_files)


  # use old info to keep as much the same as possible
  # after an update to our files
  def __restore_file_stuff(self, old_tup, disp_info):
    old_mode, old_disp_file, oldfile_to_threaddata, num_old_files = old_tup
    # first, thread objects
    for i,tup in enumerate(self.file_data):
      is_new = True
      for f in tup[0].matching_set:
        if f in oldfile_to_threaddata:
          is_changed = tup[0].reuse_disp_data(oldfile_to_threaddata[f])
          if not is_changed:
            is_new = False
          break
    # second, cursor and display index
    self.__update_display(disp_info)
    # third, mode
    if old_mode == "one thread":
      new_display_file = self.__get_repres_file(self.cursor_ind)
      if old_disp_file is not None and new_display_file is not None and new_display_file == old_disp_file:
        self.mode == "one thread"


  # note our old filenames may not exist anymore!
  def __update_all(self, disp_info):
    if not self.is_loaded:
      return
    # load from scratch
    old_tup = self.__save_file_stuff()
    num_old_files = old_tup[-1]
    self.load(draw_loading = (num_old_files >= 200))  # 200 chosen via extensive user studies
    self.__restore_file_stuff(old_tup, disp_info)
        

  # update for the case these files may have changed (but still exist)
  # a more general scenario than update_for_add
  def update_for_change(self, change_list, disp_info):
    if not self.is_loaded:
      return
    match_list = search.main_argstr(self.search_str, self.gui.mail_mgr, filelist=change_list)
    add_list = []
    ch_list = []
    for f in match_list:
      if f in self.fileset:  # files previously present, changed, still present
        ch_list.append(f)
      else:  # files previously not present, changed, present
        add_list.append(f)
    # files previously present, changed, no longer present
    match_set = set(match_list)
    rm_set = set([f for f in change_list if f in self.fileset and f not in match_set])
    updated_list = [f for f in self.filenames if f not in rm_set] + add_list

    with open(config.error_log_file, "a") as f:
      f.write("Updating for change:\nCh list: " + str(ch_list) + "\nMatch list: " + str(match_list) + "\nRm set: " + str(rm_set) + "\n\n")

    old_tup = self.__save_file_stuff()
    draw_load = abs(len(updated_list) - len(self.filenames)) >= 100  # 100 chosen via UI study
    self.load(draw_loading=draw_load, filelist=updated_list)
    self.__restore_file_stuff(old_tup, disp_info)
    

  # update for new files added to system
  # they must not already be in the tab!
  def update_for_add(self, add_list, disp_info):
    if not self.is_loaded:
      return
    add_filenames = search.main_argstr(self.search_str, self.gui.mail_mgr, filelist=add_list)
    if len(add_filenames) == 0:
      return
    old_tup = self.__save_file_stuff()
    self.load(draw_loading=(len(add_filenames)>=200), filelist=self.filenames + add_filenames)
    self.__restore_file_stuff(old_tup, disp_info)
    

  # these files no longer match our search string
  # or are deleted if is_trash
  def update_for_rm(self, rm_list, disp_info, is_trash=False):
    if not self.is_loaded:
      return
    rm_set = set(rm_list)
    new_filenames = [f for f in self.filenames if f not in rm_set]
    if len(new_filenames) == len(self.filenames):
      return  # no change
    old_tup = self.__save_file_stuff()
    self.load(draw_loading=(len(new_filenames)>=200), filelist=new_filenames)
    self.__restore_file_stuff(old_tup, disp_info)


  def update_for_trash(self, trash_list, data_list, disp_info):
    self.update_for_rm(trash_list, disp_info, is_trash=True)


  # return all filenames to be affected by the current action
  def get_curr_filenames(self):
    if not self.is_loaded:
      self.load()
    if len(self.file_data) == 0:
      return []
    elif self.mode == "one thread":
      return self.file_data[self.cursor_ind][0].get_curr_filenames()
    elif self.num_marked == 0:  # cursor thread's files only
      return self.file_data[self.cursor_ind][0].all_files
    else:  # all marked threads' files
      return [f for t in self.file_data if t[1] for f in t[0].all_files]


  def __scroll_up(self, amt=1):
    self.cursor_ind -= amt
    if self.cursor_ind < 0:
      self.cursor_ind = 0
    if self.display_ind > self.cursor_ind:
      self.display_ind = self.cursor_ind

  def __scroll_down(self, amt=1):
    self.cursor_ind += amt
    if self.cursor_ind >= len(self.file_data):
      self.cursor_ind = max(0, len(self.file_data) - 1)
    if self.cursor_ind >= self.display_ind + self.num_displayed:
      self.display_ind = self.cursor_ind

  def __scroll_down_page(self):
    self.__scroll_down(self.display_ind + self.num_displayed - self.cursor_ind)

  # attempt to scroll up until the previous cursor message leaves the screen
  def __scroll_up_page(self):
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


    # Other things are treated differently if mode is one thread
    elif self.mode == "one thread":
      return self.file_data[self.cursor_ind][0].process_key(key)


    # navgation type keys
    elif key == guicfg.DOWN_KEY:
      self.__scroll_down()
      mode, note = "tab", ""
    elif key == guicfg.UP_KEY:
      self.__scroll_up()
      mode, note = "tab", ""
    elif key == guicfg.WAY_DOWN_KEY:
      self.__scroll_down_page()
      mode, note = "tab", ""
    elif key == guicfg.WAY_UP_KEY:
      self.__scroll_up_page()
      mode, note = "tab", ""

    # mark/unmark messages
    elif key == guicfg.MARK_KEY:
      name = display_fmt.get_shortened(self.file_data[self.cursor_ind][0].repr_file, self.gui.mail_mgr)
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

    elif key == guicfg.VIEW_KEY or (guicfg.arrowkey_nav and key == "KEY_RIGHT") or (not guicfg.arrowkey_nav and key == guicfg.RIGHT_KEY):
      self.mode = "one thread"
      return "all", ""

    # sending
    elif key == guicfg.SEND_KEY:
      filename = curr_filelist[0]
      if len(curr_filelist) == 1 and filename[-5:] == "draft":
        return gui_util.go_send(self.gui, filename)
      else:
        return "note", "Cannot send: not a draft"
    else:
      return "note", "Input key not recognized"
    return mode, note


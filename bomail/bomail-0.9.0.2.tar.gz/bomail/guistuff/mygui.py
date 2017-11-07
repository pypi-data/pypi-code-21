####
# bomail.guistuff.mygui
#
# The main UI object.
####

import curses
import os
import sys
import locale

import bomail.config.config as config
import bomail.config.guiconfig as guicfg

import bomail.cli.mailfile as mailfile
import bomail.cli.search as search
import bomail.cli.process as process
import bomail.cli.check_sched as check_sched

import bomail.guistuff.display as display
import bomail.guistuff.get_txt as get_txt

from bomail.util.addr import AddrBook
from bomail.util.thread import ThreadMgr
from bomail.util.tags import TagMgr
from bomail.guistuff.acts import Acts
from bomail.guistuff.tabthread import TabThread
from bomail.guistuff.tabnothread import TabNoThread


default_tab_ind = 0
default_tab_searches = [
  "-open",
  "-draft",
  "-sent",
  ""]


class Gui:
  def __init__(self, screen):
    self.init_screen(screen)

    self.mail_mgr = mailfile.MailMgr()
    self.addr_book = AddrBook()
    if guicfg.threads_on:
      self.thread_mgr = ThreadMgr()
    else:
      self.thread_mgr = None
    self.tag_mgr = TagMgr()
    self.acts = Acts(self)

    self.unread_set = set()  # unread filenames

    try:
      with open(config.tab_config_file) as f:
        s = f.read()
        namespace = {}
        exec(s, namespace)
        self.tab_ind = namespace["tab_ind"]
        tab_searches = namespace["tab_searches"]
    except:
      self.tab_ind = default_tab_ind
      tab_searches = default_tab_searches
    if guicfg.threads_on:
      self.tabs = [TabThread(s, self) for s in tab_searches]
    else:
      self.tabs = [TabNoThread(s, self) for s in tab_searches]

    self.tabs[self.tab_ind].load()  # better load initial tab now, during loading screen
    curses.flushinp()


  def init_screen(self, screen):
    self.screen = screen
    curses.curs_set(False)  # no cursor
    screen.scrollok(1)      # writing to last line/char is allowed
    curses.init_pair(guicfg.DEFAULT_CLR_PAIR, guicfg.foreground_color, guicfg.background_color)
    curses.init_pair(guicfg.BOMAIL_CLR_PAIR, guicfg.bomail_color, guicfg.background_color)
    curses.init_pair(guicfg.AUTHOR_CLR_PAIR, guicfg.author_color, guicfg.background_color)
    curses.init_pair(guicfg.TAGS_CLR_PAIR, guicfg.tags_color, guicfg.background_color)
    curses.init_pair(guicfg.THREAD_CLR_PAIR, guicfg.thread_color, guicfg.background_color)
      
    screen.keypad(True)
    
    self.attr = curses.color_pair(guicfg.BOMAIL_CLR_PAIR) | guicfg.bomail_attr
    self.screen.bkgd(" ", curses.color_pair(guicfg.BOMAIL_CLR_PAIR))
    self.tab_area = curses.newwin(curses.LINES - display.TOPLINES - display.BOTTOMLINES, curses.COLS, display.TOPLINES, 0)
    self.tab_area.bkgd(" ", curses.color_pair(guicfg.DEFAULT_CLR_PAIR))
    self.note_area = curses.newwin(1, curses.COLS, curses.LINES - display.BOTTOMLINES + 1, 0)
    self.note_area.bkgd(" ", curses.color_pair(guicfg.DEFAULT_CLR_PAIR))
    self.commands_area = curses.newwin(display.BOTTOMLINES-3, curses.COLS, curses.LINES - display.BOTTOMLINES + 3, 0)
    self.commands_area.bkgd(" ", curses.color_pair(guicfg.DEFAULT_CLR_PAIR))

    display.draw_loading_screen(self)


  def update_for_add(self, filelist, disp_infos):
    if guicfg.threads_on:
      self.thread_mgr.update_for_add(filelist, self.mail_mgr)
    for i,t in enumerate(self.tabs):
      t.update_for_add(filelist, disp_infos[i])

  def update_for_change(self, filelist, disp_infos):
    for i,t in enumerate(self.tabs):
      t.update_for_change(filelist, disp_infos[i])

  # filelist are the now-deleted filenames
  # data_list are their data (note they are no longer in mail manager!)
  def update_for_trash(self, filelist, data_list, disp_infos):
    fileset = set(filelist)
    if guicfg.threads_on:
      self.thread_mgr.update_for_trash(filelist, data_list, self.mail_mgr)
    for i,t in enumerate(self.tabs):
      t.update_for_trash(filelist, data_list, disp_infos[i])

  def rewrite_tab_searches(self):
    with open(config.tab_config_file, "w") as f:
      f.write("tab_ind = " + str(self.tab_ind) + "\n\n")
      f.write("tab_searches = [\n")
      for t in self.tabs:
        f.write("  \"" + t.search_str.replace('"','\\"') + "\",\n")
      f.write("]\n")

  def change_tab_ind(self, new_ind):
    self.tab_ind = new_ind

  def mark_read(self, filelist):
    for f in filelist:
      self.unread_set.discard(f)  # removes if present

  def mark_unread(self, filelist):
    self.unread_set.update(filelist)

  def go(self):
    keep_alive = True
    mode, note = "all", "Welcome"  # mode is all, tab, or note
    while keep_alive:
      display.redraw(self, mode, note)
      mode, note = "note", ""
      assert(all([(not t.is_loaded) or len(t.file_data) == 0 or (t.cursor_ind >= 0 and t.cursor_ind < len(t.file_data)) for t in self.tabs]))
      key = self.screen.getkey()
      keep_alive, used_key, mode, note = self.process_key(key)
      if not used_key:
        mode, note = self.tabs[self.tab_ind].process_key(key)
    # done with program; save tab settings and quit
    self.rewrite_tab_searches()
    return self.tabs[self.tab_ind].get_curr_filenames()

  # return 4 results:
  # 1) True if keep program alive, False to exit
  # 2) True if we processed the keypress, False otherwise
  # 3) if we processed, the mode to redraw
  # 4) if we processed, the note to draw
  def process_key(self, key):
    mode, note = "note", ""
    if key == guicfg.QUIT_KEY:
      return False, True, "", ""

    # tab navigation
    elif key >= "0" and key <= "9":
      key_num = int(key)
      new_ind = key_num - 1 if key_num > 0 else 9   # key "0" goes to the 10th tab
      if new_ind < len(self.tabs):
        self.change_tab_ind(new_ind)
        mode, note = "all", ""
    elif key == guicfg.TAB_LEFT_KEY:
      if self.tab_ind > 0:
        self.change_tab_ind(self.tab_ind - 1)
        mode, note = "all", ""
    elif key == guicfg.TAB_RIGHT_KEY:
      if self.tab_ind < len(self.tabs) - 1:
        self.change_tab_ind(self.tab_ind + 1)
        mode, note = "all", ""

    # editing tabs
    elif key == guicfg.EDIT_TAB_KEY:
      old_str = self.tabs[self.tab_ind].search_str
      new_str = get_txt.get_tab_search_txt(self, old_str)
      if new_str is None:
        mode, note = "all", "Cancelled"
      else:
        mode, note = self.acts.do(("edit tab", self.tab_ind, new_str, old_str))
    elif key == guicfg.ADD_TAB_KEY:
      new_str = get_txt.get_tab_search_txt(self, "")
      if new_str is None:
        mode, note = "all", "Cancelled"
      else:
        mode, note = self.acts.do(("add tab", self.tab_ind + 1, new_str))
    elif key == guicfg.REMOVE_TAB_KEY:
      if len(self.tabs) > 0:
        mode, note = self.acts.do(("remove tab", self.tab_ind, self.tabs[self.tab_ind], self.tabs[self.tab_ind].get_old_display_info()))
      else:
        mode, note = "note", "Could not remove the only tab."
    elif key == guicfg.MOVE_TAB_LEFT_KEY:
      if self.tab_ind > 0:
        mode, note = self.acts.do(("move tab", self.tab_ind, -1))
    elif key == guicfg.MOVE_TAB_RIGHT_KEY:
      if self.tab_ind < len(self.tabs) - 1:
        mode, note = self.acts.do(("move tab", self.tab_ind, 1))

    # undo/redo
    elif key == guicfg.UNDO_KEY:
      if len(self.acts.acts) > 0 and self.acts.act_ind >= 0:
        mode, note = self.acts.undo()
      else:
        mode, note = "note", "Nothing to undo"
    elif key == guicfg.REDO_KEY:
      if len(self.acts.acts) > 0 and self.acts.act_ind + 1 < len(self.acts.acts):
        mode, note = self.acts.redo()
      else:
        mode, note = "note", "Nothing to redo"

    elif key == guicfg.GET_KEY:  # get updates
        disp_infos = [t.get_old_display_info() for t in self.tabs]
        display.redraw_note(self, "Getting new mail and updates (please wait)...")
        new_files = process.main(self.mail_mgr, self.tag_mgr)
        unsched_files = check_sched.main(self.mail_mgr)
        self.update_for_add(new_files, disp_infos)
        self.update_for_change(unsched_files, disp_infos)
        self.mark_unread(new_files)
        self.mark_unread(unsched_files)
        curses.flushinp()  # it might've been a long wait, flush keypresses
        unsched_str = "" if len(unsched_files) == 0 else ", de-scheduled " + str(len(unsched_files)) + " emails"
        mode, note = "all", "Got " + str(len(new_files)) + " new emails" + unsched_str

    else:  # if none of the above keys match, send the keypress to the tab
      return True, False, "", ""

    # if one of the keys matched, we fell through to here
    return True, True, mode, note


def main(screen):
  filenames = Gui(screen).go()
  curses.endwin()
  os.system("clear")
  print("\n".join(filenames))


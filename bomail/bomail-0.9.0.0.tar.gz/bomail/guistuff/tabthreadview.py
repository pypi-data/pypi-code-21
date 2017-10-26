####
# bomail.guistuff.tabthreadview
#
# The view of a tab when you navigate into
# a specific thread to see its list of
# emails.
####

import subprocess
import curses

import bomail.config.guiconfig as guicfg
import bomail.cli.mailfile as mailfile
import bomail.guistuff.display_fmt as display_fmt
import bomail.guistuff.gui_util as gui_util
import bomail.util.util as util


indic = lambda t: 1 if t else 0


class ThreadView:
  def __init__(self, trip, tab, gui):
    self.tab = tab
    self.gui = gui
    self.trip = trip
    self.matching_set = set(trip[0])  # files in thread that match search string
    self.repr_file = trip[0][0]       # representative file

    self.my_key = lambda f: self.gui.mail_mgr.get(f, mailfile.DATE_L)
    self.my_tup_key = lambda tup: self.my_key(tup[0])
    self.compare = lambda tup1, tup2: self.my_tup_key(tup1) <= self.my_tup_key(tup2)
    self.all_files = trip[2]          # all files in thread, chronological order
    self.all_files.sort(key=self.my_key)
    
    # filename, is_marked, is_collapsed, collapsed_disp_data, expanded_disp_data
    self.file_data = [[f, False, True, None, None] for f in self.all_files]

    self.is_display_loaded = False


  def ensure_display_loaded(self):
    if self.is_display_loaded:
      return
    self.top_y_coord = 0
    self.num_marked = 0
    self.cursor_ind = -1
    orig_data = self.gui.mail_mgr.get_all(self.all_files[0])  # use in display
    thread_total = len(self.file_data)
    ht, screen_width = self.gui.tab_area.getmaxyx()
    for i in range(len(self.file_data)):
      data = self.gui.mail_mgr.get_all(self.file_data[i][0])
      is_draft = self.file_data[i][0][-5:] == "draft"
      self.file_data[i][3] = display_fmt.get_thread_view_lines(data, orig_data, is_draft, screen_width, True, i+1, thread_total, 0)
      self.file_data[i][4] = display_fmt.get_thread_view_lines(data, orig_data, is_draft, screen_width, False, i+1, thread_total, 0)
      if self.file_data[i][0] in self.matching_set:
        self.file_data[i][2] = False  # expand
        if self.cursor_ind == -1:
          self.cursor_ind = i
    if self.cursor_ind == -1:
      self.cursor_ind = 0
    cursor_y = self.get_y_coord(self.cursor_ind)
    cursor_expanded_disp_pr = self.file_data[self.cursor_ind][4]
    last_visible_line = cursor_y + len(cursor_expanded_disp_pr[0])
    height,width = self.gui.tab_area.getmaxyx()
    first_visible_line = min(cursor_y, last_visible_line - height)
    self.top_y_coord = min(-first_visible_line, 0)

    self.is_display_loaded = True


  def get_curr_filenames(self):
    if len(self.file_data) == 0:
      return []
    elif self.num_marked == 0:
      return [self.file_data[self.cursor_ind][0]]
    else:
      return [t[0] for t in self.file_data if t[2]]  # marked


  # Attempt to reuse display data
  # Note filenames in old_threadview may not exist any more!
  def reuse_disp_data(self, old_threadview):
    if old_threadview.is_display_loaded == False:
      return  # nothing to reuse
    self.ensure_display_loaded()

    self.top_y_coord = old_threadview.top_y_coord
    i_new, i_old = 0, 0
    while i_new < len(self.file_data):
      if i_old >= len(old_threadview.file_data):
        break
      t_old = old_threadview.file_data[i_old]
      t_new = self.file_data[i_new]
      if t_old < t_new:  # old file no longer present
        i_old += 1
      elif t_old == t_new:  # old file still present
        t_new[1] = t_old[1]  # marked
        t_new[2] = t_old[2]  # collapsed
        if i_old == old_threadview.cursor_ind:
          self.cursor_ind = i_new
        i_old += 1
        i_new += 1
      else:  # new file
        t_new[1] = False
        t_new[2] = t_new[0] not in self.matching_set  # expand if matching
        i_new += 1
    self.num_marked = sum(t[2] for t in self.file_data)
    self.scroll_up_file(0)   # force cursor file into view
    self.scroll_down_file(0)
    self.scroll_up_line(0)
    self.scroll_down_line(0)


  def get_disp_prs(self, filename, orig_data, ind, num):
    data = self.gui.mail_mgr.get_all(filename)
    height, width = self.gui.screen.getmaxyx()
    pr_collapsed = display_fmt.get_thread_view_lines(data, orig_data, filename[-5:] == "draft", width, True, ind+1, num, 0)
    pr_expanded = display_fmt.get_thread_view_lines(data, orig_data, filename[-5:] == "draft", width, False, ind+1, num, 0)
    return pr_collapsed, pr_expanded


  def get_old_cursor_display(self):
    return self.file_data[self.cursor_ind][0], self.top_y_coord


  def update_display(self, old_cursor_file, old_top_y):
    old_date = self.gui.mail_mgr.get(old_cursor_file, mailfile.DATE_L)
    self.cursor_ind = util.bisect_left_key(self.file_data, old_date, key=self.my_tup_key)
    self.top_y_coord = old_top_y
    self.scroll_up_line(amt=0)
    self.scroll_down_line(amt=0)


  def get_y_coord(self, file_ind):
    y = self.top_y_coord
    for i in range(file_ind):
      disp_pr = self.file_data[i][3 if self.file_data[i][2] else 4]
      y += len(disp_pr[0])
    return y


  def get_last_y_coord(self, file_ind):
    disp_pr = self.file_data[file_ind][3 if self.file_data[file_ind][2] else 4]
    return self.get_y_coord(file_ind) + len(disp_pr[0]) - 1

  
  def scroll_up_file(self, amt=1):
    self.cursor_ind -= amt
    if self.cursor_ind < 0:
      self.cursor_ind = 0
    y = self.get_y_coord(self.cursor_ind)
    if y < 0:
      self.top_y_coord -= y


  def scroll_down_file(self, amt=1):
    self.cursor_ind += amt
    max_ind = len(self.all_files) - 1
    if self.cursor_ind > max_ind:
      self.cursor_ind = max_ind
    y = self.get_y_coord(self.cursor_ind)
    height, width = self.gui.tab_area.getmaxyx()
    if y >= height:
      self.top_y_coord -= y


  def scroll_up_line(self, amt=1):
    self.top_y_coord += amt
    if self.top_y_coord > 0:
      self.top_y_coord = 0
    height, width = self.gui.tab_area.getmaxyx()
    if self.get_y_coord(self.cursor_ind) >= height:
      self.cursor_ind -= 1


  def scroll_down_line(self, amt=1):
    self.top_y_coord -= amt
    height, width = self.gui.tab_area.getmaxyx()
    if self.cursor_ind < len(self.file_data)-1 and self.get_y_coord(self.cursor_ind) < 0 and self.get_y_coord(self.cursor_ind+1) < height:
      self.cursor_ind += 1
    if self.cursor_ind == len(self.file_data)-1:
      self.top_y_coord -= self.get_last_y_coord(self.cursor_ind)


  def collapse_current(self):
    self.file_data[self.cursor_ind][2] = True
    my_y = self.get_y_coord(self.cursor_ind)
    if my_y < 0:
      self.top_y_coord -= my_y


  def collapse_all(self):
    for tup in self.file_data:
      tup[2] = True
    my_y = self.get_y_coord(self.cursor_ind)
    if my_y < 0:
      self.top_y_coord -= my_y


  def expand_current(self):
    self.file_data[self.cursor_ind][2] = False


  def expand_all(self):
    for tup in self.file_data:
      tup[2] = False
    height, width = self.gui.tab_area.getmaxyx()
    my_y = self.get_y_coord(self.cursor_ind)
    if my_y >= height:
      self.top_y_coord -= (my_y - height)


  def process_key(self, key):
    self.ensure_display_loaded()
    kind, note = "note", ""
    if key == guicfg.DOWN_KEY:
      self.scroll_down_file(1)
      kind, note = "tab", ""
    elif key == guicfg.UP_KEY:
      self.scroll_up_file(1)
      kind, note = "tab", ""
    elif key == guicfg.WAY_DOWN_KEY:
      self.scroll_down_line(2)
      kind, note = "tab", ""
    elif key == guicfg.WAY_UP_KEY:
      self.scroll_up_line(2)
      kind, note = "tab", ""
    elif key == guicfg.RIGHT_KEY:
#    elif (guicfg.arrowkey_nav and key == "KEY_RIGHT") or (not guicfg.arrowkey_nav and key == guicfg.RIGHT_KEY):
      self.expand_current()
      kind, note = "tab", ""
    elif key == guicfg.LEFT_KEY:
#    elif (guicfg.arrowkey_nav and key == "KEY_LEFT") or (not guicfg.arrowkey_nav and key == guicfg.LEFT_KEY):
      # if collapsed already, then go back
      if self.file_data[self.cursor_ind][2]:
        self.tab.gui.mark_read(self.all_files)
        self.tab.mode = "thread list"
      else:
        self.collapse_current()
      kind, note = "tab", ""
    elif key == guicfg.WAY_RIGHT_KEY:
      self.expand_all()
      kind, note = "tab", ""
    elif key == guicfg.WAY_LEFT_KEY:
      self.collapse_all()
      kind, note = "tab", ""

    elif key == guicfg.MARK_KEY:
      summary = display_fmt.get_shortened(self.file_data[self.cursor_ind][0], self.gui.mail_mgr)
      if self.file_data[self.cursor_ind][1]:
        self.file_data[self.cursor_ind][1] = False
        self.num_marked -= 1
        kind, note = "tab", "Un-marked " + summary
      else:
        self.file_data[self.cursor_ind][1] = True
        self.num_marked += 1
        kind, note = "tab", "Marked " + summary
    elif key == guicfg.MARK_ALL_KEY:
      if self.num_marked == len(self.all_files):
        for tup in self.file_data:
          tup[1] = False
        self.num_marked = 0
        kind, note = "tab", "Un-marked all"
      else:
        for tup in self.file_data:
          tup[1] = True
        self.num_marked = len(self.all_files)
        kind, note = "tab", "Marked all"

    # writing and viewing
    elif key == guicfg.WRITE_KEY:
      filename = self.file_data[self.cursor_ind][0]
      mode, note = gui_util.go_write_key(self.gui, filename)

    elif key == guicfg.VIEW_KEY:
      self.gui.mark_read([self.file_data[self.cursor_ind][0]])
      subprocess.call(guicfg.read_prog + " '" + self.file_data[self.cursor_ind][0] + "'", shell=True)
      curses.curs_set(False)
      return "all", ""

    # sending
    elif key == guicfg.SEND_KEY:
      filename = self.file_data[self.cursor_ind][0]
      if filename[-5:] == "draft":
        return gui_util.go_send(self.gui, filename)
      else:
        return "note", "Cannot send: not a draft"

    else:
      return "note", "Input key not recognized"
    return kind, note


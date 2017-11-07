####
# bomail.util.handle
#
# Handle new emails; tag them, etc.
# Can be invoked from command line to process
# a list of already-created files.
####

import sys

import bomail.config.config as config
import bomail.cli.chstate as chstate
import bomail.cli.mailfile as mailfile
import bomail.cli.search as search
import bomail.util.tags as tags
import bomail.util.search_opts as search_opts
import bomail.util.addr as addr
import bomail.util.tags as tags
import bomail.util.datestr as datestr


# A particular rule for handling new email,
# as parsed from the mail_handlers.txt file
class Rule:
  # given the text lines from the handler file
  # and the tag manager object
  def __init__(self, my_lines, tag_mgr):
    self.filter_strs = []  # filter lines from handler file
    self.query = ""        # search query object (to which emails this applies)
    self.close = False     # close the email
    self.schedstr = None   # schedule it
    self.tags = None       # apply these tags
    self.load(my_lines, tag_mgr)

  def load(self, my_lines, tag_mgr):
    self.filter_strs = [my_lines[0]]
    ind = 1
    while ind < len(my_lines) and my_lines[ind].startswith("OR "):
      self.filter_strs.append(my_lines[ind][len("OR "):].strip())
      ind += 1

    self.query = search_opts.SQ_from_str(" -OR ".join(self.filter_strs))

    act_lines = my_lines[ind:]
    self.close = False
    self.schedstr = None
    self.tags = None
    for line in act_lines:
      s = line.strip()
      if s == "close":
        self.close = True
      elif s.startswith("schedule "):
        self.schedstr = s[len("schedule "):]
      elif s.startswith("tag "):
        tagstr = s[len("tag "):]
        taglist = [tags.clean_tag(t) for t in tagstr.split(", ")]
        self.tags = taglist if self.tags is None else self.tags + taglist
    if self.tags is not None:
      self.tags.sort()
      tag_mgr.check_and_add_tags(self.tags)
      # Remove duplicates?


  # handle this list of filenames with associated datas
  # and tagsets
  # return set of indices matched by this query
  def handle(self, filelist, datalist, tagsets, mail_mgr):
    matched_indset = self.query.filter(filelist, mail_mgr, datalist)
    if len(matched_indset) == 0:
      return matched_indset
    matched_list = [filelist[i] for i in matched_indset]

    if self.close:
      chstate.make_closed(matched_list, mail_mgr)
      mail_mgr.updated_filelist(matched_list)

    if self.schedstr is not None:
      # note: wait until now to turn schedstr into datetime because
      # it may be relative to the current time!
      chstate.schedule(matched_list, datestr.get_datetime(self.schedstr))
      mail_mgr.updated_filelist(matched_list)

    if self.tags is not None:
      for ind in matched_indset:
        if tagsets[ind] is None:
          tagsets[ind] = set()
        tagsets[ind].update(self.tags)

    return matched_indset


# The object that takes care of handling new mail
class MailHandler:
  def __init__(self, tag_mgr=None):
    self.tag_mgr = tags.TagMgr() if tag_mgr is None else tag_mgr
    self.lastlinetags = False
    self.autotagreplies = False
    self.close_sent = False
    self.handlers = []
    self.parse_handlers()

  # read mail_handlers text file options and
  # parse into Rule objects
  def parse_handlers(self):
    try:
      with open(config.handlers_file) as f:
        lines = f.readlines()
    except:
      with open(config.error_log_file, "a") as f:
        f.write("Could not find mail-handlers file (" + config.handlers_file + ")\n\n")
      return
    ind = 0
    while ind < len(lines):
      line = lines[ind].strip()
      ind += 1
      if line == "" or line[0] == "#":
        continue

      # special options
      if line.startswith("-autotagreplies"):
        self.autotagreplies = True
        continue
      elif line.startswith("-lastlinetags"):
        self.lastlinetags = True
        continue
      elif line.startswith("-close-sent"):
        self.close_sent = True
        continue

      # asssume this is the start of a rule;
      # get all its lines until a line break or comment
      # in handler_lines
      handler_lines = [line]
      while ind < len(lines):
        line = lines[ind].strip()
        ind += 1
        if line == "" or line[0] == "#":
          break
        handler_lines.append(line)

      # create the rule
      if len(handler_lines) >= 2:
        self.handlers.append(Rule(handler_lines, self.tag_mgr))


  def handle(self, filelist, mail_mgr):
    # optimize for case with lots of tag updates
    # by not writing to file every time
    tagsets = [None]*len(filelist)
    datalist = [mail_mgr.get_all(f) for f in filelist]

    # 1. Special option: lastlinetags
    if self.lastlinetags:
      for i,data in enumerate(datalist):
        lines = data[mailfile.BODY_L].split("\n")
        if len(lines) >= 2:
          line = data[mailfile.BODY_L].split("\n")[-2]  # -1 only gave a newline/blank for some reason
          if line.startswith("tags: "):
            newtags = [tags.clean_tag(t) for t in line[len("tags: "):].split(",")]
            if tagsets[i] is None:
              tagsets[i] = set(newtags)
            else:
              tagsets[i].update(newtags)

    # 2. User-defined handlers
    for h in self.handlers:
      h.handle(filelist, datalist, tagsets, mail_mgr)

    # 3. Special option: autotagreplies
    # The problem to solve is if a message and its parent are both new
    if self.autotagreplies:
      autotag_processed = [False]*len(filelist)
      ids_to_inds = {}
      for i,d in enumerate(datalist):
        ids_to_inds[d[mailfile.MSG_ID_L]] = i
      def do_autotag(i, d):
        if autotag_processed[i]:
          return
        if tagsets[i] is None:
          tagsets[i] = set()
        autotag_processed[i] = True  # important to avoid infinite loops
        my_id = d[mailfile.MSG_ID_L]
        my_reflist = mailfile.do_get_referencelist(my_id, d[mailfile.REFS_L])
        parent_id = mailfile.do_get_parent_id(my_id, my_reflist)
        if parent_id is None:
          return
        elif parent_id in ids_to_inds:
          par_ind = ids_to_inds[parent_id]
          do_autotag(par_ind, datalist[par_ind])
          par_tags = tagsets[par_ind]
        elif parent_id in mail_mgr.ids.ids_to_filenames:
          par_tags = tags.get_tagset_from_str(mail_mgr.get(mail_mgr.ids.ids_to_filenames[parent_id], mailfile.TAGS_L))
        else:
          return
        tagsets[i].update(par_tags)
      # end of function do_autotag()

      for i,data in enumerate(datalist):
        do_autotag(i, d)

    # 4. Set tags based on handlers and options
    #    (tags get special-cased for efficiency reasons)
    for fname,tset in zip(filelist, tagsets):
      if tset is not None:
        mail_mgr.set(fname, mailfile.TAGS_L, ", ".join(sorted(tset)))

    # 5. Special option: close sent mail
    if self.close_sent:
      # close if sent and not sent to myself
      sentlist = [f for f in filelist if mail_mgr.get(f, mailfile.SENT_L) == "True" and not any([addr.is_pair_me(pr) for pr in addr.str_to_pairlist(mail_mgr.get(f, mailfile.TO_L))])]
      chstate.make_closed(sentlist, mail_mgr)



if __name__ == "__main__":
  mgr = mailfile.MailMgr()
  filenames = [s[:-1] for s in sys.stdin.readlines()]  # remove newlines
  MailHandler().handle(filenames, mgr)


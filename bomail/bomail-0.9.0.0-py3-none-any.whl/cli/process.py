####
# bomail.cli.process
#
# Process any new emails and load them into bomail's formats, etc.
# Includes calling custom 'handlers' via bomail.util.handle.
####

import sys
import os, email
import time
from multiprocessing import Process, Queue

import bomail.config.config as config

import bomail.cli.chstate as chstate
import bomail.cli.mailfile as mailfile

import bomail.util.mime_to_mailfile as mime_to_mailfile
import bomail.util.unpack_attach as unpack_attach
import bomail.util.merge_lines as merge_lines
import bomail.util.handle as handle

from bomail.util.addr import AddrBook
from bomail.util.tags import TagMgr

####
# process new mail:
#  1. ensure all directories for mailfile, mime message, attachments exist
#  2. get email data - headers and plain text body
#  3. change to attachments dir, call munpack on mailfile, change back
#  4. save file, move to open list, and add to msg_ids database
#  5. move the mime message to cur/date/
#  6. update address book
#  7. handle all the files using handlers
####

usage_str = """Processes all newly arrived mail (in directory defined in config),
depositing it in cur/ (or as defined in config), creating bomail files, and
extracting attachments.

Options:
    -h           # print this help
    -limit n     # process at most n messages (-1 for unlimited, default is in config)
    -batch n     # process at most this many at a time (-1 for unlimited, default in config)

See also: config, mail-handlers.
"""


# speed up by not asking OS if a dir exists every time
# TODO test if this gives noticeable speedup
created_dirs = set()
def check_and_create_dir(name):
  if not name in created_dirs:
    created_dirs.add(name)
    os.makedirs(name, exist_ok=True)


# unpack attachments
def do_unpack(input_queue, output_queue):
  attach_prlist = []  # pairs (index, attach_list)
  ind = 0
  while True:
    pr = input_queue.get()  # blocks until something is put
    if pr is None:
      output_queue.put(attach_prlist)
      return
    # pr = (py_msg, attach_dir)
    mylist = unpack_attach.do_unpack(pr[0], pr[1])
    if len(mylist) > 0:
      attach_prlist.append((ind, mylist))
    ind += 1


def do_move(input_queue):
  while True:
    pr = input_queue.get()  # blocks until something is put
    if pr is None:
      return
    src,dest = pr   


def msg_id_filename(msg_id):
  return msg_id.replace("<","-").replace(">","-").replace("/","-")


# the main processing function
def process_list(newfilenames, mail_mgr, addr_book, handler, tag_mgr):
  # using this map ensures that a message-id fetched multiple times
  # is only created/processed once
  new_fname_to_data = {} 
  new_msgids = set()
  new_fnames = []
  rename_mimelist = []
  rm_redundant_mimelist = []

  unpack_in_q = Queue()
  unpack_out_q = Queue()
  unpack_process = Process(target=do_unpack, args=(unpack_in_q, unpack_out_q))
  unpack_process.start()
  
  try:
    for small_f in newfilenames:
      f = config.new_rawmail_dir + small_f
      with open(f, encoding='utf-8', errors='replace') as myfile:
        py_msg = email.message_from_file(myfile)
      maildata = mime_to_mailfile.get_data(py_msg)
    
      # 1. ensure directories exist
      mailfile_dir, mailfile_name = mailfile.get_mailfilepath(maildata)
      mailfile_path = mailfile_dir + mailfile_name
      msg_id = maildata[mailfile.MSG_ID_L]
      if os.path.exists(mailfile_path) or mailfile_path in new_fname_to_data or msg_id in mail_mgr.ids.ids_to_filenames or msg_id in new_msgids:
        # assume unique message_id / path means it's a duplicate!
        trash_dir, trash_ext = mailfile.get_trashfilepath(mailfile_path, maildata)
        trash_path = trash_dir + trash_ext
        rm_redundant_mimelist.append((f,trash_path))
        continue
      attach_dir = mailfile.get_attach_dir(maildata)
      rawdir, rawname = mailfile.get_rawfilepath(maildata)
      rename_mimelist.append((f, rawdir + rawname))
      check_and_create_dir(mailfile_dir)
      check_and_create_dir(rawdir)
      
      # 2. get email data
      new_fname_to_data[mailfile_path] = maildata
      new_fnames.append(mailfile_path)
      new_msgids.add(msg_id)
      
      # 3. unpack attachments (spawn process?)
      unpack_in_q.put((py_msg, attach_dir))
  finally:
    unpack_in_q.put(None)
    attach_prlist = unpack_out_q.get()
    for (i,l) in attach_prlist:
      new_fname_to_data[new_fnames[i]][mailfile.ATTACH_L] = ", ".join(l)


  # 4. create file, add to open list, and add to msg_ids file (also load into mail_mgr)
  pairs = new_fname_to_data.items()
  mailfiles = [p[0] for p in pairs]
  maildatas = [p[1] for p in pairs]
  chstate.create(mailfiles, maildatas, mail_mgr)

  # 5. update address book
  addr_book.update_for_new(maildatas)
  
  # 6. handle the mail
  handler.handle(mailfiles, mail_mgr)

  # 7. move mime files
  for a,b in rename_mimelist:
    os.rename(a, b)
  for a,b in rm_redundant_mimelist:
    check_and_create_dir(os.path.dirname(b))
    os.rename(a, b)

  return mailfiles


def main(mail_mgr, tag_mgr=None, process_new_limit=config.process_new_limit, batch_size=config.process_batch_size):
  
  # for each mime file:
  try:
    newfilenames = os.listdir(config.new_rawmail_dir)
  except:
    with open(config.error_log_file, "a") as f:
      f.write("Could not find new-email directory (" + config.new_rawmail_dir + ")")
    return []
  addr_book = AddrBook()
  handler = handle.MailHandler()
  tag_mgr = tag_mgr if tag_mgr is not None else TagMgr()
  if process_new_limit > 0:
    newfilenames = newfilenames[:process_new_limit]

  if batch_size <= 0:
   return process_list(newfilenames, mail_mgr, addr_book, handler, tag_mgr)
  
  mailfiles = []
  for i in range(0,len(newfilenames),batch_size):
    mailfiles += process_list(newfilenames[i:i+batch_size], mail_mgr, addr_book, handler, tag_mgr)
      
  return mailfiles


def main_cli():
  try:
    args = sys.argv[1:]
    if "-h" in args:
      raise
    process_limit = config.process_new_limit
    batch_size = config.process_batch_size
    if "-limit" in args:
      i = args.index("-limit")
      if i == len(args)-1:
        raise
      process_limit = int(args[i+1])
      args = args[:i] + ([] if i+2 >= len(args) else args[i+2:])
    if "-batch" in args:
      i = args.index("-batch")
      if i == len(args)-1:
        raise
      batch_size = int(args[i+1])
      args = args[:i] + ([] if i+2 >= len(args) else args[i+2:])
    if len(args) > 0:
      raise

    files = main(mailfile.MailMgr(), None, process_limit, batch_size)
    if len(files) == 0:
      print("No new messages.\n")
    else:
      print_files = len(files) <= 50      # number 50 chosen through extensive user studies
      print("Processed " + str(len(files)) + (" message" if len(files) == 1 else " messages") + (":" if print_files else "."))
      if print_files:
        print("\n".join(files))
  except:
    print(usage_str)


if __name__ == "__main__":
  main_cli()


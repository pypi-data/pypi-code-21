####
# bomail.util.unpack_attach
#
# Unpack attachments from a MIME file into a directory
####

import sys
import os, email

allowed_chars = (' ','.','_')


def sanitize(filename):
  return "".join(c for c in filename if c.isalnum() or c in allowed_chars).rstrip()

def get_fname(base_filename):
  filename = base_filename
  num = 0
  while os.path.exists(filename):
    num += 1
    filename = base_filename + "_" + str(num)
  return filename


def is_attachment(part):
  cd = part.get_content_disposition()
  return cd is not None and cd.lower() == "attachment"

  
# return a list of attachment file paths
def do_unpack(py_msg, attach_dir):
  made_dir = False
  results = []
  for part in py_msg.walk():
#    if part.is_attachment():
    if is_attachment(part):
      unclean_filename = part.get_filename()
      if unclean_filename is None:
        unclean_filename = "unknownfile"
      filename = get_fname(attach_dir + sanitize(unclean_filename))
      try:
        payload = part.get_payload(decode=True)
        mode = "wb"
      except:
        # "This should never happen" thanks python
        payload = part.get_payload(decode=False)
        mode = "w"
      if payload is not None:
        if not made_dir:
          os.makedirs(attach_dir, exist_ok=True)
          made_dir = True
        with open(filename, mode) as f:
          f.write(payload)
        results.append(filename)
  return results


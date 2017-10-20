#! /usr/bin/env python

import json, logtool, tempfile

@logtool.log_call
def linestream (keylist, cb = None, validate = False):
  keylist = keylist
  for ndx, key in enumerate (keylist):
    if cb is not None:
      cb (ndx)
    with tempfile.NamedTemporaryFile (prefix = "s3lncoll_in__") as f:
      f.write (key.get ()["Body"].read ())
      f.seek (0)
      f.flush()
      for line in file (f.name): # pylint: disable=not-an-iterable
        try:
          if validate:
            json.loads (line)
          yield line
        except ValueError:
          continue
  raise StopIteration

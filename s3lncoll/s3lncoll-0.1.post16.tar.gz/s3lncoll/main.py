#! /usr/bin/env python

from __future__ import absolute_import
import clip, logtool, logging, sys
from addict import Dict
from encodings.utf_8 import StreamWriter
from functools import partial
from path import Path
from .cmd import Action

from ._version import get_versions
__version__ = get_versions ()['version']
del get_versions

logging.basicConfig (level = logging.WARN)
LOG = logging.getLogger (__name__)
TIME_T, TIME_STR = logtool.now ()
BLOCK_LIMIT = 1024 * 1024

# Python 2 will try to coerce its output stream to match the terminal it is
# printing to. If we pipe the output, it will attempt to do plain ASCII
# encoding, which breaks on unicode characters. The following will change
# the default encoding for pipes from ascii to utf-8.
#   See : https://wiki.python.org/moin/PrintFails
sys.stdout = StreamWriter (sys.stdout)
sys.stderr = StreamWriter (sys.stderr)

APP = clip.App (name = "s3lncoll")

CONFIG = Dict ({
  "block": BLOCK_LIMIT,
  "force": False,
  "delete": False,
  "json": "False",
  "quiet": False,
  "time_str": TIME_STR,
  "time_t": TIME_T,
})

@logtool.log_call
def option_setopt (option, value):
  CONFIG[option] = value

@logtool.log_call
def option_version (opt): # pylint: disable = W0613
  print __version__
  clip.exit ()

@logtool.log_call
def option_logging (flag):
  logging.root.setLevel (logging.DEBUG)
  CONFIG.debug = flag

@APP.main (name = Path (sys.argv[0]).basename (),
           description = "Line stream s3 files into ~uniform lumps in S3",
           tree_view = "-H")
@clip.flag ("-H", "--HELP",
            help = "Help for all sub-commands")
@clip.flag ("-D", "--debug", name = "debug", help = "Enable debug logging",
            callback = option_logging)
@clip.flag ("-d", "--delete", name = "delete",
            help = "Delete source files/keys",
            callback = partial (option_setopt, "delete"))
@clip.flag ("-j", "--json", name = "json",
            help = "Validate each line as JSONM",
            callback = partial (option_setopt, "json"))
@clip.flag ("-q", "--quiet", name = "quiet",
            help = "Be quiet, be vewy vewy quiet",
            callback = partial (option_setopt, "quiet"))
@clip.flag ("-V", "--version", name = "verbose",
            help = "Report installed version",
            callback = option_version)
@clip.flag ("-z", "--compress", name = "compress",
            help = "Ccompress (gzip) the target(s)",
            callback = partial (option_setopt, "compress"))
@clip.opt ("-b", "--blocksize", default = BLOCK_LIMIT, type = int,
           help = "Maximum size of pre-compressed output files in bytes.")
@clip.arg ("from", help = "S3 URL prefix to clump")
@clip.arg ("to", help = "S3 URL for target clump ('{}' will be the count)")
@logtool.log_call
def app_main (**kwargs):
  if not CONFIG.conf.debug:
    logging.basicConfig (level = logging.ERROR)
  CONFIG.url_from = kwargs["from"]
  CONFIG.url_to = kwargs["to"]
  CONFIG.block = kwargs["blocksize"]
  Action (CONFIG).run ()

@logtool.log_call
def main ():
  try:
    APP.run ()
  except KeyboardInterrupt:
    pass
  except clip.ClipExit as e:
    sys.exit (e.status)
  except Exception as e:
    logtool.log_fault (e)
    sys.exit (1)

if __name__ == "__main__":
  main ()

import Cli
import os
import shutil
import json
import time

class Header(object):

  def __init__(self):
    self.interface = Cli.Interface()

  def status(self):
    statusHeaderString = "ID".ljust(20)
    statusHeaderString += "NAME".ljust(30)
    statusHeaderString += "IP".ljust(15)
    statusHeaderString += "CREATED".ljust(10)
    statusHeaderString += "RUNNING".ljust(10)
    self.interface.header(statusHeaderString)
    # self.interface.header("Status of %s" % self.name)

from enum import IntEnum
from datetime import datetime
from threading import Lock

class LogLevel(IntEnum):
  DEBUG     = 0
  IO        = 1
  INFO      = 2
  WARNING   = 3
  ERROR     = 4
  IMPORTANT = 5
  CRITICAL  = 6

main_level = LogLevel.INFO
main_file_level = LogLevel.WARNING

class Logger:
  def __init__(self, name = '', level = LogLevel.INFO):
    self.name = name
    self.prefix = ''
    self.directory = './'
    self.should_log_to_files = False
    self.filename = ''
    self.file = None
    self.iochars = ' IO'
    self.mutex = Lock()

  def enable_file_logging(self, directory = './', prefix = 'log'):
    self.directory = directory
    self.prefix = prefix
    self.should_log_to_files = True

  def disable_file_logging(self):
    self.should_log_to_files = False

  def write(self, message, level = LogLevel.INFO):
    self.mutex.acquire()
    if level >= main_level:
      dt = datetime.now()
      print(self.format(message, level, dt, True))
    if level >= main_file_level:
      new_filename = dt.strftime(self.prefix + '-%d.%m.%Y.log')
      if self.should_log_to_files:
        if self.filename != new_filename:
          self.filename = new_filename
          if self.file != None:
            self.file.close()
            self.file = None
          self.file = open(self.directory + '/' + new_filename, 'a')
        self.file.write(self.format(message, level, dt, False) + '\n')
        self.file.flush()
    self.mutex.release()

  def format(self, message, level, dt, colored):
    l = {'color': '',         'chars': 'UNK'}
    if level == LogLevel.DEBUG:
      l = {'color': '\x1b[32m', 'chars': 'DBG'}
    if level == LogLevel.IO:
      l = {'color': '\x1b[36m', 'chars': self.iochars} 
    if level == LogLevel.INFO:
      l = {'color': '\x1b[34m', 'chars': 'INF'} 
    if level == LogLevel.WARNING:
      l = {'color': '\x1b[33m', 'chars': 'WRN'} 
    if level == LogLevel.ERROR:
      l = {'color': '\x1b[31m', 'chars': 'ERR'} 
    if level == LogLevel.IMPORTANT:
      l = {'color': '\x1b[37m', 'chars': 'IMP'} 
    if level == LogLevel.CRITICAL:
      l = {'color': '\x1b[35m', 'chars': 'CRT'} 
    
    c_bold = '\x1b[1m';
    c_reset = '\x1b[0m';
    c_creset = '\x1b[39m';

    s = ''
    if colored:
      s += c_bold + l['color']
    s += '['
    if colored:
      s += c_creset
    s += dt.strftime('%S:%M:%H %d.%m.%Y')
    if colored:
      s += l['color']
    s += ' | '
    if colored:
      s += c_creset
    s += l['chars']
    if colored:
      s += l['color']
    s += '] '
    if colored:
      s += c_reset
    s += self.name
    if colored:
      s += c_bold + l['color']
    s += '> '
    if colored:
      s += c_reset
    s += message

    return s

  def debug(self, message):
    self.write(message, LogLevel.DEBUG)

  def io(self, message):
    self.write(message, LogLevel.IO)

  def info(self, message):
    self.write(message, LogLevel.INFO) 

  def warning(self, message):
    self.write(message, LogLevel.WARNING)

  def error(self, message):
    self.write(message, LogLevel.ERROR)

  def important(self, message):
    self.write(message, LogLevel.IMPORTANT)

  def critical(self, message):
    self.write(message, LogLevel.CRITICAL) 
from datetime import datetime

log_level = 3
min_level = 1
max_level = 4
log_str_map = {
  1 : "ERROR",
  2 : "WARNING",
  3 : "INFO",
  4 : "DEBUG"
}

def log_level_set(level):
  global log_level
  log_level = level

def log_level_get():
  return log_level

def LOGGING(level, msg):
  if level < min_level:
    level = min_level
  if level > max_level:
    level = max_level
  if level <= log_level:
    t_stamp = ""
    if log_level >= 4:
      # We include timestamp only when log_level is at DEBUG or higher
      t_now = datetime.now()
      t_stamp = "%s " % str(t_now)
    log_msg = "%s%s: %s" % (t_stamp, log_str_map[level], msg)
    print log_msg

def DEBUG(msg):
  LOGGING(4, msg)

def INFO(msg):
  LOGGING(3, msg)

def WARNING(msg):
  LOGGING(2, msg)

def ERROR(msg):
  LOGGING(1, msg)

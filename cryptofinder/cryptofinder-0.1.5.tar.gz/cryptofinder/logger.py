from .config import Config
from click import secho

class Logger():
  def __init__(self, ui):
    self.logfile = Config.logfile()
    self.verbose = ui.get('verbose')
    self.quiet = ui.get('quiet')

  def error(self, message, color='red'):
    self.logfile.error(message)
    if not self.quiet:
      secho(message, fg=color)

  def warning(self, message, color='yellow'):
    self.logfile.warning(message)
    if not self.quiet:
      secho(message, fg=color)

  def debug(self, message, color='cyan'):
    self.logfile.debug(message)
    if self.verbose and not self.quiet:
      secho(message, fg=color)

  def info(self, message, color='white'):
    self.logfile.info(message)
    if not self.quiet:
      secho(message, fg=color)
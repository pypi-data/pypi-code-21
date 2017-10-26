import os
import yaml

class Config:

  yaml = {}
  filename = '.docker-manager'

  def __init__(self, filename):
    if not os.path.isfile(filename):
      raise Exception("File %s not found" % filename)
    self.filename = filename

  def load(self):
    with open(self.filename, 'r') as stream:
      self.yaml = yaml.safe_load(stream)
      return True
    return False

  def getContainerNames(self, includeWildcard = False):
    names = list(self.yaml['container'].keys())
    if includeWildcard is True:
      names.append('all-container')
    return names

  def getDefaultContainerSettings(self):
    return self.yaml['containerDefaults'].copy()

  def getContainerSettings(self, name):
    settings = self.getDefaultContainerSettings()
    settings.update(self.yaml['container'][name])
    return settings

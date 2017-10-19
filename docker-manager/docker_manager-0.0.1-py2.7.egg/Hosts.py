import re

class Hosts(object):

  container = None
  hostsFile = '/etc/hosts'

  def __init__(self, container):
    self.container = container

  def add(self, ip, hostname):
    with open(self.hostsFile, 'r+') as f:
      hostsfile = f.read()
      if hostsfile.find(hostname) is not -1:
        hostsfile = re.sub(r"\n(.*)    %s\n" % hostname, "\n%s    %s\n" % (ip, hostname), hostsfile)
      else:
        hostsfile += "%s    %s\n" % (ip, hostname)
      f.seek(0)
      f.write(hostsfile)
      f.truncate()

  def remove(self, hostname):
    with open(self.hostsFile, 'r+') as f:
      hostsfile = f.read()
      if hostsfile.find(hostname) is not -1:
        hostsfile = re.sub(r"\n(.*)    %s\n" % hostname, "\n", hostsfile)
      f.seek(0)
      f.write(hostsfile)
      f.truncate()


  # callable methods
  def status(self):
    pass

  def start(self):
    self.add(self.container.getIpAddress(), self.container.getName())
    pass

  def stop(self):
    self.remove(self.container.getName())
    pass

  def restart(self):
    self.stop()
    self.start()
    pass

  def destroy(self):
    self.stop()
    pass

  def update(self):
    self.stop()
    self.start()
    pass
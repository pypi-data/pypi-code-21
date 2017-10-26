import Cli
import os
import shutil
import json
import time
from pprint import pprint

class Container(object):

  id = None
  name = None
  running = False
  created = False
  settings = {}
  dockerSettings = {}
  interface = None
  command = None
  waitedForIp = 0
  waitForIpMax = 20

  def __init__(self, name, settings):
    self.name = name
    self.settings = settings
    self.interface = Cli.Interface()
    self.command = Cli.Command()
    self.getId()
    if self.id is not None:
      self.created = True
      self.inspect()

  def inspect(self):
    output = self.command.execute("docker inspect %s" % self.id)
    if output is False:
      return False
    self.dockerSettings = json.loads(output)[0]
    self.running = self.dockerSettings['State']['Running']

  def getName(self):
    return self.name

  def getIpAddress(self):
    if self.running:
      return self.dockerSettings['NetworkSettings']['IPAddress']

  def getId(self):
    if self.id:
      return self.id

    output = self.command.execute('docker ps -aqf "name=%s"' % self.name)
    if output == '':
      return None

    self.id = output
    return self.id

  def isRunning(self):
    return self.running

  def isCreated(self):
    return self.created

  def create(self):
    self.interface.header("Create %s" % self.name)
    if 'sourceVolumes' in self.settings:
      for sourceVolume in self.settings['sourceVolumes']:
        if not os.path.isdir(sourceVolume['target']):
          shutil.copytree(sourceVolume['source'], sourceVolume['target'])
    volumeString = ''
    if 'volumes' in self.settings:
      for volume in self.settings['volumes']:
        if not os.path.isdir(volume['source']):
          self.interface.error("Volume source %s does not exist! - skipping" % volume['source'])
          continue

        if 'uid' in volume:
          self.command.execute('chown -R %s %s' % (volume['uid'], volume['source']))
        volumeString += '-v=%s:%s ' % (volume['source'], volume['target'])

    hostnameString = self.name
    if 'hostname' in self.settings:
      hostnameString = self.settings['hostname']
    if 'domainname' in self.settings:
      hostnameString += '.%s' % self.settings['domainname']

    dnsString = ''
    if 'dns' in self.settings:
      dnsString = '--dns=%s' % self.settings['dns']

    restartString = ''
    if 'restart' in self.settings:
      restartString = '--restart=%s' % self.settings['restart']

    exposeString = ''
    if 'expose' in self.settings:
      for expose in self.settings['expose']:
        exposeString += '--expose=%s ' % expose

    environmentString = ''
    if 'environment' in self.settings:
      for environment in self.settings['environment']:
        environmentString += '-e %s ' % environment

    privilegedString = ''
    if "privileged" in self.settings:
      privilegedString = '--privileged'

    cpuString = ''
    if 'cpus' in self.settings:
      cpuString += '--cpus="%s"' % (self.settings['cpus'])

    memoryString = ''
    if 'memory' in self.settings:
      memoryString += '--memory="%s"' % (self.settings['memory'])

    swappinessString = ''
    if 'swappiness' in self.settings:
      swappinessString += '--memory-swappiness=%s' % (self.settings['swappiness'])


    capAddString = ''
    if 'capAdd' in self.settings:
      capAddString += '--cap-add="%s"' % (self.settings['capAdd'])

    portMappingString = ''
    if 'portMapping' in self.settings:
      for portMapping in self.settings['portMapping']:
        portMappingString += '-p %s ' % portMapping

    commandString = ''
    if 'command' in self.settings:
      for command in self.settings['command']:
        commandString += " %s" % command

    command = 'docker run -d -it \
    --name=%s\
    --hostname=%s\
    %s\
    %s\
    %s\
    %s\
    %s\
    %s\
    %s\
    %s\
    %s\
    %s\
    %s\
    %s\
    %s\
    ' % (self.name, hostnameString, portMappingString, cpuString, memoryString, swappinessString, capAddString, environmentString, privilegedString, exposeString, volumeString, restartString, dnsString, self.settings['image'], commandString)
    self.interface.writeOut(command)
    self.id = self.command.execute(command)
    self.created = True
    self.waitForIp()

  def waitForIp(self):
    self.waitedForIp += 1
    if self.waitedForIp >= self.waitForIpMax:
      return False

    self.inspect()
    if self.getIpAddress() is None:

      return self.waitForIp()

    return True

  # callable methods
  def status(self):
    statusString = str(self.getId()).ljust(20)
    statusString += str(self.name).ljust(30)
    statusString += str(self.getIpAddress()).ljust(15)
    statusString += str(self.isCreated()).ljust(10)
    statusString += str(self.isRunning()).ljust(10)
    self.interface.writeOut(statusString)
    # self.interface.header("Status of %s" % self.name)
    # self.interface.writeOut("ContainerID: %s" % self.getId())
    # self.interface.writeOut("Container IP Address: %s" % self.getIpAddress())
    # self.interface.writeOut("Container is created: %s" % self.isCreated())
    # self.interface.writeOut("Container running: %s" % self.isRunning())

  def start(self):
    if not self.created:
      self.create()
      return True

    self.interface.header("Start %s" % self.name)
    if not self.running:
      self.command.execute('docker start %s' % self.id)
      self.inspect()

  def stop(self):
    self.interface.header("Stop %s" % self.name)
    if self.running:
      self.command.execute('docker stop %s' % self.id)
      self.running = False

  def restart(self):
    self.interface.header("Restart %s" % self.name)
    self.stop()
    self.start()


  def destroy(self):
    self.interface.header("Destroy %s" % self.name)
    if self.created:
      self.command.execute('docker rm -f %s' % self.id)
      self.created = False
      self.running = False

  def update(self):
    updateCommand = "docker image pull %s " % (self.settings['image'])
    ranBefore = self.isRunning()
    self.interface.writeOut(updateCommand)
    self.interface.writeOut(self.command.execute(updateCommand))
    self.destroy()

    # wait until container is properly destroyed
    counter = 1;
    while self.created is True and counter < 1000:
      counter += 1
      break

    if ranBefore:
      self.start()

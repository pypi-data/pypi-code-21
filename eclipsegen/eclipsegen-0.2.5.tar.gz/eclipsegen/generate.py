import tarfile
import tempfile
import urllib.parse
import urllib.request
import os
from enum import Enum, unique
from itertools import takewhile
from os import path, makedirs, listdir, rmdir, mkdir, remove, walk, chmod
from platform import architecture, system
from re import sub, findall, MULTILINE
from shutil import move, copytree, rmtree, make_archive, which
from subprocess import Popen
from sys import maxsize

import requests

from eclipsegen import director_path
from eclipsegen.config import X86Arch, X64Arch, WindowsOs, MacOs, LinuxOs


DEFAULT_NAME = 'Eclipse'
DEFAULT_ARCHIVE_PREFIX = 'eclipse'


@unique
class Os(Enum):
  windows = WindowsOs()
  macosx = MacOs()
  linux = LinuxOs()

  @staticmethod
  def get_current():
    sys = system()
    if sys == 'Windows':
      return Os.windows.value
    elif sys == 'Darwin':
      return Os.macosx.value
    elif sys == 'Linux':
      return Os.linux.value
    else:
      raise Exception('Unsupported OS {}'.format(sys))

  @staticmethod
  def keys():
    return Os.__members__.keys()

  @staticmethod
  def values():
    return [o.value for o in Os]

  @staticmethod
  def exists(sys):
    return sys in Os.__members__.keys()


@unique
class Arch(Enum):
  x64 = X64Arch()
  x86 = X86Arch()

  @staticmethod
  def get_current():
    if architecture()[0] == '64bit':
      return Arch.x64.value
    if maxsize > 2 ** 32:
      return Arch.x64.value
    return Arch.x86.value

  @staticmethod
  def keys():
    return Arch.__members__.keys()

  @staticmethod
  def values():
    return [a.value for a in Arch]

  @staticmethod
  def exists(arch):
    return arch in Arch.__members__.keys()


_invalidCombinations = [
  (Os.macosx.value, Arch.x86.value),
]


def _is_invalid_combination(os, arch):
  for incorrectOs, incorrectArch in _invalidCombinations:
    if os == incorrectOs and arch == incorrectArch:
      return True
  return False


class EclipseMultiGenerator(object):
  """
  Facade for generating Eclipse instances for multiple operating systems, architectures, and JREs.
  """

  def __init__(self, workingDir, destination, oss=None, archs=None, repositories=None, installUnits=None,
      name=None, fixIni=True, addJre=False, archiveJreSeparately=False, archivePrefix=None, archiveSuffix=None):
    self.workingDir = workingDir
    self.destination = destination
    self.oss = oss if oss else Os.values()
    self.archs = archs if archs else Arch.values()
    self.repositories = repositories
    self.installUnits = installUnits
    self.name = name
    self.fixIni = fixIni
    self.addJre = addJre
    self.archiveJreSeparately = archiveJreSeparately
    self.archivePrefix = archivePrefix
    self.archiveSuffix = archiveSuffix

  def generate(self):
    """
    Generate all Eclipse instances.

    :return: List of Eclipes that were generated (EclipseOutput*).
    """

    outputs = []
    combinations = [(o, a) for o in self.oss for a in self.archs]
    for os, arch in combinations:
      if not _is_invalid_combination(os, arch):
        print('Generating Eclipse for combination {}, {}'.format(os.name, arch.name))
        generator = EclipseGenerator(self.workingDir, self.destination, os=os, arch=arch,
          repositories=self.repositories, installUnits=self.installUnits, name=self.name, fixIni=self.fixIni,
          addJre=self.addJre, archive=True, archiveJreSeparately=self.archiveJreSeparately,
          archivePrefix=self.archivePrefix, archiveSuffix=self.archiveSuffix)
        outputs.extend(generator.generate())
    return outputs


class EclipseOutput(object):
  def __init__(self, os, arch, withJre, location):
    self.os = os
    self.arch = arch
    self.withJre = withJre
    self.location = location


class EclipseGenerator(object):
  """
  Eclipse instance generator.
  """

  def __init__(self, workingDir, destination, os=None, arch=None, repositories=None, installUnits=None,
      name=None, fixIni=True, addJre=False, archive=False, archiveJreSeparately=False, archivePrefix=None,
      archiveSuffix=None):
    self.os = os if os else Os.get_current()
    self.arch = arch if arch else Arch.get_current()
    self.repositories = repositories if repositories else []
    self.installUnits = installUnits if installUnits else []
    self.name = name if name else DEFAULT_NAME
    self.fixIni = fixIni
    self.addJre = addJre
    self.archive = archive
    self.archiveJreSeparately = archiveJreSeparately
    self.archivePrefix = archivePrefix if archivePrefix else DEFAULT_ARCHIVE_PREFIX
    self.archiveSuffix = archiveSuffix if archiveSuffix else ''

    self.workingDir = workingDir
    if not path.isabs(self.workingDir):
      self.workingDir = path.abspath(self.workingDir)

    self.requestedDestination = _make_abs(destination, self.workingDir)

    if archive:
      self.tempdir = tempfile.TemporaryDirectory()
      self.destination = self.tempdir.name
    else:
      self.destination = self.requestedDestination

    self.finalDestination = self.os.finalDestination(self.destination, self.name)

  def __enter__(self):
    return self

  def __exit__(self, **_):
    if self.archive:
      print('Deleting temporary directory {}'.format(self.tempdir))
      self.tempdir.cleanup()

  def generate(self):
    """
    Generate an Eclipse instance.

    :return: List of Eclipes that were generated (EclipseOutput*). Multiple Eclipes are generated when self.addJre and
             self.archiveJreSeparately are set to true, causing two archives to be created.
    """
    outputs = []
    directory = self.create_eclipse()
    if self.fixIni:
      self.fix_ini()
    if self.archive and self.archiveJreSeparately and self.addJre:
      archive = self.create_archive(prefix=self.archivePrefix, suffix=self.archiveSuffix)
      outputs.append(EclipseOutput(self.os, self.arch, False, archive))
    if self.addJre:
      self.add_jre()
    # Make everything writeable such that all files can be modified and deleted.
    _make_writeable(self.finalDestination)
    if self.archive:
      if self.archiveJreSeparately and self.addJre:
        archive = self.create_archive(prefix=self.archivePrefix, suffix='-jre' + self.archiveSuffix)
        outputs.append(EclipseOutput(self.os, self.arch, True, archive))
      else:
        archive = self.create_archive(prefix=self.archivePrefix, suffix=self.archiveSuffix)
        outputs.append(EclipseOutput(self.os, self.arch, True, archive))
    else:
      outputs.append(EclipseOutput(self.os, self.arch, self.addJre, directory))
    return outputs

  def create_eclipse(self):
    if _is_invalid_combination(self.os, self.arch):
      raise RuntimeError(
        'Combination {}, {} is invalid, cannot generate Eclipse instance'.format(self.os, self.arch))
    searchPath = director_path()
    directorPath = which('director', path=searchPath)
    if not directorPath:
      raise RuntimeError(
        'Director application was not found at {} nor on the system path, cannot generate Eclipse instance'.format(
          searchPath))
    args = [directorPath]

    if len(self.repositories) != 0:
      mappedRepositories = map(self.__to_uri, self.repositories)
      args.extend(['-r {}'.format(repo) for repo in mappedRepositories])

    args.extend(['-i {}'.format(iu) for iu in self.installUnits])

    args.append('-tag InitialState')
    args.append('-destination {}'.format(self.finalDestination))
    args.append('-profile SDKProfile')
    args.append('-profileProperties "org.eclipse.update.install.features=true"')
    args.append('-p2.os {}'.format(self.os.eclipseOs))
    args.append('-p2.ws {}'.format(self.os.eclipseWs))
    args.append('-p2.arch {}'.format(self.arch.eclipseArch))
    args.append('-roaming')

    cmd = ' '.join(args)
    print(cmd)
    try:
      process = Popen(cmd, cwd=self.workingDir, shell=True)
      process.communicate()
      if process.returncode != 0:
        raise RuntimeError("Eclipse generation failed")
    except KeyboardInterrupt:
      raise RuntimeError("Eclipse generation interrupted")

    return self.finalDestination

  def fix_ini(self, stackSize='16M', heapSize='2G', maxHeapSize='2G', maxPermGen=None,
      requiredJavaVersion='1.8', server=True):
    iniLocation = self.os.iniLocation(self.finalDestination)

    # Python converts all line endings to '\n' when reading a file in text mode like this.
    with open(iniLocation, "r") as iniFile:
      iniText = iniFile.read()

    iniText = sub(r'--launcher\.XXMaxPermSize\n[0-9]+[gGmMkK]', '', iniText, flags=MULTILINE)
    iniText = sub(r'-install\n.+', '', iniText, flags=MULTILINE)
    iniText = sub(r'-showsplash\norg.eclipse.platform', '', iniText, flags=MULTILINE)

    launcherPattern = r'--launcher\.defaultAction\nopenFile'
    launcherMatches = len(findall(launcherPattern, iniText, flags=MULTILINE))
    if launcherMatches > 1:
      iniText = sub(launcherPattern, '', iniText, count=launcherMatches - 1, flags=MULTILINE)

    iniText = sub(r'-X(ms|ss|mx)[0-9]+[gGmMkK]', '', iniText)
    iniText = sub(r'-XX:MaxPermSize=[0-9]+[gGmMkK]', '', iniText)
    iniText = sub(r'-Dorg\.eclipse\.swt\.internal\.carbon\.smallFonts', '', iniText)
    iniText = sub(r'-XstartOnFirstThread', '', iniText)
    iniText = sub(r'-Dosgi.requiredJavaVersion=[0-9]\.[0-9]', '', iniText)
    iniText = sub(r'-server', '', iniText)

    iniText = '\n'.join([line for line in iniText.split('\n') if line.strip()]) + '\n'

    if self.os == Os.macosx.value:
      iniText += '-XstartOnFirstThread\n'

    if stackSize:
      iniText += '-Xss{}\n'.format(stackSize)
    if heapSize:
      iniText += '-Xms{}\n'.format(heapSize)
    if maxHeapSize:
      iniText += '-Xmx{}\n'.format(maxHeapSize)
    if maxPermGen:
      iniText += '-XX:MaxPermSize={}\n'.format(maxPermGen)

    if requiredJavaVersion:
      iniText += '-Dosgi.requiredJavaVersion={}\n'.format(requiredJavaVersion)

    if server:
      iniText += '-server\n'

    print('Setting contents of {} to:\n{}'.format(iniLocation, iniText))
    with open(iniLocation, "w") as iniFile:
      iniFile.write(iniText)

  def add_jre(self):
    jrePath = self.__download_jre()
    targetJrePath = path.join(self.finalDestination, 'jre')
    if path.isdir(targetJrePath):
      rmtree(targetJrePath, ignore_errors=True)
    print('Copying JRE from {} to {}'.format(jrePath, targetJrePath))
    copytree(jrePath, targetJrePath, symlinks=True)

    relJreLocation = self.os.jreLocation(self.arch == Arch.x64.value)
    iniLocation = self.os.iniLocation(self.finalDestination)
    with open(iniLocation, 'r') as iniFile:
      iniText = iniFile.read()
    with open(iniLocation, 'w') as iniFile:
      print('Prepending VM location {} to eclipse.ini'.format(relJreLocation))
      iniText = sub(r'-vm\n.+\n', '', iniText, flags=MULTILINE)
      iniFile.write('-vm\n{}\n'.format(relJreLocation) + iniText)

  def create_archive(self, prefix=DEFAULT_ARCHIVE_PREFIX, suffix=''):
    name = '{}-{}-{}{}'.format(prefix, self.os.name, self.arch.name, suffix)
    print('Archiving Eclipse instance {}'.format(name))
    filename = path.join(self.requestedDestination, name)
    if self.os == Os.macosx.value:
      appFile = '{}.app'.format(self.name)
      archive = make_archive(filename, format=self.os.archiveFormat, root_dir=self.destination, base_dir=appFile)
    else:
      with tempfile.TemporaryDirectory() as tempdir:
        # Copy into another temp dir to have a directory with target as the root in archive, instead of the Eclipse directory.
        target = path.join(tempdir, self.name)
        copytree(self.destination, target, symlinks=True)
        archive = make_archive(filename, format=self.os.archiveFormat, root_dir=tempdir, base_dir=self.name)
    return archive

  def __to_uri(self, location):
    if location.startswith('http'):
      return location
    else:
      location = _make_abs(location, self.workingDir)
      return urllib.parse.urljoin('file:', urllib.request.pathname2url(location))

  def __download_jre(self):
    # http://download.oracle.com/otn-pub/java/jdk/8u152-b16/aa0333dd3019491ca4f6ddbe78cdb6d0/jdk-8u152-windows-i586.exe
    # http://download.oracle.com/otn-pub/java/jdk/8u152-b16/aa0333dd3019491ca4f6ddbe78cdb6d0/jdk-8u152-windows-x64.exe
    # http://download.oracle.com/otn-pub/java/jdk/8u152-b16/aa0333dd3019491ca4f6ddbe78cdb6d0/jdk-8u152-linux-i586.tar.gz
    # http://download.oracle.com/otn-pub/java/jdk/8u152-b16/aa0333dd3019491ca4f6ddbe78cdb6d0/jdk-8u152-linux-x64.rpm
    # http://download.oracle.com/otn-pub/java/jdk/8u152-b16/aa0333dd3019491ca4f6ddbe78cdb6d0/jdk-8u152-macosx-x64.dmg

    version = '8u152'
    build = 'b16'
    downloadId = 'aa0333dd3019491ca4f6ddbe78cdb6d0'
    urlPrefix = 'http://download.oracle.com/otn-pub/java/jdk/{0}-{1}/{2}/jre-{0}-'.format(version, build, downloadId)
    extension = 'tar.gz'
    jreOs = self.os.jreOs
    jreArch = self.arch.jreArch

    location = _to_storage_location(path.join('jre', version, build))
    makedirs(location, exist_ok=True)

    fileName = '{}-{}.{}'.format(jreOs, jreArch, extension)
    filePath = path.join(location, fileName)

    dirName = '{}-{}'.format(jreOs, jreArch)
    dirPath = path.join(location, dirName)

    if path.isdir(dirPath):
      return dirPath

    url = '{}{}'.format(urlPrefix, fileName)
    print('Downloading JRE from {}'.format(url))
    cookies = dict(gpw_e24='http%3A%2F%2Fwww.oracle.com%2F', oraclelicense='accept-securebackup-cookie')
    request = requests.get(url, cookies=cookies)
    with open(filePath, 'wb') as file:
      for chunk in request.iter_content(1024):
        file.write(chunk)

    print('Extracting JRE to {}'.format(dirPath))
    with tarfile.open(filePath, 'r') as tar:
      tar.extractall(path=dirPath)
      rootName = _common_prefix(tar.getnames())
      rootDir = path.join(dirPath, rootName)
      for name in listdir(rootDir):
        move(path.join(rootDir, name), path.join(dirPath, name))
      rmdir(rootDir)

    # Delete ._ files found on macOS
    for walkDirPath, dirs, files in os.walk(dirPath):
      for walkFileName in files:
        if '._' in walkFileName:
          os.remove(os.path.join(walkDirPath, walkFileName))

    remove(filePath)

    return dirPath


def _to_storage_location(location):
  storageLocation = path.join(path.expanduser('~'), '.eclipsegen')
  if not path.isdir(storageLocation):
    mkdir(storageLocation)
  return path.join(storageLocation, location)


def _common_prefix(paths, sep='/'):
  """
  Finds the common path prefix in given list of paths.
  The os.path.commonprefix function is broken, since it finds prefixes on the character level, not the path level.
  From: http://rosettacode.org/wiki/Find_Common_Directory_Path#Python
  """
  byDirectoryLevels = zip(*[p.split(sep) for p in paths])

  def all_names_equal(name):
    return all(n == name[0] for n in name[1:])

  return sep.join(x[0] for x in takewhile(all_names_equal, byDirectoryLevels))


def _make_abs(directory, relativeTo):
  if not path.isabs(directory):
    return path.normpath(path.join(relativeTo, directory))
  return directory


def _make_writeable(directory):
  for root, _, files in walk(directory):
    for name in files:
      full_path = path.join(root, name)
      chmod(full_path, 0o744)

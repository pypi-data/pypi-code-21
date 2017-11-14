import os


class X64Arch(object):
  name = 'x64'
  eclipseArch = 'x86_64'
  jreArch = 'x64'

  def __eq__(self, other):
    return self.name == other.name

  def __repr__(self):
    return self.name


class X86Arch(object):
  name = 'x86'
  eclipseArch = 'x86'
  jreArch = 'i586'

  def __eq__(self, other):
    return self.name == other.name

  def __repr__(self):
    return self.name


class WindowsOs(object):
  name = 'windows'
  eclipseOs = 'win32'
  eclipseWs = 'win32'
  jreOs = 'windows'
  archiveFormat = 'zip'

  def __eq__(self, other):
    return self.name == other.name

  def __repr__(self):
    return self.name

  @staticmethod
  def finalDestination(destination, _):
    return destination

  @staticmethod
  def iniLocation(destination):
    return os.path.join(destination, 'eclipse.ini')

  @staticmethod
  def jreLocation(is64):
    if is64:
      return 'jre\\bin\\server\\jvm.dll'
    else:
      return 'jre\\bin\\client\\jvm.dll'


class MacOs(object):
  name = 'macosx'
  eclipseOs = 'macosx'
  eclipseWs = 'cocoa'
  jreOs = 'macosx'
  archiveFormat = 'gztar'

  def __eq__(self, other):
    return self.name == other.name

  def __repr__(self):
    return self.name

  @staticmethod
  def finalDestination(destination, name):
    return os.path.join(destination, '{}.app'.format(name))

  @staticmethod
  def iniLocation(destination):
    return os.path.join(destination, 'Contents/Eclipse/eclipse.ini')

  @staticmethod
  def jreLocation(_):
    return '../../jre/Contents/Home/bin/java'


class LinuxOs(object):
  name = 'linux'
  eclipseOs = 'linux'
  eclipseWs = 'gtk'
  jreOs = 'linux'
  archiveFormat = 'gztar'

  def __eq__(self, other):
    return self.name == other.name

  def __repr__(self):
    return self.name

  @staticmethod
  def finalDestination(destination, _):
    return destination

  @staticmethod
  def iniLocation(destination):
    return os.path.join(destination, 'eclipse.ini')

  @staticmethod
  def jreLocation(_):
    return 'jre/bin/java'

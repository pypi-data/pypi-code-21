from abc import ABCMeta, abstractmethod
from enum import Enum, unique

_ECLIPSE_OXYGEN_REPOS = [
  'http://download.eclipse.org/releases/oxygen',
  'http://download.eclipse.org/eclipse/updates/4.7',
  'http://download.eclipse.org/technology/epp/packages/oxygen'
]


class Preset(metaclass=ABCMeta):
  @property
  @abstractmethod
  def repositories(self): pass

  @property
  @abstractmethod
  def install_units(self): pass


class PlatformPreset(Preset):
  """
  Eclipse base platform
  """

  @property
  def repositories(self):
    return _ECLIPSE_OXYGEN_REPOS

  @property
  def install_units(self):
    return [
      'org.eclipse.platform.ide',
      'org.eclipse.platform.feature.group',
      'org.eclipse.epp.package.common.feature.feature.group',
      'org.eclipse.equinox.p2.user.ui.feature.group',
      'org.eclipse.epp.mpc.feature.group',
    ]


class JavaPreset(Preset):
  """
  Java development
  """

  @property
  def repositories(self):
    return _ECLIPSE_OXYGEN_REPOS

  @property
  def install_units(self):
    return [
      'epp.package.java',
      'org.eclipse.jdt.feature.group',
      'org.eclipse.recommenders.rcp.feature.feature.group'
    ]


class XMLPreset(Preset):
  """
  XML and co support
  """

  @property
  def repositories(self):
    return _ECLIPSE_OXYGEN_REPOS

  @property
  def install_units(self):
    return [
      'org.eclipse.wst.xml_ui.feature.feature.group',
    ]


class GitPreset(Preset):
  """
  Git support
  """

  @property
  def repositories(self):
    return _ECLIPSE_OXYGEN_REPOS

  @property
  def install_units(self):
    return [
      'org.eclipse.egit.feature.group',
      'org.eclipse.jgit.feature.group',
    ]


class MavenPreset(Preset):
  """
  Maven support, through the M2Eclipse plugin
  """

  @property
  def repositories(self):
    return _ECLIPSE_OXYGEN_REPOS + [
      'http://download.jboss.org/jbosstools/updates/m2e-extensions/m2e-jdt-compiler/',
      'http://download.jboss.org/jbosstools/updates/m2e-extensions/m2e-apt/',
      'http://repo1.maven.org/maven2/.m2e/connectors/m2eclipse-buildhelper/0.15.0/N/0.15.0.201405280027/',
    ]

  @property
  def install_units(self):
    return [
      'org.eclipse.m2e.feature.feature.group',
      'org.jboss.tools.m2e.jdt.feature.feature.group',
      'org.jboss.tools.maven.apt.feature.feature.group',
      'org.sonatype.m2e.buildhelper.feature.feature.group'
    ]


class GradlePreset(Preset):
  """
  Gradle support, through the Buildship plugin
  """

  @property
  def repositories(self):
    return _ECLIPSE_OXYGEN_REPOS

  @property
  def install_units(self):
    return [
      'org.eclipse.buildship.feature.group',
    ]


class PluginPreset(Preset):
  """
  Eclipse plugin development
  """

  @property
  def repositories(self):
    return _ECLIPSE_OXYGEN_REPOS

  @property
  def install_units(self):
    return [
      'org.eclipse.pde.feature.group',
      'org.eclipse.platform.source.feature.group',
      'org.eclipse.pde.source.feature.group',
      'org.eclipse.jdt.source.feature.group',
    ]


class PluginMavenPreset(Preset):
  """
  Maven support for Eclipse plugin development, through the M2Eclipse plugin and Tycho connector
  """

  @property
  def repositories(self):
    return _ECLIPSE_OXYGEN_REPOS + [
      'http://repo1.maven.org/maven2/.m2e/connectors/m2eclipse-tycho/0.7.0/N/LATEST/',
    ]

  @property
  def install_units(self):
    return [
      'org.sonatype.tycho.m2e.feature.feature.group'
    ]


@unique
class Presets(Enum):
  platform = PlatformPreset()
  java = JavaPreset()
  xml = XMLPreset()
  git = GitPreset()
  maven = MavenPreset()
  gradle = GradlePreset()
  plugin = PluginPreset()
  plugin_maven = PluginMavenPreset()

  @staticmethod
  def keys():
    return Presets.__members__.keys()

  @staticmethod
  def exists(preset):
    return preset in Presets.__members__.keys()

  @staticmethod
  def combine_presets(presets):
    repositories = {r for p in presets for r in p.repositories}
    installUnits = {i for p in presets for i in p.install_units}
    return repositories, installUnits

import inspect
import os

from plumbum import cli

from eclipsegen.generate import Os, Arch, EclipseGenerator, DEFAULT_NAME, DEFAULT_ARCHIVE_PREFIX, EclipseMultiGenerator
from eclipsegen.preset import Presets


class EclipseGeneratorCLI(cli.Application):
  PROGNAME = 'eclipsegen'

  def main(self):
    if not self.nested_command:
      print('Error: no command given')
      self.help()
      return 1
    return 0


@EclipseGeneratorCLI.subcommand("list-presets")
class ListPresetsCommand(cli.Application):
  """
  Lists all presets
  """

  def main(self):
    for name, preset in Presets.__members__.items():
      print('  {}: {}'.format(name, inspect.getdoc(preset.value)))
    return 0


@EclipseGeneratorCLI.subcommand("create")
class CreateCommand(cli.Application):
  """
  Generates a single Eclipse instance
  """

  presets = cli.SwitchAttr(
    names=['-p', '--preset'], argtype=str, list=True,
    help='Presets to install. '
         'Choose from: {}. '
         'Run the list-presets command for a more detailed list of presets'
      .format(', '.join(Presets.keys())),
  )

  fixIni = cli.Flag(
    names=['-I', '--no-fix-ini'], default=True,
    help='Do not fix the Eclipse ini file',
  )
  addJre = cli.Flag(
    names=['-j', '--jre'], default=False,
    help='Embed a JRE into the Eclipse instance',
  )
  archive = cli.Flag(
    names=['-a', '--archive'], default=False,
    help='Archive the Eclipse instance. Always true when multiple operating systems or architectures are specified',
  )
  archiveJreSeparately = cli.Flag(
    names=['-e', '--archive-jre-separately'], default=False,
    requires=['--archive'],
    help='Create two archives; one with and one without an embedded JRE',
  )

  name = cli.SwitchAttr(
    names=['-n', '--name'], argtype=str, mandatory=False, default=DEFAULT_NAME,
    help='Name of the application for MacOSX instances, or name of the directory in an archive',
  )
  archivePrefix = cli.SwitchAttr(
    names=['-f', '--archive-prefix'], argtype=str, mandatory=False, default=DEFAULT_ARCHIVE_PREFIX,
    requires=['--archive'],
    help='Prefix for the archive file',
  )
  archiveSuffix = cli.SwitchAttr(
    names=['-s', '--archive-suffix'], argtype=str, mandatory=False,
    requires=['--archive'],
    help='Suffix for the archive file',
  )

  oss = cli.SwitchAttr(
    names=['-o', '--os'], argtype=str, mandatory=False, list=True,
    help='Operating system to generate Eclipse for. '
         'Choose from: {}. '
         'Defaults to OS of this computer: {}'
      .format(', '.join(Os.keys()), Os.get_current().name),
  )
  archs = cli.SwitchAttr(
    names=['-h', '--arch'], argtype=str, mandatory=False, list=True,
    help='Processor architecture to generate Eclipse for. '
         'Choose from: {}. '
         'Defaults to architecture of this computer: {}'
      .format(', '.join(Arch.keys()), Arch.get_current().name),
  )

  extraRepositories = cli.SwitchAttr(
    names=['-r', '--repo'], argtype=str, list=True,
    help='Additional repositories to install units from',
  )
  extraInstallUnits = cli.SwitchAttr(
    names=['-i', '--install'], argtype=str, list=True,
    help='Additional units to install',
  )

  def main(self, destination):
    if os.path.exists(destination):
      if os.path.isdir(destination) and os.listdir(destination):
        print('ERROR: destination {} is not empty'.format(destination))
        return 1
      print('ERROR: destination {} already exists'.format(destination))
      return 1

    presets = []
    for presetStr in self.presets:
      if not Presets.exists(presetStr):
        print('ERROR: preset {} does not exist'.format(presetStr))
        return 1
      presets.append(Presets[presetStr].value)

    oss = []
    if self.oss:
      for osStr in self.oss:
        if not Os.exists(osStr):
          print('ERROR: operating system {} does not exist'.format(osStr))
          return 1
        oss.append(Os[osStr].value)
    else:
      oss.append(Os.get_current())

    archs = []
    if self.archs:
      for archStr in self.archs:
        if not Arch.exists(archStr):
          print('ERROR: architecture {} does not exist'.format(archStr))
          return 1
        archs.append(Arch[archStr].value)
    else:
      archs.append(Arch.get_current())

    repositories, installUnits = Presets.combine_presets(presets)
    repositories.update(self.extraRepositories)
    installUnits.update(self.extraInstallUnits)

    if not repositories:
      print('ERROR: no presets or extra repositories were given')
      return 1
    if not installUnits:
      print('ERROR: no presets or extra units to install were given')
      return 1

    if len(oss) == 1 and len(archs) == 1:
      eclipseOs = oss[0]
      eclipseArch = archs[0]
      generator = EclipseGenerator(workingDir=os.getcwd(), destination=destination, os=eclipseOs, arch=eclipseArch,
        repositories=repositories, installUnits=installUnits, name=self.name, fixIni=self.fixIni, addJre=self.addJre,
        archive=self.archive, archiveJreSeparately=self.archiveJreSeparately, archivePrefix=self.archivePrefix,
        archiveSuffix=self.archiveSuffix)
      print('Generating Eclipse instance for {}, {} to path {}'.format(eclipseOs, eclipseArch, destination))
    else:
      generator = EclipseMultiGenerator(workingDir=os.getcwd(), destination=destination, oss=oss, archs=archs,
        repositories=repositories, installUnits=installUnits, name=self.name, fixIni=self.fixIni, addJre=self.addJre,
        archiveJreSeparately=self.archiveJreSeparately, archivePrefix=self.archivePrefix,
        archiveSuffix=self.archiveSuffix)
      print('Generating Eclipse instances for to path {}'.format(destination))
      print('Operating systems: {}'.format(', '.join([o.name for o in oss])))
      print('Architectures: {}'.format(', '.join([a.name for a in archs])))

    print('Repositories: ')
    for repository in repositories:
      print('  {}'.format(repository))
    print('Units to install: ')
    for installUnit in installUnits:
      print('  {}'.format(installUnit))
    print()

    generator.generate()

    return 0

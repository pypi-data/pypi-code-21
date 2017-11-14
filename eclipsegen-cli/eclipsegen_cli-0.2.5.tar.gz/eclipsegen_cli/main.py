import sys

from eclipsegen_cli.cmd import EclipseGeneratorCLI


def main(*argv, exitAfter=True):
  try:
    if not argv:
      argv = sys.argv
    _, ret = EclipseGeneratorCLI.run(argv=argv, exit=exitAfter)
    return ret
  except KeyboardInterrupt as ex:
    print(ex)

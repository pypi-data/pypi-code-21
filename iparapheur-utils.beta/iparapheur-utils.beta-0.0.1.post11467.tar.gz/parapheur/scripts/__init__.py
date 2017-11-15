import os
import sys
from subprocess import check_call, CalledProcessError


def checkinstallation():
    import checkInstallationIP


def recuparchives():
    import recupArchives


def import_data():
    import import_data


def export_data():
    import export_data


def properties_merger():
    args = sys.argv[1:]
    args.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/shell/properties-merger/properties-merger.sh")
    try:
        check_call(args)
    except CalledProcessError:
        pass

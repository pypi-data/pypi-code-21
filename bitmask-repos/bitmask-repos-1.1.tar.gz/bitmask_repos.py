#!/usr/bin/env python3
import os
import sys
IS_ROOT = os.getuid() == 0

PATH = '/etc/apt/sources.list.d/bitmask.list'
DEBIAN_VERSION = '/etc/debian_version'
DISTROS = ['stretch', 'buster', 'sid', 'zesty']
COMPONENTS = ['release', 'staging', 'master']


def _parse():
    try:
        with open(PATH, 'r') as inputf:
            return inputf.readlines()[0].strip()
    except FileNotFoundError:
        return None


def get_repo_info():
    info = _parse()
    try:
        deb, uri, distro, component = info.split()
        assert deb == 'deb'
        assert uri == 'http://deb.leap.se/client'
        return (distro, component)
    except AttributeError:
        return None


def get_source(distro=None, component=None):
    if distro is None:
        distro = 'stretch'
    if component is None:
        component = 'release'
    return 'deb http://deb.leap.se/client {component} {distro}'.format(
        distro=distro, component=component)


def write_repo_info(distro, component):
    if not IS_ROOT:
        print('[!] Need root to update sources. Run as sudo?')
        sys.exit(1)
    repo_info = get_repo_info()
    if repo_info != (distro, component):
        source = get_source(distro, component)
        with open(PATH, 'w') as outputf:
            outputf.write(source + '\n')


def print_current_setup():
    info = get_repo_info()
    if not info:
        print('[!] Bitmask repo is not set')
        sys.exit(1)
    distro, component = info
    print('[+] Bitmask repo is set for %s/%s' % (distro, component))


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--distro',
        choices=DISTROS, help="set distro",
        default=None)
    parser.add_argument(
        '-c', '--component',
        choices=COMPONENTS, help="set component",
        default=None)
    ns = parser.parse_args()
    if ns.distro is None and ns.component is None:
        print_current_setup()
    else:
        write_repo_info(ns.distro, ns.component)
        print_current_setup()

if __name__ == '__main__':
    main()

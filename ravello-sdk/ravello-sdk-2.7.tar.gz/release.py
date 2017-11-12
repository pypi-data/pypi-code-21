# Copyright 2012-2014 Ravello Systems, Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, print_function

import sys
import subprocess
import argparse
import logging
from setup import version_info as vinfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if sys.version_info[0] == 2:
    input = raw_input


def sh(cmd, *args):
    """Execute shell command *cmd*. Exit on failure."""
    if args:
        cmd = cmd.format(*args)
    ret = subprocess.call(cmd, shell=True)
    if ret == 0:
        return
    logger.error('Error: cmd {0!r} exited with status {1}'.format(cmd, ret), file=sys.stderr)
    sys.exit(1)


def confirm(prompt):
    """Get a confirmation from the user for an action."""
    response = None
    prompt += ' (y/n) '
    while True:
        response = input(prompt)
        if response in 'yn':
            break
        logger.info('Please answer "y" or "n"')
    return response == 'y'


def get_release_versions(script_bool):
    """Prompt the user for the current and next release versions."""
    version = vinfo['version']
    if version.endswith('.dev'):
        logger.info('Current development version: {0}'.format(version))
        relver = version[:-4]
        if not script_bool:
            override = input('What version do you want to release [{0}]: '.format(relver))
            if override:
                relver = override
    else:
        logger.info('Current version is NOT a development version: {0}'.format(version))
        if  not script_bool and not confirm('Do you want to release this version?'):
            return None, None
        relver = version
    try:
        nums = list(map(int, relver.split('.')))
        nums[-1] += 1
        nextver = '.'.join(map(str, nums))
    except ValueError:
        nextver = ''
    if not script_bool:
        override = input('What will be the next version [{0}]: '.format(nextver))
        if override:
            nextver = override
    logger.info('Version to release: {0}'.format(relver))
    logger.info('New version to start: {0}'.format(nextver or '(none)'))
    if not script_bool and not confirm('Is this correct?'):
        return None, None
    return relver, nextver


def confirm_file_list(script_bool):
    """Confirm differences between files in Git and in the sdist."""
    sh('git ls-files | sort > files.git')
    logger.info('Comparing files in git against the source distribution...')
    sh('python setup.py sdist >/dev/null 2>&1')
    sh('tar tvfz dist/ravello-sdk-{0}.tar.gz'
       ' | sed -e \'s/^.*{0}\///\' -e \'/\/$/d\' -e \'/^$/d\''
       ' | sort > files.sdist', vinfo['version'])
    sh('diff -u files.git files.sdist || true')
    sh('rm files.git; rm files.sdist')
    if not script_bool:
        return confirm('Are these changes OK?')
    else:
        return True


def make_release(relver, nextver):
    """Make a release for *relver*. Next version will be *nextver*."""
    logger.info('Creating the release..')
    if relver != vinfo['version']:
        sh('sed -i -e \'s/{0}/{1}/\' setup.py', vinfo['version'], relver)
        sh('git add setup.py')
        sh('git commit -m "version {0}"', relver)
    sh('git tag -a -m "version {0}" {1}-{0}', relver, vinfo['name'])
    sh('python setup.py sdist upload >/dev/null')
    if nextver:
        sh('sed -i -e \'s/{0}/{1}.dev/\' setup.py', relver, nextver)
        sh('git add setup.py')
        sh('git commit -m "start working on {0}"', nextver)
    sh('git push')
    sh('git push --tags')
    logger.info('Done!')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', action='store_true', default=False,
                    dest='script_mode',
                    help='Run the release in script mode , non-interactive')
    parser.add_argument('-c', action='store', dest='current_version',
                     help='Current version')
    parser.add_argument('-n', action='store', dest='next_version',
                     help='Next version')
    results = parser.parse_args()
    logger.info('script_mode  = %s' % results.script_mode)
    logger.info('current_version   = %s' % results.current_version)
    logger.info('next_version      = %s' % results.next_version)
    if results.current_version is not None or results.next_version is not None:
        if results.current_version is not None:
            relver=results.current_version
        if results.next_version is not None:
            nextver=results.next_version
        logger.info('Version to release: {0}'.format(relver))
        logger.info('New version to start: {0}'.format(nextver or '(none)'))
    else:
        relver, nextver = get_release_versions(results.script_mode)
    if relver is None:
        return
    if not confirm_file_list(results.script_mode):
        return
    make_release(relver, nextver)

main()

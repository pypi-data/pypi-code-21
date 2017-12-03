#!/usr/bin/env python
import subprocess
import sys


def run():
    if not getattr(sys, 'base_prefix', ''):
        print('This must be run from within an virtualenv')
        exit(1)

    print('Starting server...')
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'])
    subprocess.run(['python', 'server/manage.py', 'migrate', '--noinput'])
    subprocess.run(['python', 'server/manage.py', 'runserver'])


if __name__ == '__main__':
    run()

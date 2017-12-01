import os
import sys


def main():
    print '\n\nRunning Test Suite...\n\n'
    os.system('nosetests -v --with-coverage --cover-package=cgutils')


if __name__ == '__main__':
    main()

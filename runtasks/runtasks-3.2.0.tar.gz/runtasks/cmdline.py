#!/usr/bin/env python

# The command line utility.  This is called by the shell script and Windows batch file in the
# scripts directory.

import os, sys
from os.path import dirname
from .findfile import findfile

try:
    from importlib.machinery import SourceFileLoader
except ImportError:
    # python 2 won't have SourceFileLoader
    pass

args = None
# Once we parse out any global options, these will be the args tasks and options that
# are procesed by `run`.


def run():
    # Parse the global command line options. (Everything before the first task name, which we
    # assume is the first thing that does not have a dash.)
    #
    # ArgumentParser.parse_known_args looked like it did what we want but it will *skip* things
    # it doesn't recognize and grab arguments from tasks.  That makes no sense to me.  We'll
    # use our own task parser by making a "run" task to deal with the global flags.a
    global args

    def _run(help=False, verbose=False, version=False, list=False, filename='tasks.py'):
        global args

        if help:
            print('run [options] task1 [task options] task2 [task options] ...')
            print('')
            print(' -h --help      show this help message and exit')
            print(' -l --list      list available tasks and documentation')
            print(' -V --version   print version and exit')
            print(' -v --verbose   incrase verbosity')
            print(' -f --filename FILENAME')
            print('                the name of the tasks file to search for')
            return 1

        if version:
            from runtasks import version
            print('runtasks version %s' % version)
            return 1

        # Find the tasks file and load it.

        fqn = findfile(filename=filename)

        m = None
        try:
            l = SourceFileLoader('tasks', fqn)
            m = l.load_module()
        except NameError:
            # If importlib.machinery.SourceFileLoader raised ImportError (aka python 2).
            import imp
            m = imp.load_module('tasks', *imp.find_module('tasks', [dirname(fqn)]))

        # Find all of the functions in the module marked as tasks.

        tasks = {name: func._task for (name, func) in m.__dict__.items() if hasattr(func, '_task')}

        if list:
            from runtasks.lister import print_list
            print_list(tasks)
            return 1

        # Parse the task arguments.

        from runtasks.parser import parse
        parsed = parse(args, tasks)

        # If "--help" was passed for a task, print help for that task and abort.  Do not run
        # any previous tasks since the user is still working on their command line.
        #
        # Also note that there will only be 1 task with help.  Once we hit --help I am not sure
        # that future tokens will be valid.

        for (task, args) in parsed:
            if args == "help":
                from runtasks.lister import print_doc
                print_doc(task)
                return 1

        os.chdir(dirname(fqn))

        for (task, args) in parsed:
            if verbose == 1:
                print(task.name)
            elif verbose > 1:
                print('-' * 80)
                print('Running', task.name)
                print()

            task.call(args)

            if verbose > 1:
                print()

    from runtasks.tasks import Task
    task = Task(
        _run,
        flags={
            'V': 'version',
            'v': 'verbose'
        },
        allow_positional=False
    )
    from runtasks.parser import parse_task
    parsed, args = parse_task(task, sys.argv, [])
    task.call(parsed)

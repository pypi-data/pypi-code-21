import argparse
import sys
import collections

from .pipeline import Pipeline
from .launcher import LocalDockerLauncher, NerscSerialLauncher, PegasusLauncher

parser = argparse.ArgumentParser(description="Manage, build, and launch DESC pipelines")
subparsers = parser.add_subparsers(help="What to do with the pipeline", dest='task')


parser_local = subparsers.add_parser('local', help='Make a bash script to the pipeline locally under docker')
parser_local.add_argument('pipe_file', type=str, help='Input pipeline file to generate a script for')
parser_local.add_argument('script_file', type=str, help='Output bash script to generate')
parser_local.add_argument('-b', "--build",  action='store_true', help='Run "make" in the pipe directories before running')

parser_local = subparsers.add_parser('build', help='Run "make" in the pipe directories')
parser_local.add_argument('pipe_file', type=str, help='Input pipeline file to build')

parser_local = subparsers.add_parser('push', help='Run "make push" in the pipe directories')
parser_local.add_argument('pipe_file', type=str, help='Input pipeline file to push')

parser_local = subparsers.add_parser('nersc', help='Make a bash script to the pipeline under shifter')
parser_local.add_argument('pipe_file', type=str, help='Input pipeline file to generate a script for')
parser_local.add_argument('script_file', type=str, help='Output bash script to generate')

parser_local = subparsers.add_parser('pegasus', help='Make a bash script to the pipeline under shifter')
parser_local.add_argument('pipe_file', type=str, help='Input pipeline file to generate a script for')
parser_local.add_argument('daxfile', type=str, help='Output DAX generation script')
parser_local.add_argument('--tcfile', default='tc.txt', type=str, help='Output transformation catalog')


tasks = {}

def task(function):
    tasks[function.__name__] = function
    return function

@task
def build(args):
    pipeline=Pipeline(args.pipe_file)
    pipeline.build()

@task
def push(args):
    pipeline=Pipeline(args.pipe_file)
    pipeline.push()

@task
def nersc(args):
    pipeline=Pipeline(args.pipe_file)
    launcher=NerscSerialLauncher(pipeline)
    launcher.generate(args.script_file)

@task
def pegasus(args):
    pipeline=Pipeline(args.pipe_file)
    launcher=PegasusLauncher(pipeline)
    launcher.generate(args.daxfile, args.tcfile)



@task
def local(args):
    pipeline=Pipeline(args.pipe_file)
    if args.build:
        pipeline.build()
    launcher=LocalDockerLauncher(pipeline)
    launcher.generate(args.script_file)

def unknown(args):
    sys.stderr.write("Unknown command {}\n".format(args.task))


def main():
    args = parser.parse_args()
    if not args.task:
        parser.print_help()
        return 1
    else:
        task = tasks.get(args.task, unknown)
        return task(args)        

if __name__ == '__main__':
    status = main()
    sys.exit(status)


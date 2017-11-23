"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from __future__ import print_function
import argparse
import signal
from os import getcwd
from time import sleep

import sys

from .vlab import Vlab


def run(args):
    uart_output = args.uart_output != ""
    if (args.uart_output == "stdout"):
        args.uart_output = ""

    trace = args.trace != ""
    if (args.trace == "stdout"):
        args.trace = ""

    jemu = Vlab(working_directory=args.directory, sudo_mode=args.sudo, gdb_mode=args.gdb, 
        print_trace=trace, trace_output_file=args.trace, print_uart=uart_output, uart_output_file=args.uart_output)
    jemu.load(args.bin.name)

    jemu.start()
    print('Virtual device is running')
    while jemu.is_running():
        sleep(0.1)


def signal_handler(signal, frame):
    sys.exit(1)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser(
        prog='jumper',
        description="CLI interface for using Jumper's emulator"
    )
    subparsers = parser.add_subparsers(title='Commands', dest='command')

    run_parser = subparsers.add_parser(
        'run',
        help='Runs an emulator with a binary FW file. Currently only support nRF52 devices'
    )
    run_parser.add_argument(
        '--bin',
        '-b',
        type=file,
        help='Binary file used to generate the FW from',
        required=True
    )
    run_parser.add_argument(
        '--directory',
        '-d',
        help='Working directory, must include the peripherals.json and scenario.json files. Default is current working directory',
        default=getcwd()
    )

    run_parser.add_argument(
        '--sudo',
        '-s',
        help='Run in sudo mode => FW can write to read-only registers. This should usually be used for testing low-level drivers',
        action='store_true',
        default=False
    )

    run_parser.add_argument(
        '--gdb',
        '-g',
        help='Opens a GDB port for debugging the FW on port 5555. The FW will not start running until the GDB client connects.',
        action='store_true',
        default=False
    )

    run_parser.add_argument(
        '--trace',
        '-t',
        type=str,
        help='Prints a trace log to a destination file. To print to stdout, type -t stdout (or --trace=stdout). Every executed instruction will print the value of all of the CPU registers,',
        default=""
    )

    run_parser.add_argument(
        '--uart_output',
        '-u',
        type=str,
        help='Prints the uart prints to a destination file. To print to stdout, type -u stdout (or --uart_output=stdout),',
        default="",
    )

    args = parser.parse_args()

    if args.command == 'run':
        run(args)


if __name__ == '__main__':
    main()

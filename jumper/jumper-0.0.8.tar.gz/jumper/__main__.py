"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from __future__ import print_function
import argparse
import signal
from os import getcwd
from time import sleep
from threading import Event

import sys

from .vlab import Vlab


def run(args):
    vlab = Vlab(
        working_directory=args.directory,
        sudo_mode=args.sudo,
        gdb_mode=args.gdb,
        print_trace=args.trace,
        trace_output_file=args.trace_dest,
        print_uart=args.uart,
        uart_output_file=args.uart_dest
    )
    vlab.load(args.bin.name)
   
    reached_bkpt = Event()

    def bkpt_callback(code):
        print('Firmware reached a BKPT instruction with code {}'.format(code))
        reached_bkpt.set()

    vlab.on_bkpt(bkpt_callback)

    vlab.start()
    print('Virtual device is running')
    while (not reached_bkpt.is_set()) and vlab.is_running():
        sleep(0.1)

    if reached_bkpt and vlab.is_running():
        vlab.stop()


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
        action='store_true',
        help='Prints a trace report to stdout, use this in accordance with --trace-dest to forward it to a file.',
        default=False
    )

    run_parser.add_argument(
        '--trace-dest',
        type=str,
        help=
        """
        Forwards the trace report to a destination file. Use this in accordane with --trace or -t.
        To print to stdout, do not use this flag.
        """,
        default="",
    )

    run_parser.add_argument(
        '--uart',
        '-u',
        action='store_true',
        default=False,
        help='Forwards UART prints to stdout, use this in accordance with --uart-dest to forward it to a file.'
    )

    run_parser.add_argument(
        '--uart-dest',
        type=str,
        help=
        """
        Forwards UART prints to a destination file. Use this in accordane with --uart or -u.
        To print to stdout, do not use this flag.
        """,
        default="",
    )


    args = parser.parse_args()

    if args.command == 'run':
        run(args)


if __name__ == '__main__':
    main()

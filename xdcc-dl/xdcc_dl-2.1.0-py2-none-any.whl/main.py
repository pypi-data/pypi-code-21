u"""
Copyright 2016-2017 Hermann Krumrey

This file is part of xdcc-dl.

xdcc-dl is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

xdcc-dl is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with xdcc-dl.  If not, see <http://www.gnu.org/licenses/>.
"""

# imports
from __future__ import absolute_import
import os
import sys
import argparse
from xdcc_dl.xdcc.XDCCDownloader import XDCCDownloader
from xdcc_dl.tui.XDCCDownloaderTui import XDCCDownloaderTui
from xdcc_dl.entities.XDCCPack import xdcc_packs_from_xdcc_message
from itertools import imap

try:
    from xdcc_dl.gui.XDCCDownloaderGui import start as start_gui
except ImportError:  # pragma: no cover
    start_gui = None


def main():
    u"""
    Starts the main method of the program

    :return: None
    """
    try:

        parser = argparse.ArgumentParser()
        parser.add_argument(u"message", nargs=u'?',
                            help=u"An XDCC Message. "
                                 u"Supports ranges (1-100) and "
                                 u"also ranges with steps (1-100,2)")
        parser.add_argument(u"-s", u"--server",
                            help=u"Specifies the IRC Server. "
                                 u"Defaults to irc.rizon.net")
        parser.add_argument(u"-d", u"--destination",
                            help=u"Specifies the target download destination. "
                                 u"Defaults to " + os.getcwdu())
        parser.add_argument(u"-u", u"--username",
                            help=u"Specifies the username")
        parser.add_argument(u"-v", u"--verbosity", type=int, default=1,
                            help=u"Specifies the verbosity of the output "
                                 u"on a scale of 1-7. Default: 1")
        parser.add_argument(u"-g", u"--gui", action=u"store_true",
                            help=u"Starts the XDCC Downloader GUI")
        parser.add_argument(u"-t", u"--tui", action=u"store_true",
                            help=u"Starts the XDCC Downloader TUI")
        args = parser.parse_args()

        if args.message:

            destination = os.getcwdu() if not args.destination \
                else args.destination

            server = u"irc.rizon.net" if not args.server else args.server
            user = u"random" if not args.username else args.username
            verbosity = args.verbosity

            packs = xdcc_packs_from_xdcc_message(
                args.message, destination, server
            )

            downloader = XDCCDownloader(server, user, verbosity)
            results = downloader.download(packs)
            downloader.quit()

            max_length = max(imap(
                lambda x: len(x.get_filepath()), results.keys()
            ))
            for result in results:
                print_result = result.get_filepath().ljust(max_length) + u" - "
                print_result += results[result]
                print print_result

        elif args.gui:  # pragma: no cover
            if start_gui is not None:
                start_gui()
            else:
                print u"Error: PyQt5 not installed"

        elif args.tui:  # pragma: no cover
            XDCCDownloaderTui().start()

        else:
            print u"No arguments passed. See --help for more details"
            sys.exit(0)

    except KeyboardInterrupt:
        print u"Thanks for using xdcc-dl!"


if __name__ == u"__main__":  # pragma: no cover

    if sys.platform == u"win32" and len(sys.argv) == 1:
        sys.argv.append(u"-g")
    main()

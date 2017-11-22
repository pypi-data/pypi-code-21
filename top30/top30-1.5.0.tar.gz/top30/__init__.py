###########################################################################
# Top30 is Copyright (C) 2016-2017 Kyle Robbertze <krobbertze@gmail.com>
#
# Top30 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Top30 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Top30.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################
"""
Runs the Rundown creator
"""
import argparse
import os
import platform

from top30.chart import Chart
from top30.handlers import UserInterface
from top30.top_30_creator import Top30Creator
from top30.settings import Settings

VERSION = "1.5.0"

def find_file(filename):
    """
    Locates a file. It uses the last one it finds in order:
    ./<filename>
    ~/.<filename>
    <module_path>/<filename>
    /etc/top30/<filename>
    """
    if os.path.isfile(os.path.join(".", filename)):
        return os.path.join(".", filename)
    if platform.system() == 'Linux':
        home = os.path.expanduser(os.path.join(os.getenv('HOME'), "." + filename))
        if os.path.isfile(home):
            return home
        if os.path.isfile(os.path.join("/etc", filename)):
            return os.path.join("/etc", filename)
    elif platform.system() == "Darwin":
        home = os.path.expanduser(os.path.join(os.getenv('HOME'), "." + filename))
        if os.path.isfile(home):
            return home
        #TODO: FINISH
    if os.path.isfile(os.path.join( \
                      __file__[:-len("__init__.py")], filename)):
        return os.path.join(__file__[:-len("__init__.py")], filename)

    raise FileNotFoundError("Unable to find file " + filename)

SETTINGS = Settings()

def main():
    """
    Main function. Runs the program
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--current-chart", dest="current_chart",
                        help="chart document to create the rundowns from, " \
                                "required for command line operation")
    parser.add_argument("-g", "--gui", help="runs the graphical version of Top30",
                        action="store_true")
    parser.add_argument("-p", "--previous-chart", dest="previous_chart",
                        help="the previous chart document, required for " \
                                "command line operation")
    parser.add_argument("-v", "--version", action="store_true",
                        help="prints the version information and exits")
    args = parser.parse_args()
    creator = Top30Creator()
    if args.version:
        print("top30", VERSION)
        print("This project comes with NO WARRENTY, to the extent permitted by the law.")
        print("You may redistribute it under the terms of the GNU General Public License")
        print("version 3; see the file named LICENSE for details.")
        print("\nWritten by Kyle Robbertze")
        return
    if args.gui:
        gui = UserInterface()
        gui.run(creator)
    else:
        if args.previous_chart == None or args.current_chart == None:
            print("Missing chart file arguments")
            parser.print_help()
            exit(120)
        chart = Chart(args.current_chart)
        previous_chart = Chart(args.previous_chart, "last-week_")
        print("Creating 30 - 21 rundown...")
        creator.create_rundown(30, 21, chart)
        print("Creating 20 - 11 rundown...")
        creator.create_rundown(20, 11, chart)
        print("Creating 10 - 2 rundown...")
        creator.create_rundown(10, 2, chart)
        print("Creating last week's 10 - 1 rundown...")
        creator.create_rundown(10, 1, previous_chart)

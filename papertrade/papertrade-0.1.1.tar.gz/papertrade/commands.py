#!/usr/bin/python3

#    This file is part of 'papertrade'.
#
#    papertrade is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    papertrade is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with papertrade.  If not, see <http://www.gnu.org/licenses/>.

import os
import ui
import papertrade as p
import papertrade.database as db

def main():
    info = (
        "    papertrade  Copyright (C) 2017  Svein-Kåre Bjørnsen\n"
        "    This program comes with ABSOLUTELY NO WARRANTY.\n"
        "    This is free software, and you are welcome to redistribute it\n"
        "    under certain conditions; see\n"
        "    https://github.com/morngrar/papertrade/blob/master/LICENSE.md\n"
        "    for details.\n\n"
    )
    print("\n\n" + info)

    if not os.path.exists(p.DBFILE):
        info = ui.underline("New database")
        info += (
            "Couldn't find an existing database. Making new one.\n"
            "What shall be your starting capital?\n"
            "\nEnter staring capital in USD: "
        )
        starting_capital = float(input("\n\n" + info))

        db.generate(p.DBFILE, starting_capital, new=True)

    p.main_menu()

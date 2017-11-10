#!/usr/bin/python3


#    This file is part of 'spendtime'.
#
#    spendtime is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    spendtime is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with spendtime.  If not, see <http://www.gnu.org/licenses/>.



import time
import sqlite3
import sys
import logging
import os

# Imports with dependencies
import ui


try:
    os.remove("spendtime.log")
except:
    pass

# Uncomment if debug log is needed
#logging.basicConfig(filename="timetable.log", level=logging.DEBUG)

DATABASE_FILE = "spendtime.db"

def setup_db():
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    return cursor, connection

def teardown_db(connection):
    connection.commit()
    connection.close()

def generate_db(table = None):
    cursor, connection = setup_db()

    if not table:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS 'Default timetable'"
            "(start REAL PRIMARY KEY, stop REAL, duration INTEGER)"
        )
    else:
        cursor.execute(
            (
                "CREATE TABLE IF NOT EXISTS '{0}'"
                "(start REAL PRIMARY KEY, stop REAL, duration INTEGER)"
            ).format(table)
        )

    teardown_db(connection)


def read_table(table = None):
    cursor, connection = setup_db()

    dblist = []
    if not table:
        cursor.execute("SELECT * FROM 'Default timetable'")
    else:
        cursor.execute("SELECT * FROM '{0}'".format(table))
    data = cursor.fetchall()
    for row in data:
        dblist.append(row)

    teardown_db(connection)
    return dblist



def enter_record(start, stop, duration, table = None):
    cursor, connection = setup_db()

    if not table:
        cursor.execute(
            "INSERT INTO 'Default timetable' VALUES (?, ?, ?)",
            (start, stop, duration)
        )
    else:
        cursor.execute(
            "INSERT INTO '{0}' VALUES (?, ?, ?)".format(table),
            (start, stop, duration)
        )

    teardown_db(connection)

def list_tables():
    cursor, connection = setup_db()
    result = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    )
    returnlist = []
    for data in result:
        returnlist.append(data[0])
    teardown_db(connection)
    return returnlist

def delete_table(tablename):
#    ui.show("This is where a table will be deleted.")
    cursor, connection = setup_db()
    cursor.execute(
        (
            "DROP TABLE IF EXISTS '{0}'"
        ).format(tablename)
    )
    teardown_db(connection)
    return 1

def worktime():
    start = time.time()
    input("Press enter when finished.\n")
    stop = time.time()
    duration = round(stop - start)
    return (start, stop, duration)

def total_seconds(table):
    seconds = 0
    for row in table:
        seconds += row[2]
    return seconds

def run_worktime(table = None):
    stamp = worktime()
    enter_record(stamp[0], stamp[1], stamp[2], table)

    heading = ui.underline("Done!")
    info = (
        "\nTime spent: {0} min\n"
        "In total {1} hours\n"
    ).format(
        round(stamp[2]/60, 1),
        round(total_seconds(read_table(table))/3600, 2)
    )

    ui.show(heading + info)

COPYRIGHT_SHOWN = False

def menu():
    if not COPYRIGHT_SHOWN:
        global COPYRIGHT_SHOWN
        COPYRIGHT_SHOWN = True
        copyright_notice = (
            "\n\n"
            "    spendtime  Copyright (C) 2017  Svein-Kåre Bjørnsen\n"
            "    This program comes with ABSOLUTELY NO WARRANTY.\n"
            "    This is free software, and you are welcome to redistribute it\n"
            "    under certain conditions; see\n"
            "    https://github.com/morngrar/spendtime/blob/master/LICENSE.md\n"
            "    for details.\n\n"
        )
        ui.show(copyright_notice)

    heading = ui.underline("Main menu")
    options = [
        {"key":"l", "text":"List tables", "function":menu_list_tables},
        {"key":"n", "text":"Create new table", "function":menu_new_table}
    ]
    ui.menu(options, heading)


def menu_list_tables():
    def make_lambda(tablename):
        return lambda:menu_table(tablename)
    tables = list_tables()
    heading = ui.underline("Available timetables")
    options = []
    i = 0

    if tables:
        for table in tables:
            i += 1
            options.append(
                {
                    "key":str(i),
                    "text":table,
                    "function":make_lambda(table)
                }
            )
    options.append(
        {
            "key":"n",
            "text":"New table",
            "function":menu_new_table
        }
    )
#    if ui.menu(options, heading):
#        return 1
    ui.menu(options, heading)

def menu_new_table():
    tablename = input("\nName of new table: ")
    generate_db(table = tablename)
    return 1

def menu_table(tablename):
    heading = ui.underline(tablename)
    table = read_table(tablename)

    info = (
        "Total time spent: {0} hours\n"
    ).format(round(total_seconds(table)/3600, 2))

    options = [
        {
            "key":"s",
            "text":"Spend time on this",
            "function":lambda:this_table(tablename)
        },
        {
            "key":"d",
            "text":"Delete this table",
            "function":lambda:delete_table(tablename)
        }
    ]
    ui.menu(options, heading + info)
    return 1

def this_table(text = None):
    """Run worktime with specific table. Fails on non-existing table"""
    global ARGUMENT_TEXT

    if not text:
        ARGUMENT_TEXT = True
        return

    tables = list_tables()
    if text not in tables:
        print("This timetable doesn't exist yet!")
        return

    ui.clear_screen()
    print("Spending time on", text)
    run_worktime(table=text)
    return 1

def print_help():
    info = (
        "Usage: spendtime [[-l][-m][-t tablename][--help]]\n\n"
        "Available options are:\n"
        "-l\t Lists all available timetables\n"
        "-m\t Starts the program in menu-mode\n"
        "-t\t Starts spending time on the specified table\n"
        "-h\t Show this help message\n"
        "--help\t Show this help message"
    )
    print(info)

def main():
    global ARGUMENT_TEXT
    ARGUMENT_TEXT = False   # if true, the argument is text needed for function
    ARGUMENT_DICT = {
        "-m":menu,
        "-t":this_table,
        "-l":menu_list_tables,
        "-h":print_help,
        "--help":print_help
    }

    generate_db()

    last_argument = None
    if len(sys.argv) > 1:
        for argument in sys.argv:
            logging.debug("Start of argument loop: {0}".format(argument))

            if ARGUMENT_TEXT:
                logging.debug("Argument text true")

                ARGUMENT_DICT[last_argument](text = argument)
                ARGUMENT_TEXT = False

                logging.debug("returned from argument function")
            else:
                logging.debug("Argument text false")

                if argument not in ARGUMENT_DICT.keys():
                    logging.debug("Argument not in dict")
                    continue

                logging.debug("calling argument function")
                ARGUMENT_DICT[argument]()

                logging.debug(
                    "returned from argument function(text false)"
                )
            last_argument = argument
    else:
        logging.debug("arguments <= 1")
        run_worktime()

if __name__ == "__main__":
    main()

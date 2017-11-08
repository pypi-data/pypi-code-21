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


import sqlite3

def generate(db_file, starting_capital, new = False):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS total"
        "(post TEXT PRIMARY KEY, value REAL)"
    )

    if new:
        values = [
            ("Capital", starting_capital),
            ("Profit", 0.0),
            ("Loss", 0.0),
        ]
        for e in values:
            cursor.execute(
                "INSERT INTO total VALUES (?, ?)",
                (e[0], e[1])
            )


    cursor.execute(
        "CREATE TABLE IF NOT EXISTS trades"
            "(time INTEGER PRIMARY KEY, "
            "ticker TEXT, "
            "quote INTEGER, "
            "buy REAL, "
            "sell REAL, "
            "prov REAL)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS history"
        "(time INTEGER PRIMARY KEY, "
            "ticker TEXT, "
            "quote INTEGER, "
            "buy REAL, "
            "sell REAL, "
            "prov REAL)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS annualhist"
        "(year INTEGER PRIMARY KEY, capital REAL, profit REAL, loss REAL)"
    )

    connection.commit()
    connection.close()

    print("Done.\n")

def update_total_record(db_file, post, value):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE total SET value = ? WHERE post = ?;",
        (value, post)
    )

    connection.commit()
    connection.close()

def get_capital(db_file):
    data = read_table(db_file, "total")
    return data[0][1]

def get_profit(db_file):
    data = read_table(db_file, "total")
    return data[2][1]

def get_loss(db_file):
    data = read_table(db_file, "total")
    return data[1][1]

def enter_record(db_file, table, row):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    if table == "trades" or table == "history":
        cursor.execute(
            "INSERT INTO {0} VALUES (?, ?, ?, ?, ?, ?)".format(table),
            (row[0], row[1], row[2], row[3], row[4], row[5])
        )
    elif table == "annualhist":
        cursor.execute(
            "INSERT INTO annualhist VALUES (?, ?, ?, ?)",
            (row[0], row[1], row[2], row[3])
        )

    connection.commit()
    connection.close()

def delete_trade(db_file, table, time):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    query = "DELETE FROM {0} WHERE time='{1}'".format(table, time)
    cursor.execute(query)

    connection.commit()
    connection.close()

def read_table(db_file, table):

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    dblist = []

    cursor.execute('SELECT * FROM {0}'.format(table))
    data = cursor.fetchall()

    connection.close()

    return sorted(data)

if __name__ == "__main__":
    generate("test-db.db", new = True)
    data = read_table("test-db.db", "total")
    print(data)
    print(get_capital("test-db.db"))
    update_total_record("test-db.db", "Capital", get_capital("test-db.db")-500000)
    print(get_capital("test-db.db"))

    import random as r
    db = "test-db.db"
    rows = [
        [123, "USDBTC", 9000, 13.45, 0.0, 2.0],
        [124, "ASDFHT", r.randrange(10000), r.randrange(100)+r.randrange(99)/100.0, 0.0, 2.0],
        [125, "UEJ", r.randrange(10000), r.randrange(100)+r.randrange(99)/100.0, 0.0, 2.0],
        [126, "BW", r.randrange(10000), r.randrange(100)+r.randrange(99)/100.0, 0.0, 2.0],
        [127, "QQE", r.randrange(10000), r.randrange(100)+r.randrange(99)/100.0, 0.0, 2.0]
    ]

    for e in rows:
        pass#enter_record(db, "trades", e)

    print(read_table(db, "trades"))

    row = [128, "QQE", r.randrange(10000), r.randrange(100)+r.randrange(99)/100.0, 40.33, 2.0]
    enter_record(db, "history", row)
    delete_trade(db, "trades", 127)

    print(read_table(db, "trades"))

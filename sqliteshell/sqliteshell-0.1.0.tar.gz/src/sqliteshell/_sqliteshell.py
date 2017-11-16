import contextlib
import sqlite3
import textwrap


def shell(conn):
    """Drop into a just-about-tolerable sqlite shell.

    Vaguely resembles the shell provided by sqlite3 itself (but this one works
    with in-memory sqlite db).

    Note that this messes with the isolation level.  It's intended for use in
    tests, I don't recommend it for use in production.

    To use:

    import sqlite3
    import sqliteshell
    conn = sqlite3.connect(':memory:')
    sqliteshell.shell(conn)
    """
    orig_level = conn.isolation_level
    conn.isolation_level = None
    try:
        with contextlib.closing(conn.cursor()) as cur:
            buffer = ""

            def tables():
                """List names of all tables"""
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'")
                tables = [t for [t] in cur.fetchall()]
                print('\n'.join(tables))

            def schema(*tables):
                """Show the CREATE statements

                If there are arguments, only show schemas for the tables listed
                as arguments.
                """
                if len(tables) == 0:
                    cur.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [t for [t] in cur.fetchall()]
                for table in tables:
                    cur.execute(
                        textwrap.dedent("""\
                        SELECT sql FROM sqlite_master
                          WHERE type='table'
                          AND name='{}'""".format(table)))
                    print(table)
                    for [sql] in cur.fetchall():
                        print(sql)
                    print()

            def help():
                """Show this message."""
                print('\n'.join(('.{}  {}').format(name, c.__doc__)
                                for name, c in commands.items()))

            commands = dict(
                tables=tables,
                schema=schema,
                help=help, )

            print('Enter your SQL commands to execute in sqlite3.')
            print('Enter ".help" for usage hints.')

            print('Enter a blank line to exit.')

            while True:
                line = input('sqlite-ish> ')
                if line == "":
                    break

                if line.startswith('.'):
                    cmd_name, _, rest = line[1:].partition(' ')
                    if len(rest) != 0:
                        args = rest.split(' ')
                    else:
                        args = ()
                    command = commands.get(cmd_name)
                    if command is None:
                        print('Unknown command')
                        continue
                    command(*args)
                    continue

                buffer += line
                if sqlite3.complete_statement(buffer):
                    try:
                        buffer = buffer.strip()
                        cur.execute(buffer)

                        if buffer.lstrip().upper().startswith("SELECT"):
                            print(cur.fetchall())
                    except sqlite3.Error as e:
                        print("An error occurred:", e.args[0])
                    buffer = ""
    finally:
        conn.isolation_level = orig_level

import sqlite3 as lite

con = None
cur = None

def sqLen(tabella):
    global con
    global cur
    #len table
    lineaSql = ('SELECT * FROM ' + tabella)
    #cur.execute("SELECT * FROM myTable")
    cur.execute(lineaSql)
    rows = cur.fetchall()
    return len(rows)

def sqOpen(path):
    global con
    global cur
    con = lite.connect(path)
    cur = con.cursor()
    print 'open'

def sqClose():
    global con
    global cur

    print 'close'
    con.commit()
    cur.close()

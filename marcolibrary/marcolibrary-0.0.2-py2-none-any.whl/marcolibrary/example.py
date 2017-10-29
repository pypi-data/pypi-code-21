#import mysqlite
from marcolibrary import *

mypath = '/home/pi/Desktop/SQLITE/Databases/Casanova5min.db'
tabella = 'myTable'


mysqlite.sqOpen(mypath)
print mysqlite.sqLen(tabella)
mysqlite.sqClose()

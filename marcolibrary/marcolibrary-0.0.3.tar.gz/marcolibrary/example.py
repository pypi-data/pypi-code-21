#import mysqlite

import sys

try:
    from marcolibrary import *
except ImportError:
    print('importa libreria: pip install marcolibrary')
    sys.exit()
    
    
#sqlite    
mypath = '/home/pi/Desktop/SQLITE/Databases/Casanova5min.db'
tabella = 'myTable'
mysqlite.sqOpen(mypath)
print mysqlite.sqLen(tabella)
mysqlite.sqClose()
print('__________________')


data = myTime.getTime13()
data2 = myTime.from13ToData(data)
print data2

data = myTime.getTime10()
data2 = myTime.from10ToData(data)
print data2


print myUrl.myIpPublic()


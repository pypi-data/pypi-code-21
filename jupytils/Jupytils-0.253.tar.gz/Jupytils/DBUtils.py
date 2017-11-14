##---------------------------------------------------------------------
## DB Utilities 
# First: run a localconnection for postgres to connect locally:
# ssh -i "schas.pem"  -N -L 5400:localhost:5432 centos@35.160.151.26

import re;
import numpy as np
import collections
from collections import defaultdict
import pandas as pd;
import datetime

import sqlalchemy
from sqlalchemy import Sequence, inspect, create_engine
from sqlalchemy.engine import reflection

#----------------------------------------------------------------------
class DBUtils:
    RE=[
        re.compile("(.*?)#--------*", re.M|re.DOTALL),
        re.compile("(\$\w*)", re.M|re.DOTALL)
    ];

#----------------------------------------------------------------------
    def __init__(self, conn = 'postgresql://postgres:postgres@localhost:5400/SCHASDB'):
        self.meta = sqlalchemy.MetaData()
        try:
            self.engine = create_engine(conn)
            self.insp = reflection.Inspector.from_engine(self.engine)
            self.QCACHE=defaultdict(None)
            self.error = None
        except Exception as e: 
            ret = "Exception: " + str(e)
            print(ret);
            self.error = ret 
        #self.meta.reflect(engine)  # <==== THIS TAKES LONG TIME - RUN IT ONLY ONCE
#----------------------------------------------------------------------
    def Connect(self):
        c = self.engine.connect()
        return c;
#----------------------------------------------------------------------
    def execQ(self, q="SELECT * from test", limit=1000, printTime=False):
        a = datetime.datetime.now()
        try:
            c = self.Connect()
            df = None;
            df = pd.read_sql(q, c)
            if (printTime):
                b = datetime.datetime.now()
                d = b - a
                print(d)
        except Exception as e: 
            ret = "Exception: " + str(e)
            print(ret);
            return ret
        else:
            c.close()

        return df;
#----------------------------------------------------------------------
    def _getID_Query(q):
        q = q.strip()
        l = q.split("\n")    
        id = l[0].strip()
        qq = '\n'.join(l[1:])
        return id, qq
#----------------------------------------------------------------------
    def prepare(qq="select * from test where id=$TAGID and name=$NAME", params={'TAGID': 1}):
        mytemp="^^^DO_NOT_REPLACE^^^"
        qt = qq.replace("$$", mytemp)
        tags = re.findall(DBUtils.RE[1], qt)
        qt = qt.replace(mytemp, '$')

        tags=sorted(set(tags), reverse=True)

        for t in tags:
            id = t[1:]
            if( id in params):
                qt = qt.replace(t, str(params[id]) )
            else:
                qt = qt.replace(t, id)
        return qt, tags
#----------------------------------------------------------------------
    def load(self, file=None, SQL= None, clearAll=True, debug=False):
        if (clearAll): self.QCACHE.clear()
        self.SQL =SQL;
        if (SQL is None):
            with(open(file, "r")) as f:
                self.SQL = f.read()
        qs = re.findall(DBUtils.RE[0], self.SQL)
        for q in qs:
            id, qq = DBUtils._getID_Query(q)
            self.QCACHE[id]= qq
            if (debug): print(id + " =++++= ", qq)
            
    def dump(self):
        i = 0
        for q in sorted(self.QCACHE.keys()):
            qu = (self.QCACHE[q])
            qt, tags = DBUtils.prepare(qu)
            ret += ("[{}: {} ==> {}]  [{}] ".format(q, qu, qt, tags) )
        print(ret)
        return 
        
    def test():
        SQL='''
1
-- comment
SELECT * from loc ORDER BY id DESC LIMIT 1000
#--------------------------------------------------------------------------
2  
SELECT ID  from $id = $id 
#--------------------------------------------------------------------------
3
UPDATE id = $id $fg = $iddd uid=$uid $$$$$$fg
#--------------------------------------------------------------------------'''
        params={'id': 1}
        for q in QCACHE:
            qu = (QCACHE[q])
            qt, tags = prepare(qu, params)
            print ("[{} ==> {}]  [{}] ".format(qu, qt, tags) ) 

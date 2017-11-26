#!/usr/local/bin/python
from flask import Flask
from flask import request
from flask import Response
import traceback, sys, datetime
from Jupytils.DBUtils import DBUtils

app = Flask(__name__)
#----------------------------------------------------------------------
class FlaskSQLWS:
    def __init__(self):
        pass;
#----------------------------------------------------------------------
    @app.route('/', methods=['POST', 'GET', 'OPTIONS', 'HEAD'])
    def ws():
        defr = '''Data Service: Version 1.0'''
        return Response(defr, mimetype='text');
#----------------------------------------------------------------------
    @app.route('/echo', methods=['POST', 'GET', 'OPTIONS', 'HEAD'])
    def echo():
        tags = [t+"="+request.args[t] for t in request.args ]
        reqs =  str(request.json)
        t = str(tags)  + "\n" + reqs + "\n"
        return t
#--------------------------------------------------------------------------
    @app.route('/q/<qid>/', methods=['POST', 'GET', 'OPTIONS', 'HEAD'])
    @app.route('/q/<type>/<qid>/', methods=['POST', 'GET', 'OPTIONS', 'HEAD'])
    def q(type = 'html', qid=''):
        if ( qid in db.QCACHE ):
            q1 = db.QCACHE[qid]
        else:
            q1 = qid;

        try: 
            q2, tags = DBUtils.prepare(q1, request.args);
            if (type not in ['html', 'text', 'json', 'csv'] ):
                type = 'html';
            print(q2, " ==>", type)
            df = db.execQ(q2)

            if (type == 'html'):
                r = q2 + "<br/><br/>"
                r = r + df.to_html();
                return Response(r, mimetype='text/html');
            elif (type == 'text' or type == 'csv' ):
                r = df.to_csv(index=False);
                return Response(r, mimetype='text');
            else:
                r = df.to_json();
                return Response(r, mimetype='text/json');
        except Exception as E:
            #E = sys.exc_info()[0]
            traceback.print_exc(file=sys.stdout)
            r = "Exception: " + qid + ":" + type + "\n\n" + q1 + "\n\n" + q2 + "\n\n"+ str(E) +"\n"+df;
            return Response(r, mimetype="text");
#--------------------------------------------------------------------------
    @app.route('/dump', methods=['POST', 'GET', 'OPTIONS', 'HEAD'])
    def dump():
        ret = db.SQL
        return  Response(ret, mimetype='text')
#---------------------------------------------------------------------
    def start(self, port=8500, sqlText=None, conn=None):
        global db;
        if (sqlText is not None):
            db = DBUtils(conn = conn);
            db.load(file=sqlText);

        print( "Starting at port: ", port)
        app.run(debug=True, host="0.0.0.0", port=port)
#--------------------------------------------------------------------------
if __name__ == '__main__':
    import os.path;
    if not os.path.exists('SQL.txt'):
        with open("SQL.txt", "w") as f:
            f.write("#---------\nex1\n\nSELECT * from test Limit 10\n#---------")

    s = "SQL.txt";
    conn = 'postgresql://postgres:postgres@localhost/SCHASDB'
    f = FlaskSQLWS()
    f.start(sqlText=s, conn=conn)
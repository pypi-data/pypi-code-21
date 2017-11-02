from bobo.image import Image, ImageDetection
from bobo.video import VideoDetection
from janus.template import GalleryTemplate
import numpy as np
from bobo.util import load, saveas, Stopwatch
from StringIO import StringIO
import dill
import os, re, sys, time, math, socket, datetime
import bobo.app
from itertools import product

class Tracker(object):
    def __init__(self, trackid=1):
        self.imscene = []
        self.trackid = int(trackid)
        
    def __call__(self, im, minOverlap=0.1):
        """ Given SceneDetection, assign bounding boxes to prior SceneDetection and update category with a trackid """
        if len(im) == 0 or len(self.imscene) == 0:
            self.imscene = im.clone()
            for im in self.imscene.objects():
                c = '%s-%d' % (im.category(), self.trackid)
                im = im.category(c)
                self.trackid += 1
        else:
            S = [imp.bbox.overlap(imq.bbox)for (imp, imq) in product(im.objects(), self.imscene.objects())]  # pairwise overlap
            S = np.array(S).reshape(len(im), len(self.imscene))
            for i in range(0,S.shape[0]):
                k = np.argmax(S[i,:])
                if S[i,k] > minOverlap:
                    S[:,k] = 0  # best first assignment
                    im[i].category(self.imscene[k].category())
                else:
                    c = '%s-%d' % (im[i].category(), self.trackid)  # new object
                    im[i].category(c)
                    self.trackid += 1                    
            self.imscene = im.clone()
                
        return self.imscene.clone()

    def track(self, im, minOverlap=0.1):
        return self.__call__(im, minOverlap)
    
    def birth(self, imscene, minOverlap=0.1):
        P = set([im for im in self.imscene])  # previous categories
        Q = set([im for im in self.__call__(imscene, minOverlap)])  # current categories
        return list(Q-P)  # new image detections in Q not in P

    def show(self):
        return self.imscene.show(figure=1)
        
class FaceRecognition(object):
    def __init__(self):
        self.f_serialize = (lambda v: dill.dumps(v).encode('hex'))
        self.f_deserialize = (lambda s: dill.loads(s.decode('hex')))
                
    def client(self, f_tracker, ipaddr='127.0.0.1', port=9999, sleep=1.0, iterations=10000):
        """ run face detection locally on client, serialize to known port"""

        # Create server socket 
        socket.setdefaulttimeout(None)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((ipaddr, port))
        s.listen(1)         
        (conn, addr) = s.accept()                

        # Client loop (fixed iterations)
        for n in range(0, int(iterations)):
            v = f_tracker()
            try:
                # http://stackoverflow.com/questions/19551805/send-multiple-data-text-and-images-to-a-server-through-a-socket
                BUFFER_SIZE = 1024  #normally 1024
                full_payload = StringIO(self.f_serialize(v))
                current_payload = full_payload.read(BUFFER_SIZE)
                while current_payload:
                    #print "sending ",len(current_payload)," bytes"
                    conn.send(current_payload)
                    current_payload = full_payload.read(BUFFER_SIZE)
                conn.send('\n')  # final newline for TextStream
            except socket.error, e: # catch a broken pipe
                raise
            time.sleep(sleep)
        return None

    
    def server(self, f_video2id, f_id2db, ipaddr="127.0.0.1", port=9999, interval=5):
        """ run streaming face detection on server, unserialize and process"""

        # Create a local StreamingContext with four working threads and batch interval of 1 second
        from pyspark.streaming import StreamingContext
        sc = bobo.app.init(appName='StreamingFaceRecognition')
        ssc = StreamingContext(sc, interval)
        rdd = (ssc.socketTextStream(ipaddr, port)  # listen from local socket
                  .map(lambda s: self.f_deserialize(s))  # deserialize to video object
                  .map(f_video2id) # video object to identity
                  .map(f_id2db)  # store identity response to database
                  #.foreachRDD(lambda x: x.foreach(f_id2db) if not x.isEmpty() else None))  # store identity response to database
                  .pprint())
            
        # Block
        ssc.start()             # Start the computation, client must already have created socket
        ssc.awaitTermination()  # Wait for the computation to terminate
                                  

    
class BiometricsDB(object):
    def __init__(self, host='str.cyx2eauxjhnl.us-east-1.rds.amazonaws.com', user='root', passwd='strjanus', port=3306, db='STR', table='DETECTIONS'):
        """ This uses Jeff's Amazon RDS credentials """
        import pymysql
        self.con = pymysql.connect(host=host, user=user, passwd=passwd, port=port)
        self.cur = self.con.cursor()
        self.cur.execute('CREATE DATABASE IF NOT EXISTS %s' % db)
        self.cur.execute('USE %s' % db)        
        self.dbname = db
        self.tblname = table.upper()
        
    def __del__(self):
        self.con.close()

    def close(self):
        self.con.close()

    def initialize(self, d):
        """Delete entire database and create table in database with example dictionary"""
        self.cur.execute('DROP DATABASE %s' % self.dbname)
        self.cur.execute('CREATE DATABASE %s' % self.dbname)
        self.cur.execute('USE %s' % self.dbname)
        schema = {"<type 'str'>":'varchar(32)', "<type 'int'>":'Int', "<type 'float'>":'Float'}
        s = ', '.join(['%s %s' % (k, schema[str(type(v))]) for (k,v) in sorted(d.iteritems())])    
        sql = 'CREATE TABLE %s ( Timestamp Int, %s );' % (self.tblname, s)
        self.cur.execute(sql)
        self.con.commit()
        return self
                        
    def write(self, d):
        """Write dictionary to database"""
        if d is not None and len(d) > 0:
            print '[BiometricsDB.write]: writing key (%s,%s)' % (str(d.keys()), str(d.values()))
            v = ",".join(["'%s'" % str(v) for (k,v) in sorted(d.iteritems())])
            sql = "INSERT INTO %s VALUES (UNIX_TIMESTAMP(), %s);" % (self.tblname, v)  # unix timestamp is UTC, convert on query to eastern
            self.cur.execute(sql)        
            self.con.commit()
        return d
        
    def query(self, sql):
        self.cur.execute(sql)
        return self.cur.fetchall()
        #d.query('SELECT FROM_UNIXTIME(Timestamp) from DETECTIONS');  a[0].ctime()
    
    

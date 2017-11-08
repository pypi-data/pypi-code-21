from __future__ import generators
import requests
from django.db import connections
import vertica_python
from .logger import logging
import threading
import uuid
from django.core import cache as clarity_cache

class HCEntityFactory:
    factories = {
        'SERVICES':'Service',
        'VERTICA':'Vertica',
        'DATABASES':'Djangodb',
        'CACHES':'Cache'

    }

    def addFactory(id, class_name):
        HCEntityFactory.factories.put[id] = class_name

    addFactory = staticmethod(addFactory)


    def createHCEntity(class_name,info):
        if not HCEntityFactory.factories.has_key(class_name):
            raise NotImplementedError("Invalid factory key: {0}".format(class_name))

        obj = eval(HCEntityFactory.factories[class_name] + '.Factory()')
        return obj.create(info)

    createHCEntity = staticmethod(createHCEntity)


class HCEntity(object): pass


class Service(HCEntity):
    def __init__(self,urls):
        self.urls = urls
    def check_status(self):

        status_dict= {}

        for serv, url in self.urls.iteritems():
            logging.info("checking service : %s".format(url))
            try:
                r = requests.get(url)
                if r.status_code == 200:
                    status = 1
                    logging.info("Successful")
                else:
                    status = 0
                    logging.info("Service is down")
            except Exception as ex:
                status = 0
                logging.error("Error while checking status of %s, %s".format(url, str(ex)))
            status_dict[serv] = status

        return status_dict

    class Factory:
        def create(self,info): return Service(info)


class Datasource(HCEntity): pass

class Vertica(Datasource):
    def __init__(self,conn_info):
        self.conn_info = conn_info

    def check_status(self):
        status_dict= {}
        try:
            logging.info("Checking VERTICA Health Status ...")
            connection = vertica_python.connect(**self.conn_info)
            cur = connection.cursor()
            cur.execute("select table_id from columns limit 1")
            result = cur.fetchall()
            connection.close()

            if len(result) == 1:
                self.status=1
                logging.info("VERTICA is UP")
            else:
                self.status=0
                logging.info("VERTICA has NO data")

        except Exception as ex:
            self.status=0
            logging.info("Error Connecting Vertica with {0}".format(str(ex)))

        status_dict["Vertica"]=self.status

        return status_dict

    class Factory:
        def create(self,conn_info): return Vertica(conn_info)

class Djangodb(Datasource):
    time_limit = 5.0
    def __init__(self,databases):
        self.databases = databases

    def hc_database(self,db, status):
        status[db] = 0
        logging.info("Checking Health for DB : {0} ...".format(db))
        try:
            conn = connections[db]
            conn.introspection.table_names()
            conn.close()

            status[db] = 1
            logging.info("DB : {0} is UP".format(db))
        except Exception as ex:
            status[db] = 0
            logging.error("DB : {0} is DOWN with {1}".format(db, str(ex)))

    def check_status(self):
        status = {}
        threads = [threading.Thread(target=self.hc_database, args=(db, status)) for db in self.databases]
        for thread in threads:
            thread.start()
            thread.join(self.time_limit)
        return status
    class Factory:
        def create(self,databases): return Djangodb(databases)


class Cache(Datasource):
    def __init__(self,caches):
        self.caches = caches

    def check_status(self):
        status = {}

        key = 'CHC_{}'.format(uuid.uuid4())
        value = 'CHC'

        for cache_name in self.caches:
            try:
                cache = clarity_cache.caches[cache_name]

                logging.info("Checking Health for CACHE : {0} ...".format(cache_name))

                if cache.set(key, value):
                    if cache.delete(key) > 0:
                        status[cache_name] = 1
                    else:
                        status[cache_name] = 0
                else:
                    status[cache_name] = 0

                logging.info("CACHE : {0} is UP".format(status[cache_name]))
            except Exception as ex:
                status[cache_name] = 0
                logging.error("Error while connecting to CACHE : {0}".format(str(ex)))

        return status

    class Factory:
        def create(self,caches): return Cache(caches)
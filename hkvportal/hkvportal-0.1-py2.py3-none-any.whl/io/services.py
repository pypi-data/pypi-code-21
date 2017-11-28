
# coding: utf-8

# In[1]:

################################
#### Author: Mattijn van Hoek ##
####  While working for HKV   ##
####     Date 2017/06/28      ##
####     Version: 0.1.1       ##
################################
import zeep
from datetime import datetime, timezone, timedelta
import pytz
import pandas as pd
from hkvportal.io import untangle
import geopandas as gpd
import json
import types
from shapely.geometry import Point
import io
import gzip
import requests
import urllib.parse
import fire

try:
    get_ipython().magic('matplotlib inlinde')
except:
    pass


# In[2]:

class dataportal(object):
    """
    hkv dataportal to create/update databases, set and get entries.
    """    
    class errors(object):
        """
        error class with different errors to provide for fewsPi
        """        
        def nosetDataservice():     
            raise AttributeError('dataservice not known. set first using function setDataservice()') 

    def setDataservice(self, dataservice, dump=False):
        """
        function to set URL for dataservice to be used in other functions
        
        Parameters
        ----------
        dataservice: str
            URL of dataservice instance (eg. 'http://85.17.82.66/dataservices/')
        """
        setattr(dataportal, 'dataservice', dataservice)
        wsdl = urllib.parse.urljoin(self.dataservice,'data.asmx?WSDL')     
        self.client = zeep.Client(wsdl=wsdl)    
        if dump == False:
            return print('dataservice is set.',self.dataservice, 'will be used as portal')
        if dump == True:
            return self.client.wsdl.dump()

    def createDatabase(self,database):
        """
        Create database
        
        Parameters
        ----------
        database: str
            name of database instance (eg. 'Myanmar')        
        """
        if not hasattr(self, 'dataservice'):
            self.errors.nosetDataservice()

        url = urllib.parse.urljoin(self.dataservice,'database.asmx/create?database='+database)
        r = requests.get(url)
        return r.json()

    def listDatabase(self,database):
        """
        Check database info
        
        Parameters
        ----------
        database: str
            name of database instance (eg. 'Myanmar')        
        """
        if not hasattr(self, 'dataservice'):
            self.errors.nosetDataservice()        
        url = urllib.parse.urljoin(self.dataservice,'data.asmx/list?database='+database)
        r = requests.get(url)
        return r.json()

    def setEntryDatabase(self,database,key,data,description=''):
        """
        Set/create/insert new entry in database
        
        Parameters
        ----------
        database: str
            name of database instance (eg. 'Myanmar') 
        key: str
            key to identify datarecord in the database (eg. 'parameter|location|unit')
        data: obj
            object to store in the datarecord (eg. JSON object)
        description: str
            description of the datarecord (default = '')
        """
        if not hasattr(self, 'dataservice'):
            self.errors.nosetDataservice() 
        
        # Set data using create datarecord
        zeep_out = self.client.service.create(database=database, key=key,description=description,data=data)
        return json.loads(zeep_out)

    def updateEntryDatabase(self,database,key,data,description=''):
        """
        Update existing  entry in database
        
        Parameters
        ----------
        database: str
            name of database instance (eg. 'Myanmar') 
        key: str
            key to identify datarecord in the database (eg. 'parameter|location|unit')
        data: obj
            object to store in the datarecord (eg. JSON object)
        description: str
            description of the datarecord (default = '')
        """
        if not hasattr(self, 'dataservice'):
            self.errors.nosetDataservice() 
        
        # Set data using create datarecord
        zeep_out = self.client.service.update(database=database, key=key,description=description,data=data)
        return json.loads(zeep_out)        

    def getEntryDatabase(self,database, key):
        """
        Get entry after create/insert
        
        Parameters
        ----------
        database: str
            name of database instance (eg. 'Myanmar') 
        key: str
            key to identify datarecord in the database (eg. 'parameter|location|unit')       
        """
        if not hasattr(self, 'dataservice'):
            self.errors.nosetDataservice()        
        url = urllib.parse.urljoin(self.dataservice,'data.asmx/read?database='+database+'&key='+key)
        print (url)
        r = requests.get(url)
        return r.json()

    def deleteEntryDatabase(self,database, key):
        """
        Delete entry from database
        
        Parameters
        ----------
        database: str
            name of database instance (eg. 'Myanmar') 
        key: str
            key to identify datarecord in the database (eg. 'parameter|location|unit')       
        """        
        # delete data from database
        if not hasattr(self, 'dataservice'):
            self.errors.nosetDataservice()        
        url = urllib.parse.urljoin(self.dataservice,'data.asmx/delete?database='+database+'&key='+key)
        r = requests.get(url)
        return r.json()

    
if __name__ == '__main__':
    try:
        # for command line requests
        fire.Fire(dataportal)
        #pi = pi()
    except:
        # for jupyter notebooks
        #pi = pi()
        pass



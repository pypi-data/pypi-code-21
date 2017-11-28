# coding: utf-8
"""
    assetic.layertools  (layertools.py)
    Tools to assist with using arcgis integration with assetic
"""
from __future__ import absolute_import

import arcpy
import assetic
import os

from .__version__ import __version__
from .settings.assetic_esri_config import LayerConfig

def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

@singleton
class Config(object):
    """
    class to initialise
    """
    def __init__(self):
        """
        Constructor of the class.
        """
        #,configfile=None,inifile=None,logfile=None,loglevelname=None
        self.asseticsdk = None
        self.layerconfig = None
        self.loglevel = None
        self.logfile = None

        #set the logger for this package (to separate from assetic logger)
        #self.logger = logging.getLogger("assetic_esri")
        

class Initialise(object):
    def __init__(self,configfile=None,inifile=None,logfile=None,loglevelname=None):
        """
        Constructor of the class.
        :Param configfile: the name of the XML config file with ESRI to Assetic
        field mappings. If none then will look in the users appdata\Assetic
        folder for arcmap_edit_config.xml
        :Param inifile: the file name (including path) of the ini file
        (host, username, api_key).
        If none then will look in local folder for assetic.ini
        ,else look in environment variables for asseticSDKhost, asseticSDKusername
        ,asseticSDKapi_key
        :Param logfile: the file name (including path) of the log file.
        If None then no logfile will be created
        :Param loglevelname: set as a valid logging level description e.g. INFO
        """
        config = Config()
        #read xml config file if one was passed in
        if configfile != None:
            config.layerconfig = LayerConfig(configfile)

        #check of log level is defined in config file and use that
        if config.layerconfig.loglevel == None:
            if loglevelname == None:
                loglevelname="Info"
        else:
            loglevelname = config.layerconfig.loglevel
            
        #check of log file name defined in config file and use that
        #otherwise use the value passed in
        if config.layerconfig.logfile != None:
            logfile = config.layerconfig.logfile

        #initialise the assetic sdk library
        config.asseticsdk = assetic.AsseticSDK(inifile,logfile,loglevelname)
        msg = "Initiated Assetic-ESRI. Version {0}".format(__version__)
        config.asseticsdk.logger.info(msg)

##        # Log format
##        logger_format = '%(asctime)s %(levelname)s %(message)s'                      
##        # log file location
##        if config.layerconfig.logfile != None:
##            logger_file_handler = logging.FileHandler(
##                config.layerconfig.logfile)
##            logger_file_handler.setFormatter(logger_format)
##            self.logger.addHandler(logger_file_handler)
##        else:
##            logger_stream_handler = logging.StreamHandler()
##            logger_stream_handler.setFormatter(logger_format)
##            self.logger.addHandler(self.logger_stream_handler)
##        #log level
##        if config.layerconfig.loglevel != None:
##            #self.logger["assetic_esri_logger"].setLevel = config.layerconfig.loglevel
##            self.logger.setLevel = logging.DEBUG

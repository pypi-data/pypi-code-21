# -*- encoding: utf-8 -*-
##############################################################################
#
#    Acrisel LTD
#    Copyright (C) 2008- Acrisel (acrisel.com) . All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
'''
Created on Sep 21, 2017

@author: arnon
'''
import logging
from copy import copy
from datetime import datetime
from acrilib import get_hostname, get_ip_address


class LoggerAddHostFilter(logging.Filter):
    """
    This is filter adds host information to LogRecord.
    """

    def filter(self, record):

        if not hasattr(record, 'host'):
            record.host = get_hostname()
        if not hasattr(record, 'host'):
            record.ip = get_ip_address()
        return True


class MicrosecondsDatetimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = datetime.fromtimestamp(record.created)
        
        if ct is  None:
            ct=datetime.now()
            
        if datefmt is not None:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s.%03d" % (t, record.msecs)
            
        return s


class LevelBasedFormatter(logging.Formatter):
    
    defaults={
        logging.DEBUG : u"%(asctime)-15s: %(process)-7s: %(levelname)-7s: %(message)s: %(module)s.%(funcName)s(%(lineno)d)",
        'default' : u"%(asctime)-15s: %(process)-7s: %(levelname)-7s: %(message)s",
        }
 
    def __init__(self, level_formats={}, datefmt=None):
        super(LevelBasedFormatter, self).__init__()
        formats = LevelBasedFormatter.defaults
        if level_formats:
            formats = copy(LevelBasedFormatter.defaults)
            formats.update(level_formats)
            
        self.datefmt = datefmt  
        self.formats = dict([(level, MicrosecondsDatetimeFormatter(fmt=fmt, datefmt=self.datefmt)) for level, fmt in formats.items()])
        self.default_format = self.formats['default']  

    def format(self, record):
        formatter = self.formats.get(record.levelno, self.default_format,)
        result = formatter.format(record)
        return result

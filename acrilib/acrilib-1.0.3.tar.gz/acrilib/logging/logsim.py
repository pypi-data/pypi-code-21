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
Created on Oct 11, 2017

@author: arnon
'''

class LogSim(object):
    def __init__(self, file=None):
        self.file = file
        if file:
            self.file = open(file, 'w')
    
    def debug(self, msg):
        self._print('debug', msg)
    
    def info(self, msg):
        self._print('info', msg)
    
    def warning(self, msg):
        self._print('warning', msg)
    
    def error(self, msg):
        self._print('error', msg)
    
    def critical(self, msg):
        self._print('critical', msg)
        
    def _print(self, key, msg):
        print("{}: {}".format(key, msg), file=self.file)
        
    def close(self):
        if self.file:
            self.file.close()
            
    def __del__(self):
        self.close()


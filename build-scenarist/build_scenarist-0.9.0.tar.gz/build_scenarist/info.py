# -*- coding: UTF-8 -*-
 
import os
import platform
import build_scenarist.utility
from build_scenarist.config import scriptNameEnding

class Info:
    def osName(self):
        return platform.system().replace('"', '')
    
    def distName(self):
        distName = "None_None"
        if self.osName() == "Linux":
            distName = platform.dist()[0].replace('"', '')+'_'+platform.dist()[1].replace('"', '')
        elif self.osName() == "Windows":
            distName = platform.win32_ver()[0].replace('"', '')+'_'+platform.win32_ver()[1].replace('"', '')
        return distName

    def fullPlatformName(self):
        return self.osName() + '_' + self.distName()

    def defaultScriptName(self):
        return self.fullPlatformName() + scriptNameEnding

    def scriptName(self, osName, distName, distVer):
        return osName + '_' + distName + ' ' + distVer + scriptNameEnding

    def about_platform(self):
        return """            OS name: {0}
          Dist name: {1}
Default script name: {2}""".format(self.osName(), self.distName(), self.defaultScriptName())

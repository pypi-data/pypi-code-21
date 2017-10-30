# -*- coding: UTF-8 -*-
 
import sys
import argparse
import re
import os
import platform

from subprocess import call
import subprocess
import shlex

from os.path import exists, isfile, join
from os import makedirs, listdir

from build_scenarist.config import scriptNameEnding, bcolors

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        try:
            os.chdir(self.newPath)
        except OSError:
            raise Exception(bcolors.FAIL + "Path: {0}. No such file or directory!".format(self.newPath) + bcolors.ENDC)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def runShell(cmd, fallAtFail=True):
    sys.stdout.write("\n" + bcolors.HEADER + "shell: " + bcolors.ENDC + "\n")
    sys.stdout.write(bcolors.BOLD + cmd + bcolors.ENDC + "\n")
    sys.stdout.flush()
    retCode = subprocess.call(shlex.split(cmd))
    if retCode != 0 and fallAtFail:
        sys.stdout.write("\nShell code failed with code: " + str(retCode) + "\n")
        sys.stdout.flush()
        sys.exit(retCode)
    sys.stdout.write("\n")
    sys.stdout.flush()
    return retCode

def runPythonCode(code):
    #sys.stdout.write("\n" + bcolors.HEADER + "python >" + bcolors.ENDC + "\n")
    #sys.stdout.write(bcolors.BOLD + code + bcolors.ENDC + "\n")
    #sys.stdout.flush()
    exec(code)

def chooseScriptVariant(systemName, scriptsNames):
    sizeOfMatch = {}
    for scriptsName in scriptsNames:
        match = re.match("^(" + scriptsName + ")", systemName)
        if bool(match):
            sizeOfMatch[scriptsName]=len(match.group())
    if len(sizeOfMatch) == 0:
        return None
    return max(sizeOfMatch, key=sizeOfMatch.get)

def getScriptsVariants(scriptsDir):
    onlyfiles = [f for f in listdir(scriptsDir) if isfile(join(scriptsDir, f))]
    scriptsNames = []
    for fileName in onlyfiles:
        match = re.match("^(.*" + scriptNameEnding + ")$", fileName)
        if bool(match):
            scriptsNames.append(fileName[:-1 * len(scriptNameEnding)])
    return scriptsNames    

def splitTargetCallToNameAndParams(targetCall):
    nameString = re.findall("^([a-zA-Z][a-zA-Z0-9\_]*):*.*$", targetCall)
    name = ""
    if len(nameString) == 1:
        name = nameString[0]
    paramsString = re.findall("^[a-zA-Z][a-zA-Z0-9\_]*:(.+)$", targetCall)
    params = ""
    if len(paramsString) == 1:
        params = re.findall(r"([a-zA-Z][a-zA-Z0-9\_]*=(\[.*\])*([0-9]+)*(\"[a-zA-Z0-9\,\.\:\/\_\-]*\")*)", paramsString[0])
    return (name, [param[0] for param in params])

def countLeadingSymbols(line, symbol):
    counter = 0
    for i in line:
        if i == symbol:
            counter+=1
        else:
            break
    return counter

def calculateShiftings(text, symbol):
    shiftings = []
    for i in text.split('\n'):
        if len(i) != 0:
            shiftings.append(countLeadingSymbols(i, symbol))

    return shiftings

def findMinimumShiftingLength(shiftings):
    minimumShiftingLength = sys.maxint
    for i in shiftings:
        if i < minimumShiftingLength:
            minimumShiftingLength = i
    if minimumShiftingLength != sys.maxint:
        return minimumShiftingLength
    else:
        return 0

def removeShiftings(text):
    shiftingsByTabs   = calculateShiftings(text, '\t')
    shiftingsBySpaces = calculateShiftings(text, ' ')
    minimumShiftingLengthByTabs   = findMinimumShiftingLength(shiftingsByTabs)
    minimumShiftingLengthBySpaces = findMinimumShiftingLength(shiftingsBySpaces)

    if minimumShiftingLengthByTabs > 0:
        minimumShiftingLength = minimumShiftingLengthByTabs
    else:
        minimumShiftingLength = minimumShiftingLengthBySpaces

    if minimumShiftingLength > 0:
        cleanText = ""
        for i in text.split('\n'):
            cleanLine = i
            if len(i) != 0:
                cleanLine = i[minimumShiftingLength:]
            cleanText += cleanLine + '\n'
        return cleanText
    else:
        return text
# -*- coding: UTF-8 -*-
 
import sys
import argparse
import re
import os
import platform

from subprocess import call
import subprocess
import shlex

from os.path import exists
from os import makedirs

from build_scenarist.utility import cd, runShell, runPythonCode, splitTargetCallToNameAndParams, removeShiftings
from build_scenarist.info import Info
from build_scenarist.config import bcolors, global_vars

def getTargets(pathToScript):
    with open(pathToScript) as f:
        content = f.readlines()

    targetPositions = []
    for lineIndex, text in enumerate(content):
        if bool(re.match("^(\[+.*\]+)$", text)):
            targetPositions.append(lineIndex)

    targets = {}
    fro=0
    to=0
    targetName="None"
    for i, val in enumerate(targetPositions):
        fro = targetPositions[i]+1
        if i+1 < len(targetPositions):
            to = targetPositions[i+1]
        else:
            to = len(content)
        targetName = content[targetPositions[i]][1:-2]
        targetCode = '\n'.join(content[fro:to])
        targets[targetName] = targetCode
    return targets

def targetsNotInScript(targets, pathToScript):
    targetsCode = getTargets(pathToScript)
    result = []
    for target, params in targets:
        if not(target in targetsCode):
            result.append(target)
    return result

def executeTargets(p_targets, pathToScript):
    notFoundTargets = targetsNotInScript(p_targets, pathToScript)

    isFaill = False
    if len(notFoundTargets) != 0:
        for target in notFoundTargets:
            isFaill = True
            print bcolors.FAIL + "\nError: Target %s not found in %s" % (target, pathToScript) + bcolors.ENDC
            sys.stdout.flush()

    if isFaill == False:
        targetsCode = getTargets(pathToScript)
        for target, params in p_targets:
            print bcolors.OKGREEN + "Target " + target + "..." + bcolors.ENDC
            sys.stdout.flush()
            code = "from build_scenarist.runner import runTarget\n"
            for paramCode in params:
                code += "%s\n" % (paramCode)

            code += removeShiftings(targetsCode[target])

            runPythonCode(code)
    else:
        print bcolors.FAIL + "\nError: Please, specify existed targets name!" + bcolors.ENDC
        sys.stdout.flush()

def runTarget(targetCall):
    nameAndParams = splitTargetCallToNameAndParams(targetCall)
    executeTargets([nameAndParams], global_vars["pathToScript"])

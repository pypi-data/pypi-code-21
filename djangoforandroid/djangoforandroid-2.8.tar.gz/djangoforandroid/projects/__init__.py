#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose:
  Created: 11/12/2017
"""

import os
import shutil
import sys
from collections import defaultdict


if sys.argv[1] != 'startproject':
    sys.exit()

TEMPLATE = sys.argv[2]
PROJECT = sys.argv[3]
APPNAME = "some"

SRC = os.path.join(os.path.abspath(os.path.dirname(__file__)), TEMPLATE)
TRG = os.path.join(os.getcwd(), PROJECT )


#----------------------------------------------------------------------
def parcefile(filename, kwargs):
    """"""
    #for filename in editfiles:
    if not os.path.exists(filename):
        return
    file = open(filename, "r")
    lines = file.readlines()
    file.close()
    new_lines = "".join(lines)
    new_lines = new_lines.replace("{{", "#&<<").replace("}}", ">>&#")
    new_lines = new_lines.replace("{", "{{").replace("}", "}}")
    new_lines = new_lines.replace("#&<<", "{").replace(">>&#", "}")

    #new_lines = new_lines.format(**kwargs)
    d = defaultdict(lambda: 'UNKNOWN')
    d.update(kwargs)

    new_lines = new_lines.format_map(d)

    file = open(filename, "w")
    file.write(new_lines)
    file.close()


try:
    shutil.copytree(SRC, TRG)
except FileExistsError as e:
    print(e)
    sys.exit()


ignore = ('migrations',
          '__pycache__',
          )


for root, dirs, files in os.walk(TRG):
    [dirs.remove(dir_) for dir_ in ignore if dir_ in dirs]

    for f in files:
        if f.endswith(".png"):
            continue
        file = os.path.join(root, f)
        parcefile(file, {'PROJECT': PROJECT, 'APPNAME': APPNAME,})


os.rename(os.path.join(TRG, TEMPLATE), os.path.join(TRG, PROJECT))

os.chdir(TRG)
os.system("python manage.py migrate")
os.system("python manage.py compilestatic")
os.system("python manage.py collectstatic --noinput")

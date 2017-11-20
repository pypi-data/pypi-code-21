#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess


DirUI = 'resources'
DirStore = 'qtsnbl'


def compile_ui():
    for fl in os.listdir(DirUI):
        if fl.endswith('.ui'):
            prog = 'pyuic5 --from-imports'
            out = f'{fl[:-2]}py'
        elif fl.endswith('.qrc'):
            prog = 'pyrcc5'
            out = f'{fl[:-4]}.py'
        else:
            prog = None
        if prog:
            s = f'{prog} {DirUI}/{fl} > {DirStore}/{out}'
            print(s)
            subprocess.run(s, shell=True)


if __name__ == '__main__':
    compile_ui()

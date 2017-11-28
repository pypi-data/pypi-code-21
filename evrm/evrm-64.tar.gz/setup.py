#!/usr/bin/env python3
#
#

import os
import sys
import os.path

def j(*args):
    if not args: return
    todo = list(map(str, filter(None, args)))
    return os.path.join(*todo)

if sys.version_info.major < 3:
    print("you need to run evrm with python3")
    os._exit(1)

try:
    use_setuptools()
except:
    pass

try:
    from setuptools import setup
except Exception as ex:
    print(str(ex))
    os._exit(1)

target = "evrm"
upload = []

def uploadfiles(dir):
    upl = []
    if not os.path.isdir(dir):
        print("%s does not exist" % dir)
        os._exit(1)
    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if not os.path.isdir(d):
            if file.endswith(".pyc") or file.startswith("__pycache"):
                continue
            upl.append(d)
    return upl

def uploadlist(dir):
    upl = []

    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if os.path.isdir(d):   
            upl.extend(uploadlist(d))
        else:
            if file.endswith(".pyc") or file.startswith("__pycache"):
                continue
            upl.append(d)

    return upl

setup(
    name='evrm',
    version='64',
    url='https://bitbucket.org/thatebart/evrm2',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="Het betreft hier gif !!",
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    install_requires=["botlib"],
    scripts=["bin/evrm"],
    packages=['evrm', ],
    long_description='''Geachte leden van de Eerste Kamer der Staten-Generaal,

   ik schrijf u om u te informeren dat de medicatie genoemd in de Wet verplichte GGZ in de praktijk ook het toedienen van gif omvat.

Er is bewijs dat antipsychotica gif zijn:

 * haloperiodol (haldol) - https://echa.europa.eu/substance-information/-/substanceinfo/100.000.142
 * clozapine (leponex) - https://echa.europa.eu/substance-information/-/substanceinfo/100.024.831
 * olanzapine (zyprexa) - https://echa.europa.eu/substance-information/-/substanceinfo/100.125.320
 * aripriprazole (abilify) https://echa.europa.eu/substance-information/-/substanceinfo/100.112.53

Uw wettelijk voorschrift word gebruikt voor het toedienen van gif wat strafbaar is als u met de Wet verplichte GGZ straffeloosheid verschaft.

Straffeloosheid verschaffen (verzekeren) is strafbaar met levenslang.

Ik hoop dat u deze wet zult heroverwegen en de toedieningen van gif verder laat onderzoeken.

Hoogachtend,


| Bart Thate
| Heerhugowaard
| 22-10-2017


''',
   data_files=[("docs", ["docs/conf.py","docs/index.rst"]),
               (j('docs', 'jpg'), uploadlist(os.path.join("docs","jpg"))),
               (j('docs', 'txt'), uploadlist(os.path.join("docs", "txt"))),
               (j('docs', '_templates'), uploadlist(os.path.join("docs", "_templates")))
              ],
   package_data={'': ["*.crt"],
                 },
   classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Utilities'],
)

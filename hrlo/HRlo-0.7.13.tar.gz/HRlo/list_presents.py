#!/usr/bin/python
import re
import sys
import subprocess

print "Reading names ...",
sys.stdout.flush()

cmd = 'HRcompany --key office name --value roma'
o, e = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True ).communicate()

names = re.findall("ROMA - (.*)", o)

print "done"

print "Workers found =", len(names)

print "Search presents ...",
sys.stdout.flush()

cmd = 'HRpresence --in ' + " ".join([ '"%s"' % n for n in names ])
o, e = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True ).communicate()

presents = re.findall("(.*) : PRESENTE", o)

print "done"

print "Presents found =", len(presents)

print "\nList of presents: "
print "\n".join(presents)

import sys
import os

#print(__file__)
#print(os.path.realpath(__file__))
dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir)
sys.path.append(os.path.join(dir, 'settings'))

dir = os.getcwd()
prepath = os.getcwd()
DEPTH = 0
while not os.path.exists('db'):
    dir = os.path.abspath(os.path.join(dir, '..'))
    os.chdir(dir)
    if DEPTH == 5:
        raise Exception("Can't find module named 'db',please create a python package named 'db' in your project" )


if os.getcwd() not in sys.path: sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'db'))
os.chdir(os.path.join(os.getcwd(), 'db'))

if not os.path.isfile('__init__.py'):
    open("__init__.py", "w+").close()

if not os.path.exists('migrations'):
    os.mkdir('migrations')
os.chdir(os.path.join(os.getcwd(), 'migrations'))

if not os.path.isfile('__init__.py'):
    open("__init__.py", "w+").close()

os.chdir(prepath)

del DEPTH
del dir
del prepath
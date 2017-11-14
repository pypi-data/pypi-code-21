Jupytils_debug=0;

def log(*args, debug=False, end=' ', **kwargs):
    if (not debug or 'debug' in kwargs and not kwargs(debug) ):
        return;

    for a in args:
        print(a, end=end)
    for k,v in kwargs.items():
        print ("%s = %s" % (k, v))

log("This will load or reload Jupytils; This message will be removed in Future Versions", debug=Jupytils_debug)

#
import sys
dels=[]
for m in sys.modules:
    if (m.startswith('Jupytils')):
        dels.append(m)

#print("Modules loaded: ", dels)

try:
    from Jupytils.jcommon import *
    LoadJupytils()
except:
    pass

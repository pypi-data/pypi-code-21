from os import \
    X_OK as _XOK, \
    access as _access,\
    environ as _environ

def which(prog):
	for path in _environ['PATH'].split(':'):
		if _access('%s/%s'%(path, prog), _XOK):
			return '%s/%s'%(path, prog)

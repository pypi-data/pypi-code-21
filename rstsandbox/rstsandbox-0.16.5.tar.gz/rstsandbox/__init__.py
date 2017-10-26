import sys
import pkgutil

import rst
import rstsandbox
import logging

logger = logging.getLogger("rstsandbox")
# prevent logging warnings about missing handlers as per:
# https://docs.python.org/2.6/library/logging.html#configuring-logging-for-a-library
# do so before importing anything from RSB itself, which might already log
# stuff
class _NullHandler(logging.Handler):
    """
    Null logging handler to prevent warning messages
    """
    def emit(self, record):
        pass
logger.addHandler(_NullHandler())

def addSandboxToRST():
    def importIt(designator, error = True):
        logger.debug("importIt called with '%s'" % designator)
        if hasattr(designator, '__iter__'):
            name = '.'.join(designator)
        else:
            name = designator
        try:
            logger.debug("Really importing name '%s'" % name)
            return __import__(name, fromlist = [ '__dict__' ]) # WT?
        except Exception, e:
            if error:
                raise e

    # Find two things within the sandbox:
    # + All Modules (since there should be no duplicates between rst
    #   and rstsandbox)
    # + Packages which do not have a corresponding package relative to
    #   the rst package.
    #   E.g. rstsandbox.communicationpatterns when there is no
    #   rst.communicationpatterns
    # We record errors caused by dependency problems so the caller can
    # trigger additional iterations to resolve dependencies.
    def findModules(root):
        result = []
        errors = []
        for _, name, ispkg in pkgutil.iter_modules(root.__path__):
            fullname = root.__name__ + '.' + name
            if ispkg:
                kind = 'package'
            else:
                kind = 'module'
            logger.debug("Processing %s %s.%s", kind, root.__name__, name)
            logger.debug('Importing %s', fullname)
            try:
                loaded = importIt(fullname)
                logger.debug('Loaded %s', loaded)
                proposedRstName = [ 'rst' ] + fullname.split('.')[1:]
                logger.debug("Checking whether %s in rst exists" % proposedRstName)
                if ispkg and importIt(proposedRstName, error = False):
                    logger.debug('%s is a package which also exists under rst', fullname)
                    subresult, suberrors = findModules(loaded)
                    result.extend(subresult)
                    errors.extend(suberrors)
                else:
                    result.append(loaded)
            except Exception, e:
                errors.append((name, "%s: %s" % (type(e).__name__, e)))
                logger.warn('Failed to load %s: %s', name, e)
        return result, errors

    # Process packages and modules that are present in the sandbox,
    # but not in the stable section:
    # + Add package or module to respective parent package. This
    #   corresponds to "mounting" the entire module tree rooted at the
    #   particular package under the parent package in the stable
    #   section.
    # + Add to sys.modules
    modules, errors = findModules(rstsandbox)
    logger.debug("Found modules %s and errors %s" % (modules, errors))
    for module in modules:

        logger.debug("Processing module or package %s" % module)

        components = module.__name__.split('.')
        rstName    = 'rst.' + '.'.join(components[1:])
        logger.debug('Mounting %s -> %s', module.__name__, rstName)

        sys.modules[rstName] = module
        rstPackage = importIt([ 'rst' ] + components[1:-1])
        rstPackage.__dict__[components[-1]] = module


    return modules, errors

# We need multiple iterations to resolve dependencies since sandbox
# types may depend on each other. Since we do not attempt to load the
# modules in a dependency-respecting order, some modules may initially
# fail to load but succeed later, after their dependencies have been
# loaded.
logger.debug("---- ITERATION ----")
_, initial = addSandboxToRST()
while len(initial) > 0:
    logger.debug("---- ITERATION ----")
    _, new = addSandboxToRST()
    if len(new) == len(initial):
        raise RuntimeError, "Unable to install modules/packages in rst namespace:\n%s" \
            % '\n'.join([("%s - %s" % (e[0], e[1])) for e in new])
    initial = new

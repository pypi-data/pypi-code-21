from __future__ import absolute_import, division, print_function


def safeCompile(string, filename, mode='exec', flags=0, dont_inherit=0):
    '''
    Compiles a string into Python code object dealing with some issue that
    can happen with /r values in the file
    '''
    return compile(
        string.replace('\r', '') + '\n', filename, mode, flags, dont_inherit)

# pylint: disable=locally-disabled, redefined-builtin, exec-used
def execFile(fname, locals, globals):
    with open(fname, 'r') as f:
        exec (safeCompile(f.read(), fname), globals, locals)

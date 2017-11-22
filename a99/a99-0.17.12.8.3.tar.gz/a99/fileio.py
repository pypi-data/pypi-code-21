import collections
import os.path
import re
import shutil
from threading import Lock
import sys
import a99
import logging


__all__ = [
    "rename_to_temp", "is_text_file", "multirow_str_vector", "add_bits_to_path", "crunch_dir",
    "slugify", "write_lf", "int_vector", "float_vector", "get_path",
    "str_vector", "new_filename", "readline_strip", "create_symlink", "which",
]


# # Filename or pathname-related string manipulations

def slugify(string):
    """
    Removes non-alpha characters, and converts spaces to hyphens. Useful for making file names.


    Source: http://stackoverflow.com/questions/5574042/string-slugification-in-python
    """
    string = re.sub('[^\w .-]', '', string)
    string = string.replace(" ", "-")
    return string


def crunch_dir(name, n=50):
    """Puts "..." in the middle of a directory name if lengh > n."""
    if len(name) > n + 3:
        name = "..." + name[-n:]
    return name

def add_bits_to_path(path_, filename_prefix=None, extension=None):
    """
    Adds prefix/suffix to filename

    Arguments:
        path_ -- path to file
        filename_prefix -- prefix to be added to file name
        extension -- extension to be added to file name. The dot is automatically added, such as
            "ext" and ".ext" will have the same effect

    Examples:
        > add_bits_to_path("/home/user/file", "prefix-")
        /home/user/prefix-file

        > add_bits_to_path("/home/user/file", None, ".ext")
        /home/user/file.ext

        > add_bits_to_path("/home/user/file", None, "ext")  # dot in extension is optional
        /home/user/file.ext

        > add_bits_to_path("/home/user/", None, ".ext")
        /home/user/.ext
    """

    dir_, basename = os.path.split(path_)

    if filename_prefix:
        basename = filename_prefix+basename
    if extension:
        if not extension.startswith("."):
            extension = "."+extension
        basename = basename+extension

    return os.path.join(dir_, basename)



# # Text file parsing utillities

def str_vector(f):
    """
    Reads next line of file and makes it a vector of strings

    Note that each str.split() already strips each resulting string of any whitespaces.
    """
    return f.readline().split()


def float_vector(f):
    """Reads next line of file and makes it a vector of floats."""
    return [float(s) for s in str_vector(f)]


def int_vector(f):
    """Reads next line of file and makes it a vector of floats."""
    return [int(s) for s in str_vector(f)]


def readline_strip(f):
    """Reads next line of file and strips the newline."""
    return f.readline().strip('\n')


def multirow_str_vector(f, n, r=0):
    """
    Assembles a vector that spans several rows in a text file.

    Arguments:
      f -- file-like object
      n -- number of values expected
      r (optional) -- Index of last row read in file (to tell which file row in
                      case of error)

    Returns:
      (list-of-strings, number-of-rows-read-from-file)
    """

    so_far = 0
    n_rows = 0
    v = []
    while True:
        temp = str_vector(f)
        n_rows += 1
        n_now = len(temp)

        if n_now+so_far > n:
            a99.get_python_logger().warning(('Reading multi-row vector: '
                'row %d should have %d values (has %d)') %
                (r+n_rows, n-so_far, n_now))

            v.extend(temp[:n-so_far])
            so_far = n

        elif n_now+so_far <= n:
            so_far += n_now
            v.extend(temp)

        if so_far == n:
            break

    return v, n_rows



# # Probe, write, rename etc.

def new_filename(prefix, extension=None, flag_minimal=True):
    """returns a file name that does not exist yet, e.g. prefix.0001.extension

    Args:
        prefix:
        extension: examples: "dat", ".dat" (leading dot will be detected, does not repeat dot in name)
        flag_minimal:

          - True: will try to be as "clean" as possible
          - False: will generate filenames in a simple, same-length pattern

    Example: ``new_filename("molecules-", "dat", True)``

    In the example above, the first attempt will be "molecules.dat", then "molecules-0000.dat".
    If flag_minimal were True, it would skip the first attempt.
    """

    if extension is None:
        extension = ""

    if len(extension) > 0 and extension[0] == '.':
        extension = extension[1:]

    # extension-sensitive format for filename
    fmt = '{0!s}-{1:04d}.{2!s}' if extension else '{0!s}-{1:04d}'

    # Removes tailing dash because it would look funny (but will be re-added in format string)
    prefix_ = prefix[:-1] if prefix.endswith("-") else prefix

    i = -1
    while True:
        if i == -1:
            if flag_minimal:
                ret = "{}.{}".format(prefix_, extension) if extension else prefix_
        else:
            ret = fmt.format(prefix_, i, extension)

        if not os.path.exists(ret):
            break
        i += 1
        if i > 9999:
            raise RuntimeError("Could not make a new file name for (prefix='{0!s}', extension='{1!s}')".format(prefix, extension))
    return ret


_rename_to_temp_lock = Lock()
def rename_to_temp(filename):
    """*Thread-safe* renames file to temporary filename. Returns new name"""
    with _rename_to_temp_lock:
        root, ext = os.path.splitext(filename)
        if len(ext) > 0:
            ext = ext[1:]  # the dot (".") is originally included
        new_name = new_filename(root, ext)
        os.rename(filename, new_name)
        return new_name


def write_lf(h, s):
  """Adds lf to end of string and writes it to file."""
  h.write(s+"\n")


def create_symlink(source, link_name):
    """
    Creates symbolic link for either operating system.

    http://stackoverflow.com/questions/6260149/os-symlink-support-in-windows
    """
    os_symlink = getattr(os, "symlink", None)
    if isinstance(os_symlink, collections.Callable):
        os_symlink(source, link_name)
    else:
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(source) else 0
        if csl(link_name, source, flags) == 0:
            raise ctypes.WinError()





# ## http://eli.thegreenplace.net/2011/10/19/perls-guess-if-file-is-text-or-binary-lemented-in-python
_PY3 = sys.version_info[0] == 3

# A function that takes an integer in the 8-bit range and returns
# a single-character byte object in py3 / a single-character string
# in py2.
#
_int2byte = (lambda x: bytes((x,))) if _PY3 else chr

_text_characters = (
        b''.join(_int2byte(i) for i in range(32, 127)) +
        b'\n\r\t\f\b')

def is_text_file(filepath, blocksize=2**13):
    """ Uses heuristics to guess whether the given file is text or binary,
        by reading a single block of bytes from the file.
        If more than 30% of the chars in the block are non-text, or there
        are NUL ('\x00') bytes in the block, assume this is a binary file.
    """
    with open(filepath, "rb") as fileobj:
        block = fileobj.read(blocksize)
        if b'\x00' in block:
            # Files with null bytes are binary
            return False
        elif not block:
            # an empty file is considered a valid text file
            return True

        # Use translate's 'deletechars' argument to efficiently remove all
        # occurrences of _text_characters from the block
        nontext = block.translate(None, _text_characters)
        return float(len(nontext)) / len(block) <= 0.30



def which(program):
    """
    Mimics UNIX 'which' command: return full path to executable file

    http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    """
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def get_path(*args, module=a99):
    """Returns full path to specified module

    Args:
      *args: are added at the end of module path with os.path.join()
      module: Python module, defaults to a99

    Returns: path string

    >>> get_path()
    """

    p = os.path.abspath(os.path.join(os.path.split(module.__file__)[0], *args))
    return p

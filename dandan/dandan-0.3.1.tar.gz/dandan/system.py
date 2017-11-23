from __future__ import unicode_literals


def is_win32():
    """
    Check os platform is win32

    Returns:
        bool: True if is win32 else False
    """
    import sys
    return "win32" in sys.platform


def is_linux():
    """
    Check os platform is linux

    Returns:
        bool: True if is linux else False
    """
    import sys
    return "linux" in sys.platform


def is_python2():
    """
    Check current interpreter is python2

    Returns:
        bool: True if is python2 else False
    """
    import sys
    return sys.version_info.major == 2


def is_python3():
    """
    Check current interpreter is python3

    Returns:
        bool: True if is python3 else False
    """
    import sys
    return sys.version_info.major == 3


def set_unicode():
    """
    Set default encoding to utf8
    """
    if is_python3():
        return

    import sys
    reload(sys)
    sys.setdefaultencoding("utf8")


def execute(command, callback=None):
    '''
    Execute a system command return status and output

    Args:
        command (TYPE): execute command command must not bash command
        callback (None, optional): callback function per output line

    Returns:
        string: console output
        int: execute exit code
    '''

    import subprocess
    if not is_win32():
        command = ["/bin/sh", "-c", command]
        shell = False
    else:
        shell = True
    try:
        pipe = subprocess.Popen(
            command, shell=shell, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except Exception as e:
        return e, -1

    if not callback:
        res = pipe.stdout.read()
        pipe.communicate()
        return (res, pipe.returncode)

    line = ""
    while True:
        char = pipe.stdout.read(1)
        if not char:
            break
        if char not in ["\n", "\r"]:
            line += char
            continue
        callback(line)
        line = ""
    pipe.communicate()
    return (None, pipe.returncode)


def readable(path):
    '''
    Check if a given path is readable by the current user.

    Args:
        path (string): local system path

    Returns:
        bool: True if readable else False
    '''

    import os
    if os.access(path, os.F_OK) and os.access(path, os.R_OK):
        return True

    return False


def writeable(path, check_parent=True):
    '''
    Check if a given path is writeable by the current user.

    Args:
        * path (string): local system path
        * check_parent (bool, optional): If the path to check does not exist, check for the ability to write to the parent directory instead

    Returns:
        * bool: True if writeable else False
    '''
    import os
    if os.access(path, os.F_OK) and os.access(path, os.W_OK):
        # The path exists and is writeable
        return True

    if os.access(path, os.F_OK) and not os.access(path, os.W_OK):
        # The path exists and is not writeable
        return False

    # The path does not exists or is not writeable

    if check_parent is False:
        # We're not allowed to check the parent directory of the provided path
        return False

    # Lets get the parent directory of the provided path
    parent_dir = os.path.dirname(path)

    if not os.access(parent_dir, os.F_OK):
        # Parent directory does not exit
        return False

    # Finally, return if we're allowed to write in the parent directory of the
    # provided path
    return os.access(parent_dir, os.W_OK)


def __getch_win32():
    import msvcrt
    return msvcrt.getch()


def __getch_linux():
    import termios
    import sys
    import os

    fd = sys.stdin.fileno()

    old_ttyinfo = termios.tcgetattr(fd)
    new_ttyinfo = old_ttyinfo[:]

    new_ttyinfo[3] &= ~termios.ICANON
    new_ttyinfo[3] &= ~termios.ECHO

    try:
        termios.tcsetattr(fd, termios.TCSANOW, new_ttyinfo)
        return os.read(fd, 7)
    except Exception:
        return chr(3)
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, old_ttyinfo)


def getch():
    """
    Get a char pressed on keyboard without press Enter

    Returns:
        char(s): return pressed key
    """
    if is_win32():
        ch = __getch_win32()
    elif is_linux():
        ch = __getch_linux()
    else:
        ch = None

    if is_python2():
        return unicode(ch)
    elif is_python3():
        return ch.decode('utf8')


def clear():
    """
    Clear console screen
    """
    import os
    if is_win32():
        os.system("cls")
    elif is_linux():
        os.system("clear")

import os
import stat

def on_same_file_system(file1, file2):
    dev1 = os.stat(file1).st_dev
    dev2 = os.stat(file2).st_dev
    return dev1 == dev2


def make_user_executable(path):
    #https://stackoverflow.com/questions/12791997/how-do-you-do-a-simple-chmod-x-from-within-python
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC)

def indent(lines, n=1):
    return ["    "*n + line for line in lines]
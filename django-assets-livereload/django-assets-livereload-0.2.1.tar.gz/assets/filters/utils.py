import subprocess


def pipe(program, input, cwd=None):
    """
        Pipe :param:`input` into the program :param:`program` run in
        the directory :param:`cwd`. Returns the program output stream.
    """
    p = subprocess.Popen(program, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True, cwd=cwd, bufsize=-1)
    return p.communicate(input)[0]

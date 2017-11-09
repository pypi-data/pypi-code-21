import io
import os
from subprocess import Popen, PIPE


def parse_stdout(stdout):
    info = {}
    lines = [i for i in stdout.splitlines() if i != '']
    for i in lines:
        key, value = [i.strip() for i in i.split(':', 1)]
        info[key] = value
    return info


def info(audio_file, encoding='UTF-8'):
    if isinstance(audio_file, str):
        infile = audio_file
        input_data = None
        stdin = None
    else:
        infile = '−'
        input_data = audio_file.getvalue()
        stdin = PIPE

    cmd = f'sox --info {infile}'
    proc = Popen(cmd, stdout=PIPE, stdin=stdin)
    stdout, err = proc.communicate(input=input_data)
    info = stdout.decode(encoding=encoding)
    return parse_stdout(info)


def silence(infile, duration, threshold, cwd=None, output='letter.wav',
            verbosity=1):

    threshold = str(threshold) + '%'
    input_data = None
    stdin = None
    if cwd:
        infile = os.path.join(cwd, infile)
        output = os.path.join(cwd, 'letter.wav')

    if isinstance(infile, io._io.BytesIO):
        input_data = infile.getvalue()
        infile = '-'
        stdin = PIPE

    cmd = (f'sox -V2 -t wav "{infile}" "{output}" silence 1 {duration} '
           f'{threshold} 1 {duration} {threshold} : newfile : restart')
    proc = Popen(cmd, stdin=stdin, cwd=cwd, shell=True)
    out, err = proc.communicate(input=input_data)

    letter_count = len(os.listdir(cwd))
    return letter_count

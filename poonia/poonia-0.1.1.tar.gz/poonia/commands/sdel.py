import click
import os

def _getsize(f):
    old_file_position = f.tell()
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(old_file_position, os.SEEK_SET)
    return size

def _randombytes(size):
    return bytearray(os.urandom(size))

MB = 1024**2

@click.command(help='Securely delete specified file')
@click.argument('file', type=click.File(mode='r+b', lazy=False))
def sdel(file):
    s = _getsize(file)
    file.write(_randombytes(min(MB, s)))
    if s > MB:
        file.seek(s-MB)
        file.write(_randombytes(MB))
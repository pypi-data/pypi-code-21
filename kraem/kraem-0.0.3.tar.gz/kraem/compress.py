from subprocess import run
from kraem.utils import get_full_path
from kraem.utils import get_platform


# Get path to the binary file for compression
def get_binary():
    return get_full_path('kraem', 'bin', get_platform(), 'cjpeg')


# Compress image provided to the function
async def compress(source, destination, quality, options={}):
    run([get_binary(), '-quality', quality, '-outfile', destination, source])
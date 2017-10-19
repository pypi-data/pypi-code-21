import sys
import psutil

from typing import List


def command_timeout(args: List[str], timeout=None):
    process = psutil.Popen(args, stdout=sys.stdout, stderr=sys.stderr)
    # 'psutil' allows to use timeout in waiting for a subprocess.
    # If not timeout was specified then it is 'None' - no timeout, just waiting.
    # Runtime is useful mostly for interactive tests.
    try:
        retcode = process.wait(timeout=timeout)
    except psutil.TimeoutExpired as e:
        # Kill the subprocess and its child processes.
        for p in process.children(recursive=True):
            p.kill()
        process.kill()
        raise e


def main():
    command_timeout(sys.argv[2:], int(sys.argv[1]))

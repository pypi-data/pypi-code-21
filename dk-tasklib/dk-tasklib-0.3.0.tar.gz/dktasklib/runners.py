# -*- coding: utf-8 -*-
import subprocess


class Result(str):
    cmd = None
    returncode = None


def run(cmdline, throw=False):
    try:
        res = Result(
            subprocess.check_output(
                cmdline,
                shell=True
            )  # .decode('u8')  ## (can't decode since Result is a str)
        )
        res.cmd = cmdline
        return res
    except subprocess.CalledProcessError as e:
        if throw:
            raise
        res = Result(e.output)
        res.cmd = cmdline
        res.returncode = e.returncode
        return res


def command(executable, dryrun=False):
    def _call(*args, **kwargs):
        cmdline = " ".join(args)
        for k, v in kwargs.items():
            if v is True:
                cmdline += " --" + k
            else:
                if ' ' in v:
                    v = '"%s"' % v
                cmdline += ' --%s=%s' % (k, v)

        if dryrun:
            print cmdline
        else:
            return run(cmdline)
    return _call

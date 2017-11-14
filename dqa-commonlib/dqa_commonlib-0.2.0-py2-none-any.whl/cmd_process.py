# -*- coding:utf-8 -*-
# Author: lijian01
# Mail: lijian01@imdada.cn
import logging
import subprocess

import sys

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.DEBUG)


class CmdProcess(object):
    def __init__(self):
        pass

    @staticmethod
    def execute_cmd(cmd):
        logging.info("Cmd : {cmd}".format(cmd=cmd))

        process = subprocess.Popen(cmd, shell=True, bufsize=10,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        out_summary = ""

        while True:
            out = process.stdout.read(1)
            out_summary += out

            if not out and process.poll() is not None:
                break

            if out:
                sys.stdout.write(out)
                sys.stdout.flush()

        if process.stdout:
            process.stdout.close()

        if process.stderr:
            process.stderr.close()

        return_code = process.returncode

        return return_code, out_summary


if __name__ == '__main__':
    CmdProcess.execute_cmd("ls")

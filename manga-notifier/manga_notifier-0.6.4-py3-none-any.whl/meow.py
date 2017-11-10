# -*- coding: utf-8 -*-

import subprocess
from distutils.spawn import find_executable
import json


class Notifier(object):

    OPTIONS = ('message',
               'title',
               'subtitle',
               'group',
               'activate',
               'open',
               'sound',
               'execute',
               'actions',
               'timeout')

    def __init__(self):

        self.notifier = find_executable("terminal-notifier")
        if not self.notifier:
            raise Exception("You need to install : terminal-notifier")

    def _option_exists(self, option):

        if option not in self.OPTIONS:
            raise Exception("options :{}: doesn't exists".format(option))

    def _check_options(self, options):

        for opt in options.keys():
            self._option_exists(opt)

    def _build_command(self, message, **kwargs):

        command = [self.notifier]
        command.extend(["-message", message])
        [command.extend(["-{}".format(k), v]) for k, v in kwargs.items()]
        if self.need_response:
            command.extend(["-closeLabel", "No"])
            command.append("-json")
        return command

    def _launch_command(self, command):

        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        out, err = p.communicate()
        return out, err

    def meow(self, message, **kwargs):

        self._check_options(kwargs)

        self.need_response = False

        if 'actions' in kwargs.keys():
            self.need_response = True

        command = self._build_command(message, **kwargs)
        out, err = self._launch_command(command)  # Need to out.decode()

        if self.need_response and out:
            result = json.loads(out.decode())
            return result


Meow = Notifier()

if __name__ == "__main__":
    import time
    print("MEOW")

    t = find_executable("terminal-notifier")

    noti = Notifier()

    message = "Chapitre 91 OUT"
    title = "One-Punch Man"
    url = "http://readms.net/r/onepunch_man/081/4592/1"

    r = noti.meow(message, title=title, open=url)
    time.sleep(2)

    r = noti.meow(message, title=title, actions='Yes', timeout='3')

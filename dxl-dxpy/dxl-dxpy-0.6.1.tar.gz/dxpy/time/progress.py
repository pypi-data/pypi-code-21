"""
Utilities to measure progress of program.
"""

import time


class ProgressTimer:
    def __init__(self, nb_steps=100, min_elp=1.0):
        self._nb_steps = nb_steps
        self._step = 0
        self._start = None
        self._elaps = None
        self._pre = None
        self._min_elp = min_elp
        self.reset()

    def reset(self):
        self._start = time.time()
        self._pre = 0.0
        self._step = 0

    def event(self, step=None, msg='None'):
        if step is None:
            step = self._step
            self._step += 1
        else:
            self._step = step

        self._elaps = time.time() - self._start
        if self._elaps - self._pre < self._min_elp:
            return
        comp_percen = float(step) / float(self._nb_steps)
        if comp_percen > 0:
            eta = (1 - comp_percen) * self._elaps / comp_percen
        else:
            eta = None

        time_pas = str(datetime.timedelta(seconds=int(self._elaps)))
        time_int_v = self._elaps / (step + 1.0)
        if time_int_v < 60:
            time_int_msg = '%0.2fs/it' % (time_int_v)
        else:
            time_int_msg = str(datetime.timedelta(
                seconds=int(time_int_v)))
        if eta is None:
            time_eta = 'UKN'
        else:
            time_eta = str(datetime.timedelta(seconds=int(eta)))
        click.echo("i=%6d, %s, [%s<%s] :" %
                   (step, time_int_msg, time_pas, time_eta) + msg)
        self._pre = self._elaps

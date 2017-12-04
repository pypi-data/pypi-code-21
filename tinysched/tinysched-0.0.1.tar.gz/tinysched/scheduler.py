# -*- coding: utf-8 -*-
from threading import Thread
import sched
from datetime import timedelta


def repeat(func, interval=timedelta(seconds=0), max_repeats=None):
    """
    Repeatedly invoke function at specified time interval

    Args:
        func: function to invoke

    Keyword args:
        interval (timedelta, default 0 seconds): interval to wait between each invocation
        max_repeats (integer, default None): maximum number of repeats

    Return values:
        cancel_fn (function): call this function to cancel repeat loop
    """
    cancelled = False

    def repeat(repeats_left=max_repeats or -1):
        if not cancelled and repeats_left != 0:
            try:
                func()
            finally:
                scheduler.enter(
                    interval.total_seconds(),
                    0,
                    repeat,
                    kwargs={'repeats_left': repeats_left - 1}
                )

    scheduler = sched.scheduler()
    scheduler.enter(0, 0, repeat)

    thread = Thread(
        target=lambda: scheduler.run(),
        daemon=True
    )
    thread.start()

    def cancel():
        nonlocal cancelled
        cancelled = True

    return cancel

#-*-coding:utf-8-*-
__author__ = 'cchen'


import random
import time
from datetime import datetime, timedelta


def sleep(p, sec):
    """
    Args:
        p (float): probability that pass to next iteration
        sec (float): pause time
    """
    def rand_decorator(func):
        def func_wrapper(*name):
            if random.random() > p:
                time.sleep(sec)
            return func(*name)
        return func_wrapper
    return rand_decorator


# def sleep_hour():
#     """
#     Args:
#         p (float): probability that pass to next iteration
#         sec (float): pause time
#     """
#     def rand_decorator(func):
#         def func_wrapper(*name):
#             now = datetime.now()
#             this_hour = datetime(year=now.year, month=now.month, day=now.day, hour=now.hour)
#             next_hour = this_hour + timedelta(hours=1)
#             sleeptime = (next_hour - now).total_seconds()
#             print('Job done, restarting in {} seconds.'.format((next_hour - now).total_seconds()))
#             time.sleep(sleeptime)
#             return func(*name)
#         return func_wrapper
#     return rand_decorator

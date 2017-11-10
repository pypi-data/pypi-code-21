# -*- coding: utf-8 -*-
import random
import string


def random_str(limit_num=12):
    limit_num = 12 if limit_num < 12 else limit_num
    return '.'.join(random.sample(string.ascii_letters + string.digits, limit_num))

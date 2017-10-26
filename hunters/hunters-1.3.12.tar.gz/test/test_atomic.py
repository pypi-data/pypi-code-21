# -*- coding:utf-8 -*-
# Created by qinwei on 2017/8/11
import random
import threading
from time import sleep

from hunters.atomic import AtomicLong

count = AtomicLong()
count += 1
intcount = 1


def incr():
    global count, intcount
    sleep(random.randint(0, 10) / 100)
    for i in range(100000):
        count += 1
        intcount += 1


def sub():
    global count
    while True:
        if count.value > 100:
            count -= 100


def read():
    global count
    while True:
        sleep(0.01)
        try:
            assert count.value >= 0
        except AssertionError as e:
            print(count.value)


# for i in range(20):  # 20个线程并发减持
#     threading._start_new_thread(sub, ())
threads = [threading.Thread(target=incr, args=()) for i in range(100)];
for t in threads:
    t.start()
for t in threads:
    t.join()

# t2 = threading._start_new_thread(read, ())

# sleep(10)
print(count.value, intcount)  # 10000001 9992712

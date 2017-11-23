#!/usr/bin/env python
#coding:utf-8
# Author        : tuxpy
# Email         : q8886888@qq.com.com
# Last modified : 2017-02-16 14:27:36
# Filename      : lock.py
# Description   : 

from __future__ import print_function, unicode_literals
import iplock.tools

import json
import time
import stat
import os
import os.path
import datetime

QUIET = False

def print_log(s):
    if QUIET:
        return

    print(datetime.datetime.now(), s)

class writefile_lock(object):
    def __init__(self, target):
        self.target = target
        self.lockfile = target + ".lock"

    def __enter__(self):
        while os.path.exists(self.lockfile):
            print("update locking...")
            time.sleep(0.5) 

        with open(self.lockfile, "wb"):
            pass

    def __exit__(self, e_t, e_v, t_b):
        os.remove(self.lockfile)
        return False

class IP(object):
    def __init__(self, ip, lk_filepath):
        self.ip = ip
        self.lk_filepath = lk_filepath

    def get_data(self):
        if not os.path.exists(self.lk_filepath):
            return {}

        with open(self.lk_filepath, "rb") as fd:
            try:
                return json.loads(fd.read())

            except ValueError:
                os.remove(self.lk_filepath)
                return {}


    def update_data(self, data):
        with writefile_lock(self.lk_filepath):
            new_create = os.path.exists(self.lk_filepath)
            with open(self.lk_filepath, "a+") as fd:
                fd.seek(0)
                old_data = json.loads(fd.read().strip() or '{}')
                fd.seek(0)
                fd.truncate(0)
                old_data.update(data)
                fd.write(json.dumps(old_data))

            if new_create:
                os.path.exists(self.lk_filepath) and os.chmod(self.lk_filepath, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    def get_locked_pid(self):
        data = self.get_data()
        if data == {}:
            return None

        if not iplock.tools.pid_exists(data["pid"]):
            return None

        return data["pid"]

    def suicide(self):
        priority_item = self.get_priority_item()
        if priority_item:
            self.remove_queue(priority_item[0])
            self.update_data({
                "pid": priority_item[0],
                "priority": priority_item[1],
                })

        else:
            os.path.exists(self.lk_filepath) and os.remove(self.lk_filepath)

    def get_priority_item(self):
        data = self.get_data()
        data.setdefault("queue", {})

        while len(data["queue"]) > 0:
            max_priority_pid_in_queue = max(data["queue"].items(), key = lambda item: item[1])
            pid, priority = max_priority_pid_in_queue
            data["queue"].pop(pid)
            if not iplock.tools.pid_exists(int(pid)):
                self.remove_queue(pid)
                continue

            return int(pid), priority

        return None


    def create(self, pid, priority):
        self.wait(pid, priority)
        self.update_data({
            "pid": pid,
            "priority": priority,
            })

        print_log("locked. ip: {ip}, pid: {pid}, priority: {priority}".format(
            ip = self.ip, pid = pid, priority = priority))

    def insert_queue(self, pid, priority):
        data = self.get_data()
        if not data:
            return
        queue = data.get("queue", {})
        queue[pid] = priority
        self.update_data({"queue": queue})

    def remove_queue(self, pid):
        data = self.get_data()
        queue = data.get("queue", {})
        queue.pop(str(pid), None)
        self.update_data({"queue": queue})


    def wait(self, pid, priority):
        inserted_queue = False
        while True:
            locked_pid = self.get_locked_pid() 
            if locked_pid is None or locked_pid == pid:
                priority_item = self.get_priority_item()
                if priority_item and priority_item[1] > priority: # 如果队列中有比自己优先级高的话, 则将机会让出来
                    print_log("find a higher priprity process({pid}) than your own.".format(
                        pid = priority_item[0]))
                    self.update_data({
                        "pid": int(priority_item[0]),
                        "priority": priority_item[1],
                        })
                    self.remove_queue(int(priority_item[0]))
                    inserted_queue = False

                else:
                    break

            else:
                print_log("the {ip} was locked by {pid}".format(
                    ip = self.ip, pid = locked_pid))

            if not inserted_queue:
                self.insert_queue(pid, priority)
                inserted_queue = True

            time.sleep(3)

class IPLocker(object):
    def __init__(self, lk_path):
        self.lk_path = lk_path
        if not os.path.exists(lk_path):
            os.makedirs(lk_path)
            os.chmod(lk_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    def get(self, ip):
        return IP(ip, os.path.join(self.lk_path, ip + ".lk"))

    def unlock(self, ip):
        return self.get(ip).suicide()

    def lock(self, ip, priority = 0, quiet = True):
        global QUIET
        QUIET = quiet
        self.get(ip).create(os.getpid(), priority)


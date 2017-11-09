#!/usr/bin/env python
#coding: utf-8


class Task:
    def __init__(self, task_id, priority, tasktype, data, *subtasks):
        self.task_id = task_id
        self.priority = priority
        self.state = None
        self.type = tasktype
        self.data = data
        self.subtasks = {t.task_id: t for t in subtasks}
        self.is_remote = False 
        self.remote_server = None

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)

    def call(self, func):
        return func(self.task_id, self.data)

    def add_subtasks(self, subtask):
        self.subtasks[subtask.task_id] = subtask

    def del_subtasks(self, subtask):
        self.subtasks.pop(subtask.task_id, None)

    def renice(self, priority):
        self.priority = priority

    def setRemote(self, ip, port):
        self.is_remote = True
        self.remote_server = (ip, port)

        

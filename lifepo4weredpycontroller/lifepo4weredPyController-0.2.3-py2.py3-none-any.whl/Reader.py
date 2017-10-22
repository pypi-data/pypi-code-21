#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tinyPeriodicTask

"""
Reader is the mechanism which read periodically the data.

basically: it execute a callback function called job
added using the add function.
"""


class Reader():
    def __init__(self):
        self.jobs = []
        self.postJobs = []
        self.__task = {}

    @property
    def interval(self):
        return self.__task.interval

    @interval.setter
    def interval(self, value):
        self.__task.interval = value

    def add(self, job):
        """
        Add a callback function to execute periodically.

        :param func job: the function to call
        """
        self.jobs.append(job)

    def addPostJob(self, job):
        """
        Add a callback function to execute periodically 
            once normal job are executed.

        :param func job: the function to call
        """
        self.postJobs.append(job)

    def startPeriodicallyReading(self):
        """
        Init and start periodically reading
        """
        def _readJobs():
            for job in self.jobs:
                job()

            for job in self.postJobs:
                job()

        self.__task = tinyPeriodicTask.TinyPeriodicTask(0.5, _readJobs)
        self.__task.start()

    def restart(self):
        """
        Restart periodically reading
        """
        self.__task.start()

    def stop(self):
        """
        cease periodically reading
        """
        self.__task.stop()

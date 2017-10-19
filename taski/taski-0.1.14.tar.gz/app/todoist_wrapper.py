""" Todoist adapter """

import pickle
import os
import time
import glob
import uuid
import json
import math
import re
from datetime import datetime
import todoist
from base import Project, Task
from util import same_date
from util import dlog
import logging as log


TO_UPDATE = {}


class Todoist():
    def __init__(self):
        self.user = None
        self.completed_tasks = None
        self.planned_label = None
        self.planned_label_id = None
        self.already_planned = []

    def init(self, cfg):
        self.api = todoist.TodoistAPI()
        self.user = self.api.user.login(cfg["email"], cfg["password"])
        err = self.user.get("error")
        if err:
            raise Exception(err)

        self.api.sync()
        self.planned_label = self.get_label("planned")
        if not self.planned_label:
            log.debug("Create new planned label")
            self.planned_label = self.api.labels.add("planned")
        self.planned_label_id = int(self.planned_label['id'])
        log.debug("planned_label_id: %d", self.planned_label_id)

    def get_token(self):
        return self.user['token']

    def get_label(self, name):
        self.labels = self.api.labels.all()
        for l in self.labels:
            if not isinstance(l['id'], int):
                # skip non-regular label object
                continue
            if l['name'] == name:
                return l
        return None

    def PyTaskAdapter(self, pytodoist_task):
        t = Task()
        tt = pytodoist_task

        if isinstance(tt, todoist.models.Item):
            completed_date = tt.data.get("completed_date")
            checked = tt['checked']
        else:
            completed_date = tt.get("completed_date")
            checked = tt.get('checked')

        t.id = tt['id']
        t.name = tt['content']
        t.done = checked
        t.pid = tt['project_id']
        t._data = tt

        if completed_date is not None:
            t.ts_done = datetime.strptime(tt['completed_date'], "%a %d %b %Y %H:%M:%S +0000")
            t.done = True
        else:
            t.ts_added = datetime.strptime(tt['date_added'], "%a %d %b %Y %H:%M:%S +0000")

        return t

    def _get_ttasks(self):
        self.ttasks = self.api.items.all()
        return self.ttasks

    def get_tasks(self):
        ttasks = self._get_ttasks()
        tasks = []
        for tt in ttasks:
            tasks.append(self.PyTaskAdapter(tt))
        return tasks

    def get_projects(self):
        ttasks = self._get_ttasks()
        ttasks = sorted(ttasks, key=lambda x:x['item_order'])

        pmap = {}
        for tt in ttasks:
            already_planned = False
            if self.planned_label_id in tt['labels']:
                already_planned = True
            elif tt['date_string']:
                continue
            t = self.PyTaskAdapter(tt)
            #print(t)
            if already_planned:
                log.debug("Already planned: %-20s", t)
                self.already_planned.append(t)

            if pmap.get(tt['project_id']) is None:
                tp = self.api.projects.get_by_id(tt['project_id'])
                p = Project()
                p.id = tp['id']
                p.name = tp['name']
                p._data = tp

                m = re.match(r"(\d+)\-(.*)", p.name)
                if m:
                    p.name = m.group(2)
                    p.priority = int(m.group(1))
                p.tasks.append(t)
                pmap[tt['project_id']] = p
            else:
                p = pmap[tt['project_id']]
                p.tasks.append(t)

        projects = []
        for k, v in pmap.iteritems():
            projects.append(v)

        log.debug("Number of projects: %d", len(projects))
        log.debug("Number of tasks: %d", len(ttasks))
        log.debug("Number of already planned tasks: %d", len(self.already_planned))

        return projects

    def clean_up(self):
        log.debug("Number of tasks to clear: %d", len(self.already_planned))
        for t in self.already_planned:
            tt = t._data
            tt.update(date_string="")
            log.debug("Clear date_string: %-20s", t)
            if self.planned_label_id in tt['labels']:
                labels = tt['labels'][:]
                labels.remove(self.planned_label_id)
                tt.update(labels=labels)
                log.debug("Clear label: %-20s", t)

    def update(self):
        self.api.commit()


    def update_task(self, t, **kargs):
        tt = t._data
        tt.update(**kargs)

    def update_project(self, project):
        p = project
        i = 0
        updates = []
        if len(p.tasks) < 1:
            return
        for t in p.tasks:
            # Get pytodoist task
            tt = t._data
            tt.update(item_order=i)
            i += 1

    def update_projects(self, projects):
        for p in projects:
            self.update_project(p)

    def get_completed_tasks(self, since=None, until=None):
        # This is a premium only feature
        res = self.completed_tasks
        if not res:
            res = []
            if not self.user.get('is_premium'):
                self.completed_tasks = res
                return res

            completed = self.api.completed.get_all()
            tasks = completed['items']

            for t in tasks:
                res.append(self.PyTaskAdapter(t))

            res = sorted(res, key=lambda x: x.ts_done, reverse=True)
            self.completed_tasks = res

        if since:
            res = filter(lambda x: x.ts_done > since, res)
        if until:
            res = filter(lambda x: x.ts_done < until, res)

        return res

    def num_tasks_completed_today(self, timezone):
        now = datetime.utcnow()
        n = 0

        if not self.completed_tasks:
            self.get_completed_tasks()

        for item in self.completed_tasks:
            if same_date(now, item.ts_done, timezone):
                n = n + 1

        return n

    def mark_as_planned(self, task):
        tt = task._data
        if len(tt['labels']) == 0:
            tt.update(labels=[self.planned_label_id])
        else:
            if self.planned_label_id not in tt['labels']:
                labels = tt['labels'][:]
                labels.append(self.planned_label_id)
                tt.update(labels=labels)

        if task in self.already_planned:
            self.already_planned.remove(task)

    def get_stats(self):
        ttasks = self._get_ttasks()
        return "Total number of tasks: %d" % len(ttasks)

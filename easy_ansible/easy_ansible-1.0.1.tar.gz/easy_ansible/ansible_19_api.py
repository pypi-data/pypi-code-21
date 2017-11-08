#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ansible.runner import Runner
import json


class Command(object):
    def __init__(self, module_name='', module_args='', pattern=''):
        self.module_name = module_name
        self.module_args = module_args
        self.pattern = pattern
        self.results_raw = {}

    def run(self):
        runner = Runner(
            module_name=self.module_name,
            module_args=self.module_args,
            pattern=self.pattern,
            forks=10
        )
        self.results_raw = runner.run()
        print '[ansible] Ansible命令执行结果: \n%s' % json.dumps(self.results_raw, indent=4)

    @property
    def result(self):
        result = {}
        for k, v in self.results_raw.items():
            if k == 'dark':
                for host, info in v.items():
                    result[host] = {'dark': info.get('msg')}
            elif k == 'contacted':
                for host, info in v.items():
                    result[host] = {}
                    if info.get('stdout'):
                        result[host]['stdout'] = info.get('stdout')
                    elif info.get('stderr'):
                        result[host]['stderr'] = info.get('stderr')
        return result

    @property
    def state(self):
        result = {}
        if self.stdout:
            result['ok'] = self.stdout
        if self.stderr:
            result['err'] = self.stderr
        if self.dark:
            result['dark'] = self.dark

        return result

    @property
    def exec_time(self):
        """
        get the command execute time.
        """
        result = {}
        all = self.results_raw.get("contacted")
        for key, value in all.iteritems():
            result[key] = {
                "start": value.get("start"),
                "end": value.get("end"),
                "delta": value.get("delta"), }
        return result

    @property
    def stdout(self):
        """
        get the comamnd standard output.
        """
        result = {}
        all = self.results_raw.get("contacted")
        for key, value in all.iteritems():
            result[key] = value.get("stdout")
        return result

    @property
    def stderr(self):
        """
        get the command standard error.
        """
        result = {}
        all = self.results_raw.get("contacted")
        for key, value in all.iteritems():
            if value.get("stderr") or value.get("warnings"):
                result[key] = {
                    "stderr": value.get("stderr"),
                    "warnings": value.get("warnings"), }
        return result

    @property
    def dark(self):
        """
        get the dark results.
        """
        return self.results_raw.get("dark")
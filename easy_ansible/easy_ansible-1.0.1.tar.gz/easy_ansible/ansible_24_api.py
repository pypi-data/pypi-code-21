#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase


class ResultCallback(CallbackBase):
    def v2_runner_on_ok(self, result, **kwargs):
        """ 每个 play.cmd打印一次 """
        host = result._host
        print json.dumps({host.name: result._result}, indent=4)

    def v2_runner_on_failed(self, result, **kwargs):
        host = result._host
        print json.dumps({host.name: result._result}, indent=4)

    def v2_runner_on_unreachable(self, result, **kwargs):
        host = result._host
        print json.dumps({host.name: result._result}, indent=4)


class PlayQueue(object):
    Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check', 'diff'])

    def __init__(self, module_path, user, sources):
        self.loader = DataLoader()
        self.options = self.Options(
            connection='smart',
            module_path=module_path, forks=100,
            become=None, become_method=None, become_user=user, check=False,
            diff=False
        )
        self.passwords = dict(vault_pass='secret')
        self.results_callback = ResultCallback()
        self.inventory = InventoryManager(loader=self.loader, sources=sources)
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
        self.tqm = TaskQueueManager(
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords=self.passwords,
            stdout_callback=self.results_callback,  # default is 'default'
        )
        self.plays = []

    def add_play(self, play):
        self.plays.append(
            Play().load(play.play_source, variable_manager=self.variable_manager, loader=self.loader)
        )

    def run(self):
        try:
            for play in self.plays:
                print '[ansible] %s流程执行结果: %s' % (play, self.tqm.run(play))
        finally:
            if self.tqm is not None:
                self.tqm.cleanup()
            self.plays = []


class EachPlay(object):
    def __init__(self, name, hosts):
        self.play_source = dict(
            name=name,
            hosts=hosts,
            gather_facts='no',
            tasks=[]
        )

    def add_cmd(self, module_name, module_args):
        self.play_source['tasks'].append(dict(action=dict(module=module_name, args=module_args), register='shell_out'))

# Copyright (c) Ran Dugal 2014
#
# This file is part of dust cluster
#
# Licensed under the GNU Affero General Public License v3, which is available at
# http://www.gnu.org/licenses/agpl-3.0.html
# 
# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero GPL for more details.
#

import logging
import json
import yaml
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase

''' install spark on a base cluster '''

# export commands 
commands  = ['install_spark']


class ResultCallback(CallbackBase):
    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check', 'diff'])


def install_spark(cmdline, cluster, logger):
    '''
    install_spark master workers - install spark on nodes master, workers 
    '''

    args = cmdline.split()
    if len(args) < 2:
        print "usage: install_spark master_node_filter worker_node_filter"
        return

    # initialize needed objects
    loader = DataLoader()
    options = Options(connection='ssh', module_path="", forks=100, become=None, become_method=None, become_user=None, check=False, diff=False)

    # Instantiate our ResultCallback for handling results as they come in
    results_callback = ResultCallback()

    # create inventory and pass to var manager
    inventory = InventoryManager(loader=loader, sources=['/home/booda/hosts'])
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    # create play with tasks
    with open('/home/booda/dev/dust/p2.yaml') as data_file:    
        data = yaml.load(data_file)

    play_source = data
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    # actually run it
    tqm = None
    try:
        tqm = TaskQueueManager(
                inventory=inventory,
                variable_manager=variable_manager,
                loader=loader,
                options=options,
                passwords = None, 
                stdout_callback=None 
            )

        result = tqm.run(play)
    finally:
        if tqm is not None:
            tqm.cleanup()

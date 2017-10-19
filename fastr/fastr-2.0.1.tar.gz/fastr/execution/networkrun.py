# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Network module containing Network facilitators and analysers.
"""
import copy
import datetime
import functools
import itertools
import json
import os
import re
import sys
import time
import traceback
import urlparse
import uuid
from collections import defaultdict
from tempfile import mkdtemp
from threading import Event, Lock
import weakref

import fastr
import fastr.exceptions as exceptions
from fastr.core.samples import SampleItem
from fastr.core.link import Link
from fastr.core.node import Node
from fastr.core.serializable import Serializable
from fastr.core.version import Version
from fastr.data import url
from fastr.execution import node_run_mapping
from fastr.execution.inputoutputrun import OutputRun
from fastr.execution.job import JobState
from fastr.execution.linkrun import LinkRun
from fastr.execution.networkanalyzer import DefaultNetworkAnalyzer
from fastr.execution.networkchunker import DefaultNetworkChunker
from fastr.execution.sinknoderun import SinkNodeRun
from fastr.execution.sourcenoderun import ConstantNodeRun, SourceNodeRun
from fastr.utils import iohelpers, pim_publisher

__all__ = ['NetworkRun']


class NetworkRun(Serializable):
    """
    The Network class represents a workflow. This includes all Nodes (including ConstantNodes, SourceNodes and Sinks) and
    Links.
    """

    NETWORK_DUMP_FILE_NAME = '__fastr_network__.json'
    SOURCE_DUMP_FILE_NAME = '__source_data__.pickle.gz'
    SINK_DUMP_FILE_NAME = '__sink_data__.json'

    def __init__(self, network):
        """
        Create a new, empty Network

        :param str name: name of the Network
        :return: newly created Network
        :raises OSError: if the tmp mount in the fastr.config is not a writable directory
        """
        # Parent for when the run is part of another run (e.g. MacroNodes are involved)
        self.parent = None
        self.thread = None

        # Basic information about the network the Run is based on, and a copy of the network state
        self._network = network.__getstate__()
        self.network_id = network.id
        self.network_version = network.version
        self.network_namespace = network.namespace
        self.network_filename = network.filename
        self.description = network.description

        # Info about the execution run
        self.timestamp = datetime.datetime.now()
        self.uuid = uuid.uuid1()

        # Preferred types
        self.preferred_types = list(network.preferred_types)

        # Recreate nodes
        self.nodelist = {k: node_run_mapping[type(v).__name__](v, parent=self) for k, v in network.nodelist.items()}

        # Set self as parent
        for node in self.nodelist.values():
            node.parent = self

        # Sink results
        self.sink_results = {}

        # Create the link list, make sure all Nodes are in place first
        self.linklist = {}
        for link_id, link in network.linklist.items():
            state = link.__getstate__()

            # Change the link state to target the contents of this NetworkRun
            #  instead of the Network
            state['source'] = state['source'].replace(network.fullid, self.fullid)
            state['target'] = state['target'].replace(network.fullid, self.fullid)

            # Recreate the link inside the NetworkRun
            self.linklist[link_id] = LinkRun.createobj(state, self)

        # Copy step ids
        self.stepids = {}
        for key, nodes in network.stepids.items():
            self.stepids[key] = [self.nodelist[x.id] for x in nodes]

        self.callback_edit_lock = Lock()
        self.executing = False
        self.execution_lock = Event()
        self.execution_lock.set()
        self._job_finished_callback = None
        self._job_status_callback = None

        # Check if temp dir exists, if not try to create it
        if not os.path.exists(fastr.config.mounts['tmp']):
            fastr.log.info("fast temporary directory does not exists, creating it...")
            try:
                os.mkdir(fastr.config.mounts['tmp'])
            except OSError:
                message = "Could not create fastr temporary directory ({})".format(fastr.config.mounts['tmp'])
                fastr.log.critical(message)
                raise exceptions.FastrOSError(message)

        self.tmpdir = None
        self.tmpurl = None

    def _get(self, path):
        value = self
        path = path.split('/')
        for part in path:
            if hasattr(value, part):
                value = getattr(value, part)
            elif hasattr(value, '__getitem__'):
                if isinstance(value, (list, tuple, OutputRun)):
                    value = value[int(part)]
                else:
                    value = value[part]
            else:
                raise exceptions.FastrLookupError('Could not find {} in {}'.format(part, value))

        return value

    def __repr__(self):
        return '<NetworkRun {})>'.format(self.id)

    def __eq__(self, other):
        """
        Compare two Networks and see if they are equal.

        :param other:
        :type other: :py:class:`Network <fastr.core.network.Network>`
        :return: flag indicating that the Networks are the same
        :rtype: bool
        """
        if not isinstance(other, NetworkRun):
            return NotImplemented

        dict_self = {k: v for k, v in self.__dict__.items()}
        del dict_self['callback_edit_lock']
        del dict_self['execution_lock']
        del dict_self['_job_finished_callback']
        del dict_self['_job_status_callback']
        del dict_self['sink_results']

        dict_other = {k: v for k, v in other.__dict__.items()}
        del dict_other['callback_edit_lock']
        del dict_other['execution_lock']
        del dict_other['_job_finished_callback']
        del dict_other['_job_status_callback']
        del dict_other['sink_results']

        return dict_self == dict_other

    def __ne__(self, other):
        """
        Tests for non-equality, this is the negated version __eq__
        """
        return not (self.__eq__(other))

    # Retrieve a Node/Link/Input/Output in the network based on the fullid
    def __getitem__(self, item):
        """
        Get an item by its fullid. The fullid can point to a link, node, input, output or even subinput/suboutput.

        :param str,unicode item: fullid of the item to retrieve
        :return: the requested item
        """
        if not isinstance(item, (str, unicode)):
            raise exceptions.FastrTypeError('Key should be a fullid string, found a {}'.format(type(item).__name__))

        parsed = urlparse.urlparse(item)
        if parsed.scheme != 'fastr':
            raise exceptions.FastrValueError('Item should be an URL with the fastr:// scheme (Found {} in {})'.format(parsed.scheme, item))

        path = parsed.path.split('/')[1:]

        if (len(path) < 2 or
                path[0] != 'networks' or
                path[1] != self.network_id or
                path[2] != str(self.network_version) or
                path[3] != 'runs' or
                path[4] != self.id):
            raise exceptions.FastrValueError(
                'URL {} does not point to anything in this network run, {}'.format(item, path)
            )

        value = self

        for part in path[5:]:
            if hasattr(value, '__getitem__'):
                try:
                    if isinstance(value, (list, tuple, OutputRun)):
                        value = value[int(part)]
                    else:
                        value = value[part]
                except (KeyError, IndexError, TypeError, ValueError):
                    pass
                else:
                    continue

            if hasattr(value, part):
                value = getattr(value, part)
            else:
                raise exceptions.FastrLookupError('Could not find {} in {} (path {})'.format(part, value, path))

        return value

    def __getstate__(self):
        """
        Retrieve the state of the Network

        :return: the state of the object
        :rtype dict:
        """
        state = {
            'timestamp': datetime.datetime.strftime(self.timestamp, '%Y-%m-%dT%H:%M:%S.%f'),
            'uuid': str(self.uuid),
            'network_id': self.network_id,
            'network_version': str(self.network_version),
            'network_filename': self.network_filename,
            'nodelist': [x.__getstate__() for x in self.nodelist.values()],
            'linklist': [x.__getstate__() for x in self.linklist.values()],
            'preferred_types': [x.id for x in self.preferred_types],
            'tmpdir': self.tmpdir,
            'tmpurl': self.tmpurl,
            'network': self._network,
        }

        return state

    def __setstate__(self, state):
        """
        Set the state of the Network by the given state. This completely
        overwrites the old state!

        :param dict state: The state to populate the object with
        :return: None
        """
        # Basic info
        self.network = state.pop('_network', None)
        self.network_id = state.pop('network_id')
        self.network_version = Version(state.pop('network_version'))
        self.network_filename = state.pop('network_filename')
        self.parent = None

        # Info about the execution run (should be moved to NetworkRun in the future)
        self.timestamp = datetime.datetime.strptime(state.pop('timestamp'), '%Y-%m-%dT%H:%M:%S.%f')
        self.uuid = uuid.UUID(state.pop('uuid'))
        self.tmpdir = state.pop('tmpdir', None)
        self.tmpurl = state.pop('tmpurl', None)

        # Initialize nodelists empty to avoid errors further on
        self.nodelist = {}
        self.linklist = {}
        self.preferred_types = []

        # Create required locks
        self.callback_edit_lock = Lock()
        self.execution_lock = Event()
        self.execution_lock.set()
        self.executing = False

        # Set callbacks
        self._job_finished_callback = None
        self._job_status_callback = None

        # These should not be shared between Networks
        state.pop('callback_edit_lock', None)
        state.pop('execution_lock', None)

        # Recreate nodes
        if 'nodelist' in state:
            for node_state in state['nodelist']:
                # Get the node class
                node_class = node_state.get('class', 'NodeRun')
                node_class = getattr(fastr.core.node, node_class)

                node = node_class.createobj(node_state, self)

                fastr.log.debug('Adding node: {}'.format(node))
                self.nodelist[node.id] = node
                node.parent = self
            del state['nodelist']

        # Add preferred types
        state['preferred_types'] = [fastr.typelist[x] for x in state['preferred_types']]

        # Insert empty link_list
        statelinklist = state['linklist']
        state['linklist'] = {}

        # Update the objects dict
        self.__dict__.update(state)

        # Create the link list, make sure all Nodes are in place first
        for link in statelinklist:
            self.linklist[link['id']] = Link.createobj(link, self)

    def check_id(self, id_):
        """
        Check if an id for an object is valid and unused in the Network. The
        method will always returns True if it does not raise an exception.

        :param str id_: the id to check
        :return: True
        :raises FastrValueError: if the id is not correctly formatted
        :raises FastrValueError: if the id is already in use
        """

        regex = r'^\w[\w\d_]*$'
        if re.match(regex, id_) is None:
            raise exceptions.FastrValueError('An id in Fastr should follow'
                                             ' the following pattern {}'
                                             ' (found {})'.format(regex, id_))

        if id_ in self.nodelist or id_ in self.linklist:
            raise exceptions.FastrValueError('The id {} is already in use in {}!'.format(id_, self.id))

        return True

    @property
    def id(self):
        """
        The id of the Network. This is a read only property.
        """
        return '{}_{}'.format(self.network_id,
                              datetime.datetime.strftime(self.timestamp,
                                                         '%Y-%m-%dT%H-%M-%S'))

    @property
    def fullid(self):
        """
        The fullid of the Network
        """
        return 'fastr:///networks/{}/{}/runs/{}'.format(self.network_id,
                                                        self.network_version,
                                                        self.id)

    @property
    def global_id(self):
        """
        The global id of the Network, this is different for networks used in
        macronodes, as they still have parents.
        """
        if self.parent is None:
            return self.fullid
        else:
            return '{}/network_run'.format(self.parent.global_id)

    @property
    def nodegroups(self):
        """
        Give an overview of the nodegroups in the network
        """
        nodegroups = defaultdict(list)
        for node in self.nodelist.values():
            if node.nodegroup is not None:
                nodegroups[node.nodegroup].append(node)
        return nodegroups

    @property
    def long_id(self):
        if self.parent is None:
            return self.network_id
        else:
            return '{}_{}_{}'.format(self.parent.parent.network_id,
                                     self.parent.id,
                                     self.network_id)

    @property
    def job_finished_callback(self):
        if self.parent is not None:
            return self.parent.parent.job_finished_callback
        else:
            return self._job_finished_callback

    @property
    def job_status_callback(self):
        if self.parent is not None:
            return self.parent.parent.job_status_callback
        else:
            return self._job_status_callback

    @property
    def network(self):
        return self._network

    @property
    def sourcelist(self):
        return {k: v for k, v in self.nodelist.items() if isinstance(v, SourceNodeRun) and not isinstance(v, ConstantNodeRun)}

    @property
    def constantlist(self):
        return {k: v for k, v in self.nodelist.items() if isinstance(v, ConstantNodeRun)}

    @property
    def sinklist(self):
        return {k: v for k, v in self.nodelist.items() if isinstance(v, SinkNodeRun)}

    def set_data(self, sourcedata, sinkdata):
        # Set the source and sink data
        for id_, source in self.sourcelist.items():
            if isinstance(source, ConstantNodeRun):
                source.set_data()
            elif id_ in sourcedata:
                source.set_data(sourcedata[id_])
            else:
                raise exceptions.FastrKeyError('Could not find source data for SourceNode {}!'.format(id_))

            source.update()

        for id_, sink in self.sinklist.items():
            if id_ not in sinkdata:
                raise exceptions.FastrKeyError('Could not find sink data for SinkNode {}!'.format(id_))
            sink.set_data(sinkdata[id_])

    def generate_jobs(self):
        fastr.log.debug('=== GENERATE JOBS FOR {} ==='.format(self.id))
        # Create execution objects
        chuncker = DefaultNetworkChunker()
        analyzer = DefaultNetworkAnalyzer()

        # Create a network chuncker to Chunk the Network in executable blocks
        chunks = chuncker.chunck_network(self)

        for chunk in chunks:
            if not self.executing:
                return

            # Create a network analyzer to create the optimal execution order
            executionlist = analyzer.analyze_network(self, chunk)

            # Do not create sink jobs for a macro node
            if self.parent is not None:
                executionlist = [x for x in executionlist if not isinstance(x, SinkNodeRun)]

            for job_lists in itertools.izip_longest(*[x.execute() for x in executionlist]):
                if not self.executing:
                    return

                # Flatten the array of arrays while dropping the Nones (drained iterators)
                job_list = [x for y in job_lists if y is not None for x in y]

                # Only try to process chunks that actually have jobs...
                if len(job_list) > 0:
                    # First queue all jobs that need to run
                    yield job_list

        fastr.log.debug('=== END GENERATE JOBS FOR {} ==='.format(self.id))

    def execute(self, sourcedata, sinkdata, execution_plugin=None, tmpdir=None, cluster_queue=None):
        """
        Execute the Network with the given data. This will analyze the Network,
        create jobs and send them to the execution backend of the system.

        :param dict sourcedata: dictionary containing all data for the sources
        :param dict sinkdata: dictionary containing directives for the sinks
        :param str execution_plugin: the execution plugin to use (None will use the config value)
        :raises FastrKeyError: if a source has not corresponding key in sourcedata
        :raises FastrKeyError: if a sink has not corresponding key in sinkdata
        """
        fastr.log.debug('Acquiring execution lock...')
        self.execution_lock.wait()
        self.execution_lock.clear()
        self.executing = True

        fastr.log.info("####################################")
        fastr.log.info("#     network execution STARTED    #")
        fastr.log.info("####################################")

        # Display the main file the Network is created from, if known it
        # is the network.filename, otherwise try to estimate the entry
        # point for the script used
        entry_file = self.network_filename

        if entry_file is None:
            for x in sys.argv[:2]:
                if os.path.isfile(x):
                    entry_file = x
                    break

        # If there is no entry_file or the first argument is ipython or
        # bpython we assume that is not a network but via prompt
        if entry_file is not None and not entry_file.endswith((os.path.sep + "ipython",
                                                               os.path.sep + "bpython")):
            entry_file = os.path.abspath(entry_file)
            entry_file_date = time.ctime(os.path.getmtime(entry_file))
            message = 'Running network via {} (last modified {})'.format(entry_file, entry_file_date)
        else:
            if entry_file is not None:
                entry_file = os.path.basename(entry_file)
            message = 'Running network via {} session'.format(entry_file or 'python')

        fastr.log.info(message)
        fastr.log.info('FASTR loaded from {}'.format(fastr.__file__))

        if tmpdir is None:
            tmpdir = os.path.normpath(mkdtemp(prefix='fastr_{}_'.format(self.id),
                                              dir=fastr.config.mounts['tmp']))
        else:
            if url.isurl(tmpdir):
                if not tmpdir.startswith('vfs://'):
                    raise exceptions.FastrValueError('The tmpdir keyword argument should be a path or vfs:// url!')
                tmpdir = fastr.vfs.url_to_path(tmpdir)

            if not os.path.exists(tmpdir):
                os.makedirs(tmpdir)

        self.tmpdir = tmpdir
        self.tmpurl = fastr.vfs.path_to_url(self.tmpdir)
        fastr.log.info('Network run tmpdir: {}'.format(self.tmpdir))

        network_file = os.path.join(self.tmpdir, self.NETWORK_DUMP_FILE_NAME)

        # Save a copy of the Network
        iohelpers.save_json(network_file, self.network, indent=2)

        iohelpers.save_gpickle(os.path.join(self.tmpdir,
                                            '__source_run_{}__.pickle.gz'.format(
                                                datetime.datetime.now().isoformat()
                                            )),
                               sourcedata)

        # If needed, send network to PIM for registration
        pim_session = pim_publisher.PimPublisher()
        pim_session.pim_register_run(self)
        self._job_finished_callback = functools.partial(pim_session.pim_update_status, self)
        self._job_status_callback = functools.partial(pim_session.pim_update_status, self)

        try:
            self.set_data(sourcedata, sinkdata)

            # Select desired server execution plugin and instantiate
            fastr.log.debug('Selecting {} as executor plugin'.format(fastr.config.execution_plugin))

            # Checlk what execution plugin to use
            if execution_plugin is None:
                execution_plugin = fastr.config.execution_plugin

            if execution_plugin not in fastr.execution_plugins:
                message = 'Selected non-existing execution plugin ({}), available plugins: {}'.format(execution_plugin,
                                                                                                      fastr.execution_plugins.keys())
                fastr.log.error(message)
                raise exceptions.FastrValueError(message)

            fastr.log.debug('Retrieving execution plugin ({})'.format(execution_plugin))
            execution_interface_type = fastr.execution_plugins[execution_plugin]
            fastr.log.debug('Creating execution interface')

            with execution_interface_type(self.job_finished, self.job_finished, self._job_status_callback) as execution_interface:
                if cluster_queue is not None:
                    execution_interface.default_queue = cluster_queue
                execution_interface._finished_callback = functools.partial(self.job_finished, execution_interface=execution_interface)
                execution_interface._cancelled_callback = functools.partial(self.job_finished, execution_interface=execution_interface)

                for job_list in self.generate_jobs():
                    # Queue jobs but allow cancelling in between
                    for job in job_list:
                        if not self.executing:
                            return
                        execution_interface.queue_job(job)

                    fastr.log.info('Waiting for execution to finish...')
                    # Wait in chuncks of two seconds (hopefully this will allow ipython to update more regularly)
                    while len(execution_interface.job_dict) > 0:
                        sys.stdout.flush()
                        if not self.executing:
                            return
                        time.sleep(1.0)

                    if not self.executing:
                        return

                    fastr.log.info('Chunk execution finished!')

            fastr.log.info("####################################")
            fastr.log.info("#    network execution FINISHED    #")
            fastr.log.info("####################################")
        finally:
            if not self.executing:
                fastr.log.info("####################################")
                fastr.log.info("#    network execution ABORTED     #")
                fastr.log.info("####################################")

            # Make sure to unlock the Network
            fastr.log.debug('Releasing execution lock')
            self.executing = False
            self.execution_lock.set()

        fastr.log.info('===== RESULTS =====')
        result = True
        for sink_node, sink_data in sorted(self.sink_results.items()):
            nr_failed = sum(len(x[1]) > 0 for x in sink_data.values())
            nr_success = len(sink_data) - nr_failed

            if nr_failed > 0:
                result = False

            fastr.log.info('{}: {} success / {} failed'.format(sink_node, nr_success, nr_failed))
        fastr.log.info('===================')

        sink_data_json = {
            sink_node: {
                str(sample_id): {
                    "status": str(job.status),
                    "errors": [list(str(e) for e in x) for x in failed_annotations],
                } for sample_id, (job, failed_annotations) in sink_data.items()
            } for sink_node, sink_data in self.sink_results.items()
        }

        sink_result_file = os.path.join(self.tmpdir, self.SINK_DUMP_FILE_NAME)
        with open(sink_result_file, 'w') as fh_out:
            json.dump(sink_data_json, fh_out, indent=2)

        if not result:
            fastr.log.warning(
"""There were failed samples in the run, to start debugging you can run:

    fastr trace {sink_data_file} --sinks

see the debug section in the manual at https://fastr.readthedocs.io/en/{branch}/static/user_manual.html#debugging for more information.""".format(
    sink_data_file=sink_result_file,
    branch='default' if fastr.version.hg_branch == 'default' else 'develop',
)
            )

        return result

    def abort(self):
        self.executing = False

    def job_finished(self, job, execution_interface):
        """
        Call-back handler for when a job is finished. Will collect the results
        and handle blocking jobs. This function is automatically called when
        the execution plugin finished a job.

        :param job: the job that finished
        :type job: :py:class:`Job <fastr.execution.job.Job>`
        """
        # Find the Node for this job
        node = self[job.node_global_id]

        # Collect earlier failed annotations
        failed_job_annotation = set()
        if not isinstance(node, SourceNodeRun):
            for input_id, input_argument in job.input_arguments.items():
                if not isinstance(input_argument, SampleItem) and isinstance(node, SinkNodeRun):
                    fastr.log.debug('Skipping sink system input: {}'.format(input_argument))
                    continue

                if not isinstance(input_argument, list):
                    input_argument = [input_argument]

                for input_argument_element in input_argument:
                    if str(input_argument_element.id) == '__EMPTY__':
                        continue

                    # Get the annotation from the input
                    fastr.log.debug('Getting annotation from {} --> {}'.format(node.inputs[input_id].get_sourced_outputs(),
                                                                               node.inputs[input_id][input_argument_element.index].failed_annotations))
                    item = node.inputs[input_id][input_argument_element.index]
                    failed_job_annotation.update(item.failed_annotations)

        # Log the status and add annotations if needed
        status_message = "Finished job {} with status {}".format(job.id, job.status)
        fastr.log.info(status_message)

        if job.status not in (JobState.finished, JobState.cancelled):
            if len(job.errors) > 0:
                error = job.errors[0]
                status_message = 'Encountered error: [{e[0]}] {e[1]} ({e[2]}:{e[3]})'.format(e=error)
            else:
                status_message = 'Encountered error in job {}'.format(job.id)

            job_relative_path = job.logurl.replace(self.tmpurl, '.')
            failed_job_annotation.add((job.id, str(job.status), status_message, job_relative_path))

        # Lock Network for editing, make sure not multiple threads will edit network data at the same time
        with self.callback_edit_lock:
            # Data is stored here, need to place it back in the Nodes
            node.set_result(job, failed_job_annotation)

        if self._job_finished_callback is not None:
            #  We will run a callback of which we do not know what it can
            # raise. Since we do not want to callback to crash we use a
            # bare except.
            # pylint: disable=bare-except
            try:
                self._job_finished_callback(job)
            except:
                fastr.log.error('Error in network job finished callback')
                fastr.log.error(traceback.format_exc())
        sys.stdout.flush()


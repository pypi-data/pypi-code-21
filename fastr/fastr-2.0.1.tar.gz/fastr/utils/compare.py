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
Module to compare various fastr specific things such as a execution directory
or a reference directory.
"""

import os

import fastr
from fastr.execution.job import Job
from fastr.execution.networkanalyzer import DefaultNetworkAnalyzer
from fastr.utils.iohelpers import load_gpickle


def compare_set(set1, set2, path, sub_compare_func, f_args=None, f_kwargs=None):
    """
    Compare two sets and dispatch each item to a sub comparison function

    :param Iterable set1: first set of items
    :param Iterable set2: second set of items
    :param str path: identifier of the data location
    :param sub_compare_func: function to apply to items
    :param f_args: args to pass to sub_compare_func
    :param f_kwargs: kwargs to pass to sub_compare_func
    :return: generator that iterates over the differences
    :rtype: generator
    """
    if not isinstance(set1, set):
        set1 = set(set1)

    if not isinstance(set2, set):
        set2 = set(set2)

    if f_args is None:
        f_args = ()

    if f_kwargs is None:
        f_kwargs = {}

    if set1 != set2:
        yield ("{} contains different keys, set 1 exclusively"
               " contains {} and set 2 exclusively contains {}").format(
            path,
            set1.difference(set2),
            set2.difference(set1)
        )

    for item in sorted(set1.intersection(set2)):
        for diff in sub_compare_func(item, *f_args, **f_kwargs):
            yield diff


def compare_execution_dir(path1, path2):
    # Compare network dumps
    network_file1 = os.path.join(path1, fastr.Network.NETWORK_DUMP_FILE_NAME)
    network_file2 = os.path.join(path2, fastr.Network.NETWORK_DUMP_FILE_NAME)

    fastr.log.info('Loading network 1: {}'.format(network_file1))
    network1 = fastr.Network.loadf(network_file1)
    fastr.log.info('Loading network 2: {}'.format(network_file2))
    network2 = fastr.Network.loadf(network_file2)

    fastr.log.debug('Network1 filename: {}'.format(network1.filename))
    fastr.log.debug('Network2 filename: {}'.format(network2.filename))

    if network1 != network2:
        yield "Networks dumps are not equal!"
    else:
        del network2

    # Get the order of the Nodes
    analyzer = DefaultNetworkAnalyzer()
    execution_order = analyzer.analyze_network(
        network1,
        (None, network1.nodelist.values())
    )

    fastr.log.debug('Execution order: "{}"'.format(execution_order))

    # Compare node outputs in execution order
    for node in execution_order:
        fastr.log.debug('Checking node {}'.format(node.id))
        # Get the sample present
        node_dir1 = os.path.join(path1, node.id)
        node_dir2 = os.path.join(path2, node.id)

        if isinstance(node, fastr.SourceNode):
            # Possible source nodes do not exist
            if not os.path.isdir(node_dir1):
                if not os.path.isdir(node_dir2):
                    # Non-existing in both
                    continue
                else:
                    yield("NodeRun '{}' does not have output for result 2")
                    continue
            elif not os.path.isdir(node_dir2):
                yield("NodeRun '{}' does not have output for result 1")
                continue

        for diff in compare_set(
                        os.listdir(node_dir1),
                        os.listdir(node_dir2),
                        node.id,
                        compare_job_dirs,
                        (node, node_dir1, node_dir2)):
            yield diff


def compare_job_dirs(sample, node, node_dir1, node_dir2):
    fastr.log.debug('Checking sample {}'.format(sample))
    result1 = os.path.join(node_dir1, sample, Job.RESULT_DUMP)
    result2 = os.path.join(node_dir2, sample, Job.RESULT_DUMP)

    if not isinstance(node, fastr.SourceNode) or os.path.exists(result1) or os.path.exists(result2):
        job1 = load_gpickle(result1)
        job2 = load_gpickle(result2)

        for diff in compare_set(
                job1.output_data.keys(),
                job2.output_data.keys(),
                '{}/{}'.format(job1.node_id, job1.sample_id),
                compare_job_output_data,
                (job1, job2)):
            yield diff


def compare_job_output_data(output, job1, job2):
    # Compare output data
    data1 = job1.output_data[output]
    data2 = job2.output_data[output]

    if isinstance(data1, list):
        for diff in compare_value_list(data1, data2, '{}/{}'.format(job1.id, output)):
            yield diff
    else:
        for diff in compare_set(
                data1.keys(),
                data2.keys(),
                '{}/{}'.format(job1.node_id, job1.sample_id),
                compare_value_dict_item,
                (data1, data2, '{}/{}'.format(job1.id, output))):
            yield diff


def compare_value_dict_item(key, data1, data2, path):
    if key is not None:
        data1 = data1[key]
        data2 = data2[key]

    path = '{}/{}'.format(path, key)

    for diff in compare_value_list(data1, data2, path):
        yield diff


def compare_value_list(data1, data2, path, key=None):
    if key is not None:
        data1 = data1[key]
        data2 = data2[key]

    fastr.log.debug('Job1 data: {}'.format(data1))
    fastr.log.debug('Job2 data: {}'.format(data2))
    if len(data1) != len(data2):
        yield "Cardinality for {} differs ({} vs {})".format(
                path,
                len(data1),
                len(data2),
        )
    else:
        for index, (item1, item2) in enumerate(zip(data1, data2)):
            if item1 != item2:
                yield "Output data for path {}, index {} does not match ({} vs {})".format(
                        path,
                        index,
                        item1,
                        item2
                      )

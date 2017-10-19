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

import os
import imp

import nose.tools as nt

import fastr


def test_examples():
    examples_dir = fastr.config.examplesdir
    examples = [os.path.join(examples_dir, x) for x in os.listdir(examples_dir) if x.endswith(".py")]
    for example_path in examples:
        example_base, _ = os.path.splitext(os.path.basename(example_path))
        try:
            example_module = imp.load_source(example_base, example_path)
        except:
            # Invalid module, assume that is should be ignored
            continue

        # Only use tests that are marked as such
        if hasattr(example_module, 'IS_TEST') and getattr(example_module, 'IS_TEST'):
            yield run, example_path


def run(example_path):
    # Set some config variables
    fastr.config.pim_host = ''  # Do not publish anything to PIM
    fastr.config.execution_plugin = "LinearExecution"  # This is the safest option
    fastr.config.source_job_limit = 0  # No need to limit in blocking option

    example_base, _ = os.path.splitext(os.path.basename(example_path))
    example_module = imp.load_source(example_base, example_path)
    network = example_module.create_network()

    reference_dir = os.path.join(os.path.dirname(example_path),
                                 'data',
                                 'reference',
                                 '{}_{}'.format(network.id, network.version))

    fastr.log.info('Using reference dir: {}'.format(reference_dir))
    if os.path.isdir(reference_dir):
        result = network.test(reference_dir, network)
        nt.ok_(len(result) == 0, 'Test Network run did not yield same result as the reference run (see log)')
    else:
        nt.ok_(False, 'Could not find reference data for test!')


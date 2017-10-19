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

"""A module to maintain a tool.

Exported classes:

* Tool -- A class encapsulating a tool.
* ParameterDescription -- The base class containing the shared description of
  a parameter (both input and ouput).
* InputParameterDescription -- A class containing the description of an input
  parameter.
* Output ParameterDescription -- A class containing the description of an
  output parameter.
"""

import itertools
import os
import platform
import re
import shutil
from collections import namedtuple, OrderedDict
from tempfile import mkdtemp

import jsonschema

import fastr
from fastr.core.baseplugin import PluginState
import fastr.core.target
import fastr.exceptions as exceptions
from fastr.core.serializable import Serializable
from fastr.core.version import Version
from fastr.data import url
from fastr.utils.checksum import hashsum
from fastr.utils import iohelpers



class Tool(Serializable):
    """
    The class encapsulating a tool.
    """

    __dataschemafile__ = 'Tool.schema.json'

    test_spec = namedtuple('TestSpecification', ['input', 'command', 'output'])
    TOOL_REFERENCE_FILE_NAME = '__fastr_tool_ref__.json'
    TOOL_RESULT_FILE_NAME = '__fastr_tool_result.pickle.gz'

    def __init__(self, doc=None):
        """
        Create a new Tool
        :param doc: path of toolfile or a dict containing the tool data
        :type doc: str or dict
        """

        # Cache value for target binary
        self._target = None

        if doc is None:
            return

        filename = None
        if not isinstance(doc, dict):
            fastr.log.debug('Trying to load file: {}'.format(doc))
            filename = os.path.expanduser(doc)
            filename = os.path.abspath(filename)
            doc = self._loadf(filename)

        # Check if the doc is a valid Tool structure
        try:
            # __unserializer__ is supplied by the serializable meta-class
            # pylint: disable=no-member
            doc = Tool.get_serializer().instantiate(doc)
        except jsonschema.ValidationError:
            fastr.log.error('Could not validate Tool data again the schema!')
            raise
        else:
            fastr.log.debug('Tool schema validated!')

        # Get attributes from root node
        self.filename = filename

        #: Identifier for the tool
        regex = r'^[A-Z][\w\d_]*$'
        if re.match(regex, doc['id']) is None:
            message = 'A tool id in Fastr should be UpperCamelCase as enforced' \
                      ' by regular expression {} (found {})'.format(regex, doc['id'])
            fastr.log.warning(message)

        self.id = doc['id']

        #: The namespace this tools lives in, this will be set by the ToolManager on load
        self.namespace = None

        #: Name of the tool, this should be a descriptive, human readable name.
        self.name = doc.get('name', self.id)

        #: Version of the tool, not of the underlying software
        self.version = Version(str(doc.get('version')))

        #: Class for of the Node to use
        self.node_class = doc.get('class', 'Node')

        if self.id is None or self.name is None or self.version is None:
            raise exceptions.FastrValueError('Tool should contain an id, name and version!')

        #: URL to website where this tool can be downloaded from
        self.url = doc.get('url', '')

        #: Description of the tool and it's functionality
        self.description = doc.get('description', '')

        #: List of authors of the tool. These people wrapped the executable but
        #: are not responsible for executable itself.
        self.authors = doc['authors']

        #: List of tags for this tool
        self.tags = doc.get('tags', [])

        # Parse references field and format them into a dictionary
        #: A list of documents and in depth reading about the methods used in this tool
        self.references = doc.get('references', [])

        #: Requirements for this Tool
        #:
        #: .. warning:: Not yet implemented
        self.requirements = None

        #: Test for this tool. A test should be a collection of inputs, parameters
        #: and outputs to verify the proper functioning of the Tool.
        #:
        #: The format of the tests is a list of namedtuples, that have 3 fields:
        #: - input: a dict of the input data
        #: - command: a list given the expected command-line arguments
        #: - output: a dict of the output data to validate
        #:
        #: .. warning:: Not yet implemented

        self.tests = doc['tests']

        command = doc['command']

        # Find commands
        #: Command is a dictionary contain information about the command which is
        #: called by this Tool:
        #: command['interpreter'] holds the (possible) interpreter to use
        #: command['targets'] holds a per os/arch dictionary of files that should be executed
        #: command['url'] is the webpage of the command to be called
        #: command['version'] is the version of the command used
        #: command['description'] can help a description of the command
        #: command['authors'] lists the original authors of the command
        self.command = {
            'targets': command['targets'],
            'license': command.get('license', ''),
            'url': command.get('url', ''),
            'version': Version(str(command.get('version'))),
            'description': command.get('description', ''),
            'authors': command.get('authors', [])
        }

        if len(self.command['targets']) == 0:
            raise exceptions.FastrValueError("No targets defined in tool description.")

        #: This holds the citation you should use when publishing something based on this Tool
        self.cite = doc['cite']

        #: Man page for the Tool. Here usage and examples can be described in detail
        self.help = doc['help']

        #: Create the Interface based on the class specified in the tool file
        interface_class = fastr.interfaces[doc['interface'].get('class', 'FastrInterface')]

        if interface_class.status != PluginState.loaded:
            raise exceptions.FastrPluginNotLoaded('Required InterfacePlugin {} was not loaded properly (status {})'.format(interface_class.id,
                                                                                                                           interface_class.status))

        self.interface = interface_class(id_='{}_{}_interface'.format(self.id, self.command['version']), document=doc['interface'])

    @property
    def hash(self):
        return hashsum(self.__getstate__())

    @property
    def ns_id(self):
        """
        The namespace and id of the Tool
        """
        if self.namespace is None:
            return self.id
        else:
            return '{}.{}'.format(self.namespace, self.id)
    @property
    def fullid(self):
        """
        The full id of this tool
        """
        return 'fastr:///tools/{}/{}'.format(self.ns_id, self.version)

    @property
    def inputs(self):
        return self.interface.inputs

    @property
    def outputs(self):
        return self.interface.outputs

    @property
    def target(self):
        """
        The OS and arch matched target definition.
        """
        if self._target is not None:
            return self._target

        # Get platform and os
        arch = platform.architecture()[0].lower()
        os_ = platform.system().lower()

        matching_targets = [x for x in self.command['targets'] if x['os'] in [os_, '*'] and x['arch'] in [arch, '*']]

        if len(matching_targets) == 0:
            return None
        elif len(matching_targets) == 1:
            target = matching_targets[0]
        else:
            # This should give the optimal match
            for match in matching_targets:
                match['score'] = 0

                if match['os'] == os_:
                    match['score'] += 2

                if match['arch'] == arch:
                    match['score'] += 1

            matching_targets = sorted(matching_targets, reverse=True, key=lambda x: x['score'])
            fastr.log.debug('Sorted matches: {}'.format(matching_targets))
            target = matching_targets[0]

        cls = target.get('class', 'LocalBinaryTarget')
        cls = fastr.targets[cls]

        # Create target from curdir
        old_curdir = os.path.abspath(os.curdir)
        os.chdir(self.path)

        # Check if the argument binary exists
        if 'binary' not in target:
            if 'bin' in target:
                target['binary'] = target['bin']
                del target['bin']
            else:
                fastr.exceptions.FastrValueError('Target does not contain required "binary" (or "bin") argument')

        self._target = cls(**target)
        os.chdir(old_curdir)

        return self._target

    def _prepare_payload(self, payload=None, **kwargs):
        # Allow kwargs to be used instead of payload
        if payload is None:
            payload = {'inputs': {}, 'outputs': {}}
            for key, value in kwargs.items():
                if key in self.inputs and key in self.outputs:
                    raise exceptions.FastrValueError('Cannot figure out if "{}" is an input or output, please prefix with input_/output_ as needed')
                elif key in self.inputs:
                    payload['inputs'][key] = value
                elif key in self.outputs:
                    payload['outputs'][key] = value
                elif key.startswith('input_') and key[6:] in self.inputs:
                    payload['inputs'][key[6:]] = value
                elif key.startswith('output_') and key[7:] in self.outputs:
                    payload['outputs'][key[7:]] = value
                else:
                    raise exceptions.FastrValueError('Cannot match key "{}" to any input/output!'.format(key))

        # Make sure all values are wrapped in a tuple (for single values)
        for key, value in payload['inputs'].items():
            if not isinstance(value, (tuple, OrderedDict)):
                payload['inputs'][key] = (value,)
        for key, value in payload['outputs'].items():
            if not isinstance(value, (tuple, OrderedDict)):
                payload['outputs'][key] = (value,)

        return payload

    def execute(self, payload=None, **kwargs):
        """
        Execute a Tool given the payload for a single run

        :param payload: the data to execute the Tool with
        :returns: The result of the execution
        :rtype: InterFaceResult
        """
        payload = self._prepare_payload(payload=payload, **kwargs)
        target = self.target
        fastr.log.info('Target is {}'.format(target))

        if target is None:
            arch = platform.architecture()[0].lower()
            os_ = platform.system().lower()
            raise exceptions.FastrValueError('Cannot find a viable target for {}/{} on {} ({} bit)'.format(self.id, self.version, os_, arch))

        fastr.log.info('Using payload: {}'.format(payload))
        with target:
            result = self.interface.execute(target, payload)

        return result

    def __str__(self):
        """
        Get a string version for the Tool

        :return: the string version
        :rtype: str
        """
        return '<Tool: {} version: {}>'.format(self.id, self.version)

    def __repr__(self):
        """
        Get a string representation for the Tool. This will show the inputs
        and output defined in a table-like structure.

        :return: the string representation
        :rtype: str
        """
        if self.name is not None and len(self.name) > 0:
            name_part = ' ({})'.format(self.name)
        else:
            name_part = ''

        return_list = ["Tool {} v{}{}".format(self.id, str(self.command['version']), name_part)]

        # The "+ [8]" guarantees a minimum of 8 width and avoids empty lists
        width_input_keys = max([len(x.id) for x in self.inputs.values()] + [8])
        width_input_types = max([len(x.datatype) for x in self.inputs.values()] + [8]) + 2
        width_output_keys = max([len(x.id) for x in self.outputs.values()] + [8])
        width_output_types = max([len(x.datatype) for x in self.outputs.values()] + [8]) + 2

        return_list.append('{:^{}}  | {:^{}}'.format('Inputs', width_input_types + width_input_keys + 1,
                                                     'Outputs', width_output_types + width_output_keys + 1))
        return_list.append('-' * (width_input_keys + width_input_types + width_output_keys + width_output_types + 7))
        for input_, output in itertools.izip_longest(self.inputs.values(), self.outputs.values()):
            if input_ is None:
                input_id = ''
                input_type = ''
            else:
                input_id = input_.id
                input_type = '({})'.format(input_.datatype)

            if output is None:
                output_id = ''
                output_type = ''
            else:
                output_id = output.id
                output_type = '({})'.format(output.datatype)

            return_list.append('{:{}} {:{}}  |  {:{}} {:{}}'.format(input_id, width_input_keys,
                                                                    input_type, width_input_types,
                                                                    output_id, width_output_keys,
                                                                    output_type, width_output_types))

        return '\n'.join(return_list)

    def __eq__(self, other):
        """Compare two Tool instances with each other.

        :param other: the other instances to compare to
        :type other: Tool
        :returns: True if equal, False otherwise
        """
        if not isinstance(other, Tool):
            return NotImplemented

        dict_self = dict(self.__dict__)
        del dict_self['_target']

        dict_other = dict(other.__dict__)
        del dict_other['_target']

        return dict_self == dict_other

    def __getstate__(self):
        """
        Retrieve the state of the Tool

        :return: the state of the object
        :rtype dict:
        """
        state = {k: v for k, v in self.__dict__.items()}
        state['command'] = {k: v for k, v in self.command.items()}

        state['class'] = state['node_class']
        state['interface'] = self.interface.__getstate__()
        state['command']['version'] = str(self.command['version'])
        state['version'] = str(self.version)
        del state['node_class']
        del state['_target']

        return state

    def __setstate__(self, state):
        """
        Set the state of the Tool by the given state.

        :param dict state: The state to populate the object with
        """
        if 'filename' not in state:
            state['filename'] = None

        state['version'] = Version(state['version'])
        state['command']['version'] = Version(str(state['command']['version']))

        state['node_class'] = state['class']
        del state['class']

        interface_class = fastr.interfaces[state['interface'].get('class', 'FastrInterface')]
        if 'id' not in state['interface']:
            state['interface']['id'] = '{}_{}_interface'.format(state['id'], state['command']['version'])

        if interface_class.status != PluginState.loaded:
            raise exceptions.FastrPluginNotLoaded('Required InterfacePlugin {} was not loaded properly (status {})'.format(interface_class.id,
                                                                                                                           interface_class.status))

        state['interface'] = interface_class.createobj(state['interface'])
        self.__dict__.update(state)
        self._target = None

        # TODO: set interface link

    @property
    def path(self):
        """
        The path of the directory in which the tool definition file was
        located.
        """
        return os.path.dirname(self.filename)

    @property
    def command_version(self):
        return self.command['version']

    def create_reference(self, input_data, output_directory, mount_name='__ref_tmp__', copy_input=True):
        # Make sure the output directory is absolute for later on
        output_directory = os.path.abspath(os.path.expanduser(output_directory))

        # Create output directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        input_data_dir = os.path.join(output_directory, 'input_data')

        if not os.path.exists(input_data_dir):
            os.mkdir(input_data_dir)

        output_data_dir = os.path.join(output_directory, 'output_data')

        if not os.path.exists(output_data_dir):
            os.mkdir(output_data_dir)

        # Add the temporary mount
        fastr.config.read_config_string('mounts["{}"] = "{}"'.format(mount_name, output_directory))

        # If desired, copy input data to data directory in output directory
        if copy_input:
            fastr.log.info('Copying input data into reference directory...')
            new_input_data = {}
            stored_input_data = {}
            for input_id, input_value in input_data.items():
                new_input_value = []
                stored_input_value = []

                # Make sure we are working with tuples
                if isinstance(input_value, list):
                    input_value = tuple(input_value)

                if not isinstance(input_value, tuple):
                    input_value = input_value,

                # Datatype for this input
                datatype = fastr.typelist[self.inputs[input_id].datatype]

                # If needed copy the data
                for value in input_value:
                    if isinstance(value, basestring) and os.path.exists(value):
                        filename = os.path.basename(value)
                        destination = 'vfs://{}/input_data/{}'.format(mount_name, filename)
                        fastr.vfs.push_sink_data(value, destination, datatype=datatype)
                        new_input_value.append(fastr.vfs.url_to_path(destination))
                        stored_input_value.append('$REFDIR/input_data/{}'.format(filename))
                    else:
                        new_input_value.append(value)
                        stored_input_value.append(value)
                new_input_data[input_id] = tuple(new_input_value)
                stored_input_data[input_id] = tuple(stored_input_value)
        else:
            new_input_data = input_data
            stored_input_data = input_data

        test_data = {
            'input_data': stored_input_data,
            'used_input_data': new_input_data,
            'original_input_data': input_data,
            'tool': self.ns_id,
            'version': str(self.command_version),
        }

        # New replace input_data with new input data
        input_data = new_input_data

        # Save the test summary to the reference file
        fastr.log.info('Saving basic reference information')
        iohelpers.save_json(
            os.path.join(output_directory, self.TOOL_REFERENCE_FILE_NAME),
            test_data
        )

        # Reference payload as a shortcut
        payload = {'inputs': input_data, 'outputs': {}}

        # Create output arguments automatically
        from fastr.execution.job import Job

        fastr.log.info('Determining values for outputs')
        for id_, argument in self.outputs.items():
            # Determine cardinality
            if not argument.automatic:
                cardinality = Job.calc_cardinality(argument.cardinality, payload)
            else:
                cardinality = 1

            # Create output arguments automatically
            payload['outputs'][id_] = Job.fill_output_argument(output_spec=argument,
                                                               cardinality=cardinality,
                                                               desired_type=fastr.typelist[argument.datatype],
                                                               requested=True,
                                                               tmpurl='vfs://{}/output_data'.format(mount_name))

        fastr.log.info('Resulting test data: {}'.format(test_data))

        fastr.log.info('Executing tool...')
        result = self.execute(payload=payload)
        result.command = result.log_data['command']

        # Translate command to avoid hard links to output_directory
        fastr.log.info('Processing results for use as reference data')
        pattern = r'^{}'.format(output_data_dir)  # Do no substitute for input data
        result.reference_command = [re.sub(pattern, '$OUTDIR', x, 1) for x in result.log_data['command']]
        result.reference_command = ['$INDIR/{}'.format(os.path.basename(x)) if os.path.exists(x) else x for x in result.reference_command]

        # Translate results back
        output_data = {}
        for key, value in result.result_data.items():
            datatype = fastr.typelist[self.outputs[key].datatype]
            preferred_type = datatype

            output_data[key] = Job.translate_output_results(value,
                                                            datatype=datatype,
                                                            preferred_type=preferred_type,
                                                            mountpoint=mount_name)

        result.output_data = output_data

        fastr.config.read_config_string('del mounts["{}"]'.format(mount_name))

        fastr.log.info('Saving results for reference...')
        iohelpers.save_gpickle(
            os.path.join(output_directory, self.TOOL_RESULT_FILE_NAME),
            result
        )
        fastr.log.info('Finishing creating reference data for {}/{}'.format(self.ns_id, self.command_version))

    @staticmethod
    def compare_output_data(current_output_data, reference_output_data, validation_result, output):
        fastr.log.info('Current output data: {}'.format(current_output_data))
        fastr.log.info('Reference output data: {}'.format(reference_output_data))
        for nr, (current_value, reference_value) in enumerate(zip(current_output_data, reference_output_data)):
            if current_value != reference_value:
                validation_result.append('\n'.join((
                    'Value for {}/{} was not equal! (found "{}", expected "{}")'.format(
                        output,
                        nr,
                        current_value,
                        reference_value,
                    ),
                    'Output: [{}] {!r}'.format(type(current_value).__name__,
                                               current_value),
                    'Reference: [{}] {!r}'.format(type(reference_value).__name__,
                                                  reference_value),
                )))

    @classmethod
    def test_tool(cls, reference_data_dir, tool=None, input_data=None):
        """
        Execute the tool with the input data specified and test the results
        against the refence data. This effectively tests the tool execution.

        :param str reference_data_dir: The path or vfs url of reference data to compare with
        :param dict source_data: The source data to use
        """
        if not isinstance(reference_data_dir, basestring):
            raise exceptions.FastrTypeError('reference_data_dir should be a string!')

        if reference_data_dir.startswith('vfs://'):
            reference_data_dir = fastr.vfs.url_to_path(reference_data_dir)

        if not os.path.isdir(reference_data_dir):
            raise exceptions.FastrTypeError('The reference_data_dir should be pointing to an existing directory!'
                                            ' {} does not exist'.format(reference_data_dir))

        test_data = iohelpers.load_json(
            os.path.join(reference_data_dir, cls.TOOL_REFERENCE_FILE_NAME)
        )

        if tool is None:
            tool = fastr.toollist[test_data['tool'], test_data['version']]

        fastr.log.info('Testing tool {}/{} against {}'.format(
            tool.ns_id,
            tool.command_version,
            reference_data_dir,
        ))

        if input_data is None:
            input_data = {}

            for key, value in test_data['input_data'].items():
                if not isinstance(value, (tuple, list)):
                    value = value,

                # Set the $REFDIR correctly (the avoid problems with moving the reference dir)
                value = tuple(x.replace('$REFDIR', reference_data_dir) if isinstance(x, basestring) else x for x in value)
                input_data[key] = value

        temp_results_dir = None
        reference_result = iohelpers.load_gpickle(os.path.join(reference_data_dir, cls.TOOL_RESULT_FILE_NAME))

        validation_result = []
        try:
            # Create temporary output directory
            temp_results_dir = os.path.normpath(mkdtemp(
                prefix='fastr_tool_test_'.format(tool.id), dir=fastr.config.mounts['tmp']
            ))

            # Create a new reference for comparison
            fastr.log.info('Running tool and creating new reference data for comparison...')
            try:
                tool.create_reference(input_data,
                                      temp_results_dir,
                                      mount_name='__test_tmp__',
                                      copy_input=False)
            except Exception as exception:
                fastr.log.warning('Encountered exception when trying to run the {}/{} tool!'.format(tool.ns_id, tool.command_version))
                fastr.log.warning('Exception: [{}] {}'.format(type(exception).__name__, exception))
                validation_result.append('Encountered {}: {}'.format(type(exception).__name__, exception))
                return validation_result

            current_result = iohelpers.load_gpickle(os.path.join(temp_results_dir, cls.TOOL_RESULT_FILE_NAME))

            fastr.log.info('Comparing current run against reference run...')

            # First check the command and return code
            if current_result.reference_command != reference_result.reference_command:
                validation_result.append('\n'.join((
                    'Different command used for execution of tool "{}/{}"'.format(tool.ns_id, tool.command_version),
                    'Current command: {}'.format(current_result.reference_command),
                    'Reference command {}'.format(reference_result.reference_command),
                )))

            if current_result.log_data['returncode'] != reference_result.log_data['returncode']:
                validation_result.append('\n'.join((
                    'Different returncode used for execution of tool "{}/{}"'.format(tool.ns_id, tool.returncode_version),
                    'Current returncode: {}'.format(current_result.log_data['returncode']),
                    'Reference returncode {}'.format(reference_result.log_data['returncode']),
                )))

            # Check if the outputs are the same
            current_outputs = sorted(reference_result.output_data.keys())
            reference_outputs = sorted(current_result.output_data.keys())
            if current_outputs != reference_outputs:
                validation_result.append('\n'.join((
                    'Different outputs found in tool "{}/{}"'.format(tool.ns_id, tool.command_version),
                    'Current outputs: {}'.format(current_outputs),
                    'Reference outputs {}'.format(reference_outputs),
                )))

            # Add the mounts need to find the data
            fastr.config.read_config_string('mounts["__test_tmp__"] = "{}"'.format(temp_results_dir))
            fastr.config.read_config_string('mounts["__ref_tmp__"] = "{}"'.format(reference_data_dir))

            # Check if values for all outputs match
            for output in reference_outputs:
                current_output_data = current_result.output_data[output]
                reference_output_data = reference_result.output_data[output]
                if type(current_output_data) != type(reference_output_data):
                    validation_result.append('\n'.join((
                        'Different type for output {} found in tool "{}/{}"'.format(tool.ns_id, tool.command_version),
                        'Current type: {}'.format(type(current_output_data)),
                        'Reference type {}'.format(type(reference_output_data)),
                    )))

                if isinstance(current_output_data, dict):
                    raise exceptions.FastrNotImplementedError('Output comparison of dict structures is not supported yet!')
                else:
                    cls.compare_output_data(
                        current_output_data,
                        reference_output_data,
                        validation_result,
                        output
                    )

            # Remove the temporary mounts again
            fastr.config.read_config_string('del mounts["__test_tmp__"]')
            fastr.config.read_config_string('del mounts["__ref_tmp__"]')

            if len(validation_result) == 0:
                fastr.log.info('Run and reference were equal! Test passed!')
            else:
                fastr.log.info('Found difference with reference data! Test failed!')
                for line in validation_result:
                    fastr.log.info(line)
            return validation_result
        finally:
            # Clean up
            fastr.log.info('Removing temp result directory {}'.format(temp_results_dir))
            if temp_results_dir is not None and os.path.isdir(temp_results_dir):
                shutil.rmtree(temp_results_dir, ignore_errors=True)

    def test(self, reference=None):
        """
        Run the tests for this tool
        """
        if reference is None:
            result = []
            tool_dir = os.path.dirname(self.filename)
            for test in self.tests:
                reference_dir = os.path.abspath(os.path.join(tool_dir, test))
                try:
                    result.extend(self.test_tool(reference_data_dir=reference_dir, tool=self))
                except exceptions.FastrTypeError:
                    message = 'Reference data in {} is not valid!'.format(reference_dir)
                    fastr.log.warning(message)
                    result.append(message)
        else:
            result = self.test_tool(reference_data_dir=reference, tool=self)

        return result

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
Classes for arranging the input and output for nodes.

Exported classes:

Input -- An input for a node (holding datatype).
Output -- The output of a node (holding datatype and value).
ConstantOutput -- The output of a node (holding datatype and value).

.. warning::
   Don't mess with the Link, Input and Output internals from other places.
   There will be a huge chances of breaking the network functionality!
"""
import itertools
from abc import abstractmethod

import sympy

import fastr
import fastr.exceptions as exceptions
from fastr.core.dimension import Dimension
from fastr.core.samples import SampleItem, SampleId, SampleIndex, SampleValue, SampleCollection, ContainsSamples, HasSamples
from fastr.core.datatypemanager import typelist
from fastr.core.inputoutput import BaseInput, BaseOutput
from fastr.datatypes import DataType


class BaseInputRun(HasSamples, BaseInput):
    """
    Base class for all inputs runs.
    """

    def __init__(self, node_run, template):
        """
        Instantiate a BaseInput

        :param node: the parent node the input/output belongs to.
        :param description: the :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
                            describing the input/output.
        :return: the created BaseInput
        :raises FastrTypeError: if description is not of class
                                :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
        :raises FastrDataTypeNotAvailableError: if the DataType requested cannot be found in the ``fastr.typelist``
        """
        super(BaseInputRun, self).__init__(node_run, template.description)

    @abstractmethod
    def itersubinputs(self):
        """
        Iterator over the SubInputs

        :return: iterator

        example:

        .. code-block:: python

          >>> for subinput in input_a.itersubinputs():
                  print subinput

        """
        raise exceptions.FastrNotImplementedError('Purposefully not implemented')


class InputRun(BaseInputRun):
    """
    Class representing an input of a node. Such an input will be connected
    to the output of another node or the output of an constant node to provide
    the input value.
    """

    def __init__(self, node_run, template):
        """
        Instantiate an input.

        :param template: the Input that the InputRun is based on
        """
        self._source = {}
        super(InputRun, self).__init__(node_run, template)
        self._input_group = template.input_group

    def __getstate__(self):
        """
        Retrieve the state of the Input

        :return: the state of the object
        :rtype dict:
        """
        state = super(InputRun, self).__getstate__()
        state['input_group'] = self.input_group

        return state

    def __setstate__(self, state):
        """
        Set the state of the Input by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(InputRun, self).__setstate__(state)
        self._input_group = state['input_group']

    def __getitem__(self, key):
        """
        Retrieve an item from this Input.

        :param key: the key of the requested item, can be a key str, sample
                    index tuple or a :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :type key: str, :py:class:`SampleId <fastr.core.sampleidlist.SampleId>` or tuple
        :return: the return value depends on the requested key. If the key was
                 an int the corresponding :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
                 will be returned. If the key was a :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
                 or sample index tuple, the corresponding
                 :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` will be returned.
        :rtype: :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` or
                :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        :raises FastrTypeError: if key is not of a valid type
        :raises FastrKeyError: if the key is not found
        """
        if not isinstance(key, (int, str, SampleId, SampleIndex)):
            raise exceptions.FastrTypeError('Input indices must a int, str, SampleId or '
                                            'SampleIndex, not {}'.format(type(key).__name__))

        if isinstance(key, (SampleId, SampleIndex)):
            data = []
            # Create mapping items of key; value and combine those
            self_size = self.size
            for subindex_key, sub in self.source.items():
                # Allow the same mixing of parts of a mapped input as in input groups
                if sub.size == self_size:
                    value = sub[key]
                elif sub.size == (1,):
                    value = sub[SampleIndex(0)]
                elif sub.size == (0,) or sub.size == ():
                    value = SampleItem(SampleIndex(0), '__EMPTY__', SampleValue(), set(), set())
                else:
                    raise exceptions.FastrSizeMismatchError('Input has inconsistent size/dimension'
                                                            ' info for (sub)Input {}'.format(sub.fullid))

                data.append(SampleItem(value.index,
                                       value.id,
                                       {subindex_key: tuple(value.data.sequence_part())},
                                       value.jobs,
                                       value.failed_annotations))

            combination = SampleItem.combine(data)
            return combination

        if key not in self.source:
            # This is to allow for linking against inputs['key'][0]
            try:
                key = int(key)
            except ValueError:
                pass  # No problem, just go for the str

            self.source[key] = SubInputRun(self)

        return self.source[key]

    def __str__(self):
        """
        Get a string version for the Input

        :return: the string version
        :rtype: str
        """
        return '<InputRun: {})>'.format(self.fullid)

    def cardinality(self, key=None, job_data=None):
        """
        Cardinality for an Input is the sum the cardinalities of the SubInputs,
        unless defined otherwise.

        :param key: key for a specific sample, can be sample index or id
        :type key: tuple of int or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        """

        cardinality = 0

        for subinput in self.source.values():
            cardinality += subinput.cardinality(key, job_data)

        return cardinality

    def remove(self, value):
        """
        Remove a SubInput from the SubInputs list.

        :param value: the :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
                      to removed from this Input
        :type value: :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        """
        for key, val in self.source.items():
            if value is val:
                self._source.pop(key)

    @property
    def datatype(self):
        """
        The datatype of this Input
        """
        return self._datatype

    @datatype.setter
    def datatype(self, value):
        # This does not differ, as it is a property
        # pylint: disable=arguments-differ
        self._datatype = value
        for subinput in self.itersubinputs():
            subinput.datatype = value

    @property
    def fullid(self):
        """
        The full defining ID for the Input
        """
        if self.node is not None:
            return '{}/inputs/{}'.format(self.node.fullid, self.id)
        else:
            return 'fastr://ORPHANED/inputs/{}'.format(self.id)

    @property
    def input_group(self):
        """
        The id of the :py:class:`InputGroup <fastr.core.node.InputGroup>` this
        Input belongs to.
        """
        return self._input_group

    @property
    def dimensions(self):
        """
        The size of the sample collections that can accessed via this Input.
        """
        subinputs = list(self.itersubinputs())
        sizes = [sub.size for sub in subinputs]
        unique_sizes = set(sizes) - set([(0,), (1,)])

        if len(unique_sizes) > 1:
            size_map = {x.source_output.id: x.size for x in self.itersubinputs()}

            # Check if the sizes can match if we ignore symbols
            for index in itertools.izip_longest(*unique_sizes):
                index = set(x for x in index if isinstance(x, int))

                if len(index) > 1:
                    message = 'Conflicting sizes of SubInputs ({}) full size map: {}'.format(unique_sizes,
                                                                                             size_map)
                    fastr.log.error(message)
                    raise exceptions.FastrSizeMismatchError(message)

            # Return dimensions of first subinput with possible size match
            for sub in subinputs:
                if sub.size in unique_sizes:
                    return sub.dimensions
        elif len(unique_sizes) == 1:
            return subinputs[sizes.index(unique_sizes.pop())].dimensions
        elif (1,) in sizes:
            return subinputs[sizes.index((1,))].dimensions
        elif (0,) in sizes:
            return subinputs[sizes.index((0,))].dimensions
        else:
            return ()

    @property
    def source(self):
        """
        The mapping of :py:class:`SubInputs <fastr.core.inputoutput.SubInput>`
        that are connected and have more than 0 elements.
        """
        return self._source

    @source.setter
    def source(self, value):
        """
        The list of :py:class:`SubInputs <fastr.core.inputoutput.SubInput>`
        that are connected and have more than 0 elements. (setter)
        """
        self.clear()

        self._source = {0: SubInputRun(self)}
        self._source[0].source = value

    def get_sourced_nodes(self):
        """
        Get a list of all :py:class:`Nodes <fastr.core.node.Node>` connected as sources to this Input

        :return: list of all connected :py:class:`Nodes <fastr.core.node.Node>`
        :rtype: list
        """
        return list(set(n for subinput in self.itersubinputs() for n in subinput.get_sourced_nodes()))

    def get_sourced_outputs(self):
        """
        Get a list of all :py:class:`Outputs <fastr.core.inputoutput.Output>` connected as sources to this Input

        :return: tuple of all connected :py:class:`Outputs <fastr.core.inputoutput.Output>`
        :rtype: tuple
        """
        return tuple(n for subinput in self.itersubinputs() for n in subinput.get_sourced_outputs())

    def index(self, value):
        """
        Find index of a SubInput

        :param value: the :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
                      to find the index of
        :type value: :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        :return: key
        :rtype: int, str
        """
        for key, val in self.source.items():
            if val is value:
                return key
        else:
            return None

    def insert(self, index):
        """
        Insert a new SubInput at index in the sources list

        :param int key: positive integer for position in _source list to insert to
        :return: newly inserted :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        :rtype: :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        """
        newsub = SubInputRun(self)
        self.source[index] = newsub
        return newsub

    def itersubinputs(self):
        """
        Iterate over the :py:class:`SubInputs <fastr.core.inputoutput.SubInput>`
        in this Input.

        :return: iterator yielding  :py:class:`SubInput <fastr.core.inputoutput.SubInput>`


        example:

        .. code-block:: python

          >>> for subinput in input_a.itersubinputs():
                  print subinput

        """
        for subinput in self.source.values():
            yield subinput

    def _update(self, key, forward=True, backward=False):
        """Update the validity of the Input and propagate the update downstream.
        An Input is valid if:

        * All SubInputs are valid (see :py:meth:`SubInput.update <fastr.core.inputoutput.SubInput.update>`)
        * Cardinality is correct
        * If Input is required, it must have a size larger than (0,)
        """
        # fastr.log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.fullid))
        for subinput in self.itersubinputs():
            subinput.update(key, forward, backward)

        valid = True
        messages = []
        for subinput in self.itersubinputs():
            if not subinput.valid:
                valid = False
                for message in subinput.messages:
                    messages.append('SubInput {} is not valid: {}'.format(subinput.fullid, message))

        if self.check_cardinality() is None or self:
            # If the cardinality is 0 and Input is not required, this is fine,
            # all other cases are not allowed
            if self.required and self.cardinality() == 0:
                valid = False
                messages.append(('Input "{}" cardinality ({}) is not valid (must'
                                 ' be {}, required is {})').format(self.id,
                                                                   self.cardinality(),
                                                                   self._description.cardinality,
                                                                   self.required))
        if self.size is None:
            valid = False
            messages.append('Cannot determine size of Input "{}"'.format(self.id))

        fastr.log.debug('Size: {}'.format(self.size))
        if self.required and (len([x for x in self.size if x != 0]) == 0):
            valid = False
            nodes = ', '.join([x.id for x in self.get_sourced_nodes()])
            messages.append(('Required Input "{}" cannot have size 0. Input obtained'
                             ' from nodes: {}').format(self.id, nodes))

        self._status['valid'] = valid
        self._status['messages'] = messages

        # Update downstream
        self.node.update(key, forward, backward)


class SubInputRun(BaseInputRun):
    """
    This class is used by :py:class:`Input <fastr.core.inputoutput.Input>` to
    allow for multiple links to an :py:class:`Input <fastr.core.inputoutput.Input>`.
    The SubInput class can hold only a single Link to a (Sub)Output, but behaves
    very similar to an :py:class:`Input <fastr.core.inputoutput.Input>` otherwise.
    """

    def __init__(self, input_):
        """
        Instantiate an SubInput.

        :param input_: the parent of this SubInput.
        :type input_: :py:class:`Input <fastr.core.inputoutput.Input>`
        :return: the created SubInput
        """
        self._source = None

        if not isinstance(input_, InputRun):
            raise exceptions.FastrTypeError('First argument for a SubInput constructor should be an Input')

        self.parent = input_
        super(SubInputRun, self).__init__(self.node, self.parent)

        self.datatype = input_.datatype

    def __getitem__(self, key):
        """
        Retrieve an item from this SubInput.

        :param key: the key of the requested item, can be a number, sample
                    index tuple or a :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :type key: int, :py:class:`SampleId <fastr.core.sampleidlist.SampleId>` or
                   :py:class:`SampleIndex <fastr.core.sampleidlist.SampleIndex>`
        :return: the return value depends on the requested key. If the key was
                 an int the corresponding :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
                 will be returned. If the key was a :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
                 or sample index tuple, the corresponding
                 :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` will be returned.
        :rtype: :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` or
                :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        :raises FastrTypeError: if key is not of a valid type

        .. note:: As a SubInput has only one SubInput, only requesting int key
                  0 or -1 is allowed, and it will return self
        """

        if not isinstance(key, (int, SampleIndex, SampleId)):
            raise exceptions.FastrTypeError('SubInput indices must be an int, SampleIndex, or SampleID, not {}'.format(type(key).__name__))

        if isinstance(key, (SampleIndex, SampleId)):
            return self.source[0][key]

        if not -1 <= key < 1:
            raise exceptions.FastrIndexError('SubInput index out of range (key: {})'.format(key))

        return self

    def __getstate__(self):
        """
        Retrieve the state of the SubInput

        :return: the state of the object
        :rtype dict:
        """
        state = super(SubInputRun, self).__getstate__()
        return state

    def __setstate__(self, state):
        """
        Set the state of the SubInput by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(SubInputRun, self).__setstate__(state)

        if not hasattr(self, '_source'):
            self._source = None

    def __str__(self):
        """
        Get a string version for the SubInput

        :return: the string version
        :rtype: str
        """
        if self.source_output is not None:
            return '<SubInputRun: {} => {}>'.format(self.fullid, self.source_output.fullid)
        else:
            return '<SubInputRun: {} => None>'.format(self.fullid)

    def cardinality(self, key=None, job_data=None):
        """
        Get the cardinality for this SubInput. The cardinality for a SubInputs
        is defined by the incoming link.

        :param key: key for a specific sample, can be sample index or id
        :type key: :py:class:`SampleIndex <fastr.core.sampleidlist.SampleIndex>` or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        """
        if self.source is not None:
            return self.source[0].cardinality(index=key)
        else:
            return 0

    @property
    def description(self):
        return self.parent.description

    @property
    def dimensions(self):
        """
        The sample size of the SubInput
        """
        if self.source is None:
            return ()
        else:
            return self.source[0].dimensions

    @property
    def fullid(self):
        """
        The full defining ID for the SubInput
        """
        return '{}/{}'.format(self.parent.fullid, self.parent.index(self))

    @property
    def input_group(self):
        """
        The id of the :py:class:`InputGroup <fastr.core.node.InputGroup>` this
        SubInputs parent belongs to.
        """
        return self.parent.input_group

    @property
    def node(self):
        """
        The Node to which this SubInputs parent belongs
        """
        return self.parent.node

    @property
    def source_output(self):
        """
        The :py:class:`Output <fastr.core.inputoutput.Output>`
        linked to this SubInput
        """
        if self.source is not None and len(self.source) > 0:
            return self.source[0].source
        else:
            return None

    @property
    def source(self):
        """
        A list with the source :py:class:`Link <fastr.core.link.Link>`.
        The list is to be compatible with :py:class:`Input <fastr.core.inputoutput.Input>`
        """
        if self._source is None:
            self.parent.remove(self)
            return []

        return [self._source]

    @source.setter
    def source(self, value):
        """
        Set new source, make sure previous link to source is released
        """
        if value is self._source:
            return

        if self._source is not None:
            self._source.destroy()

        if value is None:
            self.parent.remove(self)

        self._source = value

    def get_sourced_nodes(self):
        """
        Get a list of all :py:class:`Nodes <fastr.core.node.Node>` connected as sources to this SubInput

        :return: list of all connected :py:class:`Nodes <fastr.core.node.Node>`
        :rtype: list
        """
        return [x.source.node for x in self.source]

    def get_sourced_outputs(self):
        """
        Get a list of all :py:class:`Outputs <fastr.core.inputoutput.Output>` connected as sources to this SubInput

        :return: list of all connected :py:class:`Outputs <fastr.core.inputoutput.Output>`
        :rtype: list
        """
        return [x.source for x in self.source]

    def iteritems(self):
        """
        Iterate over the :py:class:`SampleItems <fastr.core.sampleidlist.SampleItem>`
        that are in the SubInput.

        :return: iterator yielding :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` objects
        """
        for item in self.source.items():
            yield item

    def itersubinputs(self):
        """Iterate over SubInputs (for a SubInput it will yield self and stop iterating after that)

        :return: iterator yielding  :py:class:`SubInput <fastr.core.inputoutput.SubInput>`

        example:

        .. code-block:: python

          >>> for subinput in input_a.itersubinputs():
                  print subinput

        """
        yield self

    def _update(self, key, forward=True, backward=False):
        """Update the validity of the SubInput and propagate the update downstream.
        A SubInput is valid if:

        * the source Link is set and valid (see :py:meth:`Link.update <fastr.core.link.Link.update>`)
        """
        # fastr.log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.fullid))
        valid = True
        messages = []
        if len(self.source) == 0:
            self.parent.remove(self)
            valid = False
            messages.append('No source in this SubInput, removing!')
        elif not self.source[0].valid:
            valid = False
            messages.append('SubInput source ({}) is not valid'.format(self.source[0].id))
            messages.extend(self.source[0].messages)

        self._status['valid'] = valid
        self._status['messages'] = messages

        # Update downstream
        self.parent.update(key, forward, backward)


class OutputRun(BaseOutput, ContainsSamples):
    """
    Class representing an output of a node. It holds the output values of
    the tool ran. Output fields can be connected to inputs of other nodes.
    """

    def __init__(self, node_run, template):
        """Instantiate an Output

        :param node: the parent node the output belongs to.
        :param description: the :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
               describing the output.
        :return: created Output
        :raises FastrTypeError: if description is not of class
                                :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
        :raises FastrDataTypeNotAvailableError: if the DataType requested cannot be found in the ``fastr.typelist``
        """
        self._suboutputlist = {}
        self._samples = None
        super(OutputRun, self).__init__(node_run, template.description)
        # Create the output_cardiality member function
        self._datatype = template.datatype
        self._output_cardinality = template._output_cardinality
        self._listeners = []
        self._preferred_types = template.preferred_types
        self._samples = SampleCollection(template.dimnames, self)

    def __str__(self):
        """
        Get a string version for the Output

        :return: the string version
        :rtype: str
        """
        return '<OutputRun: {})>'.format(self.fullid)

    def __getitem__(self, key):
        """
        Retrieve an item from this Output. The returned value depends on what type of key used:

        * Retrieving data using index tuple: [index_tuple]
        * Retrieving data sample_id str: [SampleId]
        * Retrieving a list of data using SampleId list: [sample_id1, ..., sample_idN]
        * Retrieving a :py:class:`SubOutput <fastr.core.inputoutput.SubOutput>` using an int or slice: [n] or [n:m]

        :param key: the key of the requested item, can be a number, slice, sample
                    index tuple or a :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :type key: int, slice, :py:class:`SampleId <fastr.core.sampleidlist.SampleId>` or tuple
        :return: the return value depends on the requested key. If the key was
                 an int or slice the corresponding :py:class:`SubOutput <fastr.core.inputoutput.SubOutput>`
                 will be returned (and created if needed). If the key was a
                 :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
                 or sample index tuple, the corresponding
                 :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` will be returned. If the
                 key was a list of :py:class:`SampleId <fastr.core.sampleidlist.SampleId>` a tuple
                 of :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` will be returned.
        :rtype: :py:class:`SubInput <fastr.core.inputoutput.SubInput>` or
                :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` or
                list of :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>`
        :raises FastrTypeError: if key is not of a valid type
        :raises FastrKeyError: if the parent Node has not been executed
        """
        if isinstance(key, (SampleId, SampleIndex, tuple, list)):
            # If the key is a index, then get the sample id
            if isinstance(key, (SampleId, SampleIndex)):
                return self.samples[key]
            else:
                # A list or tuple of SampleId/SampleIndex
                if not all(isinstance(k, (SampleId, SampleIndex)) for k in key):
                    message = ('If a list/tuple of keys is used, all elements should be of SampleId or SampleIndex type'
                               ' found key {}'.format(key))
                    fastr.log.error(message)
                    raise exceptions.FastrValueError(message)

                return tuple(self.samples[k] for k in key)
        elif isinstance(key, (int, slice)):
            return self._get_suboutput(key)
        else:
            raise exceptions.FastrTypeError('Key should be an integer/slice (for getting a SubOutput) or an index tuple/sample_id str for getting value(s)')

    def __setitem__(self, key, value):
        """
        Store an item in the Output

        :param key: key of the value to store
        :type key: tuple of int or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :param value: the value to store
        :return: None
        :raises FastrTypeError: if key is not of correct type
        """
        if isinstance(value, SampleItem):
            self.samples[key] = value
        else:
            if not isinstance(value, (tuple, list)):
                value = (value,)

            self.samples[key] = tuple(self._cast_to_storetype(x) for x in value)

    def __getstate__(self):
        """
        Retrieve the state of the Output

        :return: the state of the object
        :rtype dict:
        """
        state = super(OutputRun, self).__getstate__()

        # Add specific fields to the state
        state['suboutputs'] = [x.__getstate__() for x in self._suboutputlist.values()]
        if self._preferred_types is not None:
            state['preferred_types'] = [x.id for x in self._preferred_types]
        else:
            state['preferred_types'] = None

        return state

    def __setstate__(self, state):
        """
        Set the state of the Output by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(OutputRun, self).__setstate__(state)

        if state['preferred_types'] is not None:
            self._preferred_types = [fastr.typelist[x] for x in state['preferred_types']]
        else:
            self._preferred_types = None

        suboutputlist = []
        for substate in state['suboutputs']:
            suboutput = SubOutputRun(self, slice(None))
            suboutput.__setstate__(substate)
            suboutputlist.append((suboutput.indexrep, suboutput))

        # Re-create the dict from the array
        self._suboutputlist = dict(suboutputlist)
        self._listeners = []

    def _cast_to_storetype(self, value):
        """
        Cast a given value to a DataType that matches this Outputs datatype.

        :param value: value to cast
        :return: cast value
        :rtype: DataType matching self.datatype
        """
        if isinstance(value, self.datatype):
            return value

        fastr.log.info('CAST VALUE: [{}] {!r} / {}'.format(type(value).__name__,
                                                           value,
                                                           value))

        storetype = typelist.match_types(self.datatype, type(value))

        if storetype is None:
            storetype = typelist.match_types(self.datatype)

        if not isinstance(value, storetype):
            if isinstance(value, DataType):
                fastr.log.warning('Changing value type from {} to {}'.format(type(value), storetype))
            value = storetype(str(value))

        return value

    def _get_suboutput(self, key):
        """
        Get a suboutput based on the key

        :param int, slice key: The key of the suboutput
        :return: the suboutput
        """
        # Get a string representation of the key
        if isinstance(key, slice):
            keystr = '{}:{}'.format(key.start, key.stop)
            keystr = keystr.replace('None', '')

            if key.step is not None and key.step != 1:
                keystr = '{}:{}'.format(keystr, key.step)
        else:
            keystr = str(key)

        if keystr in self._suboutputlist:
            # Re-use the same SubOutput
            subout = self._suboutputlist[keystr]
        else:
            # Create the desired SubOutput object
            subout = SubOutputRun(self, key)
            self._suboutputlist[keystr] = subout

        return subout

    @property
    def blocking(self):
        """
        Flag indicating that this Output will cause blocking in the execution
        """
        return self._output_cardinality[0] in ('val', 'unknown')

    def cardinality(self, key=None, job_data=None):
        """
        Cardinality of this Output, may depend on the inputs of the parent Node.

        :param key: key for a specific sample, can be sample index or id
        :type key: tuple of int or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        :raises FastrCardinalityError: if cardinality references an invalid :py:class:`Input <fastr.core.inputoutput.Input>`
        :raises FastrTypeError: if the referenced cardinality values type cannot be case to int
        :raises FastrValueError: if the referenced cardinality value cannot be case to int
        """
        desc = self._output_cardinality

        if isinstance(key, SampleId):
            sample_index = self.samples[key].index if key in self.samples else None
        elif isinstance(key, SampleIndex):
            sample_index = key
        else:
            sample_index = None

        if desc[0] == 'int':
            return desc[1]
        elif desc[0] == 'as':
            if desc[1] in self.node.inputs:
                target = self.node.inputs[desc[1]]

                if sample_index is None:
                    # No key is used, call target without key
                    cardinality = target.cardinality(None)
                elif all(x == 0 for x in target.size):
                    # Target is empty, cardinality can be set to 0
                    cardinality = 0
                elif target.size == (1,):
                    # Target has only sample, it will be repeated, use first sample
                    cardinality = target.cardinality((0,))
                elif len(self.node.input_groups) == 1:
                    # The InputGroups are not mixed, we can request the sample_index
                    if len(sample_index) == len(target.size):
                        cardinality = target.cardinality(sample_index)
                    else:
                        index_map = dict(zip(self.dimnames, sample_index))
                        lookup = {v: dimname for dimname in self.dimnames for value in self.node.parent.nodegroups.values() if dimname in value for v in value}
                        lookup.update({x: x for x in self.dimnames})
                        if all(x in lookup for x in target.dimnames):
                            # Print there is broadcasting going on, we need to undo that here
                            matched_dimnames = [lookup[x] for x in target.dimnames]
                            matched_index = SampleIndex(index_map[x] for x in matched_dimnames)
                            cardinality = target.cardinality(matched_index)
                        else:
                            raise exceptions.FastrSizeMismatchError('InputGroup has inconsistent size/dimension info for Input {}, cannot figure out broadcasting used!'.format(target.fullid))
                else:
                    fastr.log.debug('Unmixing key "{}" for cardinality retrieval'.format(sample_index))
                    # The InputGroups are mixed, find the part of the ID relevant to this Input
                    test = self.node.input_group_combiner.unmerge(sample_index)
                    index = test[target.input_group]

                    if len(index) == len(target.size):
                        cardinality = target.cardinality(index)
                    else:
                        raise exceptions.FastrSizeMismatchError('TODO: add broadcasting to this branch?')

                return cardinality
            else:
                raise exceptions.FastrCardinalityError('Cardinality references to invalid field ({} is not an Input in this Node)'.format(desc[1]))
        elif desc[0] == 'val':
            if desc[1] in self.node.inputs:
                if job_data is None:
                    # We cannot access to the jobs inputs it appears, so we
                    # check if the output has already been generated.
                    if self.samples is not None and key in self.samples:
                        value = self.samples[key].data
                        fastr.log.debug('Got val via output data result, got {}'.format(value))
                        return len(value)
                    else:
                        fastr.log.debug('Cannot get val: cardinality if there is not job_data supplied!')
                        return None

                value = job_data[desc[1]]

                # Make sure the value is a tuple, not a sample item
                if isinstance(value, SampleItem):
                    value = value.data.sequence_part()

                fastr.log.debug('Extracted cardinality field {} from {} resulting in {}'.format(desc[1], job_data, value))

                if len(value) != 1:
                    message = 'Cardinality of Input {} with defining value for {} should have cardinality 1! Found {} (value {})'.format(
                        self.node.inputs[desc[1]].fullid,
                        self.fullid,
                        len(value),
                        value
                    )
                    fastr.log.error(message)
                    raise exceptions.FastrCardinalityError(message)

                try:
                    cardinality = int(str(value[0]))
                except TypeError:
                    raise exceptions.FastrTypeError('The value of the val: cardinality has an type that cannot be cast to an int ({})'.format(type(value[0].value).__name__))
                except ValueError:
                    raise exceptions.FastrValueError('The value of the val: cardinality has a value that cannot be cast to an int ({}, type: {})'.format(value[0].value, type(value[0].value).__name__))

                return cardinality
            elif desc[1] in self.node.outputs:
                # Get the value an output
                if key is None:
                    return None

                output = self.node.outputs[desc[1]]

                if output.samples is None:
                    return None

                # Try to cast via str to int (To make sure Int datatypes fares well)
                try:
                    return int(str(output[key]))
                except exceptions.FastrKeyError:
                    return None
            else:
                raise exceptions.FastrCardinalityError('Cardinality references to invalid field ({} is not an Input or Output in this Node)'.format(desc[1]))
        elif desc[0] == 'unknown':
            if key is None:
                return None

            if key not in self.samples:
                return None

            value = self.samples[key].data
            return len(value)
        else:
            raise exceptions.FastrCardinalityError('Invalid output cardinality specification found! ({})'.format(desc))

    @property
    def datatype(self):
        """
        The datatype of this Output
        """
        return self._datatype

    @property
    def fullid(self):
        """
        The full defining ID for the Output
        """
        if self.node is not None:
            return '{}/outputs/{}'.format(self.node.fullid, self.id)
        else:
            return 'fastr://ORPHANED/outputs/{}'.format(self.id)

    @property
    def listeners(self):
        """
        The list of :py:class:`Links <fastr.core.link.Link>` connected to this Output.
        """
        return self._listeners

    @property
    def preferred_types(self):
        """
        The list of preferred :py:class:`DataTypes <fastr.core.datatypemanager.DataType>`
        for this Output.
        """
        if self._preferred_types is not None and len(self._preferred_types) > 0:
            return self._preferred_types
        elif self.node.parent is not None and self.node.parent.preferred_types is not None and len(self.node.parent.preferred_types) > 0:
            return self.node.parent.preferred_types
        else:
            return fastr.typelist.preferred_types

    @property
    def samples(self):
        """
        The SampleCollection of the samples in this Output. None if the NodeRun
        has not yet been executed. Otherwise a SampleCollection.
        """
        return self._samples

    @property
    def valid(self):
        """
        Check if the output is valid, i.e. has a valid cardinality
        """
        return self.check_cardinality()

    @property
    def resulting_datatype(self):
        """
        The :py:class:`DataType <fastr.core.datatypemanager.DataType>` that
        will the results of this Output will have.
        """
        requested_types = [l.target.datatype for l in self.listeners if l.target is not None]
        requested_types.append(self.datatype)

        if self.preferred_types is not None and len(self.preferred_types) > 0:
            return typelist.match_types(requested_types,
                                        preferred=self.preferred_types)
        else:
            return typelist.match_types(requested_types)

    @property
    def automatic(self):
        """
        Flag indicating that the Output is generated automatically
        without being specified on the command line
        """
        return self._description.automatic

    @staticmethod
    def create_output_cardinality(desc):
        """Create a lambda function that returns an integer value of the cardinality.

        :param str desc: The cardinality description string
        :return: output cardinality description
        :rtype tuple:

       The description string can be one of the following forms:

        * N: N number of values needed.
        * as:input_name: the same number of values as attached to input_name are needed.
        * val:input_name: the number of values needed is the value of input_name.
        * unknown: the output cardinality cannot be estimated a priori
        """
        try:
            int(desc)
            is_int = True
        except ValueError:
            is_int = False

        if is_int:
            # N
            output_cardinality = ('int', int(desc))
        elif desc[0:3] == "as:":
            # as:input_name
            output_cardinality = ('as', desc[3:])
        elif desc[0:4] == "val:":
            output_cardinality = ('val', desc[4:])
        elif desc == 'unknown':
            output_cardinality = ('unknown',)
        else:
            raise exceptions.FastrCardinalityError('Invalid cardinality specification "{}"!'.format(desc))

        return output_cardinality

    def iterconvergingindices(self, collapse_dims):
        """
        Iterate over all data, but collapse certain dimension to create lists
        of data.

        :param collapse_dims: dimension to collapse
        :type collapse_dims: iterable of int
        :return: iterator SampleIndex (possibly containing slices)
        """
        if all(-self.ndims <= x < self.ndims for x in collapse_dims):
            iter_dims = [xrange(s) for s in self.size]
            for idx in collapse_dims:
                iter_dims[idx] = slice(None),

            for idx in itertools.product(*iter_dims):
                yield SampleIndex(idx)
        else:
            raise exceptions.FastrIndexError('Index of a converging dimension {} out out of range (number of dimensions {})'.format(collapse_dims, self.ndims))

    def _update(self, key, forward=True, backward=False):
        """Update the status and validity of the Output and propagate the update the NodeRun.
        An Output is valid if:

        * the parent NodeRun is valid (see :py:meth:`NodeRun.update <fastr.core.node.NodeRun.update>`)
        """
        # fastr.log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.fullid))

        self.node.update(key, forward, backward)

        if self.node.valid:
            self._status['valid'] = True
        else:
            self._status['valid'] = False
            self._status['messages'] = ['Parent NodeRun is not valid']


class SubOutputRun(OutputRun):
    """
    The SubOutput is an Output that represents a slice of another Output.
    """

    def __init__(self, output, index):
        """Instantiate a SubOutput

        :param output: the parent output the suboutput slices.
        :param index: the way to slice the parent output
        :type index: int or slice
        :return: created SubOutput
        :raises FastrTypeError: if the output argument is not an instance of :py:class:`Output <fastr.core.inputoutput.Output>`
        :raises FastrTypeError: if the index argument is not an ``int`` or ``slice``
        """
        if not isinstance(output, OutputRun):
            raise exceptions.FastrTypeError('Second argument for a SubOutput init should be an Output')

        if not isinstance(index, (int, slice)):
            raise exceptions.FastrTypeError('SubOutput index should be an integer or a slice, found ({}, type {})'.format(index, type(index).__name__))

        self._suboutputlist = {}  # SubOutput can have SubOutputs again
        BaseOutput.__init__(self, output.node, output.description)
        self.parent = output
        self.index = index

    def __str__(self):
        """
        Get a string version for the SubOutput

        :return: the string version
        :rtype: str
        """
        return '<SubOutputRun {}>'.format(self.fullid)

    def __getitem__(self, key):
        """
        Retrieve an item from this SubOutput. The returned value depends on what type of key used:

        * Retrieving data using index tuple: [index_tuple]
        * Retrieving data sample_id str: [SampleId]
        * Retrieving a list of data using SampleId list: [sample_id1, ..., sample_idN]
        * Retrieving a :py:class:`SubOutput <fastr.core.inputoutput.SubOutput>` using an int or slice: [n] or [n:m]

        :param key: the key of the requested item, can be a number, slice, sample
                    index tuple or a :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :type key: int, slice, :py:class:`SampleId <fastr.core.sampleidlist.SampleId>` or tuple
        :return: the return value depends on the requested key. If the key was
                 an int or slice the corresponding :py:class:`SubOutput <fastr.core.inputoutput.SubOutput>`
                 will be returned (and created if needed). If the key was a
                 :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
                 or sample index tuple, the corresponding
                 :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` will be returned. If the
                 key was a list of :py:class:`SampleId <fastr.core.sampleidlist.SampleId>` a tuple
                 of :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` will be returned.
        :rtype: :py:class:`SubInput <fastr.core.inputoutput.SubInput>` or
                :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` or
                list of :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>`
        :raises FastrTypeError: if key is not of a valid type
        """

        if isinstance(key, (int, slice)):
            return self._get_suboutput(key)

        item = self.parent[key]

        if isinstance(item, SampleItem):
            if isinstance(self.index, int):
                return SampleItem(item.index, item.id, {0: (item.data.sequence_part()[self.index],)}, item.jobs, item.failed_annotations)
            else:
                return SampleItem(item.index, item.id, {0: item.data.sequence_part()[self.index]}, item.jobs, item.failed_annotations)
        else:
            if isinstance(self.index, int):
                return tuple(SampleItem(x.index, x.id, {0: (x.data.sequence_part()[self.index],)}, x.jobs, x.failed_annotations) for x in item)
            else:
                return tuple(SampleItem(x.index, x.id, {0: x.data.sequence_part()[self.index]}, x.jobs, x.failed_annotations) for x in item)

    def __setitem__(self, key, value):
        """
        A function blocking the assignment operator. Values cannot be assigned to a SubOutput.

        :raises FastrNotImplementedError: if called
        """
        raise exceptions.FastrNotImplementedError('[{}] Cannot assign values to a SubOutput, assign to parent Output instead!'.format(self.fullid))

    def __getstate__(self):
        """
        Retrieve the state of the SubOutput

        :return: the state of the object
        :rtype dict:
        """
        state = BaseOutput.__getstate__(self)
        state['index'] = self.indexrep
        return state

    def __setstate__(self, state):
        """
        Set the state of the SubOutput by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        if isinstance(state['index'], str):
            index = [int(x) if len(x) > 0 else None for x in state['index'].split(':')]
            state['index'] = slice(*index)

        state = BaseOutput.__getstate__(self, state)

    def __len__(self):
        """Return the length of the Output.

        .. note::

            In a SubOutput this is always 1.
        """
        return 1

    @property
    def indexrep(self):
        """
        Simple representation of the index.
        """
        if isinstance(self.index, slice):
            index = '{}:{}'.format(self.index.start, self.index.stop)
            index = index.replace('None', '')

            if self.index.step is not None and self.index.step != 1:
                index = '{}:{}'.format(index, self.index.step)
        else:
            index = self.index

        return index

    def cardinality(self, key=None, job_data=None):
        """
        Cardinality of this SubOutput depends on the parent Output and ``self.index``

        :param key: key for a specific sample, can be sample index or id
        :type key: tuple of int or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        :raises FastrCardinalityError: if cardinality references an invalid :py:class:`Input <fastr.core.inputoutput.Input>`
        :raises FastrTypeError: if the referenced cardinality values type cannot be case to int
        :raises FastrValueError: if the referenced cardinality value cannot be case to int
        """
        parent_cardinality = self.parent.cardinality(key)

        if parent_cardinality is not None:
            if isinstance(parent_cardinality, int):
                if isinstance(self.index, int):
                    if parent_cardinality >= 1:
                        return 1
                    else:
                        return 0
                else:
                    # Calculate the slice effect on a list of length parent cardinality
                    ind_range = self.index.indices(parent_cardinality)
                    return (ind_range[1] - ind_range[0]) // ind_range[2]
            else:
                return parent_cardinality
        else:
            return None

    @property
    def datatype(self):
        """
        The datatype of this SubOutput
        """
        return self.parent.datatype

    @property
    def fullid(self):
        """
        The full defining ID for the SubOutput
        """
        return '{}/{}'.format(self.parent.fullid, self.indexrep)

    @property
    def listeners(self):
        """
        The list of :py:class:`Links <fastr.core.link.Link>` connected to this Output.
        """
        return self.parent.listeners

    @property
    def node(self):
        """
        The NodeRun to which this SubOutput belongs
        """
        return self.parent.node

    @property
    def preferred_types(self):
        """
        The list of preferred :py:class:`DataTypes <fastr.core.datatypemanager.DataType>`
        for this SubOutput.
        """
        return self.parent.preferred_types

    @property
    def samples(self):
        """
        The :py:class:`SampleCollection <fastr.core.sampleidlist.SampleCollection>`
        for this SubOutput
        """
        return self.parent.samples

    @property
    def resulting_datatype(self):
        """
        The :py:class:`DataType <fastr.core.datatypemanager.DataType>` that
        will the results of this SubOutput will have.
        """
        return self.parent.resulting_datatype

    def _update(self, key, forward=True, backward=False):
        """Update the status and validity of the SubOutput and propagate the update downstream.
        An SubOutput is valid if:

        * the parent NodeRun is valid (see :py:meth:`NodeRun.update <fastr.core.node.NodeRun.update>`)

        """
        # fastr.log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.fullid))
        self.parent.update(key, forward, backward)

        if self.node.valid:
            self._status['valid'] = True
        else:
            self._status['valid'] = False
            self._status['messages'] = ['Parent NodeRun is not valid']


class AdvancedFlowOutputRun(OutputRun):
    pass


class MacroOutputRun(OutputRun):
    @property
    def dimensions(self):
        return self.node.get_output_info(self)


class SourceOutputRun(OutputRun):
    """
    Output for a SourceNodeRun, this type of Output determines the cardinality in
    a different way than a normal NodeRun.
    """
    def __init__(self, node_run, template):
        """Instantiate a FlowOutput

        :param node: the parent node the output belongs to.
        :param description: the :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
               describing the output.
        :return: created FlowOutput
        :raises FastrTypeError: if description is not of class
                                :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
        :raises FastrDataTypeNotAvailableError: if the DataType requested cannot be found in the ``fastr.typelist``
        """
        super(SourceOutputRun, self).__init__(node_run, template)

        self._linearized = None

    def __getitem__(self, item):
        """
        Retrieve an item from this Output. The returned value depends on what type of key used:

        * Retrieving data using index tuple: [index_tuple]
        * Retrieving data sample_id str: [SampleId]
        * Retrieving a list of data using SampleId list: [sample_id1, ..., sample_idN]
        * Retrieving a :py:class:`SubOutput <fastr.core.inputoutput.SubOutput>` using an int or slice: [n] or [n:m]

        :param key: the key of the requested item, can be a number, slice, sample
                    index tuple or a :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :type key: int, slice, :py:class:`SampleId <fastr.core.sampleidlist.SampleId>` or tuple
        :return: the return value depends on the requested key. If the key was
                 an int or slice the corresponding :py:class:`SubOutput <fastr.core.inputoutput.SubOutput>`
                 will be returned (and created if needed). If the key was a
                 :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
                 or sample index tuple, the corresponding
                 :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` will be returned. If the
                 key was a list of :py:class:`SampleId <fastr.core.sampleidlist.SampleId>` a tuple
                 of :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` will be returned.
        :rtype: :py:class:`SubInput <fastr.core.inputoutput.SubInput>` or
                :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` or
                list of :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>`
        :raises FastrTypeError: if key is not of a valid type
        :raises FastrKeyError: if the parent NodeRun has not been executed
        """
        if len(item) != 1:
            fastr.log.debug('Non-linear access to SourceOutput attempted! (linearized data: {})'.format(self.linearized))
            raise exceptions.FastrIndexError('SourceOutput only allows for linear indices')

        return self.linearized[item[0]]

    def __setitem__(self, key, value):
        """
        Store an item in the Output

        :param key: key of the value to store
        :type key: tuple of int or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :param value: the value to store
        :return: None
        :raises FastrTypeError: if key is not of correct type
        """
        super(SourceOutputRun, self).__setitem__(key, value)
        self._linearized = None

    @property
    def dimensions(self):
        """
        The dimensions of this SourceOutputRun
        """
        if self.node.nodegroup is not None:
            name = self.node.nodegroup
        else:
            name = self.node.id

        return Dimension(name, len(self.linearized)),

    @property
    def size(self):
        """
        The sample size of the SourceOutput
        """
        return len(self.linearized),

    @property
    def ndims(self):
        """
        The number of dimensions in this SourceOutput
        """
        return 1

    @property
    def linearized(self):
        """
        A linearized version of the sample data, this is lazily cached
        linearized version of the underlying SampleCollection.
        """
        if self._linearized is None:
            self._linearized = tuple(self.samples[x] for x in self.samples)

        return self._linearized

    def cardinality(self, key=None, job_data=None):
        """
        Cardinality of this SourceOutput, may depend on the inputs of the parent NodeRun.

        :param key: key for a specific sample, can be sample index or id
        :type key: tuple of int or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        """
        if key is None:
            return None

        if self.samples is None:
            return sympy.symbols('N_{}'.format(self.node.id.replace(' ', '_')))

        try:
            value = self[key]
        except (KeyError, IndexError):
            fastr.log.debug('Could not find sample {}, cardinality unknown!'.format(key))
            return None

        return len(value.data)

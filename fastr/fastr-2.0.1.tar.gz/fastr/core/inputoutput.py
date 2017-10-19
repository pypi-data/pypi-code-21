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
import re
from abc import abstractmethod, abstractproperty
from collections import OrderedDict

import sympy

import fastr
import fastr.exceptions as exceptions
from fastr.core.dimension import HasDimensions, Dimension
from fastr.core.datatypemanager import typelist
from fastr.core.interface import InputSpec, OutputSpec
from fastr.core.serializable import Serializable
from fastr.core.updateable import Updateable
from fastr.datatypes import DataType
from fastr.utils.dicteq import dicteq


class BaseInputOutput(HasDimensions, Updateable, Serializable):

    """
    Base class for Input and Output classes. It mainly implements the
    properties to access the data from the underlying ParameterDescription.
    """

    def __init__(self, node, description):
        """Instantiate a BaseInputOutput

        :param node: the parent node the input/output belongs to.
        :param description: the :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
               describing the input/output.
        :return: created BaseInputOutput
        :raises FastrTypeError: if description is not of class
                                :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
        :raises FastrDataTypeNotAvailableError: if the DataType requested cannot be found in the ``fastr.typelist``
        """
        super(BaseInputOutput, self).__init__()

        self._node = node

        # Get DataType
        if description.datatype in typelist:
            self._description = description
            self._datatype = typelist[description.datatype]

            # Create a validator for the cardinality
            self.cardinality_spec = self._create_cardinality_spec(description.cardinality)
        else:
            raise exceptions.FastrDataTypeNotAvailableError('DataType {} does not exist'.format(description.datatype))

    def __iter__(self):
        """
        This function is blocked to avoid support for iteration using a lecacy __getitem__ method.

        :return: None
        :raises FastrNotImplementedError: always
        """
        raise exceptions.FastrNotImplementedError('Not iterable, this function is to block legacy iteration using getitem')

    def __getstate__(self):
        """
        Retrieve the state of the BaseInputOutput

        :return: the state of the object
        :rtype dict:
        """
        state = super(BaseInputOutput, self).__getstate__()
        state['id'] = self.id
        state['datatype'] = self.datatype.id
        return state

    def __setstate__(self, state):
        """
        Set the state of the BaseInputOutput by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(BaseInputOutput, self).__setstate__(state)

        if 'datatype' in state:
            self._datatype = fastr.typelist[state['datatype']]

        self.cardinality_spec = self._create_cardinality_spec(self.description.cardinality)

    def __repr__(self):
        """
        Get a string representation for the Input/Output

        :return: the string representation
        :rtype: str
        """
        return '<{}: {}>'.format(type(self).__name__, self.fullid)


    @property
    def datatype(self):
        """
        The datatype of this Input/Output
        """
        return self._datatype

    @datatype.setter
    def datatype(self, value):
        """
        The datatype of this Input/Output (setter)
        """
        self._datatype = value

    @property
    def description(self):
        """
        The description object of this input/output
        """
        return self._description

    def cardinality(self, key=None, job_data=None):
        """
        Determine the cardinality of this Input/Output. Optionally a key can be
        given to determine for a sample.

        :param key: key for a specific sample
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        """

        # We need to key for the signature in subclasses, shut pylint up
        # pylint: disable=unused-argument,no-self-use

        raise exceptions.FastrNotImplementedError('Purposefully not implemented')

    @property
    def id(self):
        """
        Id of the Input/Output
        """
        return self._description.id

    @property
    def node(self):
        """
        The NodeRun to which this Input/Output belongs
        """
        return self._node

    @property
    def required(self):
        """
        Flag indicating that the Input/Output is required
        """
        return self._description.required

    @abstractproperty
    def fullid(self):
        """
        The fullid of the Input/Output, the fullid should be unnique and
        makes the object retrievable by the network.
        """
        raise exceptions.FastrNotImplementedError('Purposefully not implemented')

    def check_cardinality(self, key=None):
        """
        Check if the actual cardinality matches the cardinality specified in
        the ParameterDescription. Optionally you can use a key to test for a
        specific sample.

        :param key: sample_index (tuple of int) or
                    :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
                    for desired sample
        :return: flag indicating that the cardinality is correct
        :rtype: bool
        :raises FastrCardinalityError: if the Input/Output has an incorrect
                cardinality description.
        """
        spec = self.cardinality_spec
        cardinality = self.cardinality(key)

        fastr.log.debug('Cardinality: {} (type {})'.format(cardinality, type(cardinality).__name__))
        if isinstance(cardinality, sympy.Symbol):
            fastr.log.debug('A symbol cardinality cannot be checked a priori!')
            return True

        if spec[0] == 'any':
            return True
        elif spec[0] == 'min':
            return cardinality >= spec[1]
        elif spec[0] == 'max':
            return cardinality <= spec[1]
        elif spec[0] == 'int':
            return cardinality == spec[1]
        elif spec[0] == 'range':
            return cardinality >= spec[1] and cardinality <= spec[2]
        elif spec[0] == 'as':
            return cardinality == self.node.inputs[spec[1]].cardinality(key)
        elif spec[0] == 'val':
            fastr.log.warning('Value cardinality specification cannot be checked a priori!')
            return True
        elif spec[0] == 'unknown':
            fastr.log.warning('Value cardinality specification cannot be checked a priori!')
            return True
        else:
            raise exceptions.FastrCardinalityError('Invalid cardinality specification ({})'.format(spec))

    @staticmethod
    def _create_cardinality_spec(desc):
        """
        Create simplified description of the cardinality. This changes the
        string representation to a tuple that is easier to check at a later
        time.

        :param str desc: the string version of the cardinality
        :return: the simplified cardinality description
        :rtype: tuple
        :raises FastrCardinalityError: if the Input/Output has an incorrect
                cardinality description.

        The translation works with the following table:

        ==================== ============================= ===============================================================
        cardinality string   cardinality spec              description
        ==================== ============================= ===============================================================
        ``"*"``              ``('any',)                    Any cardinality is allowed
        ``"N"``              ``('int', N)``                A cardinality of N is required
        ``"N-M"``            ``('range', N, M)``           A cardinality between N and M is required
        ``"*-M"``            ``('max', M)``                A cardinality of maximal M is required
        ``"N-*"``            ``('min', N)``                A cardinality of minimal N is required
        ``"[M,N,...,O,P]"``  ``('choice', [M,N,...,O,P])`` The cardinality should one of the given options
        ``"as:input_id"``    ``('as', 'input_id')``        The cardinality should match the cardinality of the given Input
        ``"val:input_id"``   ``('val', 'input_id')``       The cardinliaty should match the value of the given Input
        ==================== ============================= ===============================================================
        """

        if isinstance(desc, int) or re.match(r'^\d+$', desc) is not None:
            # N
            cardinality_spec = ('int', int(desc))
        elif desc == '*':
            # * (anything is okay)
            cardinality_spec = ('any',)
        elif re.match(r'^\[\d+(,\d+)*\]', desc) is not None:
            # [M,N,..,O,P]
            cardinality_spec = ('choice', tuple(int(x) for x in desc[1:-1].split(',')))
        elif '-' in desc:
            match = re.match(r'^(\d+|\*)-(\d+|\*)$', desc)
            if match is None:
                raise exceptions.FastrCardinalityError("Not a valid cardinality description string (" + desc + ")")

            lower, upper = match.groups()

            if lower == '*' and upper == '*':
                # *-* (anything is okay)
                cardinality_spec = ('any',)
            elif lower == '*' and upper != '*':
                # N-*
                cardinality_spec = ('max', int(upper))
            elif lower != '*' and upper == '*':
                # *-M
                cardinality_spec = ('min', int(lower))
            else:
                # N-M
                cardinality_spec = ('range', int(lower), int(upper))

        elif desc.startswith("as:"):
            # as:other
            field = desc[3:]
            cardinality_spec = ('as', field)
        elif desc.startswith("val:"):
            # val:other
            field = desc[5:]
            cardinality_spec = ('val', field)
        elif desc == 'unknown':
            cardinality_spec = ('unknown',)
        else:
            raise exceptions.FastrCardinalityError("Not a valid cardinality description string (" + desc + ")")

        return cardinality_spec


class BaseInput(BaseInputOutput):
    """
    Base class for all inputs.
    """

    def __init__(self, node, description):
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
        if not isinstance(description, InputSpec):
            fastr.log.error('Description has type "{}" (must be ParameterDescription)'.format(type(description).__name__))
            raise exceptions.FastrTypeError('An input must be constructed based on an '
                                            'object of a class derived from NodeRun and an '
                                            'object of class InputSpec')

        super(BaseInput, self).__init__(node, description)

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

    def __lshift__(self, other):
        if not isinstance(other, (BaseOutput, list, tuple, dict, OrderedDict)):
            return NotImplemented

        return self.create_link_from(other)

    def __rrshift__(self, other):
        if not isinstance(other, (BaseOutput, list, tuple, dict, OrderedDict)):
            return NotImplemented

        return self.create_link_from(other)

    def create_link_from(self, value):
        if isinstance(value, BaseOutput):
            if self.node.parent is not value.node.parent:
                message = 'Cannot create links between members of different Network'
                fastr.log.warning(message)

            network = value.node.parent
            if network is None:
                message = 'Cannot create links between non-network-attached Nodes'
                fastr.log.warning(message)
            else:
                fastr.log.debug('Linking {} to {}'.format(value.fullid, self.fullid))
                return network.create_link(value, self)
        elif isinstance(value, (list, dict, OrderedDict)) or\
                (isinstance(value, tuple) and all(not isinstance(x, BaseOutput) for x in value)):
            # This is data for a ConstantNode, so create one and set it
            # First make sure the stepid of the new ConstantNode will match the stepid of the current Node
            inp = self
            for k, i in inp.node.parent.stepids.items():
                if inp.node in i:
                    stepid = k
                    break
            else:
                stepid = None
            network = inp.node.parent

            # Add the index of the SubOutput to avoid id clashes
            if isinstance(self, Input):
                index = len(self.source)
            elif isinstance(self, SubInput):
                index = self.parent.index(self)
            else:
                raise exceptions.FastrTypeError("Cannot create link to non Input or SubInput")

            new_id = 'const_{}_{}_{}'.format(inp.node.id, inp.id, index)
            const_node = network.create_constant(datatype=inp.datatype, data=value, id_=new_id, stepid=stepid)
            return network.create_link(const_node.output, self)
        elif isinstance(value, tuple) and isinstance(self, Input):
            # First remove all current links
            self.clear()
            new_links = []

            # Create all required links, find all consecutive parts of non-outputs and
            # create ConstantNodes for those, link all outputs separately
            current_part = []
            for element in value:
                if isinstance(element, BaseOutput):
                    # If there were non-outputs found, first combine those
                    # before creating a link from the output
                    if len(current_part) > 0:
                        self.append(tuple(current_part))
                        current_part = []
                    new_links.append(self.append(element))
                else:
                    current_part.append(element)
            if len(current_part) > 0:
                new_links.append(self.append(tuple(current_part)))

            # Return a tuple of all links created
            return tuple(new_links)
        else:
            message = 'Cannot link from object of type {} to type {}'.format(type(value).__name__,
                                                                             type(self).__name__)
            fastr.log.critical(message)
            raise exceptions.FastrTypeError(message)


class Input(BaseInput):
    """
    Class representing an input of a node. Such an input will be connected
    to the output of another node or the output of an constant node to provide
    the input value.
    """

    def __init__(self, node, description):
        """
        Instantiate an input.

        :param node: the parent node of this input.
        :type node: :py:class:`NodeRun <fastr.core.node.NodeRun>`
        :param ParameterDescription description: the ParameterDescription of the input.
        :return: the created Input
        """
        self._source = {}
        super(Input, self).__init__(node, description)
        self._input_group = 'default'

    def __eq__(self, other):
        """Compare two Input instances with each other. This function ignores
        the parent node and update status, but tests rest of the dict for equality.

        :param other: the other instances to compare to
        :type other: :py:class:`Input <fastr.core.inputoutput.Input>`
        :returns: True if equal, False otherwise
        :rtype: bool
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        dict_self = {k: v for k, v in self.__dict__.items()}
        del dict_self['_node']
        del dict_self['_status']

        dict_other = {k: v for k, v in other.__dict__.items()}
        del dict_other['_node']
        del dict_other['_status']

        return dicteq(dict_self, dict_other)

    def __getstate__(self):
        """
        Retrieve the state of the Input

        :return: the state of the object
        :rtype dict:
        """
        state = super(Input, self).__getstate__()
        state['input_group'] = self.input_group

        return state

    def __setstate__(self, state):
        """
        Set the state of the Input by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(Input, self).__setstate__(state)
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
        if not isinstance(key, (int, str)):
            raise exceptions.FastrTypeError('Input indices must a int or str'
                                            ''.format(type(key).__name__))

        if key not in self.source:
            # This is to allow for linking against inputs['key'][0]
            try:
                key = int(key)
            except ValueError:
                pass  # No problem, just go for the str

            self.source[key] = SubInput(self)

        return self.source[key]

    def __setitem__(self, key, value):
        """
        Create a link between a SubInput of this Inputs and an Output/Constant

        :param key: the key of the SubInput
        :type key: int, str
        :param value: the target to link, can be an output or a value to create a constant for
        :type value: BaseOutput, list, tuple, dict, OrderedDict
        :raises FastrTypeError: if key is not of a valid type
        """
        if not isinstance(key, (int, str)):
            raise exceptions.FastrTypeError('The key of an SubInput to set should be an '
                                            'int or str (found {})'.format(type(key).__name__))

        if key not in self.source:
            subin = Input(self.node, self.description)
            self.source[key] = subin

        self.source[key].create_link_from(value)

    def __str__(self):
        """
        Get a string version for the Input

        :return: the string version
        :rtype: str
        """
        return '<Input: {})>'.format(self.fullid)

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
    def dimensions(self):
        """
        The list names of the dimensions in this Input. This will be a list of str.
        """
        subinputs = list(self.itersubinputs())
        sizes = [sub.size for sub in subinputs]

        unique_sizes = set(sizes) - {(0,), (1,), ()}

        if len(unique_sizes) > 1:
            nr_non_symbolic_sizes = sum(not all(isinstance(x, sympy.Symbol) for x in size) for size in unique_sizes)

            if nr_non_symbolic_sizes == 0:
                max_dimensions = max(len(x) for x in unique_sizes)
                for subinput in subinputs:
                    if len(subinput.size) == max_dimensions and subinput.size not in ((0,), (1,), ()):
                        return subinput.dimensions

            raise exceptions.FastrSizeMismatchError('Cannot determine dimensions: sizes of SubInputs do not match!')
        elif len(unique_sizes) == 1:
            return subinputs[sizes.index(unique_sizes.pop())].dimensions
        elif (1,) in sizes:
            return subinputs[sizes.index((1,))].dimensions
        elif (0,) in sizes:
            return subinputs[sizes.index((0,))].dimensions
        else:
            return []

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

    @input_group.setter
    def input_group(self, value):
        """
        The id of the :py:class:`InputGroup <fastr.core.node.InputGroup>` this
        Input belongs to. (setter)
        """
        self._input_group = value
        self.node.update()

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

        self._source = {0: SubInput(self)}
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

    def remove(self, value):
        """
        Remove a SubInput from the SubInputs list based on the connected Link.

        :param value: the :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
                      or :py:class:`SubLink <fastr.core.link.Link>`
                      to removed from this Input
        :type value: :py:class:`SubInput <fastr.core.link.Link>`, <fastr.core.inputoutput.SubInput>`
        """
        for key, subinput in self.source.items():
            if subinput is value or (len(subinput.source) == 1 and subinput.source[0] is value):
                self.source.pop(key)
                if subinput.source is not None:
                    subinput.source[0].destroy()

    def clear(self):
        for key in self.source.keys():
            subinput = self.source.pop(key)
            if subinput.source is not None:
                subinput.source[0].destroy()

    def insert(self, index):
        """
        Insert a new SubInput at index in the sources list

        :param int key: positive integer for position in _source list to insert to
        :return: newly inserted :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        :rtype: :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        """
        newsub = SubInput(self)
        self.source[index] = newsub
        return newsub

    def append(self, value):
        """
        When you want to append a link to an Input, you can use the append
        property. This will automatically create a new SubInput to link to.

        example:

        .. code-block:: python

          >>> link = node2['input'].append(node1['output'])

        will create a new SubInput in node2['input'] and link to that.
        """
        new_sub = SubInput(self)
        # Get the next index-like key to use
        new_key = max([-1] + [x for x in self.source.keys() if isinstance(x, int)]) + 1
        self.source[new_key] = new_sub
        return new_sub.create_link_from(value)

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


class SubInput(BaseInput):
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

        if not isinstance(input_, Input):
            raise exceptions.FastrTypeError('First argument for a SubInput constructor should be an Input')

        self.parent = input_
        super(SubInput, self).__init__(self.node, self.description)

        self.datatype = input_.datatype
        if self.parent.valid:
            self.update()

    def __getitem__(self, key):
        """
        Retrieve an item from this SubInput.

        :param key: the index of the requested item
        :type key: int
        :return: the corresponding :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        :rtype: :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        :raises FastrTypeError: if key is not of a valid type

        .. note:: As a SubInput has only one SubInput, only requesting int key
                  0 or -1 is allowed, and it will return self
        """

        if not isinstance(key, int):
            raise exceptions.FastrTypeError('SubInput indices must be an int, not {}'.format(type(key).__name__))

        if not -1 <= key < 1:
            raise exceptions.FastrIndexError('SubInput index out of range (key: {})'.format(key))

        return self

    def __eq__(self, other):
        """Compare two SubInput instances with each other. This function ignores
        the parent, node, source and update status, but tests rest of the dict
        for equality.

        :param other: the other instances to compare to
        :type other: SubInput
        :returns: True if equal, False otherwise
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        dict_self = {k: v for k, v in self.__dict__.items()}
        del dict_self['_node']
        del dict_self['parent']
        del dict_self['_source']
        del dict_self['_status']

        dict_other = {k: v for k, v in other.__dict__.items()}
        del dict_other['_node']
        del dict_other['parent']
        del dict_other['_source']
        del dict_other['_status']

        return dicteq(dict_self, dict_other)

    def __getstate__(self):
        """
        Retrieve the state of the SubInput

        :return: the state of the object
        :rtype dict:
        """
        state = super(SubInput, self).__getstate__()
        return state

    def __setstate__(self, state):
        """
        Set the state of the SubInput by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(SubInput, self).__setstate__(state)

        if not hasattr(self, '_source'):
            self._source = None

    def __str__(self):
        """
        Get a string version for the SubInput

        :return: the string version
        :rtype: str
        """
        if self.source_output is not None:
            return '<SubInput: {} => {}>'.format(self.fullid, self.source_output.fullid)
        else:
            return '<SubInput: {} => None>'.format(self.fullid)

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
        List of dimension for this SubInput
        """
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

    def remove(self, value):
        """
        Remove a SubInput from parent Input.

        :param value: the :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
                      to removed from this Input
        :type value: :py:class:`SubInput <fastr.core.inputoutput.SubInput>`
        """
        # Pass on to the parent Input
        self.parent.remove(value)

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


class BaseOutput(BaseInputOutput):
    """
    Base class for all outputs.
    """

    def __init__(self, node, description):
        """Instantiate a BaseOutput

        :param node: the parent node the output belongs to.
        :param description: the :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
               describing the output.
        :return: created BaseOutput
        :raises FastrTypeError: if description is not of class
                                :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
        :raises FastrDataTypeNotAvailableError: if the DataType requested cannot be found in the ``fastr.typelist``
        """
        if not isinstance(description, OutputSpec):
            fastr.log.error('Description has type "{}" (must be ParameterDescription)'.format(type(description).__name__))
            raise exceptions.FastrTypeError('An output must be constructed based on an '
                                            'object of a class derived from Node and an '
                                            'object of class OutputSpec')
        super(BaseOutput, self).__init__(node, description)

    @property
    def automatic(self):
        """
        Flag indicating that the Output is generated automatically
        without being specified on the command line
        """
        return self._description.automatic


class Output(BaseOutput):
    """
    Class representing an output of a node. It holds the output values of
    the tool ran. Output fields can be connected to inputs of other nodes.
    """

    def __init__(self, node, description):
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
        super(Output, self).__init__(node, description)
        # Create the output_cardiality member function
        self._output_cardinality = self.create_output_cardinality(description.cardinality)
        self._listeners = []
        self._preferred_types = []

    def __str__(self):
        """
        Get a string version for the Output

        :return: the string version
        :rtype: str
        """
        return '<Output: {})>'.format(self.fullid)

    def __eq__(self, other):
        """
        Compare two Output instances with each other. This function ignores
        the parent node, listeners and update status, but tests rest of the
        dict for equality.

        :param other: the other instances to compare to
        :type other: Output
        :returns: True if equal, False otherwise
        :rtype: bool
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        dict_self = {k: v for k, v in self.__dict__.items()}
        del dict_self['_node']
        del dict_self['_listeners']
        del dict_self['_status']

        dict_other = {k: v for k, v in other.__dict__.items()}
        del dict_other['_node']
        del dict_other['_listeners']
        del dict_other['_status']

        return dicteq(dict_self, dict_other)

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
        if isinstance(key, (int, slice)):
            return self._get_suboutput(key)
        else:
            raise exceptions.FastrTypeError('Key should be an integer/slice (for getting a SubOutput)')

    def __getstate__(self):
        """
        Retrieve the state of the Output

        :return: the state of the object
        :rtype dict:
        """
        state = super(Output, self).__getstate__()

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
        super(Output, self).__setstate__(state)

        if state['preferred_types'] is not None:
            self._preferred_types = [fastr.typelist[x] for x in state['preferred_types']]
        else:
            self._preferred_types = None

        suboutputlist = []
        for substate in state['suboutputs']:
            suboutput = SubOutput(self, slice(None))
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
            subout = SubOutput(self, key)
            self._suboutputlist[keystr] = subout

        return subout

    @property
    def blocking(self):
        """
        Flag indicating that this Output will cause blocking in the execution
        """
        return self._output_cardinality[0] in ('val', 'unknown')

    def cardinality(self):
        """
        Cardinality of this Output, may depend on the inputs of the parent Node.

        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        :raises FastrCardinalityError: if cardinality references an invalid :py:class:`Input <fastr.core.inputoutput.Input>`
        :raises FastrTypeError: if the referenced cardinality values type cannot be case to int
        :raises FastrValueError: if the referenced cardinality value cannot be case to int
        """
        desc = self._output_cardinality

        if desc[0] == 'int':
            # Return fixed value
            return desc[1]
        elif desc[0] == 'as':
            # Get cardinality from target if possible
            if desc[1] in self.node.inputs:
                target = self.node.inputs[desc[1]]
                return target.cardinality()
            else:
                raise exceptions.FastrCardinalityError('Cardinality references to invalid field ({} is not an Input in this Node)'.format(desc[1]))
        elif desc[0] in ['val', 'unknown']:
            # Cardinality unknown a priori, need to run first
            return None
        else:
            raise exceptions.FastrCardinalityError('Invalid output cardinality specification found! ({})'.format(desc))

    @property
    def datatype(self):
        """
        The datatype of this Output
        """
        return self._datatype

    @datatype.setter
    def datatype(self, value):
        # This does not differ, as it is a property
        # pylint: disable=arguments-differ
        self._datatype = value

    @property
    def dimensions(self):
        """
        The list of the dimensions in this Output. This will be a tuple of Dimension.
        """
        return self.node.dimensions

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

    @preferred_types.setter
    def preferred_types(self, value):
        """
        The list of preferred :py:class:`DataTypes <fastr.core.datatypemanager.DataType>`
        for this Output. (setter)
        """
        if isinstance(value, type) and issubclass(value, DataType):
            self._preferred_types = [value]
        elif isinstance(value, list) and all([isinstance(x, type) and issubclass(x, DataType) for x in value]):
            self._preferred_types = value
        else:
            fastr.log.warning('Invalid definition of preferred DataTypes, must be a DataType or list of DataTypes! Ignoring!')

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


class SubOutput(Output):
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
        if not isinstance(output, Output):
            raise exceptions.FastrTypeError('Second argument for a SubOutput init should be an Output')

        if not isinstance(index, (int, slice)):
            raise exceptions.FastrTypeError('SubOutput index should be an integer or a slice, found ({}, type {})'.format(index, type(index).__name__))

        super(SubOutput, self).__init__(output.node, output.description)
        self.parent = output
        self.index = index

    def __str__(self):
        """
        Get a string version for the SubOutput

        :return: the string version
        :rtype: str
        """
        return '<SubOutput {}>'.format(self.fullid)

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
        else:
            raise exceptions.FastrTypeError(
                'Index of SubOutput should be int/slice, found {}'.format(type(key).__name__)
            )

    def __getstate__(self):
        """
        Retrieve the state of the SubOutput

        :return: the state of the object
        :rtype dict:
        """
        state = super(SubOutput, self).__getstate__()
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

        state['_preferred_types'] = []
        super(SubOutput, self).__setstate__(state)
        self._preferred_types = None

    def __eq__(self, other):
        """Compare two SubOutput instances with each other. This function ignores
        the parent, node and update status, but tests rest of the dict for equality.
        equality

        :param other: the other instances to compare to
        :type other: SubOutput
        :returns: True if equal, False otherwise
        :rtype: bool
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        dict_self = {k: v for k, v in self.__dict__.items()}
        del dict_self['_node']
        del dict_self['parent']
        del dict_self['_status']

        dict_other = {k: v for k, v in other.__dict__.items()}
        del dict_other['_node']
        del dict_other['parent']
        del dict_other['_status']

        return dicteq(dict_self, dict_other)

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

    def cardinality(self):
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
        parent_cardinality = self.parent.cardinality()

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

    @preferred_types.setter
    def preferred_types(self, value):
        # We need to key for the signature in subclasses, shut pylint up
        # pylint: disable=unused-argument,no-self-use,arguments-differ
        raise exceptions.FastrNotImplementedError('Cannot set DataType of SubOutput, use the parent Output instead')

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


class AdvancedFlowOutput(Output):
    """
    Output for nodes that have an advanced flow. This means that the output
    sample id and index is not the same as the input sample id and index.
    The AdvancedFlowOutput has one extra dimensions that is created by the
    Node.
    """
    @property
    def dimensions(self):
        parent_dimensions = super(AdvancedFlowOutput, self).dimensions

        return tuple(Dimension('{}_{}'.format(d.name, self.id), d.size) for d in parent_dimensions[:-1]) + (parent_dimensions[-1],)


class MacroOutput(Output):
    @property
    def dimensions(self):
        return self.node.get_output_info(self)


class SourceOutput(Output):
    """
    Output for a SourceNodeRun, this type of Output determines the cardinality in
    a different way than a normal NodeRun.
    """
    def __init__(self, node, description):
        """Instantiate a FlowOutput

        :param node: the parent node the output belongs to.
        :param description: the :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
               describing the output.
        :return: created FlowOutput
        :raises FastrTypeError: if description is not of class
                                :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
        :raises FastrDataTypeNotAvailableError: if the DataType requested cannot be found in the ``fastr.typelist``
        """
        super(SourceOutput, self).__init__(node, description)

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

    @property
    def linearized(self):
        """
        A linearized version of the sample data, this is lazily cached
        linearized version of the underlying SampleCollection.
        """
        if self._linearized is None:
            self._linearized = tuple(self.samples[x] for x in self.samples)

        return self._linearized

    def cardinality(self):
        """
        Cardinality of this SourceOutput, may depend on the inputs of the parent NodeRun.

        :param key: key for a specific sample, can be sample index or id
        :type key: tuple of int or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        """
        return sympy.symbols('N_{}'.format(self.node.id.replace(' ', '_')))

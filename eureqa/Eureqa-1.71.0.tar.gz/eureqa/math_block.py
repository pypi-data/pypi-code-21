# Copyright (c) 2017, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json

class MathBlock(object):
    """Represents a building block of a mathematical model. Created
    automatically during the construction of a :py:class:`~eureqa.search_settings.SearchSettings` object.

    MathBlocks can be enabled or disabled to specify whether their corresponding
    mathematical operations are allowed in a :py:class:`~eureqa.search.Search`'s solutions.
    They should be accessed through the :py:attr:`eureqa.search.Search.math_blocks` 
    or :py:attr:`eureqa.search_settings.SearchSettings.math_blocks` properties.
    For a list of available Math Blocks, view the properties of :py:class:`~eureqa.math_block_set.MathBlockSet`.

    """

    def __init__(self, id_, name, complexity, notation):
        """For internal use only.
        PARAM_NOT_EXTERNALLY_DOCUMENTED
        """

        
        self._name = name
        self._id = id_
        self._complexity = complexity
        self._default_complexity = complexity
        self._notation = notation
        self._enabled = False

    @property
    def name(self):
        """ MathBlock's name (read-only) """
        return self._name

    @property
    def complexity(self):
        """ MathBlock's complexity (settable) """
        return self._complexity

    @complexity.setter
    def complexity(self, val):
        self._complexity = val

    @property
    def enabled(self):
        """ Can this MathBlock be used for modeling? """
        return self._enabled

    def enable(self, complexity=None):
        """ Allow this MathBlock to be used for modeling

        :param int complexity: The level of complexity of the MathBlock. If you do not specify a complexity, the default complexity will be used.

        """
        if complexity is None:
            complexity = self._default_complexity
        assert complexity is not None, "Called 'enable()' without specifying a complexity on a MathBlock that's not fully constructed"

        self.complexity = complexity

        self._enabled = True
            
    def disable(self):
        """ Don't allow this MathBlock to be used for modeling """
        self._enabled = False

    def _from_json(self, body):
        self._name = body['op_name']
        self._complexity = int(body['complexity'])
        self._id = int(body['op_id'])
        # only some endpoints return the notation field.
        if 'op_notation' in body:
            self._notation = body['op_notation']
        self._enabled = body.get('enabled', True)
        self._body = body

    @classmethod
    def from_json(cls, body):
        mathBlock = MathBlock(None, None, None, None)
        mathBlock._from_json(body)
        return mathBlock

    def _to_json(self):
        body = {'op_name': self.name,
                'complexity': self.complexity,
                'op_id': self._id,
                'enabled': self._enabled}
        if self._notation is not None:
            body['op_notation'] = self._notation
        return body

    def __eq__(self, other):
        if not isinstance(other, MathBlock):
            return False
        return other._id == self._id and other.name == self.name and other.complexity == self.complexity

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        tpl = (self._id, self.name, self.complexity)
        return hash(tpl)

    def __str__(self):
        return json.dumps(self._to_json(), indent=4, sort_keys=True)

    def __repr__(self):
        return "MathBlock(%s, %s, %s, %s)" % (repr(self._id), repr(self._name), repr(self._complexity), repr(self._notation))


def _from_json(body):
    bloc = MathBlock(None, None, None, None)
    bloc._from_json(body)
    return bloc


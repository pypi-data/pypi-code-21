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


class ComplexityWeights:
    """Represents complexity penalties applied to each model to reward for increased interpretability.

    :param int continuous_variable: additional complexity added for each continuous variable in a term after the first continuous variable.
    :param int boolean_variable: additional complexity added for each binary variable in a model.
    :param int nest_depth: additional complexity added for each term with nested functions, like log(sin(x)).
    """

    def __init__(self, continuous_variable=2, boolean_variable=0, nest_depth=0):
        """For internal use only.
        :param int continuous_variable: additional complexity added for each continuous variable in a term after the first continuous variable.
        :param int boolean_variable: additional complexity added for each binary variable in a model.
        :param int nest_depth: additional complexity added for each term with nested functions, like log(sin(x)).
        """
        self.nest_depth = nest_depth
        self.boolean_variable = boolean_variable
        self.continuous_variable = continuous_variable

    def _from_json(self, body):
        self.nest_depth = body['nest_depth_weight']
        self.boolean_variable = body['num_boolean_variable_weight']
        self.continuous_variable = body['num_continuous_variable_weight']
        self._body = body

    @classmethod
    def from_json(cls, body):
        complexityWeights = ComplexityWeights()
        complexityWeights._from_json(body)
        return complexityWeights

    def _to_json(self):
        body = {'nest_depth_weight': self.nest_depth,
                'num_boolean_variable_weight': self.boolean_variable,
                'num_continuous_variable_weight': self.continuous_variable}
        return body

    def __eq__(self, other):
        if not isinstance(other, ComplexityWeights):
            return False
        return (self.nest_depth == other.nest_depth and self.boolean_variable == other.boolean_variable
                and self.continuous_variable == other.continuous_variable)

    def __ne__(self, other):
        return not (self == other)


def _from_json(body):
    weights = ComplexityWeights()
    weights._from_json(body)
    return weights

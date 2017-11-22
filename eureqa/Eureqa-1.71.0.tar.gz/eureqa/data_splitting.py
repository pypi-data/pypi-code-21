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

class DataSplitting:
    """Represents data splitting settings for the genetic algorithm. Each :py:class:`~eureqa.search.Search` contains a DataSplitting
    object that describes how the genetic algorithm will run. 

    :param bool shuffle: Indicates whether data are shuffled or not before the training.
    :param float training_data_percentage: The percentage of data used for training.
    :param float validation_data_percentage: The percentage of data used for validation.
    :param str training_selection_expression: The expression used for selecting the training set.
    :param str validation_selection_expression: The expression used for selecting the validation set.
    :param str training_selection_expression_type: The type of expression used for selecting the training set. ('EXPRESSION','VARIABLE',None)
    :param str validation_selection_expression_type: The type of expression used for selecting the validation set. ('EXPRESSION','VARIABLE',None)

    :var bool shuffle: Indicates whether data are shuffled or not before the training.
    :var float training_data_percentage: The percentage of data used for training.
    :var float validation_data_percentage: The percentage of data used for validation.
    :var str training_selection_expression: The expression used for selecting the training set.
    :var str validation_selection_expression: The expression used for selecting the validation set.
    :var str training_selection_expression_type: The type of expression used for selecting the training set. ('EXPRESSION','VARIABLE',None)
    :var str validation_selection_expression_type: The type of expression used for selecting the validation set. ('EXPRESSION','VARIABLE',None)
    """

    def __init__(self, shuffle=None, training_data_percentage=None, validation_data_percentage=None,
                 training_selection_expression=None, validation_selection_expression=None,
                 training_selection_expression_type=None, validation_selection_expression_type=None):
        self._type = 'custom'
        self.shuffle = shuffle
        self.training_data_percentage = training_data_percentage
        self.validation_data_percentage = validation_data_percentage
        self.training_selection_expression = training_selection_expression
        self.validation_selection_expression = validation_selection_expression
        self.training_selection_expression_type = training_selection_expression_type
        self.validation_selection_expression_type = validation_selection_expression_type


    def _to_json(self, body):
        # The data splitting parameters are part of the entire search block.
        # So they have to be appended to the existing body.
        # If the user hasn't set any parameters yet, don't write any out yet;
        # we need some information, otherwise this isn't a valid block.
        if self._type == 'custom':
            if self.training_data_percentage and self.validation_data_percentage:
                body['shuffle_rows'] = self.shuffle
                body['training_data_percent'] = self.training_data_percentage
                body['validation_data_percent'] = self.validation_data_percentage
                body['data_splitting'] = self._type
        else:
            body['data_splitting'] = self._type
        if self.training_selection_expression:
            body['training_selection_expression'] = self.training_selection_expression
        if self.validation_selection_expression:
            body['validation_selection_expression'] = self.validation_selection_expression
        if self.training_selection_expression_type:
            body['training_selection_expression_type'] = self.training_selection_expression_type
        if self.validation_selection_expression_type:
            body['validation_selection_expression_type'] = self.validation_selection_expression_type


    def _from_json(self, body):
        self._type = body.get('data_splitting')
        if self._type == 'custom':
            self.shuffle = body.get('shuffle_rows')
            self.training_data_percentage = body.get('training_data_percent')
            self.validation_data_percentage = body.get('validation_data_percent')
        else:
            self.shuffle = None
            self.training_data_percentage = None
            self.validation_data_percentage = None

        self.training_selection_expression = body.get('training_selection_expression')
        self.validation_selection_expression = body.get('validation_selection_expression')
        self.training_selection_expression_type = body.get('training_selection_expression_type')
        self.validation_selection_expression_type = body.get('validation_selection_expression_type')

        self._body = body

    @classmethod
    def from_json(cls, body):
        dataSplitting = DataSplitting(None)
        dataSplitting._from_json(body)
        return dataSplitting

    def __eq__(self, other):
        if not isinstance(other, DataSplitting):
            return False
        return (self._type == other._type and self.shuffle == other.shuffle
                and self.training_data_percentage == other.training_data_percentage
                and self.validation_data_percentage == other.validation_data_percentage)

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        body = {}
        self._to_json(body)
        return json.dumps(body)


_in_order_sample = DataSplitting(shuffle=None, training_data_percentage=None, validation_data_percentage=None)
_in_order_sample._type = "extrapolate"

_random_sample = DataSplitting(shuffle=None, training_data_percentage=None, validation_data_percentage=None)
_random_sample._type = "equal"


def _from_json(body):
    splitting = DataSplitting(None)
    splitting._from_json(body)
    return splitting

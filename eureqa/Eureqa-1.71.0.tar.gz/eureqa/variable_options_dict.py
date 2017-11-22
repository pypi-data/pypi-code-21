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

from variable_options import VariableOptions

class VariableOptionsDict(dict):
    """
    Create a dictionary of :py:class:`~eureqa.variable_options.VariableOptions` objects
    in which the key is the :py:class:`~eureqa.variable_options.VariableOptions` name.
    
    This class is used primarily to hold variable parameter overrides for 
    :py:class:`~eureqa.eureqa.Eureqa` and :py:class:`~eureqa.search.Search` .
    """
    def add(self, variable_options):
        """
        Add an existing :py:class:`~eureqa.variable_options.VariableOptions` to this dictionary.

        :param VariableOptions variable_options:  :py:class:`~eureqa.variable_options.VariableOptions` object to add
        """
        assert isinstance(variable_options, VariableOptions), "VariableOptionsDict can only hold VariableOptions objects.  Tried to insert an object of type '%s'." % variable_options.__class__.__name__
        self[variable_options.name] = variable_options
    
    def __missing__(self, key):
        v = VariableOptions(name = key)
        self[key] = v
        return v 

    def __setitem__(self, key, value):
        ## Override __setitem__ to do some validation
        assert isinstance(value, VariableOptions), "VariableOptionsDict can only hold VariableOptions objects.  Tried to insert an object of type '%s'." % value.__class__.__name__
        assert key == value.name, "Can't assert VariableOption named '%s' into VariableOptionsDict field '%s':  Names must match" % (value.name, key)
        assert key not in self, "VariableOptionsDict already has a VariableOptions for variable %s" % (key)
        super(VariableOptionsDict, self).__setitem__(key, value)

    def _to_json(self):
        return [x._to_json() for x in self.itervalues()]

    def _from_json(self, vars):
        for var in vars:
            var = VariableOptions._from_json(var)
            self[var.name] = var

    @classmethod
    def from_json(cls, vars):
        vod = cls()
        vod._from_json(vars)
        return vod
    

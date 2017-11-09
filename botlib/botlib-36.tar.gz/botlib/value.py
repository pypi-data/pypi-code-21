# BOTLIB Framework to program bots
#
# botlib/value.py
#
# Copyright 2017 B.H.J Thate
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice don't have to be included.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" container module.. """

from botlib.object import Object

class Value(Object):

    """ A Value provides a iterator interface to any type. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args[1:], **kwargs)
        self._value = args[0]

    def __iter__(self):
        return self.__next__()

    def __next__(self):
        if type(self._value) in [[], ()]:
            for i in self._value:
                yield i
        else:
            return self._value
            
"""       
     __add__(), __radd__(), __iadd__(), __mul__(), __rmul__() and __imul__() 
     append(), count(), index(), extend(), insert(), pop(), remove(), reverse() and sort(),
      __getitem__(), __setitem__(), __delitem__()
      __contains__()
      __len__()
      __length_hint__()
      __reversed__()
      __contains__()
"""
       
# Allen Institute Software License - This software license is the 2-clause BSD
# license plus a third clause that prohibits redistribution for commercial
# purposes without further permission.
#
# Copyright 2017. Allen Institute. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Redistributions for commercial purposes are not permitted without the
# Allen Institute's written permission.
# For purposes of this license, commercial purposes is the incorporation of the
# Allen Institute's software into anything for which you will charge fees or
# other compensation. Contact terms@alleninstitute.org for commercial licensing
# opportunities.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
import pytest
from allensdk.deprecated import deprecated, class_deprecated
import warnings


@pytest.fixture
def deprecated_method():

    @deprecated()
    def i_am_deprecated():
        pass

    return i_am_deprecated
    
    
@pytest.fixture
def deprecated_class():

    @class_deprecated('msg')
    class dep_cls(object):
        def __init__(self, a):
            self.a = a
        
    return dep_cls


def test_deprecated(deprecated_method):
    expected = "Function i_am_deprecated is deprecated. "

    with warnings.catch_warnings(record=True) as c:
        warnings.simplefilter('always')
        deprecated_method()

        print(expected)
        print(str(c[-1].message))

        assert expected == str(c[-1].message)
        
        
def test_deprecated_class(deprecated_class):
    expected = 'Class dep_cls is deprecated. msg'
    
    with warnings.catch_warnings(record=True) as c:
        warnings.simplefilter('always')
        deprecated_method()

        obj = deprecated_class(1)

        assert( expected == str(c[-1].message) )
        assert( obj.a == 1 )

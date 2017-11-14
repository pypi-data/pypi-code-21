# -*- coding: utf-8 -*-

"""This module defines a decorator for classes that need to execute a static constructor."""


import inspect
import typing


__author__ = "Patrick Hohenecker"
__copyright__ = (
        "Copyright (c) 2017 Patrick Hohenecker\n"
        "\n"
        "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
        "of this software and associated documentation files (the \"Software\"), to deal\n"
        "in the Software without restriction, including without limitation the rights\n"
        "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
        "copies of the Software, and to permit persons to whom the Software is\n"
        "furnished to do so, subject to the following conditions:\n"
        "\n"
        "The above copyright notice and this permission notice shall be included in all\n"
        "copies or substantial portions of the Software.\n"
        "\n"
        "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
        "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
        "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
        "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
        "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
        "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
        "SOFTWARE."
)
__license__ = "MIT License"
__version__ = "2017.1"
__date__ = "Nov 13, 2017"
__maintainer__ = "Patrick Hohenecker"
__email__ = "mail@paho.at"
__status__ = "Production"


def init(init_meth: str = "__static_init__") -> typing.Callable[[type], type]:
    """A decorator for classes that need to execute a static constructor.

    Args:
        init_meth (str, optional): The name of the classmethod that defines the static constructor.

    Raises:
        TypeError: If ``init`` is used to decorate something else than a class.
        ValueError: If the annotated class does not have a classmethod named ``init_meth``.
    """
    # ensure that init_meth is a string
    init_meth = str(init_meth)
    
    # build function that invokes the static constructor
    def invoke_static_init(cls: type) -> type:
        
        # ensure that cls is a class
        if not inspect.isclass(cls):
            raise TypeError("@static_init.init can only be used to decorate classes!")
        
        # check whether the class has the classmethod that was specified as static constructor
        if init_meth not in cls.__dict__ or not isinstance(cls.__dict__[init_meth], classmethod):
            raise ValueError("The class {} does not have a classmethod {}!".format(cls.__qualname__, init_meth))
        
        # retrieve function that defines the static constructor
        init_op = getattr(cls, init_meth, None)
        
        # invoke constructor
        init_op()
        
        return cls
    
    return invoke_static_init

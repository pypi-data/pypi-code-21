# BOTLIB Framework to program bots
#
# botlib/error.py
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
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
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

""" botlib exceptions. """

import builtins

class Error(builtins.Exception):
    """ base error class. """
    pass

class EBUSY(Error):
    """ Cannot start threads. """
    pass

class ENOWORKER(Error):
    """ No worker available. """
    pass

class EKEY(Error):
    """ key is not found. """
    pass

class ENOTABLE(Error):
    """ No modules table is available in the kernel. """
    pass

class EDEFAULT(Error):
    """ missing default value. """
    pass

class ENOMODULE(Error):
    """ the module could not be located. """
    pass

class ENOCOMMAND(Error):
    """ a command to execute cannot be found. """
    pass

class ENOWORKDIR(Error):
    """ workdir is not provided. """
    pass

class ERSINGLENAME(Error):
    """ first level directory names are reserved. """
    pass

class ETOPLEVELDIR(Error):
    """ path is a toplevel directory and cannot be written to. """
    pass

class ENODEFAULT(Error):
    """ no default provided. """
    pass

class ENOBID(Error):
    """ no bot id available. """
    pass

class EDEFINE(Error):
    """ define error. """
    pass

class ENETWORK(Error):
    """ network error. """
    pass

class ENOTXT(Error):
    """ no text to parse. """
    pass

class ENOPATH(Error):
    """ there is not path available to save to disk. """
    pass

class ENODATA(Error):
    """ the objectect loaded from file has no data section. """
    pass

class ERE(Error):
    """ error in a regular expression. """

class ENOPREFIX(Error):
    """ first argument is not a directory in the workdir. """
    pass

class EBORDER(Error):
    """ program is reaching out of its cfgured workdir. """
    pass

class EDIR(Error):
    """ file is a directory error. """
    pass

class EWORKDIR(Error):
    """ workdir is not set or not reachable. """
    pass

class ERESUME(Error):
    """ an error occured during resume. """
    pass

class EREBOOT(Error):
    """ an error occured during reboot. """
    pass

class EPASSWORD(Error):
    """ wrong password provided. """
    pass

class ERESERVED(Error):
    """ a reserved word is used. """
    pass

class ELOAD(Error):
    """ loading of the objectect failed. """
    pass

class EFILENAME(Error):
    """ filename is not correct. """
    pass

class EISMETHOD(Error):
    """ attribute is a method. """
    pass

class ENOMETHOD(Error):
    """ no method is provided. """
    pass

class ENODATE(Error):
    """ date cannot be determined. """
    pass

class ENOTIME(Error):
    """ no time can be detected. """
    pass

class ENODIR(Error):
    """ directory is not available. """
    pass

class EDISPATCHER(Error):
    """ dispatcher is missing. """
    pass

class EATTRIBUTE(Error):
    """ item is already an attribute. """
    pass

class ENOTSET(Error):
    """ variable is not set. """
    pass

class ESET(Error):
    """ attribute is already set. """
    pass

class ESIGNATURE(Error):
    """ signature check failed. """
    pass

class ENOTIMPLEMENTED(Error):
    """ method or function is not implemented. """
    pass

class ENOJSON(Error):
    """ string cannot be _parsed as JSON. """
    pass

class EJSON(Error):
    """ a JSON compiling error occured. """
    pass

class EDISCONNECT(Error):
    """ server has disconnect. """
    pass

class ECONNECT(Error):
    """ connect error occured. """
    pass

class EFILE(Error):
    """ error reading the file. """
    pass

class EARGUMENT(Error):
    """ argument given results in an error. """
    pass

class ETYPE(Error):
    """ argument is of the wrong type. """
    pass

class EOWNER(Error):
    """ origin is not an owner. """
    pass

class EFUNC(Error):
    """ error occured during execution of the function. """
    pass

class ENOFUNC(Error):
    """ function is not provided. """
    pass

class EREGISTER(Error):
    """ error during registration, """
    pass

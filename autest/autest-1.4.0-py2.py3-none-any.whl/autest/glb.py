from __future__ import absolute_import, division, print_function

Engine = None

# Object that hold tests functions used


class When(object):
    pass


Locals = {}

# this hold meta information for any items we will add to
# any runable object
runable_items = {}

# this hold meta information for any items we will add to
# the Setup object
setup_items = {}

# set of reporters that we can use to generate reports with
reporters = {}

# extention for File creation
# mapping of file class names to the class
FileTypeMap = {}
# mapping of file extension to class
FileExtMap = {}

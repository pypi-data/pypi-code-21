# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

"""Python attribute name conversion utils"""
import re
def python_name(name):
    """Converts the file name to valid Python identifier - replaces the characters
    that are not legal in a Python identifier by underscores.
        identifier ::=  (letter|"_") (letter | digit | "_")*
        letter     ::=  lowercase | uppercase
        lowercase  ::=  "a"..."z"
        uppercase  ::=  "A"..."Z"
        digit      ::=  "0"..."9"
    """
    # replace invalid characters by underscores
    py_name = re.sub('[^0-9a-zA-Z_]', '_', name)
    # remove invalid leading (non-alphabet) characters
    return re.sub('^[^A-Za-z]*', '', py_name)

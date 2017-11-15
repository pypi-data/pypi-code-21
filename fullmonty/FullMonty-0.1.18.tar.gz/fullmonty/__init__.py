# coding=utf-8

"""\
FullMonty
=========

FullMonty is a collection of various library modules that are not big enough to justify individual packaging.

For example, I like using a context with cd:

.. code-block:: python

    with cd(path):
        # current working directory is path

Another is the list_helper module where compress_list, unique_list, and is_sequence reside.  Now the implementation
is just one liners but I find the intent of the code easier to comprehend with this:

.. code-block:: python

    new_list = compress_list(old_list)

versus:

.. code-block:: python

    new_list = [item for item in old_list if item]

Etymology
---------

The full monty is a British slang phrase of uncertain origin. It is generally used to mean "everything which is
necessary, appropriate, or possible; ‘the works’".
-- http://en.wikipedia.org/wiki/Full_monty_%28phrase%29



Installation
------------

To install from PyPI:

.. code-block:: bash

    ➤ pip install fullmonty


"""
__docformat__ = 'restructuredtext en'

__version__ = '0.1.18'

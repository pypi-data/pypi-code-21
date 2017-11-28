from __future__ import unicode_literals
import os

dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

with open(os.path.join(dir_path, 'VERSION'), 'r') as file_version:
    __version__ = file_version.read()
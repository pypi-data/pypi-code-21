"""
Common processing definitions

Copyright (c) 2017 - Eindhoven University of Technology, The Netherlands

This software is made available under the terms of the MIT License.
"""

from typing import Sequence, Tuple
from nbformat import NotebookNode
from pathlib import Path

# type alias for processing result
ProcessingResultType = Sequence[Tuple[NotebookNode, Path]]

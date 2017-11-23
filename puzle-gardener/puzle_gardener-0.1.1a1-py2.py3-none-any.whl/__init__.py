from .core import run
from .config import *
from .abstract_tree import *
from .generation import *
from .repository import *

import src.cli


def main():
    src.cli.generate()




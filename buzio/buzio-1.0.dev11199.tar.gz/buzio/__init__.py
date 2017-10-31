"""[summary]

[description]

Variables:
	init() {[type]} -- [description]
	__version__ {str} -- [description]
	console {[type]} -- [description]
	formatStr {[type]} -- [description]
"""
from colorama import init
from buzio.cli import Console

init()

__version__ = "1.0.dev"

console = Console()
formatStr = Console(format_only=True)

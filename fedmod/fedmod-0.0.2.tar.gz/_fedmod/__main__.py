#!/usr/bin/env python3

import sys
from .cli import ModtoolsCLIHelper


if __name__ == "__main__":
    cli = ModtoolsCLIHelper()
    sys.exit(cli.run())

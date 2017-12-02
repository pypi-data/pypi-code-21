#!/usr/bin/env python3
from puer.manager import Manager


if __name__ == "__main__":
    args = Manager.parse_args()
    Manager(args)

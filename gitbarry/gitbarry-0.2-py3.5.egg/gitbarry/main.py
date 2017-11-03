#!/usr/bin/python3

import sys

from gitbarry.utils.git import assert_is_git_repo
from gitbarry.reasons import REASONS


def usage(exit=True):
    print("\nUsage:")
    print("git barry %s" % '|'.join(REASONS.keys()))
    if exit:
        sys.exit(0)


def main(reason, *args):
    if reason not in REASONS.keys():
        print("Available reasons are: %s" % ", ".join(REASONS.keys()))
        usage()

    reason_inst = REASONS[reason].Reason(*args)
    errors = reason_inst.validate()
    if len(errors):
        for err in errors:
            print(" - %s" % err)
            sys.exit(7)
    else:
        reason_inst.run()


def run():
    if len(sys.argv[1:]) < 1:
        usage()

    main(*sys.argv[1:])

if __name__ == "__main__":
    assert_is_git_repo()
    run()

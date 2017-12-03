#!/usr/bin/env python

import argparse
import logging
import trust
from logging.handlers import SysLogHandler


def parseArgs():
    description = ("Extracts data from a JSON file, multiple files or MongoDB "
                   "database.")

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "source",
        help="The location of the source data."
    )

    parser.add_argument(
        "--response-mode",
        choices=["json", "text", "complete"],
        default="complete",
        help="The way to format the response."
    )

    parser.add_argument(
        "--username",
        help="The name of the user accessing the data."
    )

    parser.add_argument(
        "--password",
        help="The password of the user accessing the data."
    )

    parser.add_argument(
        "--optional",
        action='store_true',
        help="The value is optional and may not exist in the source data."
    )

    parser.add_argument(
        "query",
        help="The query path."
    )

    return parser.parse_args()


if __name__ == "__main__":
    logger = logging.getLogger("trust")
    logHandler = SysLogHandler(address="/dev/log")
    formatter = logging.Formatter("trust: [%(levelname)s] %(message)s")
    logHandler.setFormatter(formatter)
    logHandler.setLevel(logging.DEBUG)
    logger.addHandler(logHandler)
    logger.setLevel(logging.DEBUG)

    args = parseArgs()

    finder = trust.FileFinder(
        data_path=args.source,
        logger=logger,
        audit=trust.audit.AuditToSyslog("trust-audit")
    )

    engine = trust.Trust(finder)
    response = engine.process(
        args.query,
        args.response_mode,
        trust.Credentials(args.username, args.password),
        args.optional,
    )

    print(response)

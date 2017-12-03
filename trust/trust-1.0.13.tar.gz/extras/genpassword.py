#!/usr/bin/env python

import argparse
from passlib.hash import pbkdf2_sha256


rounds_map = {
    "poor": 10,
    "normal": 50000,
    "strong": 100000,
}

parser = argparse.ArgumentParser(
    description="Generates a PBKDF2 password hash."
)

parser.add_argument(
    "--level",
    choices=rounds_map.keys(),
    default="strong",
    help="The level of encryption."
)

parser.add_argument("password", help="The password to hash.")

args = parser.parse_args()

result = pbkdf2_sha256.encrypt(
    args.password,
    rounds=rounds_map[args.level],
    salt_size=16
)

print(result)

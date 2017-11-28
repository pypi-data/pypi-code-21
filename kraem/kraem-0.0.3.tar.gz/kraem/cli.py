#!/usr/bin/python3

import argparse
from kraem.engine import run


def create_args():
    parser = argparse.ArgumentParser(
        description="Compress images from a folder recursively to a new folder")

    parser.add_argument(
        '-source', help='source directory'
    )

    parser.add_argument(
        '-destination', help='destination directory'
    )

    parser.add_argument(
        '-quality', help='adjust image quality for compression'
    )

    parser.add_argument(
        '-gcs', help='Google Cloud Storage bucket'
    )

    args = parser.parse_args()

    return args


def main():
    run(create_args())

#!/usr/bin/env python
from csr_azure_guestshell import cag
import argparse

parser = argparse.ArgumentParser(description="Upload tech-support to Storage")
parser.add_argument('container', help='The name of the container to upload to')
parser.add_argument('filename', help='Filename to upload to container')
args = parser.parse_args()

container = args.container
filename = args.filename

cag().save_cmd_output(["show tech-support"], filename, container)

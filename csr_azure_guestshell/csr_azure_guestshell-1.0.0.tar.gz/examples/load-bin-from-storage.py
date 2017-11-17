#!/usr/bin/env python
import cli
import sys
from csr_azure_guestshell import cag
import argparse

parser = argparse.ArgumentParser(description="Upload bin file")
parser.add_argument('container', help='The name of the container to upload to')
parser.add_argument('filename', help='Filename to upload to container')
parser.add_argument(
    '--reload', help='After downloading, reboot system', default=None)
args = parser.parse_args()


container = args.container
filename = args.filename

csr = cag()

csr.download_file(container, filename)

configuration = "boot system flash:" + filename
cli.configure(configuration)
cli.execute("copy running start")
if args.reload is not None:
    cli.execute("reload")

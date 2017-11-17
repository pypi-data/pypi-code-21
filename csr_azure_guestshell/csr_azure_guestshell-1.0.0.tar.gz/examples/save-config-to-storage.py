#!/usr/bin/env python
import sys
import cli
from csr_azure_guestshell import cag
import argparse

parser = argparse.ArgumentParser(description="Upload config file")
parser.add_argument('container', help='The name of the container to upload to')
parser.add_argument('filename', help='Filename to upload to container')
args = parser.parse_args()

container = args.container
filename = args.filename

# first, save the config to bootflash
get_config = "copy running-config bootflash:%s" % filename
result = cli.execute(get_config)
if 'copied' not in result:
    print result
    sys.exit(1)

result = result.splitlines()

# print output of ios cli output showing the config copy
for line in result:
    if 'copied' in line:
        print line

cag().upload_file(container, filename)

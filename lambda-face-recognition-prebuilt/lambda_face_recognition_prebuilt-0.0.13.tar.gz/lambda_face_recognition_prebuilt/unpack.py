import os
import ctypes
import sys

from safe_extractor import safe_extractor
import requests

deps_path=os.path.join('/tmp', 'deps.zip')
deps_install='/tmp/'
deps_download='https://s3.amazonaws.com/lambda_face_recognition_prebuilt/deps.zip'

print("Downloading '{}' to '{}'.".format(deps_download, deps_path))
r = requests.get(deps_download)
with open(deps_path, 'wb') as outfile:
    outfile.write(r.content)

print("Unpacking '{}' into '{}'.".format(deps_path, deps_install))
safe_extractor.unzip_it(deps_path, deps_install)

print("Recursively loading all libs from '{}'.".format(deps_install))
for d, dirs, files in os.walk(deps_install):
    for f in files:
        if f.endswith('.a'):
            continue
        try:
            ctypes.cdll.LoadLibrary(os.path.join(d, f))
        except Exception as e:
            continue

print("Inserting '{}' into python's sys.path.".format(deps_install))
sys.path.insert(0, deps_install)

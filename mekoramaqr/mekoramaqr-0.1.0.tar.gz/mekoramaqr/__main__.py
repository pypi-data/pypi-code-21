# MekoramaQR
# Copyright (C) 2017 by MekoramaQR contributors

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import unicode_literals

'''
Installation:
pip install qrtools qrcode pil
apt install python-dev (to compile) --> pip install numpy
sudo apt-get install libzbar-dev --> pip install zbar
'''
import re
import binascii
import argparse
from .mekoqr import MekoQR
from .mekolevel import *

def toHex_chunk(t, nbytes):
    "Format text t as a sequence of nbyte long values separated by spaces."
    chars_per_item = nbytes * 2
    hex_version = binascii.hexlify(t)
    num_chunks = len(hex_version) / chars_per_item
    def chunkify():
        for start in xrange(0, len(hex_version), chars_per_item):
            yield hex_version[start:start + chars_per_item]
    return ' '.join(chunkify())

#convert string to hex
'''
def toHex(s):
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)

    return reduce(lambda x,y:x+y, lst)
'''
toHex = lambda x:"".join([hex(ord(c))[2:].zfill(2) for c in x])
#'''

def main():
    parser = argparse.ArgumentParser( description="Decode Mekorama levels" )
    parser.add_argument("qrimage", help="Image file containing a QR Code for a level", type=argparse.FileType('rb'))
    parser.add_argument("-j","--json", help="Output json description", type=argparse.FileType('wb'))
    parser.add_argument("-r","--raw", help="Output compressed QR data", type=argparse.FileType('wb'))
    parser.add_argument("-c","--code", help="Output uncompressed level data", type=argparse.FileType('wb'))
    parser.add_argument("--qr", help="Re-write level data to QR Code", type=argparse.FileType('wb'))
    args = parser.parse_args()

    fileobject = args.qrimage
    filename = fileobject.name
    filedata = fileobject.read()

    qr = None
    extfile = None
    basefile = None

    filepattern = re.compile(r"^(.*[\\/])?(?P<basename>[^\\/]+)\.(?P<extension>[^.\\/]+)$")
    filematch = filepattern.search(filename)
    if filematch:
        basefile = filematch.group("basename")
        extfile = filematch.group("extension")

        file_is_jpg = toHex(filedata[:3]) == 'ffd8ff'  # jpg signature
        file_is_png = toHex(filedata[:8]) == '89504e470d0a1a0a'  # png signature
        file_is_json = extfile.lower() == 'json' and filedata[0] == '{'  # json "signature" with a test on the extension

        # Test if the input is an image or the JSON data
        if file_is_jpg or file_is_png:
            qr = MekoQR(fileobject)
        elif file_is_json:
            qr = MekoQR()

    if qr is not None:
        level = None
        if qr.code is not None:
            level = MekoLevel(code=qr.code)
        elif extfile.lower() == 'json':
            level = MekoLevel(jsonfile=filename)

        if args.code is not None:
            qr.write(args.code)

        if args.json is not None:
            # Saving to JSON in order to import it in the 3D editor
            level.saveJSON(args.json)

        if args.raw is not None:
            # Note that this uses the input data
            # level.toHex() would be equivalent but different
            qr.write(args.raw, toHex(qr.qr.data).decode('hex'))

        if args.qr is not None:
            # The new QR Code to scan in Mekorama
            qr.save(level.toHex(), args.qr)



if __name__ == "__main__":
    main()

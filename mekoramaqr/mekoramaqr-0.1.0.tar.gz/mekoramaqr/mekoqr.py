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

import qrtools
import zlib
import qrcode

def toHex(x):
    "convert string to hex"
    return "".join([hex(ord(c))[2:].zfill(2) for c in x])

class MekoQR:
    signature = '01130dfc'
    def __init__(self, filename=None, improved=False):
        """Create a new level from a QR Code"""
        self.qr = qrtools.QR()
        self.code = None
        if filename is not None:
            self.read(filename)
            if not self.code and improved:
                self.read_improved(filename)

    def read_improved(self, filename):
        """Crop a supposed exported Mekorama card around the QR Code frame then enlarge it for more details"""
        from StringIO import StringIO
        try:
            from PIL import Image
        except:
            import Image

        img = Image.open(filename)
        width, height = img.size

        # Cropping image around the supposed QR Code location
        img2 = img.crop((width/3, height/2, width, height))
        width, height = img2.size

        # Resizing the QR Code x 2
        basewidth = width*2
        wpercent = (basewidth / float(width))
        hsize = int((float(height) * float(wpercent)))
        img2 = img2.resize((basewidth, hsize), Image.ANTIALIAS)

        # Saving in-memory
        output = StringIO()
        img2.save(output, format='PNG')

        # Reading again
        self.read(output)


    def read(self, filename):
        """Read from a QR Code file"""
        # populates self.code from the image file
        self.qr.decode(filename)
        signature = toHex(self.qr.data[:4])
        if not signature == self.signature:
            return False
        zlib_data = toHex(self.qr.data[4:])
        try:
            self.code = zlib.decompress(zlib_data.decode('hex'))
        except:
            print 'zlib decompression failed'
            return False
        return True

    def write(self, rawfile, hexdata=None):
        """Write decompressed level data to file.
        Accepts either a filename or a file-like object
        """
        if hexdata is None:
            hexdata = self.code

        if hexdata is not None:
            # filename
            if type(rawfile) == str:
                with open(rawfile, 'wb') as f:
                    f.write(hexdata)
                    print "Raw  saved:", rawfile
                    return True
            # file-like object
            else:
                rawfile.write(hexdata)
                print "Raw  saved:", rawfile.name if hasattr(rawfile,"name") else rawfile
                return True
        return False

    def save(self, hexdata, imgfile=None, box_size=10):
        """Write hexdata to a QR Code

        Args:
            - hexdata (bytes): binary payload
            - imgfile (str or file-like object): output filename or handle
            - box_size (int): size in pixels of the qr-code module size

        Returns:
            The QR Code image
        """
        d1 = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS)
        zlib_data = d1.compress(hexdata.decode('hex'))+d1.flush()
        qr_data = self.signature + toHex(zlib_data)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=4,
        )
        qr.add_data(qr_data.decode('hex'))
        qr.make(fit=True)

        img = qr.make_image()
        if imgfile is not None:
            img.save(imgfile)
        if hasattr(imgfile, "name"):
            print "Code saved:", imgfile.name
        return img

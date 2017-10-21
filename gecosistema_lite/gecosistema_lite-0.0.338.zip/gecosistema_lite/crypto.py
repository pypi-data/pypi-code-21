# -------------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2017 Luzzi Valerio 
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        crypto.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     19/08/2017
# -------------------------------------------------------------------------------

from base64 import b64encode, b64decode
import hashlib
import os
from Crypto.Cipher import AES
from strings import padr
from filesystem import md5sum

__KEY__ = md5sum(__file__)

def encrypt(raw, key=__KEY__):
    r = 32 - len(raw) % 32
    raw = padr(raw, len(raw) + r, chr(r))
    # iv = Random.new().read(AES.block_size)
    iv = os.urandom(AES.block_size)
    key = hashlib.sha256(key.encode()).digest()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return b64encode(iv + cipher.encrypt(raw))

def decrypt(enc, key=__KEY__):
    enc = b64decode(enc)
    iv = enc[:AES.block_size]
    key = hashlib.sha256(key.encode()).digest()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    data = cipher.decrypt(enc[AES.block_size:])
    data = data[:-ord(data[len(data) - 1:])]
    return data.decode('utf-8')

def main():
    message = "The answer is no."
    ctxt = encrypt(message)
    print ctxt
    print decrypt(ctxt)

if __name__ == "__main__":
    main()

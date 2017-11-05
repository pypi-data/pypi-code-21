# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
import base64
import logging
import lzma
import os

from cryptography.hazmat.primitives import ciphers, hmac, hashes
from cryptography.hazmat.primitives.kdf import pbkdf2
from cryptography.hazmat import backends

def _password_derive(key, salt):
   kdf = pbkdf2.PBKDF2HMAC(
      algorithm=hashes.SHA256(),
      length=16,
      salt=salt,
      iterations=100000,
      backend=backends.default_backend()
   )
   return base64.urlsafe_b64encode(kdf.derive(key))

class _WriteableEncryptedStream(object):
   """A write-only stream to an encrypted file. Data written to the stream is automatically encrypted."""
   def __init__(self, path, password):
      backend = backends.default_backend()
      str_key = password.encode()
      salt = os.urandom(16)
      hmac_salt = os.urandom(16)
      iv = os.urandom(16)
      key = _password_derive(str_key, salt)
      hmac_key = _password_derive(str_key, hmac_salt)
      self.checksummer = hmac.HMAC(hmac_key, hashes.SHA256(), backend=backend)
      cipher = ciphers.Cipher(ciphers.algorithms.AES(key), ciphers.modes.CTR(iv), backend=backend)
      self.cryptor = cipher.encryptor()
      initialiser= iv + salt + hmac_salt
      self.checksummer.update(initialiser)
      self.output_stream= open(path, mode="wb")
      self.output_stream.write(initialiser)
   def write(self, data):
      out = self.cryptor.update(data)
      self.checksummer.update(out)
      self.output_stream.write(out)
   def close(self):
      out = self.cryptor.finalize()
      self.checksummer.update(out)
      self.output_stream.write(out)
      signature = self.checksummer.finalize()
      self.output_stream.write(signature)
      self.output_stream.close()

class _ReadableEncryptedStream(object):
   """A read-only stream to an encrypted file. Data read from the stream is automatically decrypted."""
   def __init__(self, path, password):
      self.input_stream= open(path, "rb")
      str_key = password.encode()
      raw= self.input_stream.read(80)
      if len(raw)<80:
         raise RuntimeError("file too short")
      assert len(raw)==80
      initialiser= raw[:48]
      iv = initialiser[:16]
      salt = initialiser[16:32]
      hmac_salt = initialiser[32:48]
      self.read_ahead= raw[48:] # empty indicates end of input_stream
      self.outbuffer= b""
      key = _password_derive(str_key, salt)
      hmac_key = _password_derive(str_key, hmac_salt)
      backend = backends.default_backend()
      cipher = ciphers.Cipher(ciphers.algorithms.AES(key), ciphers.modes.CTR(iv), backend=backend)
      self.cryptor = cipher.decryptor()
      self.checksummer = hmac.HMAC(hmac_key, hashes.SHA256(), backend=backend)
      self.checksummer.update(initialiser)
   def _fill(self, size):
      if not self.read_ahead:
         return
      bs= 8192 if size<0 else size
      while size==-1 or size>len(self.outbuffer):
         raw= self.read_ahead + self.input_stream.read(bs)
         encrypted= raw[:-32]
         self.read_ahead= raw[-32:]
         if len(encrypted) > 0:
            self.outbuffer += self.cryptor.update(encrypted)
            self.checksummer.update(encrypted)
         else:
            # reached the end which means read_ahead is signature
            self.outbuffer += self.cryptor.finalize()
            self.checksummer.verify(self.read_ahead)
            self.read_ahead= None
            break
   def read(self, size=-1):
      self._fill(size)
      n= len(self.outbuffer) if size<0 or len(self.outbuffer)<size else size
      data= self.outbuffer[:size]
      self.outbuffer= self.outbuffer[size:]
      return data
   def seekable(self):
      return False
   def close(self):
      self.input_stream.close()

class open_bin(object):
   def __init__(self, path, mode, password):
      """Opens an encrypted binary stream in a context manager."""
      if mode == "w":
         fd= _WriteableEncryptedStream(path, password)
      elif mode == "r":
         fd= _ReadableEncryptedStream(path, password)
      else:
         raise ValueError("Invalid mode: "+mode)
      # Derived classes may append more streams using fd as underlying stream.
      self._streams= [fd]
   def __enter__(self):
      return self._streams[-1]
   def __exit__(self, exc_type, exc_val, exc_tb):
      while self._streams:
         fd= self._streams.pop()
         fd.close()

class open_txt(open_bin):
   def __init__(self, path, mode, password):
      """Opens an encrypted and compressed UTF-8 stream."""
      open_bin.__init__(self, path, mode, password)
      f= lzma.open(self._streams[-1], mode+"t", encoding="UTF-8")
      self._streams.append(f)

class open_lzma(open_bin):
   def __init__(self, path, mode, password):
      """Opens an encrypted and compressed binary stream."""
      open_bin.__init__(self, path, mode, password)
      f= lzma.open(self._streams[-1], mode+"b")
      self._streams.append(f)

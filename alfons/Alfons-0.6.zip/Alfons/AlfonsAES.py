#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
from Crypto import Random
from Crypto.Cipher import AES

def encrypt(s, key):
	"Encrypt a string"
	s = _pad(s)
	iv = Random.new().read(AES.block_size)
	cipher = AES.new(key, AES.MODE_CBC, iv)
	return base64.b64encode(iv + cipher.encrypt(s))

def decrypt(s, key):
	"Decrypt a string"
	s = base64.b64decode(s)
	iv = s[:AES.block_size]
	cipher = AES.new(key, AES.MODE_CBC, iv)
	return _unpad(cipher.decrypt(s[AES.block_size:])).decode("utf-8")

def _pad(s):
	return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)

def _unpad(s):
	return s[:-ord(s[len(s) - 1:])]
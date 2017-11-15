#!/usr/bin/env python
# -*- coding: utf-8 -*-

import AlfonsRSA
import AlfonsAES
import Alfons
import random
import base64
import string

def encrypt(s, recv):
	"Encrypt a string for the receiver"
	aesKey = "".join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(32))
	out = AlfonsAES.encrypt(s, aesKey)
	out += "." + AlfonsRSA.encrypt(aesKey, recv)
	out += "." + AlfonsRSA.sign(s)
	return out

def decrypt(s):
	"Decrypt a string encrypted with your public key"
	s = s.split(".")
	aesKey = AlfonsRSA.decrypt(s[1], Alfons.info["private_key"])
	dec = AlfonsAES.decrypt(s[0], aesKey) 
	return (dec, s[2])

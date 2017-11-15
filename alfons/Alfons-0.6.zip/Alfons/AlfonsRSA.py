#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import os.path
import Alfons
import base64

def genereteKey():
	"Generate a private key"
	randomGenerator = Random.new().read
	privateKey = RSA.generate(2048, randomGenerator)
	
	Alfons.info["private_key"] = privateKey

	return privateKey

def importKey(key):
	"Convert a key from string to object"
	return RSA.importKey(key)

def getPublicKey(privateKey):
	"Get the public key from a private key"
	return privateKey.publickey()

def encrypt(message, pubKey):
	"Encrypt a string with a public key"
	cipher = PKCS1_OAEP.new(pubKey)
	return base64.b64encode(cipher.encrypt(message))

def decrypt(ciphertext, privKey):
	"Decrypt a string with a private key"
	cipher = PKCS1_OAEP.new(privKey)
	return cipher.decrypt(base64.b64decode(ciphertext))

def sign(message):
	"Sign a string with a private key"
	signer = PKCS1_v1_5.new(Alfons.info["private_key"])
	auth = SHA256.new()
	auth.update(message)
	return base64.b64encode(signer.sign(auth))

def verify(message, signature, pubKey):
	"Verify a string with a public key"
	signer = PKCS1_v1_5.new(pubKey)
	auth = SHA256.new()
	auth.update(message)
	return signer.verify(auth, base64.b64decode(signature))

def getKey():
	"Get or generate and setup the keys"
	if not os.path.isfile("key.pem"):
		privKey = genereteKey()
		
		with open("key.pem", "w") as keyFile:
			keyFile.write(privKey.exportKey())

	with open("key.pem", "r") as keyFile:
		Alfons.info["private_key"] = importKey(keyFile.read())
	
	pub = Alfons.info["private_key"].publickey()
	Alfons.info["public_key"] = pub
	Alfons.info["device_id"] = pub.exportKey()[71:112].replace("\n", "")
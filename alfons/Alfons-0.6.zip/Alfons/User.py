#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import json
import Alfons
import time

TOKEN_TIME_LENGTH = 3600

def verify(token):
	(head, body, signature) = token.split(".")

	payload = json.loads(base64.b64decode(body))

	# Verify expired
	if payload["exp"] <= time.time():
		return False

	# Verify the signature
	signValid = Alfons.AlfonsRSA.verify(head + "." + body, signature, Alfons.info["alfons_key"])

	if not signValid:
		return False

	return payload

def verifyAuth(auth):
	auth = auth.split(" ")
	if not auth[0] == "Bearer":
		return False
	else:
		return verify(auth[1])

def generateToken(username):
	head = {}
	body = {}

	head["typ"] = "JWT"
	head["alg"] = "RS256"

	body["sub"] = username
	body["username"] = username
	
	body["iat"] = time.time()
	body["exp"] = time.time() + TOKEN_TIME_LENGTH
	body["iss"] = Alfons.info["device_id"]

	headEncoded = base64.b64encode(json.dumps(head))
	bodyEncoded = base64.b64encode(json.dumps(body))

	sign = Alfons.AlfonsRSA.sign(headEncoded  + "." + bodyEncoded)

	return headEncoded + "." + bodyEncoded + "." + sign

def requirePermissions(permissions, request):
	if "permissions" in request.headers:
		namespace = request.headers["destination"] + ":"
		userPermissions = request.headers["permissions"].replace(namespace, "").split(" ")
		
		for p in permissions:
			if not p in userPermissions:
				return False
		return True
	else:
		return False
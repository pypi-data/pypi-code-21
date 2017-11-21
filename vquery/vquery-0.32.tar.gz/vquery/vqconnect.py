# vqconnect.py

'''
Interface for clean connection-to and disconnection-from a vCenter server
'''

#from __future__ import print_function
from builtins import input
from pyVim.connect import Disconnect, SmartConnect
from sys import exit
from .vqconfig import getconfig
import ssl
import requests
import atexit
import getpass
from time import clock

START = clock()

# Disabling urllib3 ssl warnings
requests.packages.urllib3.disable_warnings()

# Disabling SSL certificate verification
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

def connect(host, username, password, port, debug, sslContext=context):
	try:
		if debug:
			print("INFO: Attempting to connect.")
		si = SmartConnect(host=host, user=username, pwd=password, port=port, sslContext=context)
	except IOError as e:
		print("I/O error({0}): {1}".format(e.errno, e.strerror))
		exit()
	except:
		print("ERROR: Unable to connect.")
		exit()
	else:
		if debug:
			print("INFO: Successfully connected to %s" % host)
		return si

def disconnect(si, debug):
	try:
		Disconnect(si)
	except:
		print("WARNING: Failed to disconnect.")
	else:
		if debug: 
			print("INFO: Disconnected.")
			end = clock()
			total = end - START
			print("INFO: Completed in {0} seconds.".format(total))

def setup_connection(server, username, password, config_id, debug):
	# Set up connection
	config = getconfig(config_id)

	# Override config params with command line input.
	if server is not None:
		config["server"] = server
	if username is not None:
		config["username"] = username
	if password is not None:
		config["password"] = password

	# Supply any missing credentials.
	if config["server"] is None:
		config["server"] = input("Host/IP: ")
	if config["username"] is None:
		config["username"] = input("Username: ")
	if config["password"] is None:
		config["password"] = getpass.getpass()  
	si = connect(config["server"], config["username"], config["password"], config["port"], debug)
	atexit.register(disconnect, si, debug)

	return si


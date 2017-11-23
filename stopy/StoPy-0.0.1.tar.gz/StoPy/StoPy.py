#!/usr/local/bin/python
import requests
import json

class StoPy:
#constructor
	def __init__(self, server, port, api_key, protocol="https", version = "v1"):
		self.server = server
		self.port = port
		self.api_key = api_key
		self.headers = self.createHeaders( self.api_key )
		self.protocol = protocol
		self.connected = False
		while self.connected != True:
			try:
				self.uri = str(self.protocol) + "://" + str(self.server) + ":" + str(self.port) + "/"
				r = requests.get(url = self.uri, headers = self.headers )
				if r.status_code != 200:
					print( self.handleError( "Error connecting to " + str( self.uri ) ) )
					quit()
				else:
					self.connected = True
			except:
				print( self.handleError( "Error connecting to " + str( self.uri ) ) )
				if self.protocol == "https":
					print( "Falling back to http" )
					self.protocol = "http"
				else:
					quit()

		self.uri = self.uri + str( version )

#create functionality
	#save data
	def insert(self, collection, owner, content, api_key=False):
		headers = self.customHeaders( api_key )
		uri = self.uri + "/insert"
		data = { 'data': content ,'owner': owner, 'collection': collection }
		try:
			r = requests.post( url=uri, headers=headers, json=data )
			return json.loads(r.text)
		except:
			return self.handleError("Error Inserting")
#read functionality	
	#read data descending
	def readLatest(self, collection, owner, limit=False, api_key=False ):
		headers = self.customHeaders( api_key )
		uri = self.uri + "/" + str(collection) + "/last/" + str(owner) + "/"
		if limit != False:
			uri = uri + str(limit)
		return self.getData(uri, headers, "Error Fetching Last Data")

	#read data descending -- paginated
	def readLatestByPage(self, collection, owner, items_per_page=1, page_number=0, api_key=False ):
		headers = self.customHeaders( api_key )
		uri = self.uri + "/" + str(collection) + "/last/" + str(owner) + "/" + str(items_per_page) + "/page/" + str(page_number)
		return self.getData(uri, headers, "Error Fetching Page Data" )

	#read data ascending
	def readOldest(self, collection, owner, limit=False, api_key=False ):
		headers = self.customHeaders( api_key )
		uri = self.uri + "/" + str(collection) + "/first/" + str(owner) + "/"
		if limit != False:
			uri = uri + str(limit)
		return self.getData(uri, headers,  "Error Fetching Last Data" )

	#read data ascending -- paginated
	def readOldestByPage(self, collection, owner, items_per_page=1, page_number=0, api_key=False ):
		headers = self.customHeaders( api_key )
		uri = self.uri + "/" + str(collection) + "/first/" + str(owner) + "/" + str(items_per_page) + "/page/" + str(page_number)
		print( uri )
		return self.getData(uri, headers,  "Error Fetching Page Data" )

	#read data using hashData
	def readHash(self, collection, hashData, api_key=False ):
		headers = self.customHeaders( api_key )
		uri = self.uri + "/" + str(collection) + "/hash/" + str(hashData) + "/"
		return self.getData(uri, headers, "Error Fetching Hash Data" )

	#read total count of collection (by owner)
	def getCount(self, collection, owner=False, api_key=False):
		headers = self.customHeaders( api_key )
		uri = self.uri + "/" + str(collection) + "/count/"
		if owner != False: 
			uri = uri + str(owner) + "/"
		return self.getData(uri, headers, "Error Fetching Count" )

#delete functionality
	#delete individual data by hash
	def deleteByHash(self, collection, hashData, api_key=False):
		headers = self.customHeaders( api_key )
		uri = self.uri + "/delete"
		data = { 'collection': collection, 'hashData': hashData }
		try:
			r = requests.delete( url=uri, headers=headers, json=data )
			return json.loads(r.text)
		except:
			return self.handleError("Error Deleting")

	#delete all data by owner (save is a count of saved data)
	def deleteByOwner(self, collection, owner, save = False, api_key = False):
		headers = self.customHeaders( api_key )
		uri = self.uri + "/delete"
		data = { 'collection': collection, 'owner': owner }
		if save != False and int(save) > 0:
			data['skip'] = int(save)
		try:
			r = requests.delete( url=uri, headers=headers, json=data )
			return json.loads(r.text)
		except:
			return self.handleError("Error Deleting")

#helpers
	#overwrite system headers
	def customHeaders(self, api_key=False ):
		if( api_key != False ):
			return self.createHeaders( api_key )
		else:
			return self.headers

	#standard format for request headers
	def createHeaders(self, api_key ):
		return {
			'Content-Type': 'application/json',
			'authorization': 'Basic api_key='+str(api_key)
		}

	#generic error handler
	def handleError(self, error ):
		return { 'errors': [ "[CLIENT] " + str(error) ] }

	#generic get request format
	def getData(self, uri, headers, error):
		try:
			r = requests.get( url=uri, headers=headers )
			return json.loads(r.text)
		except:
			return self.handleError( error )

#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2016 MasterCard International Incorporated
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list of
# conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of
# conditions and the following disclaimer in the documentation and/or other materials
# provided with the distribution.
# Neither the name of the MasterCard International Incorporated nor the names of its
# contributors may be used to endorse or promote products derived from this software
# without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#


from mastercardapicore import BaseObject
from mastercardapicore import RequestMap
from mastercardapicore import OperationConfig
from mastercardapicore import OperationMetadata
from resourceconfig import ResourceConfig

class Card(BaseObject):
	"""
	
	"""

	__config = {
		
		"561b77c7-daff-4cca-843d-4a41894adf0d" : OperationConfig("/issuer/v1/card", "create", [], []),
		
		"9b6b90fe-be4b-4fb8-8e30-56386107ada5" : OperationConfig("/issuer/v1/card/{uuid}", "read", [], []),
		
		"d30bd84a-e305-4e4a-bdd0-78394b395465" : OperationConfig("/issuer/v1/card/uuid", "create", [], []),
		
		"304c0e99-cca1-43af-b56e-963dcf8ba30a" : OperationConfig("/issuer/v1/card/{uuid}", "delete", [], []),
		
		"fc344c9e-917e-4e3a-a10b-a6b5744eba15" : OperationConfig("/issuer/v1/card/{uuid}", "create", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUID)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative())


	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type Card

		@param Dict mapObj, containing the required parameters to create a new object
		@return Card of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("561b77c7-daff-4cca-843d-4a41894adf0d", Card(mapObj))










	@classmethod
	def retrievePan(cls,id,criteria=None):
		"""
		Returns objects of type Card by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of Card
		@raise ApiException: raised an exception from the response status
		"""
		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if criteria:
			if (isinstance(criteria,RequestMap)):
				mapObj.setAll(criteria.getObject())
			else:
				mapObj.setAll(criteria)

		return BaseObject.execute("9b6b90fe-be4b-4fb8-8e30-56386107ada5", Card(mapObj))


	@classmethod
	def read(cls,mapObj):
		"""
		Creates object of type Card

		@param Dict mapObj, containing the required parameters to create a new object
		@return Card of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("d30bd84a-e305-4e4a-bdd0-78394b395465", Card(mapObj))









	@classmethod
	def deleteById(cls,id,map=None):
		"""
		Delete object of type Card by id

		@param str id
		@return Card of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""

		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if map:
			if (isinstance(map,RequestMap)):
				mapObj.setAll(map.getObject())
			else:
				mapObj.setAll(map)

		return BaseObject.execute("304c0e99-cca1-43af-b56e-963dcf8ba30a", Card(mapObj))

	def delete(self):
		"""
		Delete object of type Card

		@return Card of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("304c0e99-cca1-43af-b56e-963dcf8ba30a", self)



	@classmethod
	def update(cls,mapObj):
		"""
		Creates object of type Card

		@param Dict mapObj, containing the required parameters to create a new object
		@return Card of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("fc344c9e-917e-4e3a-a10b-a6b5744eba15", Card(mapObj))








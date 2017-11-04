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
		
		"899c18df-e13c-4c46-8cd0-6162b62c995a" : OperationConfig("/issuer/spendcontrols/v1/card", "create", [], []),
		
		"44e006ca-3ecc-41ef-8f9c-fad74593016e" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}", "read", [], []),
		
		"8ff885e2-efe6-4ee9-bb27-60a5315ac9a4" : OperationConfig("/issuer/spendcontrols/v1/card/uuid", "create", [], []),
		
		"5ee846b5-407e-4003-b746-ebc13d2e2e72" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}", "delete", [], []),
		
		"3fa368cd-a040-479f-a5fd-5354ff004029" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}", "create", [], []),
		
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
		return BaseObject.execute("899c18df-e13c-4c46-8cd0-6162b62c995a", Card(mapObj))










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

		return BaseObject.execute("44e006ca-3ecc-41ef-8f9c-fad74593016e", Card(mapObj))


	@classmethod
	def read(cls,mapObj):
		"""
		Creates object of type Card

		@param Dict mapObj, containing the required parameters to create a new object
		@return Card of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("8ff885e2-efe6-4ee9-bb27-60a5315ac9a4", Card(mapObj))









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

		return BaseObject.execute("5ee846b5-407e-4003-b746-ebc13d2e2e72", Card(mapObj))

	def delete(self):
		"""
		Delete object of type Card

		@return Card of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("5ee846b5-407e-4003-b746-ebc13d2e2e72", self)



	@classmethod
	def update(cls,mapObj):
		"""
		Creates object of type Card

		@param Dict mapObj, containing the required parameters to create a new object
		@return Card of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("3fa368cd-a040-479f-a5fd-5354ff004029", Card(mapObj))








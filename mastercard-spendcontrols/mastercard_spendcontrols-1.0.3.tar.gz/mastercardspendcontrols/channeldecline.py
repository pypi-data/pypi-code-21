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

class Channeldecline(BaseObject):
	"""
	
	"""

	__config = {
		
		"511b1d58-d921-4d2a-baa6-40b89fd0aa0e" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}/controls/declines/channels", "delete", [], []),
		
		"e5b0a0e0-ae8a-4651-98ac-f9f679deddd2" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}/controls/declines/channels", "query", [], []),
		
		"fa3be753-56a1-4db6-a86a-552939ba4f1c" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}/controls/declines/channels", "create", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUID)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative())





	@classmethod
	def deleteById(cls,id,map=None):
		"""
		Delete object of type Channeldecline by id

		@param str id
		@return Channeldecline of the response of the deleted instance.
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

		return BaseObject.execute("511b1d58-d921-4d2a-baa6-40b89fd0aa0e", Channeldecline(mapObj))

	def delete(self):
		"""
		Delete object of type Channeldecline

		@return Channeldecline of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("511b1d58-d921-4d2a-baa6-40b89fd0aa0e", self)








	@classmethod
	def query(cls,criteria):
		"""
		Query objects of type Channeldecline by id and optional criteria
		@param type criteria
		@return Channeldecline object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("e5b0a0e0-ae8a-4651-98ac-f9f679deddd2", Channeldecline(criteria))

	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type Channeldecline

		@param Dict mapObj, containing the required parameters to create a new object
		@return Channeldecline of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("fa3be753-56a1-4db6-a86a-552939ba4f1c", Channeldecline(mapObj))








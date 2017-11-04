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

class BudgetalertwithbudgetId(BaseObject):
	"""
	
	"""

	__config = {
		
		"13386d65-224b-465d-9a3d-68f9578325c6" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}/controls/alerts/budgets/{budgetId}", "delete", [], []),
		
		"c9c2369a-b067-4866-a0f9-c9bbe09ceb1d" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}/controls/alerts/budgets/{budgetId}", "read", [], []),
		
		"2060928d-a286-4ed1-ac52-356502b4bba0" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}/controls/alerts/budgets/{budgetId}", "create", [], []),
		
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
		Delete object of type BudgetalertwithbudgetId by id

		@param str id
		@return BudgetalertwithbudgetId of the response of the deleted instance.
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

		return BaseObject.execute("13386d65-224b-465d-9a3d-68f9578325c6", BudgetalertwithbudgetId(mapObj))

	def delete(self):
		"""
		Delete object of type BudgetalertwithbudgetId

		@return BudgetalertwithbudgetId of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("13386d65-224b-465d-9a3d-68f9578325c6", self)







	@classmethod
	def read(cls,id,criteria=None):
		"""
		Returns objects of type BudgetalertwithbudgetId by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of BudgetalertwithbudgetId
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

		return BaseObject.execute("c9c2369a-b067-4866-a0f9-c9bbe09ceb1d", BudgetalertwithbudgetId(mapObj))


	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type BudgetalertwithbudgetId

		@param Dict mapObj, containing the required parameters to create a new object
		@return BudgetalertwithbudgetId of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("2060928d-a286-4ed1-ac52-356502b4bba0", BudgetalertwithbudgetId(mapObj))








# -*- coding: utf-8 -*-
import inspect
from .models import ActionsModel
from .errors import error_handler
from .services import SmsService, ServiceStorage
from .activations import SmsActivation
import json


class GetBalance(ActionsModel):
	_name = 'getBalance'

	def __init__(self):
		super().__init__(inspect.currentframe())

	@error_handler
	def __response_processing(self, response):
		return int(response.split(':')[1])

	def request(self, wrapper):
		"""
		:rtype: int
		"""
		response = wrapper.request(self)
		return self.__response_processing(response)


class GetFreeSlots(ActionsModel):
	_name = 'getNumbersStatus'

	def __init__(self, country=None):
		super().__init__(inspect.currentframe())

	@error_handler
	def __response_processing(self, response):
		service_list = json.loads(response)

		service_obj = SmsService()
		for name, short_name in ServiceStorage.names.items():
			getattr(service_obj, name).count = int(service_list[short_name])
		return service_obj

	def request(self, wrapper):
		"""
		:rtype: smsactivateru.services.SmsService
		"""
		response = wrapper.request(self)
		return self.__response_processing(response)


class GetNumber(ActionsModel):
	_name = 'getNumber'

	def __init__(self, service, country=None, operator=None, forward=False, ref=None):
		service = getattr(service, '__service_short_name').split('_')[0]
		forward = int(forward)
		super().__init__(inspect.currentframe())

	@error_handler
	def __response_processing(self, response):
		data = response.split(':')
		return SmsActivation(data[1], data[2])

	def request(self, wrapper):
		"""
		:rtype: smsactivateru.activations.SmsActivation
		"""
		response = wrapper.request(self)
		return self.__response_processing(response)


class GetStatus(ActionsModel):
	_name = 'getStatus'

	def __init__(self, id):
		super().__init__(inspect.currentframe())

	@error_handler
	def __response_processing(self, response):
		data = {'status': response, 'code': None}
		if ':' in response:
			data['status'] = response.split(':')[0]
			data['code'] = response.split(':')[1]
		return data

	def request(self, wrapper):
		"""
		:rtype: dict
		"""
		response = wrapper.request(self)
		return self.__response_processing(response)


class SetStatus(ActionsModel):
	_name = 'setStatus'

	def __init__(self, id, status, forward=False):
		forward = int(forward)
		super().__init__(inspect.currentframe())

	@error_handler
	def __response_processing(self, response):
		data = {'status': response}
		return data

	def request(self, wrapper):
		"""
		:rtype: dict
		"""
		response = wrapper.request(self)
		return self.__response_processing(response)

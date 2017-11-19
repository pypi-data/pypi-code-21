import requests
import json

from datetime import datetime

from seven23lib.model.currency import currency
from seven23lib.model.account import account
from seven23lib.model.category import category
from seven23lib.model.operation import operation

API_URL = 'https://seven23.io/api/v1/'
API_ACCOUNTS = 'accounts'
API_CATEGORIES = 'categories'
API_CURRENCIES = 'currencies'
API_OPERATIONS = 'debitscredits'
HEADERS = {'Accept': 'application/json; version=1.0; version=1.0'}


class seven23(object):
	def __init__(self, token):
		self.token = token
		HEADERS['Authorization'] = ' '.join(['Token', token])

	def accounts(self, id=None):
		if id:
			url = '/'.join([API_URL + API_ACCOUNTS, str(id)])
			json = self.exec_get_req(url)
			if json:
				return [account(account(id=json['id'], name=json['name'], create=json['create'], public=json['public'],
				                        currency_id=json['currency'], archived=json['archived']))]
		else:
			url = API_URL + API_ACCOUNTS
			json = self.exec_get_req(url)
			if json:
				accounts = []
				for t in json:
					accounts.append(account(id=t['id'], name=t['name'], create=t['create'], public=t['public'],
					                        currency_id=t['currency'], archived=t['archived']))
				return accounts
		return None

	def currencies(self, id=None):
		if id:
			url = '/'.join([API_URL + API_CURRENCIES, str(id)])
			json = self.exec_get_req(url)
			if json:
				return [currency(id=json['id'], name=json['name'], sign=json['sign'], space=json['space'],
				                 after_amount=json['after_amount'])]
		else:
			url = API_URL + API_CURRENCIES
			json = self.exec_get_req(url)
			if json:
				currencies = []
				for t in json:
					currencies.append(currency(id=t['id'], name=t['name'], sign=t['sign'], space=t['space'],
					                           after_amount=t['after_amount']))
				return currencies
		return None

	def categories(self, id=None):
		if id:
			url = '/'.join([API_URL + API_CATEGORIES, str(id)])
			json = self.exec_get_req(url)
			if json:
				return [
					category(id=json['id'], account=json['account'], name=json['name'], description=json['description'],
					         parent=json['parent'], selectable=json['selectable'], active=json['active'])]
		else:
			url = API_URL + API_CATEGORIES
			json = self.exec_get_req(url)
			if json:
				categories = []
				for t in json:
					categories.append(category(id=t['id'], account=t['account'], name=t['name'],
					                           description=t['description'],
					                           parent=t['parent'], selectable=t['selectable'],
					                           active=t['active']))
				return categories
		return None

	def operations(self, id=None):
		if id:
			url = '/'.join([API_URL + API_OPERATIONS, str(id)])
			json = self.exec_get_req(url)
			if json:
				return [
					operation(id=json['id'], account=json['account'], name=json['name'],
					          local_amount=json['local_amount'],
					          local_currency=json['local_currency'], date=json['date'], active=json['active'],
					          category=json['category'], last_edited=json['last_edited'])]
		else:
			url = API_URL + API_OPERATIONS
			json = self.exec_get_req(url)
			if json:
				operations = []
				for t in json:
					operations.append(operation(id=t['id'], account=t['account'], name=t['name'],
					                            local_amount=t['local_amount'],
					                            local_currency=t['local_currency'], date=t['date'],
					                            active=t['active'],
					                            category=t['category'], last_edited=t['last_edited']))
				return operations
		return None

	def add_operation(self, op):
		assert type(op) is operation, 'Attribut must be operation type'
		response = requests.post(url=API_URL + API_OPERATIONS, headers=HEADERS, data=op.json_data())
		if response.status_code != 201:
			raise Exception(response.content)
		return None

	def add_category(self, cat):
		assert type(cat) is category, 'Attribut must be category type'
		response = requests.post(url=API_URL + API_CATEGORIES, headers=HEADERS, data=cat.json_data())
		if response.status_code != 201:
			raise Exception(response.content)
		return None

	@staticmethod
	def exec_get_req(url):
		response = requests.get(url, headers=HEADERS)
		if response.status_code == 200:
			return json.loads(response.content)
		return None
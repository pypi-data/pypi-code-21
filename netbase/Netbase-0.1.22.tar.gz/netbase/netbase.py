#!/usr/bin/env PYTHONIOENCODING="utf-8" python
# -*- coding: utf-8 -*-
import locale
import os
import re
import os.path
import dill as pickle  # BEST! no more Can't pickle <function
import json
import codecs  # codecs.open(file, "r", "utf-8")

try:  # pathetic python3 !
	from urllib2 import urlopen
	from urllib import urlretrieve
except ImportError:
	from urllib.request import urlopen, urlretrieve  # library HELL

from extensions import *  # for functions
import extensions
from os.path import expanduser

api = "http://netbase.pannous.com/json/all/"
api_list = "http://netbase.pannous.com/json/short/"
api_all = "http://netbase.pannous.com/json/query/all/"

def setGerman():
	api = "http://de.netbase.pannous.com/json/all/"
	api_list = "http://de.netbase.pannous.com/json/short/"
	api_all = "http://de.netbase.pannous.com/json/query/all/"

if "de" in locale.getdefaultlocale() or os.environ['NETBASE_LANGUAGE']:
	setGerman()

# api = "http://localhost:8181/json/all/"
api_html = api.replace("json", "html")
api_limit = 1000
caches_netbase_ = expanduser("~/Library/Caches/netbase/")
abstracts_netbase = expanduser("~/Library/Caches/netbase/all/")


def cached_names():
	return []
	# cached_files = ls(
	# 	"~/Library/Caches/netbase/").map(lambda x: x.replace(".json", "").replace(" ", "_"))
	# cached_files = cached_files.filter(lambda x: not is_number_string(x))
	# return list(set(cached_files + cache.keys() + ['OKAH']))


if not os.path.exists(abstracts_netbase):
	os.makedirs(abstracts_netbase)  # mkdir


def download(url):  # to memory
	return urlopen(url).read()


def spo(edge):
	subject, predicate, object = edge['subject'], edge['predicate'], edge['object']
	return subject, predicate, object


def spo_ids(edge):
	sid, pid, oid = edge['sid'], edge['pid'], edge['oid']
	return sid, pid, oid


class Edges(extensions.xlist):
	def show(self):
		for edge in self:
			sid, pid, oid = edge['sid'], edge['pid'], edge['oid']
			subject, predicate, object = edge['subject'], edge['predicate'], edge['object']
			print("%d %d  %d  %s  %s  %s" %
					(sid, pid, oid, subject, predicate, object))


def get(id, name=0):
	return net.get(id or name)

class SelectProxy:
	def __init__(self, node):
		self.node=node

	def __getattr__(self, item):
		return self.node.getProperty(item)


class Node:
	def __init__(self, *args, **kwargs):
		if not kwargs:
			kwargs = args[0]
		self.loaded = False
		self.id = kwargs['id']
		self.name = kwargs['name']
		self.is_abstract= 'kind' in kwargs and kwargs['kind'] == -102
		self.topic = 'topic' in kwargs and kwargs['topic'] or None
		if 'description' in kwargs:
			self.description = kwargs['description']
		else:
			self.description = ""
		if 'statementCount' in kwargs:
			self.count = kwargs['statementCount']
		if 'statements' in kwargs:
			self.edges = Edges(kwargs['statements'])
			self.loaded = True
		# self.statements = Edges(args['statements'])

	def print_csv(self):
		self.edges.show()

	def show_compact(self):
		print("%s{id:%d, topic:%s, edges=[" % (self.name, self.id, self.topic))
		for edge in self.edges:
			subject, predicate, object = edge['subject'], edge['predicate'], edge['object']
			predicate= predicate.replace(" ","_")
			if subject == self.name or edge['sid'] == self.id:
				print(" %s:%s," % (predicate, object))
			else:
				in_predicate = "_of" in predicate or "_after" in predicate or "_by" in predicate
				in_predicate = in_predicate or "_in" in predicate or "_von" in predicate
				if in_predicate:
					print(" %s:%s," % (predicate, subject))
				else:
					print(" %s_of:%s," % (predicate, subject))
		print("]}")

	def __dir__(self):
		return map(lambda x: x.replace(" ", "_"), self._predicates())

	def __str__(self):
		if self.topic:
			return "%s(%s)%s" % (self.name, self.topic, self.is_abstract and "*" or "")
		if self.name and self.id:
			return "%s(%d)%s" % (self.name, self.id, self.is_abstract and "*" or "")
		return self.name or self.id

	def __repr__(self):
		return self._short()
		# return self.name or self.id
	# return self.name + "_" + str(self.id)
	# if self.type:
	# 	return self.name + ":" + self.type.name
	# return self.name + ":" + self.type.name

	def _short(self):
		if self.topic:
			return "{name:'%s', id:%d, topic:'%s'}" % (self.name, self.id, self.topic)
		if not self.description:
			return "{name:'%s', id:%s%d}" % (self.name, self.is_abstract and "+" or "", self.id)
		return "{name:'%s', id:%d, description:'%s'}" % (self.name, self.id, self.description)

	def _json(self):
		return "{name:'%s', id:%d, description:'%s', statements:%s}" % (self.name, self.id, self.description, self.edges)

	def open(self):
		if "http" in self.name:
			os.system("open " + self.name)
		else:
			os.system("open " + api_html + self.name)

	def show(self):
		if "http" in self.name:
			os.system("open " + self.name)
		print(self.show_compact())
		# print(self._json())

	def _predicates(self):
		alles = []
		for e in self.edges:
			predicate = e['predicate']
			if not predicate in alles:
				alles.append(predicate)
		return xlist(set(alles))

	def _print_edges(self):
		for e in self.edges:
			if e['sid'] == self.id:
				print(" %s:%s" % (e['predicate'], e['object']))
			else:
				if " of" in e['predicate']:
					print(" %s: %s" %
							(e['predicate'].replace(" of", ""), e['subject']))
				else:
					print(" %s of: %s" % (e['predicate'], e['subject']))
		return self.edges

	def _map(self):
		map = {}
		for e in self.edges:
			if e['sid'] == self.id:
				map[e['predicate']] = e['object']
			else:
				if " of" in e['predicate']:
					map[e['predicate'].replace(" of", "")] = e['subject']
				else:
					map[e['predicate'] + " of"] = e['subject']
		return map

	def _load_edges(self):
		if self.loaded:
			return self.edges
		file = caches_netbase_ + str(self.id) + ".json"
		if not os.path.exists(file):
			url = api + str(self.id)
			print(url)
			urlretrieve(url, file)
		# data = open(file,'rb').read()
		data = codecs.open(file, "r", "utf-8").read()
		if py2: data=data.decode('utf8', 'ignore')
		data = json.loads(data)  # FUCK PY3 !!!
		# data = json.loads(str(data, "UTF8"))  # FUCK PY3 !!!
		result = data['results'][0]
		self.edges = Edges(result['statements'])
		self.loaded = True
		return self.edges

	def fetchProperties(self,property):
		return download(api_all+self.name+"."+property)

	def getProperties(self, property, strict=False):
		# if(self.statementCount>api_limit):
		# 	return self.fetchProperties(property)
		found = []
		for e in self.edges:
			predicate = e['predicate'].lower()
			if predicate == property or not strict and (property in predicate):
				if e['sid'] == self.id:
					found.append(Node(name=e['object'], id=e['oid']))
				elif not strict:
					found.append(Node(name=e['subject'], id=e['sid']))
			if not strict and property in e['object']:
				found.append(Node(name=e['object'], id=e['sid']))
		if property == 'instance':
			found.extend(self.getProperties('type', strict=True))
		try:
			if self in found:
				found.remove(self)
		except Exception as ex:
			pass
		if not found:
			return xlist([])
		return xlist(found)

	# print(found)
	# return set(found)

	def getProperty(self, property, strict=False):
		if property == 'predicates':
			return self._predicates()
		if property == 'net':
			return net
		if property == 'select':
			return SelectProxy(self)
		if property == 'edges':
			return self._load_edges()
		if property == 'all':
			return net._all(self.id, True, False)
		if property == 'list':
			return self._map()
		if property == 'count':
			return self.count or self.edges.count()
		if property == 'json':
			return self._json()
		if property == 'short':
			return self._short()
		if property == 'descriptions':
			return self.description

		property = property.replace("_", " ").lower()
		# print("getProperty " + self.name+"."+ property)
		for e in self.edges:
			predicate = e['predicate'].lower()
			if predicate == property:
				if e['sid'] == self.id:
					return Node(name=e['object'], id=e['oid'])
				elif not strict:
					return Node(name=e['subject'], id=e['sid'])
		if strict:
			return []#None
		for e in self.edges:
			if property in e['predicate'].lower():
				if e['oid'] == self.id:
					return Node(name=e['subject'], id=e['sid'])
				else:
					return Node(name=e['object'], id=e['oid'])
			if not strict and property in e['object']:
				return Node(name=e['object'], id=e['sid'])
		if property == 'parent':
			return self.getProperty('superclass', strict=True) or self.getProperty('type', strict=True)
		if is_plural(property):
			return self.getProperties(singular(property))

	def __getattr__(self, name):
		# print("get " + name)
		return self.getProperty(name)


# Node.show_edges = Node.print_csv
# Node._display = Node.show_compact
# Node._render = Node.show_compact
# Node._print = Node.show_compact


def is_plural(name):
	return name.endswith("s")  # todo


def singular(name):
	if name.endswith("ies"):
		return re.sub(r"ies$", "y", name)
	# return name.replace(r"ies$", "y")  # WTF PYTHON !
	if name.endswith("ses"):
		return re.sub(r"ses$", "s", name)
	if name.endswith("s"):
		return re.sub(r"s$", "", name)  # todo
	return name


class Netbase:
	def __init__(self):
		self.cache = {}
		self.caches = {}

	def types(self, name):
		return self._all(name, instances=False) # select(kind=...)

	# @classmethod
	def _all(self, name, instances=False, deep=False, reload=False):
		if isinstance(name, int):
			n=self.get(name)
			if not n.is_abstract: return n
			else: name = str(name)  # id
		if is_plural(name):
			return self._all(singular(name))
		if name in self.caches:
			return self.caches[name]
		file = abstracts_netbase + name + ".json"
		if reload or not os.path.exists(file):
			print(api + name)
			urlretrieve(api_all + name, file)
		data = codecs.open(file, "r", "utf-8", errors='ignore').read()
		# data = open(file,'rb').read()
		if not isinstance(data,unicode):
			data=data.decode("UTF8", 'ignore')
		# FUCK PY3 !!!  'str' object has no attribute 'decode'
		# 	FUCKING PYTHON MADNESS!!
		# http://stackoverflow.com/questions/5096776/unicode-decodeutf-8-ignore-raising-unicodeencodeerror#5096928
		try:
			# data = json.loads(data)
			data = json.loads(data)
		except Exception as ex:
			print(ex)
			os.remove(file)
			# return Node(id=-666, name="ERROR")
		nodes = extensions.xlist()
		for result in data['results']:
			# print(result)
			node = Node(result)
			nodes.append(node)
			if instances:
				nodes.append(self._all(node.id, False, True, reload))
				nodes.append(node.instances)
		self.caches[name] = nodes
		return nodes

	# @classmethod
	def get(self, name, get_the=False):
		# return all(name)[0]
		if isinstance(name, int):
			name = str(name)  # id
		if is_plural(name):
			return self._all(singular(name))
		if name in self.cache:
			node= self.cache[name]
			if not get_the or not node.is_abstract:
				return node
		# print("getThe "+name)

		file = caches_netbase_ + name + ".json"
		if not os.path.exists(file):
			print(api + name)
			urlretrieve(api + name, file)
		# data = open(file, 'rb').read()
		data = codecs.open(file, "rb", "utf-8").read()
		if not isinstance(data, unicode):
			data = data.decode("UTF8", 'ignore')
		try:
			data = json.loads(data)  # FUCK PY3 !!!  'str' object has no attribute 'decode'
		except Exception as ex:
			print(ex)
			pass
		# os.remove(file)
		# noinspection PyTypeChecker
		results = data['results']
		if len(results) == 0:
			return None
		for i in range(len(results)):
			result = results[i] # first == 'the'
			node = Node(result)
			if not get_the or not node.is_abstract: break
		self.cache[name] = node
		return node

	def __dir__(self):
		return cached_names()

	# return [] #  no autosuggest for root

	# def __call__(self):
	# 	return ['__call__ ??']

	def __getattr__(self, name):
		if name == "net":
			return net
		if name == "world":
			return net
		if name == "all":
			return alle  # use net.all.birds OR net.birds.all / net.bird.232.all
		# return self.all(name)
		# print("get "+name)
		return self.get(name)


class Alle(type):
	def __getattr__(self, name):
		return net._all(name, False, False)


class Alles(Netbase):
	def __getattr__(self, name):
		return net._all(name, False, False)



class The:
	def __getattr__(self, name):
		return net.get(name, get_the=True)


if py2:
	class All:
		__metaclass__ = Alle
else:
	try:
		from .alle import All# fuck py3
	except Exception as err:
		from alle import All  # fuck py3

world = net = Netbase()
cache = net.cache
alle = Alles()
the = The()
if py3: All.setNet(net)

def main():
	global net,the
	world = net = Netbase()
	cache = net.cache
	alle = Alles()
	the = The()
	if py3: All.setNet(net)
	# print(the.USA)
	# print(All.hi)
	xs= All.USA
	for bad in xs:
		print (bad.id)
		print (bad.name)
		print (bad._short())
		print (bad.topic)
		print (bad.description)
	# print(xs)
	# print(net.USA.all)
	# print(net.USA.select.country) # select proxy hack
	return

if __name__ == '__main__':
	main()

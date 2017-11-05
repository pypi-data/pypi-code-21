#!/usr/bin/env python
# -*-coding:utf-8-*-
#import sys

import urllib.request
from pymongo import MongoClient
from bs4 import BeautifulSoup
import re
import time

class retrieve(object):
	"This is a crawl"
	def __init__(self,url):
		self.url = url

	def getlinks(self):		
		links = set()
		html = urllib.request.urlopen(self.url,timeout=10)
		bsObj = BeautifulSoup(html,'lxml',from_encoding='gb18030')
		for url in  bsObj.findAll("a",href=re.compile("^(" + self.url + ")\d+.+(html)$")):
			if url.attrs['href'] is not None:	
				if url.attrs['href'] not in links:		
					links.add(url.attrs['href'])
		return links

	def executedb(self,link='',gettitle='',getcontent='',h=0,ins=False):
		client = MongoClient('172.18.0.3',27017)
		db = client.w163
		w163 = db.w163
		if ins:
			data = { "hash":h,"date":time.ctime(),"url":link,"title":gettitle,"content":getcontent}
			w163.insert(data)

	def getcontent(self,link=''):
		links = self.getlinks()		
		for link in links:
			h = hash(link)
			html = urllib.request.urlopen(link,timeout=10)
			bsObj = BeautifulSoup(html,from_encoding='gb18030')
			if bsObj.find(id="epContentLeft") is not None:
				gettitle = bsObj.find(id="epContentLeft").find('h1').getText()
				getcontent = bsObj.find(id="endText").getText()
				self.executedb(link,gettitle,getcontent,h,ins=True)
		
class getw163link(object):
	def __init__(self,url):
		self.url = url
	
	def getalllink(self):
		links = []
		html = urllib.request.urlopen(self.url,timeout=10)
		bsObj = BeautifulSoup(html)
		geta = bsObj.findAll('a',href=re.compile("^(http://)[a-zA-Z]+(.163.com/)$"))
		for link in geta:
			if link.attrs['href'] is not None:
				if link.attrs['href'] not in links:
					links.append(link.attrs['href'])			#get all links like http://news.163.com
		return links


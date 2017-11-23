#!/usr/local/bin/python
import requests
import json
import random
import StoPy

try:
    input = raw_input
except NameError:
    pass
    
print( "Server: " )
server = str(input())
print( "Port: " )
port = int(input())
print( "API Key: " )
api_key = str(input())
x = StoPy( server, port, api_key )

print( "Collection: " )
collection = str(input())
print( "Owner: " )
owner = str(input())

def generateContent(): 
	return { 'score': random.randint(0,100) }


print( "\n\nInserting\n" )
print( x.insert(collection, owner, generateContent()) )
print( x.insert(collection, owner, generateContent()) )
print( x.insert(collection, owner, generateContent()) )
print( x.insert(collection, owner, generateContent()) )
print( x.insert(collection, owner, generateContent()) )

print( "\nOldest\n" )
initial = x.readOldest(collection,owner,1)
print( json.dumps(initial) )

print( "\nNewest\n" )
recent = x.readLatest(collection,owner,1)
print( json.dumps(recent) )

print( "\nCount\n" )
count = x.getCount(collection,owner)
print( json.dumps(count) )

print( "\nOldest Page 2 (2 per page)\n" )
initialPage2 = x.readOldestByPage(collection, owner, items_per_page=2, page_number=1 ) # 0 indexed pages
print( json.dumps(initialPage2) )

print( "\nNewest Page 2 (2 per page)\n" )
recentPage2 = x.readLatestByPage(collection, owner, items_per_page=2, page_number=1 ) # 0 indexed pages
print( json.dumps(recentPage2) )

hashData = recentPage2['data'][0]['hashData']
print( "\nHashData Read " + hashData + "\n" )
hashRead = x.readHash(collection,hashData)
print( json.dumps(hashRead) )

print( "\nHashData Delete\n" )
hashDelete = x.deleteByHash(collection,hashData)
print( json.dumps(hashDelete) )

print( "\nOwner Delete (save most recent 2)\n" )
ownerDelete = x.deleteByOwner(collection,owner,2)
print( json.dumps(ownerDelete) )

print( "\nOldest 2\n" )
initial2 = x.readOldest(collection,owner,2)
print( json.dumps(initial2) )

print( "\nNewest 2\n" )
recent2 = x.readLatest(collection,owner,2)
print( json.dumps(recent2) )

print( "\nOwner Delete (all)\n" )
ownerDeleteAll = x.deleteByOwner(collection,owner)
print( json.dumps(ownerDeleteAll) )

print( "\nCount -- Final Clearance \n" )
count = x.getCount(collection,owner)
print( json.dumps(count) )

print( "\n\n" )

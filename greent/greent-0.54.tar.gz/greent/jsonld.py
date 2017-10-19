from pyld import jsonld
import json
import requests
import sys

json_ld_context = sys.argv[1]
query_string = sys.argv[2]

context = None
with open (json_ld_context, "r") as stream:
    context = json.loads (stream.read ())

r = requests.get (query_string).json ()

text = json.dumps (r)

docs = r['data']

#print ("context: {}".format (context))

expanded = jsonld.expand (docs, { 'expandContext' : context } )
print ("{}".format (json.dumps (expanded, indent=2)))

compacted = jsonld.compact (expanded, context)
print ("{}".format (json.dumps (compacted, indent=2)))

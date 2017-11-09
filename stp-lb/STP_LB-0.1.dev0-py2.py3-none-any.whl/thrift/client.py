#!/usr/bin/env python

import sys
sys.path.append('./gen-py')

from server_communicate import ServerCommunicate

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

try:
  transport = TSocket.TSocket('10.0.2.15', 8988)
  transport = TTransport.TBufferedTransport(transport)
  protocol = TBinaryProtocol.TBinaryProtocol(transport)
  client = ServerCommunicate.Client(protocol)
  transport.open()

  print "client - ping"
  print "server - " + client.ping()
  #print "server - " + client.notify('10.0.2.15', 1000)

  #print "client - say"
  #msg = client.sync_tasks({'h1':'hello', 'h2':'hello2'})
  #print "server - " + msg

  transport.close()

except Thrift.TException, ex:
  print "%s" % (ex.message)

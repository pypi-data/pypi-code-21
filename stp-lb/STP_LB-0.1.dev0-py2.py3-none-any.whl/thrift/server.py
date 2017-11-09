#!/usr/bin/env python
#coding: utf-8

import socket
import sys
sys.path.append('./gen-py')

from server_communicate import ServerCommunicate
from server_communicate.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class ServerCommunicateHandler:
  def ping(self):
    return "pong"

  def sync_tasks(self, tasks_map):
    print(tasks_map)
    return 'ok'

handler = ServerCommunicateHandler()
processor = ServerCommunicate.Processor(handler)
transport = TSocket.TServerSocket("localhost", 9090)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

print "Starting thrift server in python..."
server.serve()
print "done!"

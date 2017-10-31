#!/usr/bin/env python

#*******************************************************************************
#Copyright 2015 Intel Corporation All Rights Reserved.
#
#    The source code contained or described herein and all documents
#    related to the source code ("Material") are owned by Intel Corporation
#    or its suppliers or licensors.  Title to the Material remains with
#    Intel Corporation or its suppliers and licensors.  The Material is
#    protected by worldwide copyright and trade secret laws and treaty
#    provisions.  No part of the Material may be used, copied, reproduced,
#    modified, published, uploaded, posted, transmitted, distributed, or
#    disclosed in any way without Intel's prior express written permission.
#    
#    No license under any patent, copyright, trade secret or other
#    intellectual property right is granted to or conferred upon you by
#    disclosure or delivery of the Materials, either expressly, by
#    implication, inducement, estoppel or otherwise.  Any license under
#    such intellectual property rights must be express and approved by
#    Intel in writing.
#
#*******************************************************************************

import sys, glob, os, random, socket, threading, time, logging

#Configuring the logging
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level = logging.INFO)

#Path to thrift python package should be set either thru I_MPI_THRIFT_PYTHON_LIB or added directly to PYTHONPATH
if not os.environ.get("I_MPI_THRIFT_PYTHON_LIB"):
  logging.warning('I_MPI_THRIFT_PYTHON_LIB is not set. Make sure path to the python thrift module is added to your PYTHONPATH')
else:
  sys.path.insert(0, glob.glob(os.environ["I_MPI_THRIFT_PYTHON_LIB"])[0])

#Importing required thrift modules
from Llama import LlamaAMService, LlamaNotificationService
from Llama.ttypes import *
from thrift.Thrift import TException
from thrift.transport import TTransport, TSocket
from thrift.server import TServer
from thrift.protocol import TBinaryProtocol

#Setting up defaults
callbackServer = None
resourcesAreAllocated = False
portIsDefined = False
hostnames = ''
nodes = []
nodePinning = {}
gl_client = None
gl_am_handle = None
callback_port = 1024
default_llama_port = 15000
default_llama_host = 'localhost'
default_number_of_restarts = 3
MPIisDone = False

number_of_restarts = int(os.environ.get("I_MPI_LLAMA_CLIENT_RESTARTS_NUM") if os.environ.get("I_MPI_LLAMA_CLIENT_RESTARTS_NUM") else default_number_of_restarts)

if number_of_restarts < 1:
  number_of_restarts = 1

#Module argparse happened to be helpless there, as it can potentially match -n or -np with some unknown application arguments, like '-npmin' option of IMB-MPI1
#Using argparse.REMAINDER won't help also, as there can be unknown amount of hydra options
#There is a fix in the latest Python 3.5 for this abbreviation issue, but the decision is
#To iterate over argument list manually to keep things simple
argument_list = sys.argv[1:]
proc_num_index = -1
proc_num = -1
ppn_index = -1
ppn = -1

if '-n' in argument_list:
  proc_num_index = argument_list.index('-n')
if '-np' in argument_list:
  proc_num_index = argument_list.index('-np')
if proc_num_index > -1:
  proc_num = int(argument_list[proc_num_index + 1])
  #removing n/np from argument list to pass to hydra
  argument_list = argument_list[:proc_num_index] + argument_list[proc_num_index+2:]

if '-ppn' in argument_list:
  ppn_index = argument_list.index('-ppn')
if '-perhost' in argument_list:
  ppn_index = argument_list.index('-perhost')
if ppn_index > -1:
  ppn = int(argument_list[ppn_index + 1])
  #removing perhost/ppn from argument list to pass to hydra
  argument_list = argument_list[:ppn_index] + argument_list[ppn_index+2:]

#if n/ppn are not set, consider one node (warn)/one rank per node (info)
if proc_num == -1:
  proc_num = 1
  logging.warning('Total number of MPI ranks is not defined by -n option. Default value (1) will be used')
if ppn == -1:
  ppn = 1
  logging.info('Number of MPI ranks per node is not defined by -ppn option. Default value (1) will be used')

if '--llama-debug' in argument_list:
  logging.getLogger().setLevel(logging.DEBUG)
  argument_list.remove('--llama-debug')

#Calculating the number of nodes required
cont_num = (proc_num + ppn - 1)/ppn

#Passing the rest of options to hydra as is
hydra_options = " ".join(argument_list)

logging.info("hydra options to be used: %s", hydra_options)

#Llama host/port info should be passed explicitely with env vars
if not os.environ.get("I_MPI_LLAMA_HOST"):
  logging.warning('I_MPI_LLAMA_HOST is not set. Default value (%s) will be used', default_llama_host)
if not os.environ.get("I_MPI_LLAMA_PORT"):
  logging.warning('I_MPI_LLAMA_PORT is not set. Default value (%d) will be used', default_llama_port)

thrift_port = int(os.environ.get("I_MPI_LLAMA_PORT") if os.environ.get("I_MPI_LLAMA_PORT") else default_llama_port)
thrift_host = os.environ.get("I_MPI_LLAMA_HOST") if os.environ.get("I_MPI_LLAMA_HOST") else default_llama_host

def generate_client_id():
  #Calculating id for new Llama client
  min_value = 1
  max_value = int("0x7FFFFFFFFFFFFFFF", 16)
  res = random.uniform(min_value, max_value)
  return res

client_id = generate_client_id()

class LlamaClient(object):
  #If client_id is unique, the objects below will also be unique
  clientId = TUniqueId(client_id,1)
  reservationId = TUniqueId(client_id,3)
  am_handle = None
  client = None

  def __init__(self):
    logging.info("Llama Client initialization")

  def Register(self):
    global thrift_port
    global callback_port
    global client_id
    global gl_client
    global gl_am_handle

    for attempt in range(number_of_restarts):
      try:

        # Setting up the transport leyer
        self.transport = TSocket.TSocket(thrift_host, thrift_port)
        self.transport = TTransport.TBufferedTransport(self.transport)
        protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = LlamaAMService.Client(protocol)

        self.transport.open()

        # Register the client at Llama server
        register_request = TLlamaAMRegisterRequest()
        register_request.version = TLlamaServiceVersion.V1
        register_request.client_id = self.clientId
        register_request.notification_callback_service = TNetworkAddress(socket.gethostname(), callback_port)

        logging.debug("Register request: %s", str(register_request))

        res = self.client.Register(register_request)
        self.am_handle = res.am_handle
        gl_client = self.client
        gl_am_handle = self.am_handle

        logging.debug("Register response: %s", str(res))

        return res

      except TException as tx:
        logging.error('Exception: %s', tx.message)
        logging.info('Trying to register one more time..')

        #Redefining ID objects to cover the case when the failure is due to client_id not unique
        client_id = generate_client_id()
        self.clientId = TUniqueId(client_id,1)
        self.reservationId = TUniqueId(client_id,3)

    logging.error('Attempts to register are exhausted. Please check the configuration.')
    return -1

  def RequestResources(self):
    try:
      global nodes, ppn, proc_num
      requested_cpu_num = 0
      gn_request = TLlamaAMGetNodesRequest(TLlamaServiceVersion.V1, self.am_handle)
      for attempt in range(number_of_restarts):
        res = self.client.GetNodes(gn_request)
        if res.status.status_code == TStatusCode.OK:
          break
        logging.debug("GetNodes response: %s", str(res))
        logging.warning("Cannot get cluster inventory. Retrying..")
      if res.status.status_code != TStatusCode.OK:
        logging.error("Attempts to get inventory exhausted. Quitting..")
        quit()

      logging.debug("Cluster inventory: %s", str(res.nodes))
      nodes = res.nodes

      resources = []

      for i in range(cont_num):
        resource = TResource()
        resource.client_resource_id = TUniqueId(client_id,5+i)
        resource.v_cpu_cores = min(ppn, proc_num - requested_cpu_num)
        resource.memory_mb = 0
        resource.askedLocation = nodes[i % len(nodes)]
        resource.enforcement = TLocationEnforcement.DONT_CARE
        resources.append(resource)
        requested_cpu_num += resource.v_cpu_cores

      resource_request = TLlamaAMReservationRequest()
      resource_request.version = TLlamaServiceVersion.V1
      resource_request.am_handle = self.am_handle
      resource_request.user = "MPI"
      resource_request.resources = resources
      resource_request.gang = True
      resource_request.reservation_id = self.reservationId

      logging.debug("Resource request: %s", str(resource_request))
      res = self.client.Reserve(resource_request)
      logging.debug("Resource response: %s", str(res))

    except Exception as tx:
      logging.error('Exception: %s', tx.message)
      return -1

  def ReleaseResources(self):
    try:

      resource_release = TLlamaAMReleaseRequest()
      resource_release.version = TLlamaServiceVersion.V1
      resource_release.am_handle = self.am_handle
      resource_release.reservation_id = self.reservationId

      logging.debug("Resource Release request: %s", str(resource_release))
      res = self.client.Release(resource_release)
      logging.debug("Resource Release response: %s", str(res))

      return res

    except TException as tx:
      logging.error('Exception: %s', tx.message)
      return -1

  def Unregister(self):
    try:

      unregister_request = TLlamaAMUnregisterRequest()
      unregister_request.version = TLlamaServiceVersion.V1
      unregister_request.am_handle = self.am_handle

      logging.debug("Unregister request: %s", str(unregister_request))
      res = self.client.Unregister(unregister_request)
      logging.debug("Unregister response: %s", str(res))

      return res

    except TException as tx:
      logging.error('Exception: %s', tx.message)

    # Close!
    self.transport.close()

"""
LlamaCallbackHandler implementation
"""
class LlamaCallbackHandler(LlamaNotificationService.Iface):

  def __init__(self):
    logging.info("LlamaCallbackHandler initialization")

  def AMNotification(self, request):
    logging.debug("Resources are allocated: %s", str(request))
    global resourcesAreAllocated
    global gl_client

    if not request.allocated_resources:
      if request.heartbeat:
        logging.debug('Heartbeat received')
        #This 'pinging' is basically a workaround for the issue with expiring connection on Llama side
        gn_request = TLlamaAMGetNodesRequest(TLlamaServiceVersion.V1, gl_am_handle)
        gl_client.GetNodes(gn_request)
        pass
    elif len(request.allocated_resources) != cont_num:
      logging.debug('Partial allocation')
    else:
      global hostnames
      hostnames = ''
      for resource in request.allocated_resources:
        if resource.location not in hostnames:
          nodePinning[resource.location] = 0
          hostnames += resource.location
          hostnames += ','
        nodePinning[resource.location] += int(resource.v_cpu_cores)
        logging.debug ('allocated %d cpus on the node %s', resource.v_cpu_cores, resource.location)
      resourcesAreAllocated = True
      hostnames = hostnames[:-1]

    return TLlamaAMNotificationResponse(TStatus(TStatusCode.OK, 0, [""]))

  def NMNotification(self, request):
    """
    Parameters:
     - request
    """
    logging.debug('NMNotification received')
    return TLlamaNMNotificationResponse(status=TStatusCode.OK)

"""
LlamaCallbackService implementation
"""
class LlamaCallbackService(object):

  def __init__(self):
    global callback_port
    global portIsDefined
    handler = LlamaCallbackHandler()
    processor = LlamaNotificationService.Processor(handler)
    while True:
      transport = TSocket.TServerSocket(port=callback_port)
      try:
        transport.listen()
      except:
        logging.info('Port %d is occupied, will try the next one', callback_port)
        callback_port+=1
        continue

      portIsDefined = True
      tfactory = TTransport.TBufferedTransportFactory()
      pfactory = TBinaryProtocol.TBinaryProtocolFactory()
      self.server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

      global callbackServer
      callbackServer = self.server

      logging.info('Starting the callback daemon on port %d', callback_port)
      self.server.serve()

def start_callback_service():
  logging.info('Starting Llama callback service')
  LlamaCallbackService()

def start_MPI():
  global MPIisDone
  command_str = "mpiexec.hydra " + " -machinefile " + machineFileName + " " + hydra_options
  logging.debug('MPI launch string: %s', command_str)
  os.system(command_str)
  MPIisDone = True

#Creating thread for callback service
callbackThread = threading.Thread(target=start_callback_service)
callbackThread.setDaemon(True)
callbackThread.start()

#Waiting till callback port is defined
while not portIsDefined:
  time.sleep(1)

#Creating MPI Llama Client that is responsible for requesting/releasing resources
llama_client_obj = LlamaClient()
if llama_client_obj.Register() == -1:
  logging.error("Llama MPI client was not able to register with Llama server. Quitting..")
  quit()
if llama_client_obj.RequestResources() == -1:
  logging.error("Llama MPI client was not able to request the resources from Llama server. Quitting..")
  quit()

#Sleep till Llama lets us proceed
while not resourcesAreAllocated:
  time.sleep(1)

#Creating the machinefile for Hydra
machineFileName = "llama_nodes_%d" % (client_id)
try:
  os.remove(machineFileName)
except:
  pass
machineFile = open(machineFileName, 'w')
for k, v in nodePinning.iteritems():
  machineFile.write("%s:%d\n" % (k,v))
machineFile.close()

#Creating thread for callback service
mpiThread = threading.Thread(target=start_MPI)
mpiThread.setDaemon(True)
mpiThread.start()

while not MPIisDone:
  time.sleep(1)

#Don't retry releasing if failed, as unregistration should take care of this anyway
res = llama_client_obj.ReleaseResources()

for attempt in range(number_of_restarts):
  res = llama_client_obj.Unregister()
  if res.status.status_code == TStatusCode.OK:
    break

try:
  os.remove(machineFileName)
except:
  logging.warning("Was not able to delete temporary machinefile (%s)", machineFileName)

logging.info('MPI job has completed')

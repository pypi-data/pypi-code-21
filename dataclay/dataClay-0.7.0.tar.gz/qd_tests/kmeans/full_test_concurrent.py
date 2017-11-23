import dataclay
from dataclay.api import finish, init_connection
from dataclay.core import constants
from dataclay.core.exceptions.__init__ import DataclayException
from dataclay.debug.utils import create_users, prepare_namespace, prepare_dataclay_contrib
from dataclay.managers.classes.factory import MetaClassFactory
from jinja2.environment import Template
import os
import sys
from tempfile import mkdtemp, mkstemp
import threading
import time
import traceback
from importlib import import_module
import yaml

import model


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

def worker():
    
    try:
        # Import it now because this requires the previous init
        from main_noncompss import kmeans_frag
    
        print " # Start performance analysis on Fragment"
    
        from KMeans.model.classes import Fragment
        import numpy as np
    
        mu = list(np.random.random((10, 10)))
    
        f = Fragment(dim=2,
                     points=np.random.random((10, 10)),
                     base_index=0)
        f.make_persistent()
    
        start_time = time.time()
        f.cluster_points(mu)
        end_time = time.time()
        no_cached_1 = end_time - start_time
    
        start_time = time.time()
        f.cluster_points_cached(mu)
        end_time = time.time()
        cached_1 = end_time - start_time
    
        start_time = time.time()
        f.cluster_points(mu)
        end_time = time.time()
        no_cached_2 = end_time - start_time
    
        start_time = time.time()
        f.cluster_points_cached(mu)
        end_time = time.time()
        cached_2 = end_time - start_time
    
        print "No cached version time: %s" % no_cached_1
        print "   Cached version time: %s" % cached_1
        print "No cached version time: %s" % no_cached_2
        print "   Cached version time: %s" % cached_2

    finally:
        # Maybe catch some exception? Do something something more?
        pass
    print "Finished worker"


if __name__ == "__main__":
    # Initialization for everyone
    client_properties_path = os.getenv("DATACLAYCLIENTCONFIG", "./client.properties")
    init_connection(client_properties_path)

    print "Ready to do things"
    contract_ids = list()
    contract_ids_conf = None
    
    client = dataclay.runtime.ready_clients["@LM"]
    users = create_users()
    registrator_id = users.registrator[0]
    registrator_credential = (None, users.registrator[1])
    
    # with server:
    try:

        public_contract = prepare_dataclay_contrib(users.registrator, "consumer")

        populate_data = prepare_namespace(users.registrator, "consumer", namespace="KMeans", namespace_name="KMeans")

        mfc = MetaClassFactory(namespace="KMeans",
                               responsible_account="registrator")
        m = import_module("model.classes")
        mfc.add_class(getattr(m, "Board"))
        mfc.add_class(getattr(m, "Fragment"))

        result = client.new_class(registrator_id, registrator_credential,
                                  constants.lang_codes.LANG_PYTHON, mfc.classes)

        board_info = result['model.classes.Board']
        fragment_info = result['model.classes.Fragment']
        yaml_request_template = Template("""
---
boardinterface: &boardiface !!util.management.interfacemgr.Interface
  providerAccountName: registrator
  namespace: KMeans
  classNamespace: KMeans
  className: model.classes.Board
  propertiesInIface: !!set
  {% for property in board_info.properties %}
     ? {{ property.name }}
  {% endfor %}
  operationsSignatureInIface: !!set
  {% for operation in board_info.operations %}
    ? {{ operation.nameAndDescriptor }}
  {% endfor %}

fragmentinterface: &fragmentiface !!util.management.interfacemgr.Interface
  providerAccountName: registrator
  namespace: KMeans
  classNamespace: KMeans
  className: model.classes.Fragment
  propertiesInIface: !!set
  {% for property in fragment_info.properties %}
     ? {{ property.name }}
  {% endfor %}
  operationsSignatureInIface: !!set
  {% for operation in fragment_info.operations %}
    ? {{ operation.nameAndDescriptor }}
  {% endfor %}

kmeanscontract: !!util.management.contractmgr.Contract
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  namespace: KMeans
  providerAccountName: registrator
  applicantsNames:
    ? registrator
    ? consumer
  interfacesInContractSpecs:
    - !!util.management.contractmgr.InterfaceInContract
      iface: *boardiface
      implementationsSpecPerOperation:
        {% for operation in board_info.operations %}
          ? !!util.management.contractmgr.OpImplementations
            operationSignature: {{ operation.nameAndDescriptor }}
            numLocalImpl: 0
            numRemoteImpl: 0
        {% endfor %}
    - !!util.management.contractmgr.InterfaceInContract
      iface: *fragmentiface
      implementationsSpecPerOperation:
        {% for operation in fragment_info.operations %}
          ? !!util.management.contractmgr.OpImplementations
            operationSignature: {{ operation.nameAndDescriptor }}
            numLocalImpl: 0
            numRemoteImpl: 0
        {% endfor %}

  publicAvailable: True

kmeansdataset: !!util.management.datasetmgr.DataSet
  providerAccountName: registrator
  name: kmeansdataset

kmeansdatacontract: !!util.management.datacontractmgr.DataContract
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  providerAccountName: registrator
  dataSetProvidedName: kmeansdataset
  applicantsNames:
    ? consumer
    ? registrator
  publicAvailable: True
""")
        yaml_request = yaml_request_template.render(
            board_info=board_info,
            fragment_info=fragment_info
        )

        yaml_response = client.perform_set_of_operations(registrator_id, registrator_credential, yaml_request)
        response = yaml.load(yaml_response)

    except DataclayException as de:
        traceback.print_exc()  # Already registered
        print "Already registered"
    except Exception as e:
        traceback.print_exc()  # Already registered
        print "Already registered"
    try:
    
        contract_ids_response = client.get_contractids_of_applicant(registrator_id, registrator_credential)
        contract_ids_conf = ""
        i = 1
        num_contracts = len(contract_ids_response)
        for ctr_id, cntrct in contract_ids_response.iteritems():
            contract_ids_conf = contract_ids_conf + str(ctr_id) 
            contract_ids.append(ctr_id)
            if i < num_contracts:
                contract_ids_conf = contract_ids_conf + ","
            i = i + 1
        
        # Prepare the settings and load them
        settings_template = Template("""
Account={{ account }}
Password={{ password }}
StubsClasspath={{ stubspath }}
DataSets={{ dataset }}
DataSetForStore={{ dataset }}
DataClayClientConfig={{ clientconfig }}
Contracts={{ contracts }}
""")
        settings_filled = settings_template.render(
            account="registrator",
            password="registrator",
            stubspath=mkdtemp(),
            dataset="kmeansdataset",
            clientconfig=os.path.abspath("./client.properties"),
            contracts=contract_ids_conf,
        )
        print settings_filled
        f, settings_temp = mkstemp()
        f = os.fdopen(f, 'wb')
        f.write(settings_filled)
        f.close()

        from dataclay.conf import settings
        settings.load_properties(settings_temp)

        # Then proceed to initialize management, without standard manage.py invocation
        from dataclay import management

        management.prepare_storage()
        management.prepare_stubs(contract_ids)
        management.deploy_stubs()

        from dataclay.api import init
        init(settings_temp)
        # Prune the current models
        del sys.modules['model']
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
            
        for i in range(5):
            threads[i].join() 
            
    finally:
        # Maybe catch some exception? Do something something more?
        pass
    print "Finished All"
    finish()

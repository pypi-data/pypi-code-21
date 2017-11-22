from tempfile import mkdtemp, mkstemp
import sys

import os
from jinja2 import Template
import numpy as np
import cPickle as pickle

import dataclay
from dataclay.api import init, finish
from dataclay.core import constants
from dataclay.debug.utils import create_users, prepare_namespace
from dataclay.managers.classes.factory import MetaClassFactory
from test_classes.tiramisu import IVO

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2016 Barcelona Supercomputing Center (BSC-CNS)'


if __name__ == "__main__":
    # Initialization for everyone
    init("./configtests/client.properties", minimal=True)
    print "Ready to do things"
    contract_ids = list()
    contract_ids_conf = None
    users = create_users()
    registrator_id = users.registrator[0]
    registrator_credential = (None, users.registrator[1])
    consumer_id = users.consumer[0]
    consumer_credential = (None, users.consumer[1])
    # with server:
    try:
        client = dataclay.runtime.ready_clients["@LM"]
        populate_data = prepare_namespace(users.registrator, "consumer")

        mfc = MetaClassFactory(namespace=populate_data["test_classes"],
                               responsible_account=users.registrator[0])
        mfc.add_class(IVO)

        new_id = client.new_class_id(registrator_id, registrator_credential,
                                     'test_classes.tiramisu.IVO',
                                     constants.lang_codes.LANG_PYTHON, mfc.classes)
        print "IVO class:", str(new_id)

        metaclass_info = client.get_class_info(registrator_id, registrator_credential,
                                               populate_data["pydomain_id"],
                                               "test_classes.tiramisu.IVO")

        yaml_request_template = Template("""
---
ivointerface: !dataClay.Interface
  domainID: {{ namespaceID }}
  metaClassID: {{ metaclass_info.dataclay_id }}
  className: test_classes.tiramisu.IVO
  operationsIDs: !!set
  {% for operation in metaclass_info.operations %}
    ? {{ operation.dataclay_id }}
  {% endfor %}
  propertiesIDs: !!set
  {% for property in metaclass_info.properties %}
    ? {{ property.dataclay_id }}
  {% endfor %}
  dataClayID: !dataClay.InterfaceID &ivointerfaceID

ivocontract: !dataClay.Contract
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  applicantsAccountsIDs:
    ? {{ userID }}
    ? {{ registratorID }}
  providerDomainID: {{ namespaceID }}
  interfacesInContract:
    ? *ivointerfaceID
    : classID: {{ metaclass_info.dataclay_id }}
      accessibleImplementations:
      {% for operation in metaclass_info.operations %}
        ? {{ operation.dataclay_id }}
        : localImplementationID: {{ operation.implementations[0].dataclay_id }}
          remoteImplementationID: {{ operation.implementations[0].dataclay_id }}
      {% endfor %}
      interfaceToExtend: ~
      parentClassID: ~
  publicAvailable: True

ivodataset: !dataClay.DataSet
  language: LANG_PYTHON
  dataClayID: !dataClay.DataSetID &ivodatasetID

ivodatacontract: !dataClay.DataContract
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  applicantsAccountsIDs:
    ? {{ userID }}
    ? {{ registratorID }}
  providerDataSetID: *ivodatasetID
""")
        yaml_request = yaml_request_template.render(
            userID=str(users.consumer[0]),
            registratorID=str(users.registrator[0]),
            namespaceID=str(populate_data["pydomain_id"]),
            metaclass_info=metaclass_info
        )
        print yaml_request

        yaml_response = client.perform_set_of_operations(registrator_id, 
                                                         registrator_credential, yaml_request)
        response = dclay_yaml.load(yaml_response)
        
    except Exception as e:
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

        yaml_response = client.get_babel_stubs(
            registrator_id, registrator_credential, contract_ids)

        babel_stubs = dclay_yaml.load(yaml_response)

        print "We have Babel Stub, jumping into regular dataclay.api based thing"

        # Prepare the settings and load them
        settings_template = Template("""
Account={{ account }}
Password={{ password }}
StubsClasspath={{ stubspath }}
DataSets={{ dataset }}
DataSetForStore={{ dataset }}
DataClayClientConfig={{ clientconfig }}
""")
        settings_filled = settings_template.render(
            account="registrator",
            password="registrator",
            stubspath=mkdtemp(),
            dataset="ivodataset",
            clientconfig=os.path.abspath("./configtests/client.properties")
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

        import dataclay.api
        dataclay.api.init(settings_temp)
        # Note that currently loaded test_classes is the local one,
        # not the freshly just-generated one
        del sys.modules['test_classes']
        del sys.modules['test_classes.tiramisu']

        # Now the test_classes should be the good one
        from test_classes.tiramisu import IVO

        i = IVO()
        i.layer_data = [np.array([2, 3, 5]),
                        np.array([2, 6, 10, 12]),
                        np.array([3, 1])]
        j = IVO()
        j.layer_data = [np.array([2, 3, 0]),
                        np.array([3, 5, 0, 2]),
                        np.array([15, 3])]

        print (i + j).layer_data

        i.make_persistent()
        j.make_persistent()

        print i.layer_data
        i.image_sources = ["this", "is", "test"]
        print i.image_sources

        print "Evaluating sum"
        a = i+j
        print "Print the sum"
        print a
        print a.layer_data

        print "##############"
        print "# PICKLE!"
        v = pickle.dumps(a)
        print v
        b = pickle.loads(v)
        print b
        print b.layer_data

        print "########################"
        print "# Arithmetic testing"
        print " ======> +"
        print (i + j).layer_data
        print " ======> *"
        print (i * j).layer_data
        print " ======> /"
        print (i / j).layer_data
        print " ======> scalar *"
        print (3 * i).layer_data
        print " ======> * scalar"
        print (i * 3).layer_data
        print " ======> / scalar"
        print (i / 3).layer_data
        print " ======> scalar /"
        print (3 / i).layer_data

        print "Inplace operators!"
        i += j
        print "+= >", i.layer_data
        i *= 3
        print "*= >", i.layer_data
        i /= 2
        print "/= >", i.layer_data
        i *= j
        print "*= IVO >", i.layer_data

    finally:
        # Maybe catch some exception? Do something something more?
        pass

    print "Finished"
    finish()

from tempfile import mkdtemp

import os
import sys
from jinja2.environment import Template
import yaml

import dataclay
from dataclay.debug.utils import prepare_namespace, create_users, prepare_dataclay_contrib
from dataclay.core import constants
from dataclay.api import init_connection
from dataclay.managers.classes.factory import MetaClassFactory

import model

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


if __name__ == "__main__":
    # Initialization for everyone
    if len(sys.argv) == 1:
        client_properties_path = "./client.properties"
        storage_properties_path = "./storage.properties"
        stubs_path = mkdtemp()
    else:
        # First argument is the client.properties path
        client_properties_path = sys.argv[1]
        # Second one should be there, and be the storage.properties output path
        storage_properties_path = sys.argv[2]
        # Thid one, STUBSPATH
        stubs_path = sys.argv[3]

    init_connection(client_properties_path)

    print "Ready to do things"
    # with server:
    try:
        client = dataclay.runtime.ready_clients["@LM"]
        users = create_users()

        # Start by the public contract
        public_contract = prepare_dataclay_contrib(users.registrator, "consumer")

        # populate_data = prepare_namespace(users.registrator, "consumer", namespace="KMeans")

        consumer_id = client.get_account_id("consumer")
        consumer = (consumer_id, "consumer")

        registrator_id = client.get_account_id("registrator")
        registrator = (registrator_id, "registrator")
        registrator_credential = (None, registrator[1])

        namespace_id = prepare_namespace(registrator, "consumer", namespace="KMeans")

        mfc = MetaClassFactory(namespace="KMeans",
                               responsible_account="registrator")
        mfc.add_class(model.Board)
        mfc.add_class(model.Fragment)
        # mfc.add_class(model.SplitBoard)

        result = client.new_class(registrator_id, registrator_credential, constants.lang_codes.LANG_PYTHON, mfc.classes)

        if len(result) > 1:
            board_info = result['Board']
            fragment_info = result['Fragment']
            # splitboard_info = result['SplitBoard']
        elif len(result) == 0:
            print "Seems that the classes they had already been registered"

            account_id = client.get_account_id("registrator")

            board_info = client.get_class_info(registrator_id, registrator_credential, namespace_id, 'Board')
            fragment_info = client.get_class_info(registrator_id, registrator_credential, namespace_id, 'Fragment')
            # splitboard_info = client.get_class_info(registrator, namespace_id, 'SplitBoard')
        else:
            print " ERROR: Didn't expect that number of elements, received:"
            print "---------------------------------------------------------"
            print result
            raise RuntimeError("Could not initialize registered classes successfully")

        yaml_request_template = Template("""
---
boardinterface: &boardiface !!util.management.interfacemgr.Interface
  providerAccountName: registrator
  namespace: KMeans
  classNamespace: KMeans
  className: Board
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
  className: Fragment
  propertiesInIface: !!set
  {% for property in fragment_info.properties %}
     ? {{ property.name }}
  {% endfor %}
  operationsSignatureInIface: !!set
  {% for operation in fragment_info.operations %}
    ? {{ operation.nameAndDescriptor }}
  {% endfor %}

{#
splitboardinterface: &splitboardiface !!util.management.interfacemgr.Interface
  providerAccountName: registrator
  namespace: KMeans
  classNamespace: KMeans
  className: SplitBoard
  propertiesInIface: !!set
  {% for property in splitboard_info.properties %}
     ? {{ property.name }}
  {% endfor %}
  operationsSignatureInIface: !!set
  {% for operation in splitboard_info.operations %}
    ? {{ operation.nameAndDescriptor }}
  {% endfor %}
#}

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
{#
    - !!util.management.contractmgr.InterfaceInContract
      iface: *splitboardiface
      implementationsSpecPerOperation:
        {% for operation in splitboard_info.operations %}
          ? !!util.management.contractmgr.OpImplementations
            operationSignature: {{ operation.nameAndDescriptor }}
            numLocalImpl: 0
            numRemoteImpl: 0
        {% endfor %}
#}
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
            fragment_info=fragment_info,
            # splitboard_info=splitboard_info
        )

        yaml_response = client.perform_set_of_operations(registrator_id, registrator_credential, yaml_request)
        response = yaml.load(yaml_response)

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
            stubspath=stubs_path,
            dataset="kmeansdataset",
            clientconfig=os.path.abspath(client_properties_path),
            contracts=",".join((str(response["contracts"]["kmeanscontract"]),
                                str(public_contract))),
        )
        with open(storage_properties_path, 'wb') as f:
            f.write(settings_filled)

        print "<register_only.py> Yielded the following:\n%s\n\n -> Stored in %s" % (
            settings_filled, storage_properties_path)

        from dataclay.conf import settings

        settings.load_properties(storage_properties_path)

        # Then proceed to initialize management, without standard manage.py invocation
        from dataclay import management

        management.prepare_storage()
        management.prepare_stubs({public_contract, response["contracts"]["kmeanscontract"]})
        management.deploy_stubs(stubs_path)

    finally:
        # Maybe catch some exception? Do something something more?
        pass
    print "<register_only.py> Finished"

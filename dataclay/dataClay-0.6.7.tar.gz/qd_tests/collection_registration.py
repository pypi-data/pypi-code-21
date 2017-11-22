from tempfile import mkdtemp, mkstemp
import sys
from uuid import UUID

import os
from jinja2 import Template
import yaml

import dataclay
from dataclay.api import init
from dataclay.core import constants
from dataclay.debug.utils import create_users, prepare_namespace
from dataclay.managers.classes.factory import MetaClassFactory

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2016 Barcelona Supercomputing Center (BSC-CNS)'


if __name__ == "__main__":
    # Initialization for everyone
    init("./configtests/client.properties", minimal=True)

    print "Ready to do things"
    # with server:
    try:
        client = dataclay.runtime.ready_clients["@LM"]

        consumer_id = client.get_account_id("Consumer")
        consumer = (consumer_id,
                    "Consumer".encode('utf-16-be'))

        registrator_id = client.get_account_id("Registrator")
        registrator = (registrator_id,
                       "Registrator".encode('utf-16-be'))

        # ToDo: Pass also the account_id to the client (In this case registrator_id)
        collections_contract = client.get_contract_id_of_dataclay_provider(registrator)

        yaml_response = client.get_babel_stubs(registrator, [collections_contract])

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
            account="Consumer",
            password="Consumer",
            stubspath=mkdtemp(),
            dataset="RegistratorDataSet",
            clientconfig=os.path.abspath("./configtests/client.properties"),
            contracts=collections_contract
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
        management.prepare_stubs([collections_contract])

        import dataclay.api
        dataclay.api.init(settings_temp)

        # Proceed to import, now it should import correctly
        from test_classes.collections_related import RemoteCollectionsProbe

        mfc = MetaClassFactory(namespace="test_classes",
                               responsible_account="Registrator")
        mfc.add_class(RemoteCollectionsProbe)

        new_id = client.new_class_id(registrator,
                                     'collections_related.RemoteCollectionsProbe',
                                     constants.lang_codes.LANG_PYTHON, mfc)
        print "RemoteCollectionsProbe class:", str(new_id)

        account_id = client.get_account_id("registrator")

        # ToDo: Pass also the account_id to the client
        rcpclass_info = client.get_class_info(registrator,
                                              test_classes_domain_id,
                                              "collections_related.RemoteCollectionsProbe")

        yaml_request_template = Template("""
---
rcpinterface: &rcpiface !!util.management.interfacemgr.Interface
  providerAccountName: registrator
  namespace: test_classes
  classNamespace: test_classes
  className: collections_related.RemoteCollectionsProbe
  propertiesInIface: !!set {collection}
  operationsSignatureInIface:
  {% for operation in rcpclass_info.operations %}
    ? {{ operation.signature }}
  {% endfor %}

rcpcontract: !!util.management.contractmgr.Contract
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  namespace: test_classes
  providerAccountName: registrator
  applicantsNames:
    ? registrator
    ? consumer
  interfacesInContractSpecs:
    - !!util.management.contractmgr.InterfaceInContract
      iface: *rcpiface
      implementationsSpecPerOperation:
        {% for operation in rcpclass_info.operations %}
          ? !!util.management.contractmgr.OpImplementations
            operationSignature: {{ operation.signature }}
            numLocalImpl: 0
            numRemoteImpl: 0
        {% endfor %}

  publicAvailable: True

rcpdataset: !!util.management.datasetmgr.DataSet
  providerAccountName: registrator
  name: rcpdataset

rcpdatacontract: !!util.management.datacontractmgr.DataContract
  providerAccountName: registrator
  dataSetProvidedName: rcpdataset
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  applicantsNames:
    ? consumer
    ? registrator
  publicAvailable: True
""")
        yaml_request = yaml_request_template.render(
            rcpclass_info=rcpclass_info
        )
        print yaml_request

        yaml_response = client.perform_set_of_operations(users.registrator, yaml_request)
        response = yaml.load(yaml_response)

        yaml_response = client.get_babel_stubs(
            users.consumer, [response["contracts"]["rcpcontract"], ])

        babel_stubs = yaml.load(yaml_response)

        print "We have Babel Stub, jumping into regular dataclay.api based thing"

        ############################################################################
        ############################################################################

        # Note that currently loaded test_classes is the local one,
        # not the freshly just-generated one
        del sys.modules['test_classes']
        del sys.modules['test_classes.collections_related']

        import test_classes
        print "File in which test_classes lives:", test_classes.__file__

        from test_classes import collections_related
        print "new_style_classes lives in:", collections_related.__file__

        # Now the test_classes should be the good one
        from test_classes.collections_related import RemoteCollectionsProbe
        print RemoteCollectionsProbe.__file__

        rcp = RemoteCollectionsProbe()
        print rcp.create_collection()

        print " *** MAKE PERSISTENT . . . *** "
        rcp.make_persistent()
        print " *** MAKE PERSISTENT DONE! *** "

        print rcp.create_collection()

        print rcp.collection

    finally:
        # Maybe catch some exception? Do something something more?
        pass

    print "Finished"

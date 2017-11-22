import signal
from multiprocessing import Process

import os
from dataclay.debug.javaserver import JavaServerManager
from gevent import signal as gsignal
from jinja2.environment import Template

from dataclay.core import constants
from dataclay.core import dclay_yaml
from dataclay.core import initialize
from dataclay.debug.test_classes import complex_class
from dataclay.managers.classes.factory import MetaClassFactory
from dclay_server import main
from dclay_server.config import ServerConfigOptions

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


if __name__ == "__main__":
    # Initialization for everyone
    initialize()

    ServerConfigOptions.server_listen_port = 2127
    # initialization for the Execution Environment
    p = Process(target=main, name="dataClay Server Process")
    p.daemon = True
    p.start()
    # SIGHUP is used internally by the dataClay server process
    gsignal(signal.SIGHUP, signal.SIG_IGN)

    server = JavaServerManager()
    # server = JavaServerManager.connect_to_preloaded()

    print "Ready to do things"
    # with server:
    try:
        server.create_users()
        server.populate()

        mfc = MetaClassFactory(namespace=server.populate_data["test_classes"],
                               responsible_account_id=server.registrator_id,
                               namespace_id=server.populate_data["pydomain_id"])
        mfc.add_package(server.populate_data["test_classes"], complex_class)

        new_id = server.client.new_class_id(server.registrator,
                                            # FIXME ok, this is ugly, the namespace/full name should not be hardcoded
                                            'test_classes.complex_class.ChainedList',
                                            constants.lang_codes.LANG_PYTHON,
                                            mfc)
        print str(new_id)

        account_id = server.client.get_account_id("registrator")

        # ToDo: Pass also the account_id to the client

        chainedclass_info = server.client.get_class_info(server.registrator,
                                                         server.populate_data["pydomain_id"],
                                                         "test_classes.complex_class.ChainedList")
        linkclass_info = server.client.get_class_info(server.registrator,
                                                      server.populate_data["pydomain_id"],
                                                      "test_classes.complex_class.ChainLink")
        yaml_request_template = Template("""
---
chainedinterface: !dataClay.Interface
  domainID: {{ namespaceID }}
  metaClassID: {{ chainedclass_info.dataclay_id }}
  className: test_classes.complex_class.ChainedList
  operationsIDs: !!set
  {% for operation in chainedclass_info.operations %}
    ? {{ operation.dataclay_id }}
  {% endfor %}
  propertiesIDs: !!set
  {% for property in chainedclass_info.properties %}
    ? {{ property.dataclay_id }}
  {% endfor %}
  dataClayID: !dataClay.InterfaceID &chainedinterfaceID

linkinterface: !dataClay.Interface
  domainID: {{ namespaceID }}
  metaClassID: {{ linkclass_info.dataclay_id }}
  className: test_classes.complex_class.ChainLink
  operationsIDs: !!set
  {% for operation in linkclass_info.operations %}
    ? {{ operation.dataclay_id }}
  {% endfor %}
  propertiesIDs: !!set
  {% for property in linkclass_info.properties %}
    ? {{ property.dataclay_id }}
  {% endfor %}
  dataClayID: !dataClay.InterfaceID &linkinterfaceID

chaincontract: !dataClay.Contract
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  applicantsAccountsIDs:
    ? {{ userID }}
    ? {{ registratorID }}
  providerDomainID: {{ namespaceID }}
  interfacesInContract:
    ? *chainedinterfaceID
    : classID: {{ chainedclass_info.dataclay_id }}
      accessibleImplementations:
      {% for operation in chainedclass_info.operations %}
        ? {{ operation.dataclay_id }}
        : localImplementationID: {{ operation.implementations[0].dataclay_id }}
          remoteImplementationID: {{ operation.implementations[0].dataclay_id }}
      {% endfor %}
      interfaceToExtend: ~
      parentClassID: ~
    ? *linkinterfaceID
    : classID: {{ linkclass_info.dataclay_id }}
      accessibleImplementations:
      {% for operation in linkclass_info.operations %}
        ? {{ operation.dataclay_id }}
        : localImplementationID: {{ operation.implementations[0].dataclay_id }}
          remoteImplementationID: {{ operation.implementations[0].dataclay_id }}
      {% endfor %}
      interfaceToExtend: ~
      parentClassID: ~
  publicAvailable: True

chaindataset: !dataClay.DataSet
  language: LANG_PYTHON
  dataClayID: !dataClay.DataSetID &chaindatasetID

chaindatacontract: !dataClay.DataContract
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  applicantsAccountsIDs:
    ? {{ userID }}
    ? {{ registratorID }}
  providerDataSetID: *chaindatasetID
""")
        yaml_request = yaml_request_template.render(
            userID=str(server.user_id),
            registratorID=str(server.registrator_id),
            namespaceID=str(server.populate_data["pydomain_id"]),
            chainedclass_info=chainedclass_info,
            linkclass_info=linkclass_info
        )

        yaml_response = server.client.perform_set_of_operations(server.registrator, yaml_request)
        response = dclay_yaml.load(yaml_response)

        yaml_response = server.client.get_babel_stubs(
            server.user, [response["contracts"]["chaincontract"], ])

        babel_stubs = dclay_yaml.load(yaml_response)

        print "We have Babel Stub, jumping into regular dataclay.api based thing"

        from dataclay import debug
        from dataclay.conf import settings

        settings.CONTRACTS = {response["contracts"]["chaincontract"]}
        settings.DATASET_FOR_STORE = "chaindataset"
        settings.DATASETS = ["chaindataset"]
        from dataclay import management
        project_path = os.path.dirname(__file__)
        management.prepare_storage(project_path)
        management.prepare_stubs(project_path)

        import dataclay.api
        from test_classes.complex_class import ChainedList
        chained_list = ChainedList(10)

        def check_that(chain):
            for i, (a, b) in enumerate(zip(chain[:-1], chain[1:])):
                assert a.next._object_id == b._object_id
                assert b.previous._object_id == a._object_id

        chained_list.make_persistent()

        # Do a fibonacci strange thing hoping around dataservices
        chained_list.start_fibonacci()

        # Clean caches
        os.kill(p.pid, signal.SIGHUP)
        print "Going to check when persistent and caches are clean..."
        check_that(chained_list.chain)

        print "Done!"
    finally:
        server.close(cleanup=False)

    print "Finished"

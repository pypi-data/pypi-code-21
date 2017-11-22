import signal
from multiprocessing import Process
from tempfile import mkdtemp, mkstemp

import os
from dataclay.debug.javaserver import JavaServerManager
from gevent import signal as gsignal
from jinja2.environment import Template

import dataclay
from dataclay.conf import settings
from dataclay.core import constants
from dataclay.core import dclay_yaml
from dataclay.core import initialize
from dataclay.debug.test_classes import easy_classes
from dataclay.managers.classes.factory import MetaClassFactory
from dclay_server import main

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


if __name__ == "__main__":
    # Initialization for everyone
    initialize()

    # Load the connection settings
    settings.load_connection("./configtests/client.properties")

    # initialization for the Execution Environment
    p = Process(target=main, name="dataClay Server Process")
    p.daemon = True
    p.start()
    # SIGHUP is used internally by the dataClay server process
    gsignal(signal.SIGHUP, signal.SIG_IGN)

    server = JavaServerManager()
    # raw_input("Press enter..."); server = JavaServerManager.connect_to_preloaded()

    print "Ready to do things"
    # with server:
    try:
        server.create_users()
        server.populate()

        mfc = MetaClassFactory(namespace=server.populate_data["test_classes"],
                               responsible_account_id=server.registrator_id,
                               namespace_id=server.populate_data["pydomain_id"])
        mfc.add_package(server.populate_data["test_classes"], easy_classes)
        new_id = server.client.new_class_id(server.registrator,
                                            'test_classes.easy_classes.PropertiesClass',
                                            constants.lang_codes.LANG_PYTHON,
                                            mfc)
        print "PropertiesClass:", str(new_id)

        account_id = server.client.get_account_id("registrator")

        # ToDo: Pass also the account_id to the client
        metaclass_info = server.client.get_class_info(server.registrator,
                                                      server.populate_data["pydomain_id"],
                                                      "test_classes.easy_classes.PropertiesClass")

        print metaclass_info
        yaml_request = """
---
propertiesinterface: !dataClay.Interface
  domainID: {namespaceID}
  metaClassID: {metaclassID}
  className: test_classes.easy_classes.PropertiesClass
  operationsIDs: {{ {operations[0]}, {operations[1]}, {operations[2]},
                    {operations[3]}, {operations[4]}, {operations[5]},
                    {operations[6]} }}
  propertiesIDs: {{ {properties[0]}, {properties[1]}, {properties[2]} }}
  dataClayID: !dataClay.InterfaceID &propertiesinterfaceID

propertiescontract: !dataClay.Contract
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  applicantsAccountsIDs:
    ? {userID}
    ? {registratorID}
  providerDomainID: {namespaceID}
  interfacesInContract:
    ? *propertiesinterfaceID
    : classID: {metaclassID}
      accessibleImplementations:
        ? {operations[0]}
        : localImplementationID: {implementations[0]}
          remoteImplementationID: {implementations[0]}
        ? {operations[1]}
        : localImplementationID: {implementations[1]}
          remoteImplementationID: {implementations[1]}
        ? {operations[2]}
        : localImplementationID: {implementations[2]}
          remoteImplementationID: {implementations[2]}
        ? {operations[3]}
        : localImplementationID: {implementations[3]}
          remoteImplementationID: {implementations[3]}
        ? {operations[4]}
        : localImplementationID: {implementations[4]}
          remoteImplementationID: {implementations[4]}
        ? {operations[5]}
        : localImplementationID: {implementations[5]}
          remoteImplementationID: {implementations[5]}
        ? {operations[6]}
        : localImplementationID: {implementations[6]}
          remoteImplementationID: {implementations[6]}
      interfaceToExtend: ~
      parentClassID: ~
  publicAvailable: True

propertiesdataset: !dataClay.DataSet
  language: LANG_PYTHON
  dataClayID: !dataClay.DataSetID &propertiesdatasetID

propertiesdatacontract: !dataClay.DataContract
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  applicantsAccountsIDs:
    ? {userID}
    ? {registratorID}
  providerDataSetID: *propertiesdatasetID
""".format(userID=str(server.user_id),
           registratorID=str(server.registrator_id),
           namespaceID=str(server.populate_data["pydomain_id"]),
           metaclassID=str(new_id),
           operations=[op.dataclay_id for op in metaclass_info.operations],
           properties=[prop.dataclay_id for prop in metaclass_info.properties],
           implementations=[op.implementations[0].dataclay_id
                            for op in metaclass_info.operations])

        yaml_response = server.client.perform_set_of_operations(server.registrator, yaml_request)
        response = dclay_yaml.load(yaml_response)

        yaml_response = server.client.get_babel_stubs(
            server.user, [response["contracts"]["propertiescontract"], ])

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
            dataset="propertiesdataset",
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
        management.prepare_stubs({response["contracts"]["propertiescontract"]})

        import dataclay.api
        dataclay.api.init(settings_temp)
        from test_classes.easy_classes import PropertiesClass

        properties_class = PropertiesClass()

        print "Internal class values:", object.__getattribute__(properties_class, "__dict__")
        print properties_class.propInt
        properties_class.propInt = 43
        print properties_class.propInt

        properties_class.make_persistent()
        print "Persistent calls done"

        assert properties_class.is_persistent
        print "Internal class values:", object.__getattribute__(properties_class, "__dict__")

        print properties_class.propInt
        properties_class.propInt = 44
        print properties_class.propInt

        print properties_class.propFloat
        properties_class.propFloat = 4.4
        print properties_class.propFloat

        print properties_class.propBool
        properties_class.propBool = False
        print properties_class.propBool

        print "Internal class values:", object.__getattribute__(properties_class, "__dict__")

        # Check if it is correctly stored
        os.kill(p.pid, signal.SIGHUP)
        print properties_class.propInt
        print properties_class.propFloat
        print properties_class.propBool

    finally:
        server.close(cleanup=False)

    print "Finished"

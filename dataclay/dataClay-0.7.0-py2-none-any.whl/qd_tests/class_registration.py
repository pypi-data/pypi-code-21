import sys
from tempfile import mkdtemp, mkstemp

import numpy as np
import os
from jinja2 import Template
import yaml

import dataclay
from dataclay.api import init
from dataclay.core import constants
from dataclay.core.management.stubs import babel_stubs_load
from dataclay.debug.utils import create_users, prepare_namespace
from dataclay.managers.classes.factory import MetaClassFactory
from test_classes.new_style_classes import GenericObject

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2016 Barcelona Supercomputing Center (BSC-CNS)'


if __name__ == "__main__":
    # Initialization for everyone
    init("./configtests/client.properties", minimal=True)

    print "Ready to do things"
    # with server:
    try:
        client = dataclay.runtime.ready_clients["@LM"]
        users = create_users()
        test_classes_namespace_id = prepare_namespace(users.registrator, "consumer")

        mfc = MetaClassFactory(namespace="test_classes",
                               responsible_account="registrator")
        mfc.add_class(GenericObject)

        new_id = client.new_class_id(users.registrator,
                                     'new_style_classes.GenericObject',
                                     constants.lang_codes.LANG_PYTHON, mfc)
        print "GenericObject class:", str(new_id)

        account_id = client.get_account_id("registrator")

        # ToDo: Pass also the account_id to the client
        metaclass_info = client.get_class_info(users.registrator,
                                               test_classes_namespace_id,
                                               "new_style_classes.GenericObject")

        yaml_request_template = Template("""
---
genericiface: &genericiface !!util.management.interfacemgr.Interface
  providerAccountName: registrator
  namespace: test_classes
  classNamespace: test_classes
  className: new_style_classes.GenericObject
  propertiesInIface: !!set {propInt, propFloat, propBool}
  operationsSignatureInIface:
  {% for operation in metaclass_info.operations %}
    ? {{ operation.signature }}
  {% endfor %}

genericcontract: !!util.management.contractmgr.Contract
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  namespace: test_classes
  providerAccountName: registrator
  applicantsNames:
    ? registrator
    ? consumer
  interfacesInContractSpecs:
    - !!util.management.contractmgr.InterfaceInContract
      iface: *genericiface
      implementationsSpecPerOperation:
        {% for operation in metaclass_info.operations %}
          ? !!util.management.contractmgr.OpImplementations
            operationSignature: {{ operation.signature }}
            numLocalImpl: 0
            numRemoteImpl: 0
        {% endfor %}

  publicAvailable: True

genericdataset: !!util.management.datasetmgr.DataSet
  providerAccountName: registrator
  name: genericdataset

genericdatacontract: !!util.management.datacontractmgr.DataContract
  providerAccountName: registrator
  dataSetProvidedName: genericdataset
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  applicantsNames:
    ? consumer
    ? registrator
  publicAvailable: True
""")
        yaml_request = yaml_request_template.render(
            metaclass_info=metaclass_info
        )
        print yaml_request

        yaml_response = client.perform_set_of_operations(users.registrator, yaml_request)
        response = yaml.load(yaml_response)

        yaml_response = client.get_babel_stubs(
            users.consumer, [response["contracts"]["genericcontract"], ])

        print yaml_response
        babel_stubs = babel_stubs_load(yaml_response)

        print "We have Babel Stub, jumping into regular dataclay.api based thing"

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
            dataset="genericdataset",
            clientconfig=os.path.abspath("./configtests/client.properties"),
            contracts=response["contracts"]["genericcontract"]
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
        management.prepare_stubs([response["contracts"]["genericcontract"]])

        import dataclay.api
        dataclay.api.init(settings_temp)
        # Note that currently loaded test_classes is the local one,
        # not the freshly just-generated one
        del sys.modules['test_classes']
        del sys.modules['test_classes.new_style_classes']

        import test_classes
        print "File in which test_classes lives:", test_classes.__file__

        from test_classes import new_style_classes
        print "new_style_classes lives in:", new_style_classes.__file__

        # Now the test_classes should be the good one
        from test_classes.new_style_classes import GenericObject

        from test_classes import new_style_classes
        print new_style_classes.__file__

        g = GenericObject()
        print g.func(3, 5)

        g.assign_props()
        print g.retrieve_props()

        print " *** MAKE PERSISTENT . . . *** "
        g.make_persistent()
        print " *** MAKE PERSISTENT DONE! *** "
        print g.func(3, 5)

        g.set_props(43, 4.3, False)
        print g.propInt
        print g.propFloat
        print g.propBool

        print g.do_max([np.array([1, 2, 3]), np.array([2, 3, 4]), np.array([3, 4, 5])])

        print " *** PROPERTIES *** "
        print g.retrieve_props()
        g.assign_props()
        print g.retrieve_props()
        g.set_props(43, 4.3, False)
        print g.retrieve_props()

        print " *** now playing with ALIAS *** "
        g = GenericObject()
        g.make_persistent("ThisIsAlias")
        g.set_props(42, 0.42, True)

        g_bis = GenericObject.get_by_alias("ThisIsAlias")
        assert g.propInt == g_bis.propInt
        assert g.propFloat == g_bis.propFloat
        assert g.propBool == g_bis.propBool

    finally:
        # Maybe catch some exception? Do something something more?
        pass

    print "Finished"

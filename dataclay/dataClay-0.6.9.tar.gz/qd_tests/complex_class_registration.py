from tempfile import mkdtemp, mkstemp

import os
import sys
from jinja2.environment import Template
import yaml

import dataclay
from dataclay import debug
from dataclay.debug.utils import create_users, prepare_namespace
from dataclay.core import constants
from dataclay.api import init
from test_classes.new_complex_classes import *
from dataclay.managers.classes.factory import MetaClassFactory

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


if __name__ == "__main__":
    # Initialization for everyone
    init("./configtests/client.properties", minimal=True)

    print "Ready to do things"
    # with server:
    try:
        client = dataclay.runtime.ready_clients["@LM"]
        users = create_users()
        populate_data = prepare_namespace(users.registrator, "consumer")

        mfc = MetaClassFactory(namespace="test_classes",
                               responsible_account="registrator")
        mfc.add_class(ComplexClass)
        mfc.add_class(PartOne)
        mfc.add_class(PartTwo)
        mfc.add_class(ChainedList)
        mfc.add_class(ChainLink)

        result = client.new_class(users.registrator,
                                  constants.lang_codes.LANG_PYTHON, mfc)

        partone_info = result['new_complex_classes.PartOne']
        parttwo_info = result['new_complex_classes.PartTwo']
        complexclass_info = result['new_complex_classes.ComplexClass']
        yaml_request_template = Template("""
---
complexclassinterface: &complexiface !!util.management.interfacemgr.Interface
  providerAccountName: registrator
  namespace: test_classes
  classNamespace: test_classes
  className: new_complex_classes.ComplexClass
  propertiesInIface: !!set
  {% for property in complexclass_info.properties %}
     ? {{ property.name }}
  {% endfor %}
  operationsSignatureInIface: !!set
  {% for operation in complexclass_info.operations %}
    ? {{ operation.signature }}
  {% endfor %}

partoneinterface: &partoneiface !!util.management.interfacemgr.Interface
  providerAccountName: registrator
  namespace: test_classes
  classNamespace: test_classes
  className: new_complex_classes.PartOne
  propertiesInIface: !!set
  {% for property in partone_info.properties %}
     ? {{ property.name }}
  {% endfor %}
  operationsSignatureInIface: !!set
  {% for operation in partone_info.operations %}
    ? {{ operation.signature }}
  {% endfor %}

parttwointerface: &parttwoiface !!util.management.interfacemgr.Interface
  providerAccountName: registrator
  namespace: test_classes
  classNamespace: test_classes
  className: new_complex_classes.PartTwo
  propertiesInIface: !!set
  {% for property in parttwo_info.properties %}
     ? {{ property.name }}
  {% endfor %}
  operationsSignatureInIface: !!set
  {% for operation in parttwo_info.operations %}
    ? {{ operation.signature }}
  {% endfor %}

complexclasscontract: !!util.management.contractmgr.Contract
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  namespace: test_classes
  providerAccountName: registrator
  applicantsNames:
    ? registrator
    ? consumer
  interfacesInContractSpecs:
    - !!util.management.contractmgr.InterfaceInContract
      iface: *complexiface
      implementationsSpecPerOperation:
        {% for operation in complexclass_info.operations %}
          ? !!util.management.contractmgr.OpImplementations
            operationSignature: {{ operation.signature }}
            numLocalImpl: 0
            numRemoteImpl: 0
        {% endfor %}
    - !!util.management.contractmgr.InterfaceInContract
      iface: *partoneiface
      implementationsSpecPerOperation:
        {% for operation in partone_info.operations %}
          ? !!util.management.contractmgr.OpImplementations
            operationSignature: {{ operation.signature }}
            numLocalImpl: 0
            numRemoteImpl: 0
        {% endfor %}
    - !!util.management.contractmgr.InterfaceInContract
      iface: *parttwoiface
      implementationsSpecPerOperation:
        {% for operation in parttwo_info.operations %}
          ? !!util.management.contractmgr.OpImplementations
            operationSignature: {{ operation.signature }}
            numLocalImpl: 0
            numRemoteImpl: 0
        {% endfor %}

  publicAvailable: True

complexclassdataset: !!util.management.datasetmgr.DataSet
  providerAccountName: registrator
  name: complexclassdataset

genericdatacontract: !!util.management.datacontractmgr.DataContract
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  providerAccountName: registrator
  dataSetProvidedName: complexclassdataset
  applicantsNames:
    ? consumer
    ? registrator
  publicAvailable: True
""")
        yaml_request = yaml_request_template.render(
            complexclass_info=complexclass_info,
            partone_info=partone_info,
            parttwo_info=parttwo_info
        )

        yaml_response = client.perform_set_of_operations(users.registrator, yaml_request)
        response = yaml.load(yaml_response)

        print response

        yaml_response = client.get_babel_stubs(
            users.consumer, [response["contracts"]["complexclasscontract"], ])

        print " ***    --------------------------------------------------"
        print response

        babel_stubs = yaml.load_all(yaml_response)

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
            dataset="complexclassdataset",
            clientconfig=os.path.abspath("./configtests/client.properties"),
            contracts=response["contracts"]["complexclasscontract"],
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
        management.prepare_stubs({response["contracts"]["complexclasscontract"]})

        import dataclay.api
        dataclay.api.init(settings_temp)
        # Note that currently loaded test_classes is the local one,
        # not the freshly just-generated one
        del sys.modules['test_classes']
        del sys.modules['test_classes.new_complex_classes']

        from test_classes.new_complex_classes import ComplexClass, PartOne
        complex_class = ComplexClass()
        print dir(complex_class)

        print complex_class.get_pt1_prop()
        print complex_class.get_pt1()

        print "Making persistent (child). . ."
        complex_class.get_pt1().make_persistent()
        complex_class.get_pt2().make_persistent()

        complex_class.get_pt1().set_val(32)
        print "Invisible old value:", debug.get_property(
            complex_class.get_pt1(), "prop")
        print "New value (persistent):", complex_class.get_pt1().get_val()
        print "Also:", complex_class.get_pt1_prop()
        print "Or also:", complex_class.get_pt1().prop

        print "Making persistent (complex_class)"
        complex_class.make_persistent()

        print "Proceeding to remote calls"
        print complex_class.get_pt1_prop()
        print complex_class.get_pt1()

        complex_class.get_pt1().set_val(44)
        print complex_class.get_pt1_prop()
        print complex_class.get_pt1().prop
        print complex_class.get_pt1().get_val()

        print "Now something more interesting"
        partone = PartOne()
        partone.prop = 1978
        print "Make persistent on object one"
        partone.make_persistent()
        print "Object one already persistent"
        print partone.prop
        complex_class.set_pt1(partone)
        print "Trying to get the pt1.prop from complex class through explicit (user-provided) getter"
        print complex_class.get_pt1_prop()

    finally:
        # Maybe catch some exception? Do something something more?
        pass
    print "Finished"

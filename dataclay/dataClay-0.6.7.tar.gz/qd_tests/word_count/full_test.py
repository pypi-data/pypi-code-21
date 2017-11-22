from dataclay import debug
import dataclay
from dataclay.api import finish, init_connection
from dataclay.core import constants
from dataclay.debug.utils import create_users, prepare_namespace, prepare_dataclay_contrib
from dataclay.managers.classes.factory import MetaClassFactory
from importlib import import_module
import itertools
from jinja2.environment import Template
import os
import string
import sys
from tempfile import mkdtemp, mkstemp
import traceback
import yaml


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


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

        populate_data = prepare_namespace(users.registrator, "consumer", namespace="WordCount",
                                          namespace_name="WordCount")

        mfc = MetaClassFactory(namespace="WordCount",
                               responsible_account="registrator")
        m = import_module("model.classes")
        mfc.add_class(getattr(m, "Text"))
        mfc.add_class(getattr(m, "TextCollection"))
        mfc.add_class(getattr(m, "TextStats"))
        sys.path.pop(0)
    

        result = client.new_class(registrator_id, registrator_credential,
                                  constants.lang_codes.LANG_PYTHON, mfc.classes)
        print result.keys()
        textcollection_info = result['model.classes.TextCollection']
        textstats_info = result['model.classes.TextStats']
        text_info = result['model.classes.Text']
        yaml_request_template = Template("""
---
textinterface: &textiface !!util.management.interfacemgr.Interface
  providerAccountName: registrator
  namespace: WordCount
  classNamespace: WordCount
  className: model.classes.Text
  propertiesInIface: !!set
  {% for property in text_info.properties %}
     ? {{ property.name }}
  {% endfor %}
  operationsSignatureInIface: !!set
  {% for operation in text_info.operations %}
    ? {{ operation.nameAndDescriptor }}
  {% endfor %}

textstatsinterface: &textstatsiface !!util.management.interfacemgr.Interface
  providerAccountName: registrator
  namespace: WordCount
  classNamespace: WordCount
  className: model.classes.TextStats
  propertiesInIface: !!set
  {% for property in textstats_info.properties %}
     ? {{ property.name }}
  {% endfor %}
  operationsSignatureInIface: !!set
  {% for operation in textstats_info.operations %}
    ? {{ operation.nameAndDescriptor }}
  {% endfor %}

textcollectioninterface: &textcollectioniface !!util.management.interfacemgr.Interface
  providerAccountName: registrator
  namespace: WordCount
  classNamespace: WordCount
  className: model.classes.TextCollection
  propertiesInIface: !!set
  {% for property in textcollection_info.properties %}
     ? {{ property.name }}
  {% endfor %}
  operationsSignatureInIface: !!set
  {% for operation in textcollection_info.operations %}
    ? {{ operation.nameAndDescriptor }}
  {% endfor %}

wordcountcontract: !!util.management.contractmgr.Contract
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  namespace: WordCount
  providerAccountName: registrator
  applicantsNames:
    ? registrator
    ? consumer
  interfacesInContractSpecs:
    - !!util.management.contractmgr.InterfaceInContract
      iface: *textiface
      implementationsSpecPerOperation:
        {% for operation in text_info.operations %}
          ? !!util.management.contractmgr.OpImplementations
            operationSignature: {{ operation.nameAndDescriptor }}
            numLocalImpl: 0
            numRemoteImpl: 0
        {% endfor %}
    - !!util.management.contractmgr.InterfaceInContract
      iface: *textstatsiface
      implementationsSpecPerOperation:
        {% for operation in textstats_info.operations %}
          ? !!util.management.contractmgr.OpImplementations
            operationSignature: {{ operation.nameAndDescriptor }}
            numLocalImpl: 0
            numRemoteImpl: 0
        {% endfor %}
    - !!util.management.contractmgr.InterfaceInContract
      iface: *textcollectioniface
      implementationsSpecPerOperation:
        {% for operation in textcollection_info.operations %}
          ? !!util.management.contractmgr.OpImplementations
            operationSignature: {{ operation.nameAndDescriptor }}
            numLocalImpl: 0
            numRemoteImpl: 0
        {% endfor %}

  publicAvailable: True

wordcountdataset: !!util.management.datasetmgr.DataSet
  providerAccountName: registrator
  name: wordcountdataset

wordcountdatacontract: !!util.management.datacontractmgr.DataContract
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  providerAccountName: registrator
  dataSetProvidedName: wordcountdataset
  applicantsNames:
    ? consumer
    ? registrator
  publicAvailable: True
""")
        yaml_request = yaml_request_template.render(
            text_info=text_info,
            textstats_info=textstats_info,
            textcollection_info=textcollection_info,
        )
        print "Performing operations..."
        yaml_response = client.perform_set_of_operations(registrator_id, registrator_credential, yaml_request)
        response = yaml.load(yaml_response)

    except Exception as e:
        print e
        print "Already registered!"
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
            dataset="wordcountdataset",
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

        from WordCount.model.classes import TextCollection, TextStats, Text

        text_collection = TextCollection()
        print dir(text_collection)

        # Small test on get_execution_environments_info
        print dataclay.runtime.get_execution_environments_info()

        print " # Start initialization of TextCollection instance"

        remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
        sanitize = lambda text: unicode(text.lower()).translate(remove_punctuation_map).split()
        all_texts = [
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus a leo vitae arcu tempus malesuada. Maecenas egestas diam a urna ultricies facilisis. Cras egestas, erat eu tincidunt eleifend, velit leo auctor odio, et dignissim ligula sem quis augue. Aenean at neque non odio molestie dictum. Integer porttitor lorem molestie felis varius dictum. Donec pretium ligula ipsum, id interdum mi efficitur ac. Nulla semper, sapien in maximus vestibulum, sapien dui efficitur neque, eu pharetra risus ligula quis sem. Proin sit amet tincidunt tortor.',
            'Fusce sagittis odio nisi, in luctus enim scelerisque sollicitudin. Donec orci purus, maximus id ultricies at, vehicula in turpis. Morbi sit amet eros accumsan, hendrerit nisi in, dapibus magna. Nam convallis consectetur neque, in faucibus leo scelerisque nec. Cras mattis metus id porttitor egestas. Curabitur feugiat lobortis vulputate. Phasellus vel dignissim lectus, at gravida diam. Nam vel massa a ex hendrerit sodales. Vestibulum iaculis enim vel metus elementum cursus non quis ligula. Pellentesque ut eleifend diam.',
            'Vestibulum sit amet neque vel nisl consequat placerat. Cras id eros ut enim blandit ornare. Pellentesque elementum purus nisi. Maecenas vitae tincidunt leo. Phasellus nisl enim, volutpat non erat pharetra, rutrum euismod tellus. Sed felis felis, imperdiet in nisl et, pretium bibendum metus. Suspendisse a orci metus. Sed laoreet scelerisque rhoncus. Ut fringilla malesuada nibh non elementum. Duis aliquam tempor justo. Mauris risus lorem, eleifend vel nulla in, ultricies vehicula justo. Quisque cursus nisi eget ante pellentesque, at ultrices purus blandit. Pellentesque maximus massa felis, id pulvinar augue viverra at.',
            'Quisque sagittis nibh ex, ultrices pharetra lacus suscipit non. Donec aliquam massa sit amet laoreet blandit. Aenean ac ipsum ornare, eleifend risus a, malesuada est. Cras tempus pharetra accumsan. Nunc sed tortor pharetra, elementum sapien eget, semper augue. Suspendisse volutpat metus sem, ut aliquam erat maximus finibus. Etiam accumsan in tellus eget rhoncus. Integer quam augue, egestas non consequat nec, pretium non augue. Nulla nec rhoncus enim, at ornare ante. Nulla quis aliquet eros. Sed hendrerit ac orci sed imperdiet. Sed commodo augue diam, eget consequat ligula vestibulum quis. Maecenas dignissim nisi et ipsum elementum aliquam. Sed cursus justo id lectus ultricies, sit amet posuere nibh lobortis.',
            'Aliquam tempor augue sapien, et vestibulum turpis luctus vulputate. Curabitur tortor nibh, facilisis et mauris at, consequat faucibus leo. Morbi congue purus sit amet elit vehicula lobortis. In ultrices interdum iaculis. Pellentesque nulla tellus, consectetur eu nisi nec, facilisis rhoncus velit. Donec egestas sed mi et fermentum. Vestibulum tristique, ligula non dictum lobortis, felis tortor feugiat neque, sodales imperdiet est quam in odio. Praesent id elit laoreet, suscipit sem id, dignissim leo. Quisque vitae turpis tortor. Morbi suscipit euismod cursus. Ut lacinia egestas erat eget molestie. Donec iaculis, sem nec eleifend sodales, dolor nibh fringilla tortor, eget pretium nulla lectus a justo.',
        ]

        for t in all_texts:
            new_text = Text()
            new_text.words = sanitize(t)
            new_text.make_persistent()
            print "  --> A certain text has OID: %s" % new_text.getID()
            text_collection.add_text(new_text)

        text_collection.make_persistent()
        print "  --> The collection has OID: %s" % text_collection.getID()

        print " # Done! We have a lot of Lorem Ipsum text"

        partial_result = TextStats(dict())
        partial_result.make_persistent()

        for t in text_collection.texts:
            r = t.word_count()
            if r is None:
                print "R is None!"
            partial_result.merge_with(r)

        print partial_result.current_word_count

        print "*******************"
        print "* Local Iterators *"
        print "*******************"
        # Now doing something for local iteration

        partial_result = TextStats(dict())
        partial_result.make_persistent()


        # TODO: SPLIT ITERATOR
        # for it in text_collection.split():
        #    print "Iterable: ", it

            # This should be in a function, and probably @task-ified
        #    for t in it:
        #        r = t.word_count()
                # Using a single partial_result kills the purpose of local iteration
        #        partial_result.merge_with(r)
        for t in text_collection:
            # This should be in a function, and probably @task-ified
            r = t.word_count()
            # Using a single partial_result kills the purpose of local iteration
            partial_result.merge_with(r)
            
        print partial_result.current_word_count

        print " # Doing the sequential local double-check"
        from collections import Counter
        result = Counter()
        for t in all_texts:
            result += Counter(sanitize(t))

        print result

        assert result == partial_result.current_word_count

    finally:
        # Maybe catch some exception? Do something something more?
        pass
    print "Finished"
    finish()

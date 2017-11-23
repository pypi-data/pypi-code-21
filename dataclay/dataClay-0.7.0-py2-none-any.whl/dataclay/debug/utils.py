from collections import namedtuple
from dataclay import runtime
from dataclay.conf import settings
from dataclay.core.constants import error_codes, lang_codes
from dataclay.core.exceptions.__init__ import DataclayException
from dataclay.core.network.exceptions import RemoteException
from dataclay.managers.classes.factory import MetaClassFactory
from importlib import import_module
import logging
import os
import sys
import yaml


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)

UsersStructures = namedtuple("UsersStructure", ["registrator", "consumer"])


def create_users():
    """Create a registrator and a user.

    Note that it is idempotent with analogous implementations, but if the users
    exists while the passwords do not match the credentials returned will be
    invalid.
    """
    client = runtime.ready_clients["@LM"]
    yaml_request = """
---
 - !!util.management.accountmgr.Account
   username: registrator
   credential: !!util.management.accountmgr.PasswordCredential
     password: registrator
   role: NORMAL_ROLE
 - !!util.management.accountmgr.Account
   username: consumer
   credential: !!util.management.accountmgr.PasswordCredential
     password: consumer
   role: NORMAL_ROLE
"""
    try:
        yaml_response = client.perform_set_of_new_accounts(settings.admin_id, settings.admin_credential, yaml_request)
        response_user_ids = yaml.load(yaml_response)

        registrator_id = response_user_ids["registrator"]
        consumer_id = response_user_ids["consumer"]

    except Exception as e:
        logger.debug("Error on user creation:\n%s", e)
        # Here any exception is considered as account exists!
        logger.info("Accounts existed, trying to retrieve their ID")
        registrator_id = client.get_account_id("registrator")
        consumer_id = client.get_account_id("consumer")
        logger.info("Account IDs obtained.")

    # If somebody had already registered the users but used a different password
    # then this will break because the passwords will not match
    return UsersStructures(registrator=(registrator_id, "registrator"),
                           consumer=(consumer_id, "consumer"))


def prepare_namespace(registrator, consumer_name, namespace="test_classes", namespace_name="test_classes"):
    """Prepare a Python namespace.
    :param registrator: The user that will perform the registration.
    :param consumer_name: The name of the user with the "consumer" role.
    :param namespace: The name of the namespace to be created.
    :return: The NamespaceID for the created (or existing) Namespace
    """
    logger.info("Preparing namespace")

    lm_client = runtime.ready_clients["@LM"]

    account_id = lm_client.get_account_id("registrator")

    # The tuple "registrator" is account_id, password, same as credential but with credential_id 
    credential = (None, registrator[1])

    try:
        return lm_client.get_namespace_id(account_id, credential, namespace_name)
    except DataclayException as e:
        print e
        yaml_request = """
---
{namespace}: !!util.management.namespacemgr.Namespace
  providerAccountName: {consumer_name}
  name: {namespace_name}
  language: LANG_PYTHON
""".format(consumer_name=consumer_name,
           namespace=namespace,
           namespace_name=namespace_name)

        logger.info("Performing populate operations")
        yaml_response = lm_client.perform_set_of_operations(account_id, credential, yaml_request)
        response = yaml.load(yaml_response)

        return response["namespaces"][namespace]


def prepare_dataclay_contrib(registrator, consumer_name, modules=None):
    """Prepare the dataclay namespace and register the contrib classes.
    :param registrator: The user that will perform the registration.
    :param consumer_name: The name of the user with "consumer" role.
    :param modules: List of modules that should be registered (default: all)
    """

    # The tuple "registrator" is account_id, password, same as credential but with credential_id 
    account_id = registrator[0]
    credential = (None, registrator[1])

    #########################################################################
    # First, we prepare the namespace:
    namespace_id = prepare_namespace(registrator, consumer_name,
                                     namespace="dc_classes",
                                     namespace_name="dc_classes")

    #########################################################################
    # Then we prepare the classes
    import dataclay.contrib
    if not modules:
        modules = dataclay.contrib.MODULES_TO_REGISTER

    sys.path.insert(0, os.path.dirname(dataclay.__file__))
    mfc = MetaClassFactory(namespace="dc_classes",
                           responsible_account="registrator")
    for m_str in modules:
        m = import_module("contrib.%s" % m_str)
        for c_str in getattr(m, "CLASSES_TO_REGISTER"):
            mfc.add_class(getattr(m, c_str))

    sys.path.pop(0)

    client = runtime.ready_clients["@LM"]

    result = client.new_class(account_id, credential, lang_codes.LANG_PYTHON, mfc.classes)
    print result.keys()

    logger.debug("NEW_CLASS result:\n%s", result)
    from jinja2 import Template

    class_interface_template = Template("""
{{ brief_name }}interface: &{{ brief_name }}iface !!util.management.interfacemgr.Interface
  providerAccountName: registrator
  namespace: dc_classes
  classNamespace: dc_classes
  className: {{ class_name }}
  propertiesInIface: !!set {% if class_info.properties|length == 0 %} { } {% endif %}
  {% for property in class_info.properties %}
    ? {{ property.name }}
  {% endfor %}
  operationsSignatureInIface: !!set {% if class_info.operations|length == 0 %} { } {% endif %}
  {% for operation in class_info.operations %}
    ? {{ operation.nameAndDescriptor }}
  {% endfor %}
""")

    class_interface_in_contract_template = Template("""
    - !!util.management.contractmgr.InterfaceInContract
      iface: *{{ brief_name }}iface
      implementationsSpecPerOperation: !!set {% if class_info.operations|length == 0 %} { } {% endif %}
        {% for operation in class_info.operations %}
          ? !!util.management.contractmgr.OpImplementations
            operationSignature: {{ operation.nameAndDescriptor }}
            numLocalImpl: 0
            numRemoteImpl: 0
        {% endfor %}
    """)

    classes_render = list()
    incontract_render = list()
    for class_name, class_info in result.items():
        brief_name = class_name.rsplit(".", 1)[-1].lower()
        classes_render.append(class_interface_template.render(
            brief_name=brief_name, class_name=class_name, class_info=class_info))
        incontract_render.append(class_interface_in_contract_template.render(
            brief_name=brief_name, class_info=class_info
        ))

    yaml_request = "---\n" + "\n".join(classes_render) + """
contribcontract: !!util.management.contractmgr.Contract
  beginDate: 2012-09-10T20:00:03
  endDate: 2020-09-10T20:00:04
  namespace: dc_classes
  providerAccountName: registrator
  applicantsNames:
    ? registrator
    ? consumer
  interfacesInContractSpecs:
""" + "\n".join(incontract_render) + """
  publicAvailable: True
"""      
    yaml_response = client.perform_set_of_operations(account_id, credential, yaml_request)
    response = yaml.load(yaml_response)

    #########################################################################
    # Return the contract for this public dataclay.contrib
    return response["contracts"]["contribcontract"]

"""Functions that can be called from the command line (dataClay tool related).

See the __main__.py entrypoint for more information on the scenarios in which
the functions here are called.
"""
import atexit

from dataclay import management
from dataclay.api import init_connection
from dataclay.core import constants
from dataclay.managers.classes.factory import MetaClassFactory
from jinja2 import Template
import os
import sys
from uuid import UUID
import yaml


def _establish_client():
    client = init_connection(os.getenv("DATACLAYCLIENTCONFIG", "./cfgfiles/client.properties"))
    # The client has been correctly acquired, set the "shutdown hook"
    atexit.register(lambda: client.close())
    return client


def register_model(username, password, namespace, python_path):
    client = _establish_client()

    credential = (None, password)
    user_id = client.get_account_id(username)

    mfc = MetaClassFactory(namespace=namespace,
                           responsible_account=username)

    full_python_path = os.path.abspath(python_path)

    # Load the model_package from the path
    if full_python_path not in sys.path:
        sys.path.insert(0, python_path)

    n_base_skip = len(full_python_path.split(os.sep))

    for dirpath, dirnames, filenames in os.walk(full_python_path):
        base_import = ".".join(
            dirpath.split(os.sep)[n_base_skip:]
        )

        for f in filenames:
            if not f.endswith(".py"):
                continue

            if f == "__init__.py":
                if not base_import:
                    print >> sys.stderr, "Ignoring `__init__.py` at the root of the model folder " \
                                         "(do not put classes there!)"
                    continue
                import_str = base_import
            else:
                if not base_import:
                    import_str = os.path.splitext(f)[0]
                else:
                    import_str = "%s.%s" % (base_import, os.path.splitext(f)[0])

            # Try to import
            mfc.import_and_add(import_str)

    result = client.new_class(user_id,
                              credential,
                              constants.lang_codes.LANG_PYTHON,
                              mfc.classes)

    print >> sys.stderr, "Was gonna register: %s\nEventually registered: %s" % (
        mfc.classes, result.keys())

    if len(result.keys()) == 0:
        print >> sys.stderr, "No classes registered, exiting"
        return

    interfaces = list()
    interfaces_in_contract = list()
    for class_name, class_info in result.iteritems():
        ref_class_name = class_name.replace('.', '')

        interfaces.append(Template("""
{{ class_name }}interface: &{{ ref_class_name }}iface !!util.management.interfacemgr.Interface
  providerAccountName: {{ username }}
  namespace: {{ namespace }}
  classNamespace: {{ namespace }}
  className: {{ class_name }}
  propertiesInIface: !!set {% if class_info.properties|length == 0 %} { } {% endif %}
  {% for property in class_info.properties %}
     ? {{ property.name }}
  {% endfor %}
  operationsSignatureInIface: !!set {% if class_info.operations|length == 0 %} { } {% endif %}
  {% for operation in class_info.operations %} 
    ? {{ operation.nameAndDescriptor }}
  {% endfor %}
""").render(
            class_name=class_name,
            ref_class_name=ref_class_name,
            username=username,
            namespace=namespace,
            class_info=class_info))

        interfaces_in_contract.append(Template("""
    - !!util.management.contractmgr.InterfaceInContract
      iface: *{{ ref_class_name }}iface
      implementationsSpecPerOperation: !!set {% if class_info.operations|length == 0 %} { } {% endif %}
        {% for operation in class_info.operations %}
          ? !!util.management.contractmgr.OpImplementations
            operationSignature: {{ operation.nameAndDescriptor }}
            numLocalImpl: 0
            numRemoteImpl: 0
        {% endfor %}
""").render(
            class_name=class_name,
            ref_class_name=ref_class_name,
            class_info=class_info))

    contract = Template("""
{{ namespace }}contract: !!util.management.contractmgr.Contract
  beginDate: 1980-01-01T00:00:01
  endDate: 2055-12-31T23:59:58
  namespace: {{ namespace }}
  providerAccountName: {{ username }}
  applicantsNames:
    ? {{ username }}
  interfacesInContractSpecs:
{{ interfaces_in_contract }}
  publicAvailable: True
""").render(
        namespace=namespace,
        username=username,
        interfaces_in_contract="\n".join(interfaces_in_contract)
    )

    yaml_request = "\n".join(interfaces) + contract

    yaml_response = client.perform_set_of_operations(user_id, credential, yaml_request)
    response = yaml.load(yaml_response)

    print >> sys.stderr, " ===> The ContractID for the registered classes is:",
    print response["contracts"]["%scontract" % namespace]


def get_stubs(username, password, contract_ids_str, path):
    client = _establish_client()

    try:
        contracts = map(UUID, contract_ids_str.split(','))
    except ValueError:
        raise ValueError("This is not a valid list of contracts: %s" % contract_ids_str)
    credential = (None, password)

    user_id = client.get_account_id(username)
    management.prepare_storage(path)

    babel_data = client.get_babel_stubs(
        user_id, credential, contracts)

    with open(os.path.join(path, "babelstubs.yml"), 'wb') as f:
        f.write(babel_data)

    all_stubs = client.get_stubs(
        user_id, credential, constants.lang_codes.LANG_PYTHON, contracts)

    for key, value in all_stubs.iteritems():
        with open(os.path.join(path, key), 'wb') as f:
            f.write(value)

    management.deploy_stubs(path)

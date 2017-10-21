"""
Assumptions:
    - POST always means CREATE, PUT always means UPDATE
    - POST is the only operation on non-existing resources

"""

# TODO Preveri kako je z različnimi (required) parametri za različne verzije
# TODO Če imajo vsi enake parametre, zgeneriraj eno metodo
# TODO Ali pa na koncu samo za latest objekt naredi alias. Post -> Post_22
# TODO V kakem formatu je datetime?

# TODO Feed ima 2x get, Post ima 2x post
# TODO Poglej vse, ki imajo 2x isto metodo in ročno dodaj pravila

# TODO Po tem spusti čez library linter oz. nek tool, ki popravlja, npr. dolžino vrstic


import os
import re
import json
import shutil

import generate.iterable_names as iterable_utils


IGNORE_MODELS = ['Menu_21', 'Menu_20', 'MobileDevice_4']


def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return s2


def snake_to_capital(snake_str):
    components = snake_str.split('_')
    return "".join(x.title() for x in components)


def remove_version(name):
    return re.sub('_[0-9]+', r'', name)


def function_name(model, method):
    trans = {
        'put': 'update',
        'post': 'create',
    }
    met = method['Type'].lower()
    if met in trans:
        met = trans[met]

    return met
    # name = met + "_" + remove_version(camel_to_snake(model['Name']))
    # return name.replace("_g_mail", "_gmail").replace("_log_on_user", "_logon_user")


def pp(x):
    return json.dumps(x, sort_keys=True, indent=4, separators=(',', ': '))


api_index_file = open("api-index.json")
api_index = json.load(api_index_file)
api_index_file.close()

api_index_link_list = api_index['ApiIndexLinkList']


endpoints = {}

for model in api_index_link_list:
    # print(model)

    if model['Href'] not in endpoints:
        endpoints[model['Href']] = []

    endpoints[model['Href']].append(model)

modules = {}
i = 0
for endpoint, endpoint_models in endpoints.items():
    i += 1

    auto_endpoint_mapping = {
        "/": "api_index",
    }

    endpoint_tokens = endpoint.split("/")
    get_parameters = []
    mandatory_parameters = []
    if endpoint in auto_endpoint_mapping:
        new_endpoint_key = auto_endpoint_mapping[endpoint]
    elif len(endpoint_tokens) > 1:
        if len(endpoint_tokens) == 2:  # 2 tokens
            if '{' not in endpoint:
                new_endpoint_key = "_".join(endpoint_tokens)
            else:
                new_endpoint_key = endpoint_tokens[0]
                get_parameters = [endpoint_tokens[1][1:-1]]
                # print("--2{", endpoint, endpoint_tokens[1][1:-1])
                # continue
        elif len(endpoint_tokens) == 3:  # 3 tokens
            if "{" not in endpoint:
                new_endpoint_key = endpoint.replace("/", "_")
            else:
                if endpoint_tokens[1].startswith("{") and endpoint_tokens[2].count("{") == 0:
                    new_endpoint_key = "_".join([endpoint_tokens[0], endpoint_tokens[2]])
                    mandatory_parameters = [endpoint_tokens[1][1:-1]]
                    # print("--3-", endpoint, new_endpoint_key, mandatory_parameters)
                    # continue
                elif endpoint_tokens[1].count("{") == 0 and endpoint_tokens[2].startswith("{"):
                    new_endpoint_key = "_".join([endpoint_tokens[0], endpoint_tokens[1]])
                    mandatory_parameters = [endpoint_tokens[2][1:-1]]
                    # print("--3-", endpoint, new_endpoint_key, mandatory_parameters)
                    # continue
                else:
                    print("--3-", endpoint)
                    continue
        else:
            print("--4+", endpoint)
            continue
    else:
        new_endpoint_key = endpoint

    resources = []
    allowed_methods = set()
    for model in endpoint_models:
        for method in model['Methods']:
            allowed_methods.add(method['Type'])
            # print("  ", endpoint, method['Type'], method['Description'])

        resources.append((model['Name'], model['ContentTypes']))

    allowed_methods.discard('OPTIONS')

    # print(endpoint, len(endpoint_models), allowed_methods)
    # print()

    # MANUAL FIXES
    try:
        if new_endpoint_key == "notification":
            for model in endpoint_models:
                if model['Name'] == 'ListOfNotificationsPage_22':
                    for method in model['Methods']:
                        if method['Type'] == 'GET':
                            already_contains = any(map(lambda x: x['Name'] == 'longPolling', method['Parameters']))
                            if not already_contains:
                                missing = {'IsList': False, 'Required': False, 'Name': 'longPolling', 'Type': 'Boolean',
                                           'Description': 'Perform long polling while reading the resource.'}
                                method['Parameters'].insert(3, missing)
                                break
    except Exception:
        print("Failed to execute manual fix for notifications endpoint - add missing longPolling parameter.")
    # /MANUAL FIXES

    if new_endpoint_key not in modules:
        modules[new_endpoint_key] = {
            'endpoint': endpoint,
            # 'allowed_methods': list(allowed_methods),  # This information is useless
            'resources': resources,
            'url_parameters_existing_resources': get_parameters,  # GET-only URL parameters
            'url_parameters': mandatory_parameters,  # Mandatory URL parameters
            'models': [model for model in endpoint_models],
        }
    else:
        if '/{' not in modules[new_endpoint_key]['endpoint'] and '/{' in endpoint:
            print("FIXING ENDPOINT {} -> {}".format(modules[new_endpoint_key]['endpoint'], endpoint))
            modules[new_endpoint_key]['endpoint'] = endpoint
        modules[new_endpoint_key]['resources'] += resources
        modules[new_endpoint_key]['url_parameters_existing_resources'] += get_parameters
        modules[new_endpoint_key]['url_parameters'] += mandatory_parameters
        modules[new_endpoint_key]['models'] += [model for model in endpoint_models]
        # TODO What to do with url parameters?
        print("CARE", endpoint, new_endpoint_key)

    """
    # if endpoint == 'user/{userId}':
    # if endpoint == 'reminder/{reminderId}':
    if endpoint == 'feed':
        for model in endpoint_models:
            print(new_endpoint_key)
            print("    ", pp(model))
    # """

    # if i >= 1: break

# print(4*"\n")


"""
# API Index
for endpoint_key, module in modules.items():
    # print(module_name, module)
    # print(endpoint_key + ": " + ("/" if module['endpoint'] != "/" else "") + module['endpoint'])
    # print(pp(module))
    # for method in module['allowed_methods']: print("  ", method.lower() + "_" + endpoint_key)

    for model in module['models']:
        print("  ", model['Name'], "\t" + model['Description'])
        for method in model['Methods']:
            if method['Type'] == 'OPTIONS':
                continue
            func = function_name(model, method)
            print("    ", func, "\t" + method['Description'])

    print()

    # break
exit(0)
# """

# print(json.dumps(modules))
# print(json.dumps(api_index_link_list))

print()


def generate_parameter_doc(name, description="", p_type="", available_values=None):
    if available_values:
        description += "\n    Available values:"
        for val in available_values:
            description += "\n    - {}".format(val)
    parameter_doc_template = """:param {name}: {description}\n:type {name}: {type}\n"""
    return parameter_doc_template.format(name=name, type=p_type, description=description).split("\n")


def generate_return_doc(description, r_type):
    return ":return: {description}\n:rtype: {type}".format(description=description, type=r_type).split("\n")


def generate_function(endpoint_key, endpoint, model, method):
    # TODO Argumenti funkcije
    # TODO Kaj pa attach-anje file-ov?
    # @classmethod
    function_doc_template = """
def {function_name}({function_arguments}):
    \"\"\"{docs}
    \"\"\"
    url_parameters = {url_parameters}
    endpoint_parameters = {endpoint_parameters}
    endpoint = '{endpoint}'.format(**endpoint_parameters)
    add_headers = {{
        'Content-Type': '{headers-content-type}',
        'Accept': '{headers-accept}' if accept_type is None else accept_type,{additional_headers}
    }}{define_data}{additional_code}
    response = self.api_client.api_call('{http_method}', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id{request_set_data})
    {downloadable_return}
    {return}
    """
    # return response.json()

    modified_endpoint = endpoint if not endpoint.startswith('/') else endpoint[1:]
    t = modified_endpoint.split("/")
    if len(t) > 1 and t[len(t)-1].startswith('{'):
        if method['Type'] in ['POST', 'OPTIONS']:
            modified_endpoint = "/".join(t[:len(t)-1])  # Remove last parameter for CREATE operation

    docs = [
        method['Description'],
        "",
    ]

    set_obj = False
    endpoint_parameters = []
    url_parameters = []
    function_arguments = []
    function_arguments_docs = []
    function_optional_arguments = []
    function_optional_arguments_docs = []
    handles_files = False

    function_arguments.append('self')
    # function_arguments.append('cls')
    # docs.extend(generate_parameter_doc('cls', '', 'ApiClient'))

    if model['Name'].startswith("Document_") or model['Name'].startswith('UserAvatar_'):
        handles_files = True
        if method['Type'] in ['POST', 'PUT']:
            set_obj = True  # Actually do set an object, but a different one
            function_arguments.append('obj')
            docs.extend(generate_parameter_doc('obj', 'Object to be persisted'))  # io.BufferedIOBase, io.TextIOBase
            function_arguments.append('obj_filename')
            docs.extend(generate_parameter_doc('obj_filename', 'Filename of object to be persisted', 'str'))
    elif method['Type'] in ['POST', 'PUT']:
        set_obj = True
        function_arguments.append('obj')
        docs.extend(generate_parameter_doc('obj', 'Object to be persisted', model['Name']))

    if model['Name'].startswith("PostBody"):
        print(module['url_parameters'], module['url_parameters_existing_resources'])

    for param in module['url_parameters']:
        function_arguments.append(param)
        docs.extend(generate_parameter_doc(param))
        if '{' + param + '}' in endpoint:
            endpoint_parameters.append("'{0}': {0}".format(param))
        else:
            url_parameters.append("'{0}': {0}".format(param))

    if method['Type'] not in ['POST', 'OPTIONS']:
        for param in module['url_parameters_existing_resources']:
            function_arguments.append(param)
            docs.extend(generate_parameter_doc(param))
            # url_parameters.append("'{0}': {0}".format(param))
            endpoint_parameters.append("'{0}': {0}".format(param))

    if 'Parameters' in method:
        for param in method['Parameters']:
            a_val = param['AvailableValues'] if 'AvailableValues' in param else None
            d = generate_parameter_doc(param['Name'], param['Description'], param['Type'], a_val)
            if param['Required']:  # TODO Default value?
                function_arguments.append(param['Name'])
                function_arguments_docs.extend(d)
            else:
                function_optional_arguments.append(param['Name'] + "=None")
                function_optional_arguments_docs.extend(d)

            url_parameters.append("'{0}': {0}".format(param['Name']))

            # TODO Other parameter descriptors - IsList, AvailableValues ???
            # print(param)

    else:
        print("----", "NO 'Parameters'", method)

    # Impersonate
    function_optional_arguments.append("impersonate_user_id=None")
    function_optional_arguments_docs.extend(generate_parameter_doc("impersonate_user_id", "", 'str'))

    # Headers - Accept
    function_optional_arguments.append("accept_type=None")
    function_optional_arguments_docs.extend(generate_parameter_doc("accept_type", "", 'str', ))

    docs.extend(function_arguments_docs + function_optional_arguments_docs)
    if method['Type'] == 'DELETE':
        return_doc = generate_return_doc("True if object was deleted, otherwise an exception is raised", "bool")
    else:
        return_doc = generate_return_doc("", model['Name'])
    docs.extend(return_doc)

    docs = "".join(["\n" + 4 * " " + line for line in docs])

    # Don't know if this if statement is ok - probably not
    headers_content_type = ''
    headers_accept = ''
    if 'ContentTypes' in model:
        headers_content_type = model['ContentTypes'][0]
        if not headers_content_type.endswith('json'):
            if len(model['ContentTypes']) > 1:
                headers_content_type = model['ContentTypes'][1]

        if not headers_content_type.endswith('json'):
            print(model['Name'], headers_content_type)

        headers_accept = headers_content_type
    else:
        print('ContentTypes missing', model)

    content_type_to_class[headers_content_type] = model['Name']

    if handles_files and set_obj:
        if model['Name'].startswith('UserAvatar_'):
            if method['Type'] == 'PUT':
                headers_content_type = 'application/octet-stream'
        else:
            headers_content_type = 'application/octet-stream'

    url_parameters = "{\n" + ("".join([8 * " " + d + ",\n" for d in url_parameters])) + "    }"
    endpoint_parameters = "{\n" + ("".join([8 * " " + d + ",\n" for d in endpoint_parameters])) + "    }"

    method_name = function_name(model, method)
    additional_code = ""
    additional_headers = ""
    if not handles_files:
        request_set_data = ", data=json.dumps(data)" if set_obj else ""
    else:
        request_set_data = ", data=obj" if set_obj else ""
        if method['Type'] in ['POST', 'PUT']:
            additional_headers += "\n        " + "'X-Upload-File-Name': obj_filename,"

    return_value = 'return fill(' + model['Name'] + ', response.json()' + \
                   ', content_type=response.headers[\'Content-Type\']' + \
                   ', silence_exceptions=self.api_client.silence_fill_exceptions)'
    if method['Type'].lower() == 'delete':
        return_value = "return True"

    return function_doc_template.format(**{
        'function_name': method_name,
        'function_arguments': ", ".join(function_arguments + function_optional_arguments),
        'docs': docs,
        'url_parameters': url_parameters,
        'endpoint_parameters': endpoint_parameters,
        'define_data': "\n    " + "data = export_dict(obj)" if set_obj and not handles_files else "",
        'request_set_data': request_set_data,
        'headers-content-type':  headers_content_type,
        'headers-accept': headers_accept,
        'endpoint': modified_endpoint,
        'http_method': method['Type'].lower(),
        'class_name': model['Name'],
        'additional_code': additional_code,
        'additional_headers': additional_headers,
        'downloadable_return': "if accept_type == 'application/octet-stream' or accept_type.startswith('image/'):\n        return response.content" if handles_files and method['Type'] == 'GET' else "",
        'return': return_value,
    }), method_name

"""
for endpoint_key, module in modules.items():
    for model in module['models']:
        endpoint = module['endpoint']
        for method in model['Methods']:
            definition = generate_function(endpoint_key, endpoint, model, method)
            print(definition)
        break
exit(0)
# """

content_type_to_class = {}

endpoints_module_name = 'endpoints'
base_path = '../snapp_email/' + endpoints_module_name + '/'
if os.path.exists(base_path):
    shutil.rmtree(base_path)  # ignore_errors=True

os.makedirs(base_path, exist_ok=True)
fh_endpoints = open(base_path + "__init__.py", mode='w')
fh_endpoints_code = []
fh_endpoints_imports = []

for endpoint_key in sorted(modules):
    module = modules[endpoint_key]
    # Create folder
    module_path = base_path + endpoint_key + "/"
    endpoint_module_name = snake_to_capital(endpoint_key) + "Endpoint"

    os.makedirs(module_path, exist_ok=True)
    fh_endpoint = open(module_path + "__init__.py", mode='w')

    if endpoint_module_name == 'AppointmentEndpoint':
        print()

    module['models'].sort(key=lambda x: x['Name'])  # Sort by name for easier tracking of code changes

    for model in module['models']:
        if model['Name'] in IGNORE_MODELS: continue
        fh_endpoint.write('from .{0} import {0}\n'.format(model['Name'] + "Endpoint"))
    fh_endpoint.write("\n")
    fh_endpoint.write("""
class {}:
    def __init__(self, api_client):
        self._api_client = api_client
""".format(endpoint_module_name))

    for model in module['models']:
        if model['Name'] in IGNORE_MODELS: continue

        # Create file
        endpoint = module['endpoint']
        model_path = module_path + model['Name'] + "Endpoint" + ".py"
        fh = open(model_path, mode='w')
        fh.write('"""\nAuto generated code\n\n"""\n\n')
        fh.write('import json\n')
        fh.write('from snapp_email.datacontract.classes import {}\n'.format(model['Name']))
        fh.write('from snapp_email.datacontract.utils import export_dict, fill\n')
        # fh.write('from api_client import ApiClient\n')
        # fh.write('from api_client import ApiEndpoint\n')
        fh.write('\n')

        # {class_name}(ApiEndpoint)
        class_template = """
class {class_name}:
    def __init__(self, api_client):
        self.api_client = api_client
"""

        fh.write(class_template.format(
            class_name=model['Name'] + "Endpoint"
        ))

        method_list = [method['Type'] for method in model['Methods']]
        func_name_list = []
        for method in model['Methods']:
            definition, func_name = generate_function(endpoint_key, endpoint, model, method)
            func_name_list.append(func_name)
            c = sum(1 for f in func_name_list if f == func_name)
            if c > 1:
                definition = definition.replace(
                    "def {}".format(func_name),
                    "def {}_{}".format(func_name, c)
                )
            definition = definition.rstrip()
            definition = "".join([4*" " + l + "\n" for l in definition.split("\n")])
            definition = definition.rstrip()
            fh.write(definition + "\n")

        fh.close()

        # Add
        endpoint_entry = """
    @property
    def {resource}(self):
        \"\"\"
        :return: {resource}Endpoint
        \"\"\"
        return {resource}Endpoint(self._api_client)
        """
        # fh_endpoints_code.append(endpoint_entry.format(resource=model['Name']))
        fh_endpoint.write(endpoint_entry.format(resource=model['Name'] + ""))
        # fh_endpoint_imports.append("from {}.{} import {}".format(endpoints_module_name, endpoint_key, model['Name']))

    # Create <EndpointName>Endpoint class

    fh_endpoint.close()

    endpoints_entry = """
    @property
    def {endpoint_key}(self):
        \"\"\"
        :return: {endpoint_name}
        \"\"\"
        return {endpoint_name}(self)
    """  # return {endpoint_name}(self._api_client)
    fh_endpoints_code.append(endpoints_entry.format(endpoint_key=endpoint_key,
                                                    endpoint_name="" + endpoint_key + "." + endpoint_module_name))

    # _i = "{}.{}".format(endpoints_module_name, endpoint_key)
    fh_endpoints_imports.append("from . import {}".format(endpoint_key))

# fh_endpoints.write('import ' + endpoints_module_name + '\n')
for imp in sorted(fh_endpoints_imports):
    fh_endpoints.write(imp + "\n")
fh_endpoints.write('\n')
endpoints_code = """
class ApiEndpoints:
"""
fh_endpoints.write(endpoints_code)
for code in fh_endpoints_code:
    fh_endpoints.write(code)

fh_endpoints.close()

# Save some manually generated mappings
# This replaces the "Run `generate/iterable_names.py`" step
iterable_utils.save_iterable_details(path=base_path)
iterable_utils.save_resource_type_to_class_mappings(content_type_to_class, path=base_path)

print("Done")

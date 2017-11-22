from io import StringIO
import ramlfications as r
import json


def raml_from_file(filepath):
    """
    Load RAML object from filepath.

    @param filepath string: RAML specs file path.

    returns raml document root object.
    """
    with open(filepath) as fp:
        return r.parse(fp)


def raml_from_string(ramlsource):
    """
    Load RAML object from string.
    @param ramlsource string: RAML specs string.

    returns raml document root object
    """
    sp = StringIO(ramlsource)
    root = r.parse(sp)
    return root


class SporeFile:

    def __init__(self):
        self.base_url = ""
        self.version = ""
        self.methods = {}
        self.authority = ""
        self.name = ""
        self.meta = {
            "documentation": ""
        }
        self.media_type = ""

    def __str__(self):
        # del d['raml_obj']
        return json.dumps(self, default=lambda o: {k: v for (k, v) in o.__dict__.items() if v},
                          sort_keys=True, indent=4)


class SporeMethod:

    def __init__(self, name='', api_base_url='', method='', path='',
                 required_params=None, optional_params=None,
                 expected_status=None, required_payload=False, description='',
                 authentication=None, formats=None, base_url='',
                 documentation='', middlewares=None,
                 global_authentication=None, global_formats=None,
                 defaults=None):

        self.name = name
        self.path = path
        self.method = method
        self.required_params = required_params or []
        self.optional_params = optional_params or []
        self.required_payload = required_payload or []
        self.description = description
        self.documentation = documentation
        self.middlewares = middlewares or []
        self.formats = formats or []
        self.authentication = authentication or ""
        self.global_authentication = global_authentication
        self.global_formats = global_formats or []
        self.defaults = defaults
        self.form_data = {}
        self.media_type = ""
        self.expected_status = expected_status

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


def normalize_path(path):
    return path.replace("{", ":").replace("}", "")


def spore_from_raml_object(ramlobject):
    """
    Create SPORE from RAML specs.

    @param ramlsource str: RAML specs string.

    returns SPORE specs.
    """
    api = ramlobject
    spore_file = SporeFile()
    spore_file.base_url = api.base_uri
    spore_file.version = api.version or ''
    spore_file.media_type = api.media_type

    for resource in api.resources:
        meth = SporeMethod()

        meth.path = normalize_path(resource.path)
        try:
            meth.name = resource.raw[resource.method]['displayName']
        except:
            meth.name = resource.name
        if resource.uri_params:
            meth.required_params = [
                param.name for param in resource.uri_params if param.required]
        if resource.query_params:
            meth.optional_params = [
                param.name for param in resource.query_params]
        meth.documentation = resource.desc
        meth.description = resource.desc
        meth.expected_status = [res.code for res in resource.responses]
        meth.required_payload = []
        try:
            if resource.body:
                meth.required_payload = list(resource.body[
                    0].raw['application/json']['properties'].keys())
        except:
            meth.required_payload = []
        meth.method = resource.method.upper()
        # meth.form_data = resource.form_data
        meth.media_type = resource.media_type
        spore_file.methods[meth.name] = meth
    return spore_file


def spore_from_raml_file(filepath):
    return spore_from_raml_object(raml_from_file(filepath))


def spore_from_raml_string(source):
    return spore_from_raml_object(raml_from_string(source))

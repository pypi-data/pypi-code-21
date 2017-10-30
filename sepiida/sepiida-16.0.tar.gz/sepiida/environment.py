import attrdict
import os
import sys

class Undefined():
    pass

class UndefinedError(Exception):
    "Raised when a required setting is not provided"
    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

class ParseError(Exception):
    def __init__(self, errors):
        super().__init__()
        self.errors = errors

class Specification():
    "The full specification of all variables in the environment"
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def parse(self):
        "Parse the variables that are defined in the given spec from the environment"
        results = attrdict.AttrDict()
        errors = set()
        for k, v in self.kwargs.items():
            try:
                results[k] = v.parse(os.environ.get(k))
            except ValueError as e:
                errors.add(ValueError("The value for {} was invalid: {}".format(k, e)))
            except UndefinedError:
                errors.add(UndefinedError("The variable {} was undefined and has no default value".format(k)))
        if errors:
            raise ParseError(errors)
        return results

class Variable():
    "A single environment variable"
    def __init__(self, default=Undefined, parser=None, docs=None):
        self.default = default
        self.docs    = docs
        self.parser  = parser

    def parse(self, value):
        "Parse the given value or raise ValueError"
        if value is None:
            if self.default is Undefined:
                raise UndefinedError
            value = self.default
        return self.parser(value) if self.parser else value

class VariableInteger(Variable):
    def parse(self, value):
        return int(super().parse(value))

class VariableBoolean(VariableInteger):
    def parse(self, value):
        value = super().parse(value)
        if value not in (0, 1):
            raise ValueError("Boolean variables should be either '0' or '1'")
        return bool(value)

class VariableFloat(Variable):
    def parse(self, value):
        return float(super().parse(value))

class VariableList(Variable):
    def parse(self, value):
        val = super().parse(value)
        return val.split(';')

DEFAULT_SPEC = Specification(
    API_TOKEN       = Variable('some api token'),
    SECRET_KEY      = Variable('keep it secret, keep it safe'),
    SEPIIDA_JWT_KEY = Variable(''),
    SERVER_NAME     = Variable('sepiida.service'),
    STORAGE_SERVICE = Variable('https://woodhouse.service/'),
    TRUSTED_DOMAINS = VariableList('service;example.com;another-example.com'),
    USER_SERVICE    = Variable('https://users.service/'),
)

def parse(spec):
    try:
        default_settings = DEFAULT_SPEC.parse()
        settings = spec.parse()
        default_settings.update(settings)
        parse.settings = default_settings
        return default_settings
    except ParseError as parse_error:
        message = (
            "The program cannot start because there were errors parsing the "
            "settings from environment variables: \n\t{}"
        ).format('\n\t'.join([str(e) for e in parse_error.errors]))
        sys.exit(message)
parse.settings = None

def get():
    if not parse.settings:
        raise Exception((
            "You have attempted to access the environment settings without having "
            "first parsed them from a specification. Please first call parse(spec) "
            "with a valid environment specification before calling the get() function"
        ))
    return parse.settings

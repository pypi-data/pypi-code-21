import attrdict
import yaml


def _parse_bool(data):
    if data in (True, 'true', '1'):
        return True
    elif data in (False, 'false', '0'):
        return False
    else:
        raise ValueError("{} must be one of true/false or 1/0".format(data))

class Option():
    SPECIAL_PARSERS = {
        bool: _parse_bool,
    }
    def __init__(self, option_type, testing, description=None):
        if not (isinstance(testing, option_type) or testing is None):
            raise Exception("You cannot specify a testing value of {} because it is not of type {}".format(testing, option_type.__name__))
        self.option_type = option_type
        self.testing     = testing
        self.description = description

    def parse(self, data):
        parser = self.SPECIAL_PARSERS.get(self.option_type, self.option_type)
        return parser(data)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "sepiida.config.Option(option_type={}, testing={})".format(self.option_type.__name__, self.testing)

def _readfile(filename):
    with open(filename, 'r') as f:
        return f.read()

def get():
    if not get.cached:
        raise Exception("You must call sepiida.config.load first")
    return get.cached
get.cached = None

def load(filename, spec):
    content = _readfile(filename)
    get.cached = parse(content, spec)
    return get.cached

def parse(content, spec):
    data = yaml.load(content)
    config = {}
    for name, option in spec.items():
        try:
            config[name] = option.parse(data[name])
        except KeyError:
            raise KeyError("The config option '{}' is required and was not provided".format(name))
        except ValueError:
            err = ("The config option '{}' was provided with value "
                   "'{}' which could not be parsed into a {}").format(name, data[name], option.option_type.__name__)
            raise ValueError(err)
    return attrdict.AttrDict(config)

def extract_test_values(spec):
    return attrdict.AttrDict({k: v.testing for k, v in spec.items()})

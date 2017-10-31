

def yaml_from_file(filename_):
    with open(filename_, 'r') as iss:
        content = iss.read()
        result = yaml_load(content)
    return result


def yaml_load(text):
    from ruamel.yaml import YAML

    yaml = YAML()
    return yaml.load(text)

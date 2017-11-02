import os
import argparse
import ast
from jinja2 import Environment, FileSystemLoader

from tinyj2 import __description__

_HAS_JSON = False
try:
    import json
    _HAS_JSON = True
except ImportError:
    pass

_HAS_YAML = False
try:
    import yaml
    _HAS_YAML = True
except ImportError:
    pass


def main():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('--template-dir', '-t', default='templates/', help='Directory containing templates')
    parser.add_argument('--output-dir', '-o', default='./', help='Directory to store output files')

    parser.add_argument('--skip-env', action='store_true', default=False, help='Do not import environment variables')
    parser.add_argument('--json', help='Import parameters from json file')
    parser.add_argument('--yaml', help='Import parameters from yaml file')
    parser.add_argument('--params', '-p', help='Import parameters from string (python dict format)')
    args = parser.parse_args()

    paths = ['template_dir', 'output_dir', 'json', 'yaml']
    for path in paths:
        attr = getattr(args, path)
        if attr:
            setattr(args, path, os.path.expanduser(attr))

    template_dir = os.path.expanduser(args.template_dir)
    output_dir = os.path.expanduser(args.output_dir)

    j2_env = Environment(loader=FileSystemLoader(template_dir))

    type_matrix = {}
    type_matrix['json'] = json.load if _HAS_JSON else None
    type_matrix['yaml'] = yaml.load if _HAS_YAML else None

    template_params = {}
    for input_type, load_fn in type_matrix.items():
        input_file = getattr(args, input_type)
        if input_file:
            if not load_fn:
                print('Tried to import parameters from file, but module {} is not available.'.format(input_type))
                return
            else:
                with open(input_file) as f:
                    imported = load_fn(f)
                template_params.update(imported)

    if not args.skip_env:
        env = dict(os.environ.items())
        template_params['env'] = env

    if args.params:
        imported = ast.literal_eval(args.params)
        template_params.update(imported)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for template in j2_env.list_templates():
        if os.path.basename(template) == template:
            rendered = j2_env.get_template(template).render(**template_params)
            output_file = os.path.join(output_dir, template)
            with open(output_file, 'w') as f:
                f.write(rendered)


if __name__ == '__main__':
    main()


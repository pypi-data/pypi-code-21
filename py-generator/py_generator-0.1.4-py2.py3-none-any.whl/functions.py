import os
import sys

from decorators import (
    receives_params,
)

from file_manager.manager import (
    append_file_content_to,
    create_files,
)

from utils.utils import (
    get_extensions_dict,
    get_files_dict,
    get_config_dict,
    get_wildcards_dict,
    replace_content,
)

dirs_dict = get_config_dict()

extensions_dict = get_extensions_dict()
files_dict = get_files_dict()
wildcards_dict = get_wildcards_dict()


@receives_params('component')
def create_component(required_params):
    recipe = required_params['recipe']
    files_to_create = [{
        'ext': 'js', 'suffix': '.component'
    }, {
        'ext': 'scss', 'suffix': '.scoped'
    }, {
        'ext': 'html', 'suffix': '.raw'
    }, {
        'ext': 'vue', 'suffix': ''
    }, {
        'ext': 'js', 'suffix': 'index'
    }]

    base_path = dirs_dict['base'] + dirs_dict['components_path']
    resource_path = "%s%s/" % (base_path, required_params['component_name'])
    create_files(files_to_create, recipe, resource_path, required_params['component_name'])


@receives_params('component')
def create_filter(required_params):
    recipe = required_params['recipe']
    
    files_to_create = [{
        'ext': 'js', 'suffix': '.filter'
    }]

    resource_path = dirs_dict['base'] + dirs_dict['filters_path']

    create_files(files_to_create, recipe, resource_path, required_params['filter_name'])

    templates_path = '%s/%s/%s' % (os.path.dirname(os.path.realpath(__file__)), 'file_templates', recipe)
    template_file = "%s/%s.%s" % (templates_path, 'register', extensions_dict['txt'])

    main_file = "%s/%s" % (dirs_dict['base'], files_dict['main'])
    append_file_content_to(template_file, main_file, wildcards_dict['filter'], respect_format=False)

    with open(main_file, 'r+') as f:
        substitution_dict = {'name': required_params['filter_name']}
        f.write(replace_content(main_file, substitution_dict))


@receives_params('route')
def register_route(required_params):
    recipe = required_params['recipe']
    
    base_path = dirs_dict['base'] + dirs_dict['router_path']

    templates_path = '%s/%s/%s' % (os.path.dirname(os.path.realpath(__file__)), 'file_templates', recipe)
    template_file = "%s/%s.%s" % (templates_path, recipe, extensions_dict['txt'])

    routes_file = "%s%s" % (base_path, files_dict['index'])
    append_file_content_to(template_file, routes_file, wildcards_dict['route'])

    with open(routes_file, 'r+') as f:
        f.write(replace_content(routes_file, required_params))


import os
import sys

from file_manager.manager import (
    append_file_content_to,
    create_files,
)

from utils.utils import get_config_dict

dirs_dict = get_config_dict()
constants_dict = get_config_dict('constants')

if len(sys.argv) == 1:
    sys.exit("Error: Required 'recipe' param")

if sys.argv[1] == "component" and sys.argv[2]:
    recipe = 'component'
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
    resource_name = sys.argv[2]
    resource_path = "%s%s/" % (base_path, resource_name)

    create_files(files_to_create, recipe, resource_path, resource_name)


if sys.argv[1] == "filter" and sys.argv[2]:
    recipe = 'filter'
    files_to_create = [{
        'ext': 'js', 'suffix': '.filter'
    }]

    resource_path = dirs_dict['base'] + dirs_dict['filters_path']
    resource_name = sys.argv[2]

    create_files(files_to_create, recipe, resource_path, resource_name)

if sys.argv[1] == "route" and sys.argv[2]:
    recipe = 'route'
    base_path = dirs_dict['base'] + dirs_dict['router_path']

    templates_path = '%s/%s/%s' % (os.path.dirname(os.path.realpath(__file__)), 'file_templates', recipe)
        
    template_file = "%s/%s.%s" % (templates_path, recipe, constants_dict['txt_ext'])

    routes_file = "%s%s" % (base_path, constants_dict['index_file'])
    append_file_content_to(template_file, routes_file)


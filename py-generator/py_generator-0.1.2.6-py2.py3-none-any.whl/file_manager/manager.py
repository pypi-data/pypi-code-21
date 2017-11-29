import os
import errno

from string import Template

from generator.utils.utils import (
    get_config_dict,
    get_extensions_dict,
)

dirs_dict = get_config_dict()

extensions_dict = get_extensions_dict()


def append_file_content_to(source, destination, wildcard):
    source_lines = open(source).readlines()

    last_line_idx = len(source_lines) - 1
    source_lines[last_line_idx] = source_lines[last_line_idx].replace('\n', '')
    str_to_append = ''

    for line in source_lines:
        str_to_append += line

    new_content = []

    with open(destination) as _dest_:
        for line in _dest_:
            if wildcard in line:
                line = line.replace('\n', '')
                line = line.replace(wildcard, str_to_append)
                line += '%s%s' % (wildcard, '\n')

            new_content.append(line)

    with open(destination, 'w') as dest:
        dest.writelines(new_content)


def create_files(files_to_create, recipe, resource_path, resource_name):
    for file_to_create in files_to_create:

        templates_path = '%s/' % (os.path.dirname(os.path.realpath(__file__)))
        templates_path = templates_path.replace('manager', 'templates')

        recipe_template_path = '%s%s/' % (templates_path, recipe)
        file_name = ''
        
        if file_to_create['suffix'] != 'index':
            file_name += resource_name 
            file_path = "%s%s" % (resource_path, resource_name)
            recipe_template_path = '%s%s' % (recipe_template_path, file_to_create['ext'])
        elif file_to_create['suffix'] == 'index':
            file_path = "%s" % (resource_path)
            recipe_template_path = '%s%s' % (recipe_template_path, file_to_create['suffix'])

        file_path += "%s.%s" % (file_to_create['suffix'], file_to_create['ext'])
        file_name += "%s.%s" % (file_to_create['suffix'], file_to_create['ext'])
        
        recipe_template_path += '.%s' % (extensions_dict['txt'])

        if not os.path.exists(os.path.dirname(file_path)):
            try:
                os.makedirs(os.path.dirname(file_path))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

        with open(file_path, "w") as f:
            file_content = Template(open(recipe_template_path).read())
            substitution_dict = {"name": resource_name}
            f.write(file_content.substitute(substitution_dict))
            print 'Created successfully: %s' % (file_name)        

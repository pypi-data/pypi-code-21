import os
import yaml


class ValidationError(Exception):
    pass


def normalize_images_recursive_entry(images_recursive, curdir=None):
    curdir = curdir or os.getcwd()
    result = []
    for item in images_recursive:
        key = ('path' in item) and 'path'
        if not key:
            key = ('exclude' in item) and 'exclude'
        path = item[key]
        result.append({
            key: os.path.abspath(os.path.join(curdir, path))
        })
    return result


def normalize_images_entry(images, curdir=None):
    curdir = curdir or os.getcwd()
    result = {}
    for image_name, path in images.items():
        result[image_name] = os.path.abspath(os.path.join(curdir, path))
    return result


def normalize(config):
    if 'images' in config:
        config['images'] = normalize_images_entry(config['images'])
    if 'images_recursive' in config:
        config['images_recursive'] = normalize_images_recursive_entry(config['images_recursive'])
    return config


class ConfigurationAdapter(object):
    '''Filters out paths to Dockerfiles and adapts image_name is needed'''

    def __init__(self, images=None, images_recursive=None):
        self.images = images or {}
        self.images_recursive = images_recursive or []

    def adapt(self, dockerfile_directory, dockerfile_name, image_name):
        dockerfile_absolute = os.path.abspath(
            os.path.join(dockerfile_directory, dockerfile_name)
        )

        if self.images:
            for iname, absolute_path in self.images.items():
                # image name from configuration file should take precedense
                if absolute_path == dockerfile_absolute:
                    # we are exchanging "image_name" with "iname"
                    return dockerfile_directory, dockerfile_name, iname

        if not self.images_recursive:
            return dockerfile_directory, dockerfile_name, image_name

        for item in self.images_recursive:
            exclude = item.get('exclude')
            if not exclude:
                continue
            exclude = '%s/' % exclude if not exclude.endswith('/') else exclude
            dockerfile_directory_cmp = '%s/' % dockerfile_directory if not dockerfile_directory.endswith('/') else dockerfile_directory
            if dockerfile_directory_cmp.startswith(exclude):
                return None
            # There's probably no point in checking "path"
        return dockerfile_directory, dockerfile_name, image_name


def validate(config):
    one_of = ['images', 'images_recursive']

    if not config:
        raise ValidationError('It looks like config file is empty.')

    if not any([(key in config) for key in one_of]):
        raise ValidationError('At least one of sections needs to be defined: %s' % (one_of))

    return config


def read(config_filepath):
    with open(config_filepath, 'r') as fd:
        config = yaml.load(fd.read())
    config = validate(config)
    config = normalize(config)
    return ConfigurationAdapter(**config)

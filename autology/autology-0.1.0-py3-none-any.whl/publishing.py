"""
Provides wrapper around common publishing functionality.
"""
import pathlib

import markdown
import shutil
import yaml
from dict_recursive_update import recursive_update
from jinja2 import Environment, FileSystemLoader, select_autoescape

from autology import topics
from autology.configuration import add_default_configuration, get_configuration

_environment = None
_output_path = None
_markdown_conversion = None
_template_configuration = {}


def register_plugin():
    """
    Subscribe to the initialize method and add default configuration values to the settings object.
    :return:
    """
    topics.Application.INITIALIZE.subscribe(_initialize)
    topics.Processing.END.subscribe(_copy_static_files)

    add_default_configuration('publishing',
                              {
                                  'templates': 'templates',
                                  'output': 'output',
                                  'url_root': '/'
                              })


def _initialize():
    """
    Initialize the jinja environment.
    :return:
    """
    global _environment, _output_path, _markdown_conversion, _template_configuration
    configuration_settings = get_configuration()

    # Load up and store the configuration that is defined in the template files
    template_configuration_path = pathlib.Path(configuration_settings.publishing.templates) / 'template.yaml'
    if template_configuration_path.exists():
        with template_configuration_path.open() as tc_file:
            _template_configuration = yaml.load(tc_file)

    # Create markdown conversion object
    _markdown_conversion = markdown.Markdown()

    # Load the same jinja environment for everyone
    _environment = Environment(
        loader=FileSystemLoader(configuration_settings.publishing.templates),
        autoescape=select_autoescape()
    )

    # Load up the custom filters
    _environment.filters['autology_url'] = url_filter
    _environment.filters['markdown'] = markdown_filter

    # Verify that the output directory exists before starting to write out the content
    _output_path = pathlib.Path(configuration_settings.publishing.output)
    _output_path.mkdir(exist_ok=True)


def publish(template, output_file, context=None, **kwargs):
    """
    Notify jinja to publish the template to the output_file location with all of the context provided.
    :param template:
    :param output_file:
    :param context:
    :param kwargs:
    :return:
    """
    if not context:
        context = {}

    recursive_update(context, kwargs)

    # Insert all of the site details into the context as well
    site_configuration = get_configuration().site.toDict()
    recursive_update(context.setdefault('site', {}), site_configuration)

    try:
        root_template = _environment.get_template(str(template))
        output_content = root_template.render(context)
        output_file = _output_path / output_file

        # Verify that the path is possible.
        output_file.parent.mkdir(exist_ok=True)
        output_file.write_text(output_content)
    except Exception as e:
        print('Error rendering template: {}'.format(template))
        print('e: {}'.format(e))


def url_filter(url):
    """Filter that will prepend the URL root for links in order to put the log in a directory on a web server."""
    config = get_configuration()
    if config.publishing.url_root:
        return "{}{}".format(get_configuration().publishing.url_root, url)
    return url


def markdown_filter(content):
    """Filter that will translate markdown content into HTML for display."""
    return _markdown_conversion.reset().convert(content)


def _copy_static_files():
    """Responsible for copying over the static files after all of the contents have been generated."""
    configuration = get_configuration()
    template_path = pathlib.Path(configuration.publishing.templates)
    output_path = pathlib.Path(configuration.publishing.output)

    static_files_list = _template_configuration.get('static_files', [])

    if static_files_list:
        for glob_definition in static_files_list:
            for file in template_path.glob(glob_definition):
                print('Copying static file: {}'.format(file))

                # Make sure that the destination directory exists before copying the file into place
                destination_parent = file.parent.relative_to(template_path)
                destination = output_path / destination_parent
                destination.mkdir(parents=True, exist_ok=True)

                shutil.copy(str(file), str(destination))

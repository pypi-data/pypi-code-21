"""Sub-command that will initialize an autology area."""
import pathlib
import zipfile

import io
import requests
import yaml

from autology.configuration import get_configuration

DEFAULT_TEMPLATES_URL = 'https://github.com/MeerkatLabs/autology_templates/archive/v0.0.1.zip'


def register_command(subparser):
    """Register the sub-command with any additional arguments."""
    parser = subparser.add_parser('init', help='Initialize area for gathering content.')
    parser.set_defaults(func=_main)

    parser.add_argument('--output-dir', '-o', default='.', help='Directory that will be used for gathering content')
    parser.add_argument('--templates', '-t', default=None, help='URL Containing the templates that will be used for '
                                                                'generating content')


def _main(args):
    """Generate the content for storage."""
    main_path = pathlib.Path(args.output_dir)

    main_path.mkdir(exist_ok=True)

    templates = args.templates if args.templates else DEFAULT_TEMPLATES_URL

    try:
        template_request = requests.get(templates)
        template_file = io.BytesIO(template_request.content)
    except requests.exceptions.MissingSchema:
        template_file = templates

    # template output directory is output/templates, so need to create that location before pulling out the templates
    template_location = main_path / 'templates' / 'output'
    template_location.mkdir(parents=True, exist_ok=True)
    templates_path = None

    # Extract the entire contents of the zip file and store them in the templates/output directory of the project area
    with zipfile.ZipFile(template_file) as template_zip:
        template_definition_file = None

        # Verify that the root directory has a template.yaml file that will contain the configuration details
        for file_name in template_zip.namelist():
            zip_path = pathlib.PurePath(file_name)
            if zip_path.match('template.yaml'):
                template_definition_file = zip_path
                break

        if template_definition_file:
            template_zip.extractall(path=template_location)

            template_definition_file = template_location / template_definition_file
            print('template_definition_file: {}'.format(template_definition_file))

            with template_definition_file.open() as _file_ptr:
                template_definition = yaml.load(_file_ptr)

                print('Loaded template: {}'.format(template_definition['name']))
                templates_path = template_definition_file.parent

    # Now need to find the templates definition of that zip file and locate it in the file system so that it can be
    settings = get_configuration()

    # Override the configuration details with the new template path.  This should probably be handled by the publishing
    # plugin, but for now this will work
    settings.publishing.templates = str(templates_path)
    configuration_file_path = main_path / 'config.yaml'

    with open(configuration_file_path, 'w') as configuration_file:
        yaml.safe_dump(settings.toDict(), configuration_file, default_flow_style=False)

    # Create the initial log directories
    for directory in settings.processing.inputs:
        log_directory = main_path / directory
        log_directory.mkdir(parents=True, exist_ok=True)

"""Processes the front data in the markdown files to process project stat recordings."""
import datetime
import pathlib

import frontmatter
from yaml import load_all

from autology import topics
from autology.publishing import publish
from autology.reports.models import Report

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
from dict_recursive_update import recursive_update as _r_update
from autology.utilities import log_file as log_file_utils

# Constants:

MAIN_TEMPLATE_PATH = pathlib.Path('project', 'index.html')
PROJECT_TEMPLATE_PATH = pathlib.Path('project', 'project.html')

# This is a dictionary containing all of the defined projects, they key is a project identifier that is defined when
# defining the project. Inside should be a dictionary containing a key of datetime object for an entry, and then the
# entry that is associated with that project.
_defined_projects = {}
_defined_organizations = {}
_defined_customers = {}


def register_plugin():
    """ Subscribe to the initialize method and add default configuration values to the settings object. """
    topics.Application.INITIALIZE.subscribe(_initialize)


def _initialize():
    """ Register for all of the required events that will be fired off by the main loop """
    topics.Processing.PROCESS_FILE.subscribe(_process_file)
    topics.Processing.END.subscribe(_build_report)


def _build_report():
    """Convert all the collated data into renderable templates."""
    orphaned_projects = []

    for project in _defined_projects.values():
        organization = _defined_organizations.get(project.get('organization'))
        if organization:
            organization.setdefault('projects', []).append(project)
        else:
            orphaned_projects.append(project)

        # Also need to provide a URL value for the projects
        project['url'] = pathlib.Path('project', '{}.html'.format(project['id']))

        # Sort the logs that are stored on the project
        project['log'] = sorted(project.get('log', []), key=lambda x: x['time'])

        # Now generate a report for each of the projects.
        publish(PROJECT_TEMPLATE_PATH, project['url'], project=project)

    main_context = {
        'projects': _defined_projects.values(),
        'organizations': _defined_organizations.values(),
        'customers': _defined_customers.values(),
    }

    if orphaned_projects:
        main_context['orphaned_projects'] = orphaned_projects

    publish(MAIN_TEMPLATE_PATH, 'project/index.html', **main_context)
    topics.Reporting.REGISTER_REPORT.publish(report=Report('Project', 'List of all project files',
                                                           'project/index.html'))


def _process_file(file, date):
    """
    Process the file.

    This will subscribe to markdown files, which it will use to record the amount of time that the event is taking
    place.  For YAML files it will will look for root object definitions that it understands.  These will have the
    key:  mkl-project and will contain some kind of project identifier.

    It is not guaranteed that the files that are being processed will be processed in order.
    """
    if file.suffix == '.md':
        _process_markdown(file, date)
    elif file.suffix == '.yaml':
        _process_yaml(file=file)


def _process_markdown(file, date):
    """Process the front-matter contents, and store the markdown if necessary."""
    post = frontmatter.load(file)

    if not post.keys():
        return

    _process_yaml(front_matter=post.metadata)

    if 'mkl-project' in post.metadata and not isinstance(post['mkl-project'], dict):

        # Then is clearly must be a string
        project_definition = _defined_projects.setdefault(post['mkl-project'], {'id': post['mkl-project']})
        project_log = project_definition.setdefault('log', [])
        project_log.append(post)

        # Calculate how long the event lasts
        log_date = log_file_utils.get_start_time(date, post.metadata, file)
        log_end_date = log_file_utils.get_end_time(log_date, post.metadata)
        duration = log_end_date - log_date
        time_on_project = project_definition.get('duration', datetime.timedelta())
        project_definition['duration'] = time_on_project + duration

        # Set the date values in the post to be the python objects instead of just strings
        post.metadata['time'] = log_date
        post.metadata['end_time'] = log_end_date
        post.metadata['duration'] = duration


def _process_yaml(file=None, front_matter=None):
    """Process the documents in a yaml file and update data structures according to the data values."""

    # Create a valid documents variable based on the parameters that are provided.
    if file:
        with open(file) as yaml_file:
            documents = [d for d in load_all(yaml_file, Loader=Loader)]
    elif front_matter:
        documents = [front_matter]
    else:
        documents = []

    for document in documents:

        # Figure out if any of the documents contain definitions of project/organization/customers and if so, see if
        # the documents define them (i.e. have dictionaries), or if the document is just about the data.
        if 'mkl-project' in document:

            project_definition = document['mkl-project']
            if not isinstance(project_definition, dict):
                continue

            definition_collection = _defined_projects
            updated_definition = project_definition

        elif 'mkl-organization' in document:

            organization_definition = document['mkl-organization']
            if not isinstance(organization_definition, dict):
                continue

            definition_collection = _defined_organizations
            updated_definition = organization_definition

        elif 'mkl-customer' in document:

            customer_definition = document['mkl-customer']
            if not isinstance(customer_definition, dict):
                continue

            definition_collection = _defined_customers
            updated_definition = customer_definition

        else:
            continue

        # Update the values in the previous definition, otherwise it is the new definition.  This is because the
        # definition_collection may already contain some values from files before (i.e. received markdown files about
        # working on the project before the definition yaml file was processed).
        previous_definition = definition_collection.setdefault(updated_definition['id'], {})
        _r_update(previous_definition, updated_definition)

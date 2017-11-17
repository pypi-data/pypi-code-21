"""Sub-command that will create a new note file for the log."""
import datetime
import pathlib
import subprocess

import frontmatter
from pkg_resources import iter_entry_points

from autology import topics
from autology.configuration import add_default_configuration, get_configuration, get_configuration_root


def register_command(subparser):
    """Register the sub-command with any additional arguments."""
    parser = subparser.add_parser('make_note', help='Create a new note object.')
    parser.set_defaults(func=_main)

    parser.add_argument('--template-list', '-T', help='List all of the templates that are available',
                        action='store_true')
    parser.add_argument('--template', '-t', help='Specify the template file that will be used',
                        default=None)

    add_default_configuration('make_note',
                              {
                                  'default_template': 'timeline_base',
                                  'editor': 'xdg-open {file}',
                              })


def _main(args):
    """
    Create a new note file in the correct location.
    :param args:
    :return:
    """
    loaded_templates = {}

    for ep in iter_entry_points(group='autology_templates'):
        template_object = ep.load()()

        if not isinstance(template_object, list):
            template_object = [template_object]

        for to in template_object:
            loaded_templates[to.name] = to

    template_name = args.template if args.template is not None else get_configuration().make_note.default_template

    template = loaded_templates[template_name]

    if args.template_list:
        print('Available templates:')
        for key in loaded_templates.keys():
            print('  {}'.format(key))
    else:
        _create_note(template)


def _create_note(template):
    now = datetime.datetime.now()
    post = template.start()

    directory_structure = pathlib.Path(get_configuration().processing.inputs[0])

    # Need to figure out the root directory for all of the path objects if they are relative.
    if not directory_structure.is_absolute():
        directory_structure = get_configuration_root() / directory_structure

    directory_structure = directory_structure / now.strftime('%Y') / now.strftime('%m') / now.strftime('%d')

    directory_structure.mkdir(parents=True, exist_ok=True)

    file_name = directory_structure / now.strftime('%H%M%S.md')

    # Write out the file to the file_name
    file_name.write_text(frontmatter.dumps(post))

    commands = [a.format(file=file_name) for a in get_configuration().make_note.editor.split()]
    subprocess.run(commands)

    # Now need to reload the contents of the file
    with file_name.open() as post_file:
        post = frontmatter.load(post_file)

    template.end(post)

    # Write out the results one last time with the final contents
    file_name.write_text(frontmatter.dumps(post))

    # Notify the storage engine that everything is finished, and the file can be sent to the remote
    topics.Storage.FILE_ADDED.publish(file=file_name)
    topics.Storage.FINISHED_MODIFICATIONS.publish(message="New Note from autology make_note")
    topics.Storage.PULL_CHANGES.publish()
    topics.Storage.PUSH_CHANGES.publish()

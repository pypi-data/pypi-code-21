import os
from zerotk.zops import Console

import click


click.disable_unicode_literals_warning = True


@click.group('anatomy')
def main():
    pass


@main.command('tree')
@click.pass_context
def tree(ctx):
    from zops.anatomy.layers.feature import AnatomyFeatureRegistry
    _register_features()

    items = AnatomyFeatureRegistry.tree()
    items = sorted([('/' not in filename, filename, fileid, feature) for (feature, fileid, filename) in items])

    column_width = max([len(i[3]) for i in items])
    item_format = '{{:{}}}  {{}}'.format(column_width)

    for _priority, i_filename, i_fileid, i_feature in items:
        Console.item(item_format.format(i_feature, i_filename))


@main.command()
@click.argument('directories', nargs=-1)
@click.pass_context
def apply(ctx, directories):
    """
    Apply templates.
    """
    from .layers.playbook import AnatomyPlaybook

    _register_features()

    if not directories:
        directories = ('.',)
    directories = [os.path.abspath(i) for i in directories]

    for i_directory in directories:
        Console.title(i_directory)
        anatomy_playbook = AnatomyPlaybook.from_file(i_directory + '/anatomy-playbook.yml')
        anatomy_playbook.apply(i_directory)


@main.command('auto-apply')
@click.pass_context
def auto_apply(ctx):
    """
    Apply templates automatically configuring:
    * Features file
    * Search for anatomy-playbook.yml recursively.
    """

    def find_all(name, path):
        result = []
        for root, dirs, files in os.walk(path):
            if name in files:
                result.append(os.path.join(root, name))
        return result

    def find_up(name, path):
        directory = os.path.abspath(path)
        while directory:
            filename = os.path.join(directory, name)
            if os.path.isfile(filename):
                return filename
            directory = os.path.dirname(directory)
        return None

    features_filename = find_up('anatomy-features.yml', '.')
    if features_filename is None:
        Console.info("Can't find features file: anatomy-features.yml.")
        return 1
    Console.info("{}: Features file.".format(features_filename))

    playbook_filenames = find_all('anatomy-playbook.yml', '.')

    os.environ['ZOPS_ANATOMY_FEATURES'] = features_filename
    ctx.invoke(apply, directories=map(os.path.dirname, playbook_filenames))


def _register_features():
    from .layers.feature import AnatomyFeatureRegistry
    filename = os.environ['ZOPS_ANATOMY_FEATURES']
    AnatomyFeatureRegistry.register_from_file(filename)

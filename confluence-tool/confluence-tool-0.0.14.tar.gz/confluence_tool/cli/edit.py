import yaml, pyaml, sys
from difflib import Differ
from .cli import command, arg, optarg_cql, arg_filter, arg_parent
from ..storage_editor import StorageEditor


@command('edit',
    optarg_cql,
    arg_filter,
    arg('file', nargs="?", help="file to read data from"),
    # need arg_group
    arg('--show', action="store_true", help="show new content"),
    arg('--diff', action="store_true", help="show diff"),
    )
def cmd_edit(config):
    """edit a confluence page using CSS selections

    Pass a dictionary in YAML or JSON format via STDIN or file to
    confluence-tool, which defines edit actions to edit all matching pages.

    """

    confluence = config.getConfluenceAPI()
    first = True

    if not config['file']:
        editor_config = yaml.safe_load(sys.stdin)
    else:
        with open(fn, 'r') as f:
            editor_config = yaml.safe_load(f)

    if 'page' in editor_config:
        cql = confluence.resolveCQL(editor_config.pop('page'))
    if 'cql' in editor_config:
        cql = editor_config.pop('cql')
    if config['cql']:
        cql = config['cql']

    #editor = StorageEditor(confluence, **editor_config)

    for page,content in confluence.editPages(cql, filter=config.filter, editor=editor_config):
        if not first:
            print "---"
        first = False

        from html5print import HTMLBeautifier
        b = HTMLBeautifier.beautify

        if config.show:
            p = page.dict('id', 'spacekey', 'title')

            p['content'] = b(content, 2)
            pyaml.p(p)

        elif config.diff:
            p = page.dict('id', 'spacekey', 'title')

            old = b(page['body']['storage']['value']).splitlines(1)
            new = b(content).splitlines(1)

            d = Differ()
            result = list(d.compare(old, new))

            p['diff'] = ''.join(result)
            pyaml.p(p)

        else:
            p = page.dict('id', 'title', 'version')
            p['storage'] = content
            p['version'] = int(page['version']['number'])+1

            result = confluence.updatePage(**p)
            pyaml.p(result)


@command('move', optarg_cql, arg_filter, arg_parent)
def move(config):
    confluence = config.getConfluenceAPI()
    first = True

    parent = confluence.getPage(confluence.resolveCQL(config.parent))
    cql = confluence.resolveCQL(config.cql)
    filter = config.filter

    for page in confluence.getPages(cql, filter=filter, expand=['version']):
        result = confluence.movePage(page, parent=parent)

        if not first:
            print "---"

        pyaml.p(result)

        first = False

    if first:
        print "could not find a page matching %s (%s)" % (cql, filter)

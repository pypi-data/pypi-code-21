"""
# Confluence Tool

Confluence Tool is for doing batch operations in confluence.

## Getting Started

For configuration, please run "confluence-tool -b BASE_URL config"

"""
from argdeco import CommandDecorator, arg, mutually_exclusive, group

command = CommandDecorator(
    arg('-c', '--config',      help="Configuration name", default='default'),
    arg('-C', '--config-file', help="Configuratoin file (default ~/.confluence-tool.yaml)"),
    arg('-b', '--baseurl',     help="Confluence Base URL, e.g. http://example.com/confluence"),
    arg('-u', '--username',    help="username for logging in (if not present, tried to read from netrc)"),
    arg('-p', '--password',    help="password for logging in (if not present, tried to read from netrc)"),
    arg('-d', '--debug',       action="store_true", help="get more information on exceptions"),
)

arg_cql = positional_arg_cql = arg('cql', help="SPACE:title, pageID or CQL, run '%(prog)s cql -h' for more help")
optarg_cql = positional_optarg_cql = arg('cql', nargs="?", help="SPACE:title, pageID or CQL, '%(prog)s cql -h' for more help")

arg_expand = arg('-e', '--expand', help="values to expand")
arg_filter = arg('-f', '--filter', help="page property filter run '%(prog)s page-prop-filtering -h' for more help")
arg_state = arg('-s', '--state', help="get all pages for corresponding state '%(prog)s cw-states -h' for more help")
arg_write_format = arg('-w', '--write', help="format to write", choices=['yaml', 'json'], default="yaml")
arg_format = arg('-F', '--format', help="format string for formatting the output.  May be either mustache or format string")
arg_parent = arg('-p', '--parent', help="specify parent for a page, which might be created")
arg_message = arg('-m', '--message', help="add a note or message")

@command('cql')
def cql_help(config):
    """How to query pages.

    You can pass [CQL] queries to many commands (indicated by parameter cql).
    In many queries you have to specify the ID, which originally needs an extra
    step to find it out.  So there is a convenience syntax for most common
    queries.

    [CQL]: https://developer.atlassian.com/confdev/confluence-server-rest-api/advanced-searching-using-cql

    Here you find a little translation of convenience syntax to CQL:

    - `<QUERY> ">>"` -> `ancestor = <ID of result of QUERY>`
    - `<QUERY> ">"`  -> `parent   = <ID of result of QUERY>`
    - `<SPACE> ":" <TITLE>` -> `space = <SPACE> and title = "<TITLE>"`
    - `":" <TITLE>`   -> `title = "<TITLE>"`
    - `<PAGE_ID>`  -> `ID = <PAGE_ID>`
    - `<PAGE_URI>` -> `ID = <page ID from PAGE_URI>`

    Examples:

     - `"IT:Some title>>"` to find all descendent pages of page with title
       "Some title" in space "IT"

     - `"IT:Some title"` to find page titled "Some title" in space "IT"

    """
    command['cql'].print_help()

@command('cw-states')
def comala_workflow_states(config):
    """How to filter page versions for specific state.

    If you want to get the Approved version of all pages, a simple
    `... and state = "Approved"` gives you only the pages currently in state
    Approved, but will not return the Approved version of pages, which are
    currently in a different state.

    The filter "--state <STATENAME>" will provide you the last version of the
    corresponding state.
    """
    command['cw-states'].print_help()

@command('page-prop-filtering')
def page_prop_filtering(config):
    """How to filter pages using page properties.

    Addionally to CQL queries, you can filter results (on client side) using
    page property filters.

    These filters are pretty simple, but helpful :)

    Page property filters are passes with `-F` command line option, and you can
    repeat this option to pass multiple filters, which all have to match against
    a page.
    l
    - `-F <NAME>==<VALUE>`  Value must be in property named `<NAME>`.  If
      property is a list, then this is true, if `<VALUE>` is one of the list
      values.  (works like labels in CQL).

    - `-F <NAME>!=<VALUE>`  Value must not be in property named `<NAME>`.

    - `-F '!<NAME>'`  Matches if property `<NAME>` is not present in page

    - `-F '<NAME>?'`  Matches if property `<NAME>` is present in page

    """

    command['page-prop-filtering'].print_help()

import pyaml, re, sys

@command('get',
    arg('url', help="url start with / or /rest/ will be prepended"),
    arg('--stream', help="get raw data", default=False, action="store_true"),
    arg('--progress', help="write out progress", default=False, action="store_true"),
    arg('--output-file', '-o', help="output file"),
    arg('params', nargs="*", help="parameters to pass to url"))
def get_method(config):
    """
    Get from a rest URL

    """

    PARAM = re.compile(r'(.*?)=(.*)')

    params = {}

    for item in config.get('params'):
        m = PARAM.search(item)
        if m:
            (name, value) = m.groups()
            params[name] = value

    url = config.get('url')

    output_file = config.get('output_file')
    if output_file and output_file != '-':
        outstream = open(output_file, 'wb')
    else:
        outstream = sys.stdout

    progress = config.get('progress')

    if 1:
        if not url.startswith('/'):
            url = '/rest/'+url

        confluence = config.getConfluenceAPI()

        result = confluence.get(url, stream=config.get('stream'), **params)
        if config.get('stream'):
            _len = 0
            for data in result.iter_content(chunk_size=1024*1024):
                outstream.write(data)

                _len += len(data)
                if progress:
                    sys.stderr.write("\r%s bytes" % _len)
        else:
            pyaml.p(result)

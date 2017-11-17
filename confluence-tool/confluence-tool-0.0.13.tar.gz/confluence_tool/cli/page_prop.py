import sys, re
from .cli import command, arg, arg_format, optarg_cql, arg_filter, arg_state
import pyaml, yaml

@command('page-prop-get', optarg_cql, arg_filter, arg_format, arg_state,
    arg('--dict', action="store_true", help="transform page properties to dict (key page_id) before output"),
    arg('props', nargs="*", help="properties to retrieve"),
    )
def cmd_page_prop_get(config):
    """\
    Get page properties.

    For each page there is printed a YAML document with `id`, `title` and
    `spacekey`.  Page properties are printed under `pageProperties`.

    Optionally you can pass some page property filter expressions to filter
    pages on page properties additionally to CQL query.

    Please note, when using `--format`:

    For convenience in format string, you can directly refer to page properties
    in format string.  Items referring to page can be fetched with `page_id`,
    `page_title` and `page_spacekey`.

    Examples:

     - `ct page-prop-get "SpaceName:Some Title"`

        gets all page properties from "Some title" in space "Space Name"

     - `ct page-prop-get "SpaceName:Some Title" Pageproperty1 Pageproperty2`

       get Pageproperty1 and Pageproperty2 from "Some title" in space "Space Name"

     - `ct page-prop-get "label = 'some-label'"`

        gets all page properties for all pages with label 'some-label'
    """
    confluence = config.getConfluenceAPI()
    first = True

    if config.get('dict'):
        results = {}

    for pp in confluence.getPagesWithProperties(**config.dict('cql', 'filter', 'state')):

        if config.get('format'):
            try:

                if '{}' in config['format']:
                    fields = [ pp.pageProperty.get(f, '') for f in config['props'] ]
                    print unicode(config['format']).format(*fields).encode('utf-8')
                else:
                    _props = dict(pp.getPageProperties())
                    _props.update(dict([ (k.lower(), v) for (k,v) in _props.items()]))
                    _props.update(page_id=pp.id, page_title=pp.title, page_spacekey=pp.spacekey)

                    print unicode(config['format']).format(**_props).encode('utf-8')
            except UnicodeEncodeError:
                import traceback
                sys.stderr.write("Error formatting %s:%s\n %s\n" % (pp.spacekey, pp.title, repr(dict(pp.getPageProperties()))))
        else:
            result = pp.dict("id", "spacekey", "title")
            result['pageProperties'] = dict(pp.getPageProperties(*config.props))

            if config.get('dict'):
                results[result['id']] = result
            else:
                if not first:
                    print("---")
                else:
                    first = False

                result = pp.dict("id", "spacekey", "title")
                result['pageProperties'] = dict(pp.getPageProperties(*config.props))

                pyaml.p(result)

    if config.get('dict'):
        pyaml.p(results)


@command('page-prop-set',
    arg_filter,
    arg('-p', '--parent', help="specify parent for a page, which might be created"),
    arg('-l', '--label', action="append", help="add these labels to the page"),
    optarg_cql,
    arg('propset', nargs="*", help="property setting expression"),
    arg('file', nargs="*", help="file to read data from")
    )
def cmd_page_prop_set(config):
    """\
    Set page properties.

    # Details

    There are multiple ways of setting page properties.  CQL and page property
    filters are working like in `page-prop-get` command and select pages to
    edit properties.

    # Setting page properties via arguments

    You can add multiple `propset` epressions.  A Propset expression is:

    * `propname:=value` -
      Replace current property with this value.  Value may be JSON or a string.

    * `propname+=value` -
      add value to current property value.

    * `propname-=value` -
      remove value from current property value.

    * `propname--` -
      remove property

    This way default templates for rendering properties are used.


    # Setting page properties via YAML from STDIN

    A document may have following values:

    - `page` - specify a page to be changed
    - `templates` - dictionary of templates with following names:
      - `user` - to render user names.  Gets userkey
      - `page` - to render page Gets spacekey, title
      - `link` - to render link Gets href, caption
      - `list` - to render a list
      - `PROPKEY-TYPE`, where PROPKEY is valid propkey and TYPE is one of the
        above.  This will be used as templates only for that key
    - `pages` - list of documents like this
    - `pagePropertiesEditor` - Define how to change page properties

    Examples:

     - `ct page-prop-set -p "SpaceName:Parent Title" "SpaceName:Some Title"
       PageProp1:='Content1' 'Page Prop2:=Content 2' 'Page-Prop3:=Content3'`

       Replaces page properties for Page "SpaceName:Some Title" (creates page and
       page-properties if not existent):

     - `ct page-prop-set -p -l "label1" -l "label2" "SpaceName:Parent Title"
       "SpaceName:Some Title" PageProp:='Content'`

       Additionally adds label "label1" and "label2"
    """

    confluence = config.getConfluenceAPI()
    first = True

    PROPSET = re.compile(r'^(.*?)([:+-])=(.*)$')
    opmap = {
        ':': 'replace',
        '+': 'add',
        '-': 'remove',
    }

    files = []

    # handle propset
    propset = {}
    for prop in config['propset']:
        if prop.endswith('--'):
            propset[prop[:-2]] = 'delete'
        else:
            m = PROPSET.match(prop)
            if m:
                (name, op, value) = m.groups()
                if name not in propset:
                    propset[name] = {}

                _prop = propset[name]
                op = opmap[op]
                if op not in _prop:
                    _prop[op] = value
                else:
                    if not isinstance(_prop[op], list):
                        _prop[op] = [ _prop[op] ]
                    _prop[op].append(vlaue)

            else:
                files.append(prop)

    if not config.get('cql') or config.get('cql') == '-':
        files = ['-']
        config['cql'] = None

    # handle filenames
    input = ''
    for filename in files:
        if input != '':
            input += "---\n"
        if filename == '-':
            input += sys.stdin.read()
        else:
            with open(filename, 'r') as f:
                input += f.read()

    documents = []
    # parse yaml multidocument
    if input:
        for d in yaml.safe_load_all(input):
            if isinstance(d, list):
                documents += d
            else:
                documents.append(d)

    if len(propset):
        document = {
            'page': config['cql'],
            'pagePropertiesEditor': propset,
        }
        if config.get('parent', None):
            document['parent'] = config['parent']

        documents = [document] + documents
    else:
        if config['cql']:
            if len(documents) == 1:
                documents = [ {
                    'page': config['cql'],
                    'pagePropertiesEditor': documents[0]
                } ]

            if config.get('parent', None):
                documents[0]['parent'] = config['parent']

    labels = config.get('label', [])
    if labels is None:
        labels = []

    for doc in documents:
        if config.get('parent'):
            if 'parent' not in doc:
                doc['parent'] = config.get('parent')

        if 'pagePropertiesEditor' not in doc:
            if 'pageProperties' in doc:
                doc['pagePropertiesEditor'] = {}

                for k,v in doc['pageProperties']:
                    doc['pagePropertiesEditor'][k] = {'replace': v}

                del doc['pageProperties']

        if 'page' not in doc and 'pages' not in doc:
            doc['page'] = "%s:%s" % (doc['spacekey'], doc['title'])

        doc_labels = doc.get('labels', doc.get('label', []))
        if not isinstance(doc_labels, list):
            doc_labels = [ doc_labels ]

        for result in confluence.setPageProperties(doc):
            print "updated {spacekey}:{title} ({id})".format(**(result['page'].dict('spacekey', 'title', 'id')))

            _labels = labels+doc_labels
            if len(_labels):
                confluence.addLabels(result['result']['id'], _labels)

import os
import pytest
import requests
from urllib.parse import splitport
from guide_search.esearch import Esearch, Dsl
from utils import log, AttrDict, Helper
from guide_search import exceptions

DEBUG=True
GUIDE_API_HOST=os.environ['GUIDE_API_HOST']
ES_HOST=os.environ['ES_HOST']

@pytest.fixture
def esearch(setup):
    return setup.esearch


@pytest.fixture
def index_name(setup):
    return setup.index_name


@pytest.fixture(scope="module")
def setup():
    """
    - config is created once for all tests
    - initialises index
    """
    setup = AttrDict() # {{{

    setup.esearch = Esearch(
            host=ES_HOST,
            control='knowledge_config/control' )


    setup.helper = Helper(GUIDE_API_HOST)

    if not DEBUG:

        # delete any test indexes
        stats = requests.get(setup.esearch.host+'/_stats').json()
        indices = stats['indices']
        test_indices = [ i for i in list(indices.keys()) if i.startswith('test_') ]
        for i in test_indices:
            log('Deleting index %s' % i)
            r=requests.delete(setup.esearch.host+'/'+i).json()
            if not r or not r['acknowledged']:
                log('Failed to deleted index %s' % i)

        # recreate branch from last commit on master and update ES
        setup.index_name = setup.helper.randomName() # random branch name e.g. test_imjnxy
        setup.helper.delete_test_branches()
        setup.helper.initialise_index(setup.index_name)
    else:
        # re-use branch / ES content
        setup.index_name = setup.helper.get_test_branch_names()[0]

    yield setup
# }}}


def test_check_versions(setup):
    """ guide-api is running and connected to the right version servers """
    log('')
    host = setup.helper.info['elasticsearch']['host']
    ver = setup.helper.info['elasticsearch']['version']
    version = [int(n) for n in ver.split('.')]
    assert version[0] >= 5 and \
        log('...detected Elasticsearch version %s on %s' % (ver, host))

    host = setup.helper.info['gitlab']['content']['host']
    ver = setup.helper.info['gitlab']['content']['version']
    version = [int(n) for n in ver.split('.')]
    assert version[0] >= 8 and \
        log('...detected Gitlab version %s on %s' % (ver, host))


def test_request_base_url(esearch):
    esearch.Requests=requests
    url = esearch.make_url('')
    log('getting %s ...' % url)
    r = esearch.request(method='get', url=url)
    expected = 'version' in r.keys() 
    assert expected and log('Base ES url (%s) returns version info ' % url)


def test_request_bad_url(esearch):
    url = esearch.make_url("")
    url,port = splitport(url)
    url = '{}:{}'.format(url,int(port)+1)
    with pytest.raises(requests.exceptions.ConnectionError):
        esearch.request(method='get', url=url)
    log('Bad url (%s) raises a ConnectionError exception ' % url)


def test_request_bad_route(esearch, index_name):
    with pytest.raises(exceptions.BadRequestError):
        url = esearch.make_url(index_name, "spaghetti")
        esearch.request(method='get', url=url, params=None, data=None, raw_response=False)
    log('Right url + bad route (%s) raises a BadRequestError exception ' % url)


# def test_search_match_all_articles(esearch, index_name):
    # from pudb import set_trace; set_trace()
    # hits = esearch.search(index=index_name, type='articles', dsl= Dsl().match_all().buffer)
    # n=len(hits)
    # assert n and log('match all returns %s articles' % n)




# curl 'elasticsearch5:9200/test_g4n6yb/_search?q=mermaid'
# @pytest.mark.parametrize('id', ['acc_fence'])
# def test_search(esearch, index_name, id):
    # """
    # search successfully queries elasticsearch for a document by its ID.

    # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-ids-query.html#query-dsl-ids-query

    # """
    # dsl = {
        # 'query': {
            # 'ids': { 
            # 'values' : [id],
            # }
        # },
        # 'size': 2,
    # }
    # r = esearch.search(index=index_name, type="articles", dsl=dsl)
    # assert len(r['hits']['hits']) == 1
    # assert r['hits']['total'] == 1
    # assert r['hits']['hits'][0]['_id'] == id


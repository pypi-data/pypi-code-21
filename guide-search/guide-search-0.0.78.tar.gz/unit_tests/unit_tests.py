# vim: foldmethod=marker:foldmarker=\ {{{,\ }}}:cms=#%s

import os
import json
import pytest
from requests import codes
from guide_search.esearch import Esearch, Dsl
from mock import Mock
import requests
from utils import log, AttrDict
from guide_search.exceptions import (
    JSONDecodeError,
    BadRequestError,
    ResourceNotFoundError,
    ConflictError,
    PreconditionError,
    ServerError,
    ElasticsearchError,
    ServiceUnreachableError,
    UnknownError,
    ResultParseError,
    CommitError,
    ValidationError, )

@pytest.fixture
def esearch():
    return Esearch(host='http://', control='knowledge_config/control')



def test_unit_dsl():
    """
        Dsl.dsl() returns a well formed query.
    """
    # mocks /guide_ui/server.py::parse_search
    search = {}
    search['search'] = 'mermaid'
    search['sort_type'] = 'score'
    search['page_size'] = 25
    search['page_number'] = 1
    search['fields'] = ["id", "scope", "keywords^5", "title^5"]
    search['order'] = "desc"
    search['filter'] = []

    # mocks /guide_ui/server.py::get_search
    sortmap = {"score": "_score", "popularity": "popularity", "date": "master.lastmodified"}
    sort = sortmap.get(search['sort_type'], "_score")
    dsl = Dsl()
    dsl.ui_query(multi_match=search['search'],
       facets=search['filter'],
       fields=search['fields'])
    dsl.size(search['page_size'], search['page_number'])
    dsl.sort(sort, search['order'])
    dsl.facets()
    dsl.suggest(search['search'], "scope")

    expected = {'aggs': {'nest': {'aggs': {'facetnames': {'aggs': {'focinames': {'terms': {'field': 'facets.foci'}}}, 'terms': {'field': 'facets.facet'}}}, 'nested': {'path': 'facets'}}}, 'query': {'bool': {'filter': [{'bool': {'filter': []}}], 'must': {'multi_match': {'fields': ['id', 'scope', 'keywords^5', 'title^5'], 'query': 'mermaid'}}}}, 'size': 25, 'sort': [{'_score': {'order': 'desc'}}], 'suggest': {'didyoumean': {'term': {'field': 'scope', 'size': 10}, 'text': 'mermaid'}}} 
    assert(dsl.dsl() == expected) and log('dsl returns a well-formed query')


def test_unit_match_all():
    dsl= Dsl().match_all()
    expected = {'query': {'bool': {'must': [{'match_all': {}}]}}}
    assert(dsl.dsl() == expected) and log('match_all returns a well-formed query')


def test_unit_more_like_this():
    index_name='dummy'
    dsl= Dsl().more_like_this(index_name, source= 'franchise_fr')
    expected = {'_source': ['id', 'title', 'scope'], 'query': {'more_like_this': {'fields': ['keywords', 'scope', 'markup'], 'like': [{'_id': 'franchise_fr', '_index': index_name, '_type': 'articles'}], 'max_query_terms': 12, 'min_term_freq': 1}}}
    assert(dsl.dsl() == expected) and log('more_like_this returns a well-formed query')


@pytest.mark.parametrize("facet_filter", ["simple", "complex"])
def test_unit_m_facet_filter(facet_filter):
    root=os.path.dirname(__file__)
    filepath = os.path.join(root, 'fixtures', 'buildFacetFilter', facet_filter + '.input')
    with open(filepath) as f:
        foci_selected = json.load(f)

    filepath = os.path.join(root, 'fixtures', 'buildFacetFilter', facet_filter + '.result')
    with open(filepath) as f:
        expected = json.load(f)
    assert Dsl().m_facet_filter(foci_selected) == expected  and log('facet_filter  %s formed as expected' % facet_filter)


def test_unit_makeurl(esearch):
    url = esearch.make_url('dev', "articles", "bank")
    expected = '{}/dev/articles/bank'.format(esearch.host)
    assert url == expected and log('make_url returns a well-formed URL')


def MockGetRequests( status_code, content):
    """ mock Requests object for esearch """
    Requests = Mock()
    response = AttrDict({ 'status_code' : status_code, 'content' : content, 'text':'sometext' })
    response.json = lambda : json.loads(content)
    Requests.get.return_value=response
    return Requests


@pytest.mark.parametrize("status_code", [codes.OK, codes.CREATED])
def test_unit_request_blank_string(esearch, status_code):
    esearch.Requests = MockGetRequests(status_code = status_code, content  = '')
    assert esearch.request(method='get',url='http://google.com') == True
    log('esearch.request returns True if response is OK/CREATED but content is blank')


@pytest.mark.parametrize("status_code", [codes.OK, codes.CREATED])
def test_unit_request_bad_json(esearch, status_code):
    esearch.Requests = MockGetRequests(status_code = status_code, content  = '{')
    with pytest.raises(JSONDecodeError):
        esearch.request(method='get',url='http://google.com')
    log(' esearch.request raises exception if response is OK/CREATED but content is bad json ')


def test_unit_request_bad_400(esearch):
    esearch.Requests = MockGetRequests(status_code = codes.BAD, content  = '{}')
    with pytest.raises(BadRequestError):
        assert esearch.request(method='get',url='http://google.com')
    log(' esearch.request raises exception if response is BAD REQUEST')


def test_unit_request_bad_404(esearch):
    esearch.Requests = MockGetRequests(status_code = codes.NOT_FOUND, content  = '{}')
    with pytest.raises(ResourceNotFoundError):
        assert esearch.request(method='get',url='http://google.com')
    log(' esearch.request raises exception if response is BAD REQUEST')


def test_unit_request_bad_409(esearch):
    esearch.Requests = MockGetRequests(status_code = codes.CONFLICT, content  = '{}')
    with pytest.raises(ConflictError):
        assert esearch.request(method='get',url='http://google.com')
    log(' esearch.request raises exception if response is CONFLICT')


def test_unit_request_bad_412(esearch):
    esearch.Requests = MockGetRequests(status_code = codes.PRECONDITION_FAILED, content  = '{}')
    with pytest.raises(PreconditionError):
        assert esearch.request(method='get',url='http://google.com')
    log(' esearch.request raises exception if response is PRECONDITION_FAILED')


def test_unit_request_bad_500(esearch):
    esearch.Requests = MockGetRequests(status_code = codes.INTERNAL_SERVER_ERROR, content  = '{}')
    with pytest.raises(ElasticsearchError):
        assert esearch.request(method='get',url='http://google.com')
    log(' esearch.request raises exception if response is INTERNAL_SERVER_ERROR')


def test_unit_request_bad_503(esearch):
    esearch.Requests = MockGetRequests(status_code = codes.SERVICE_UNAVAILABLE, content  = '{}')
    with pytest.raises(ServiceUnreachableError):
        assert esearch.request(method='get',url='http://google.com')
    log(' esearch.request raises exception if response is SERVICE_UNAVAILABLE')





# @pytest.fixture
# def root():
    # return os.path.dirname(__file__)

# @pytest.fixture
# def index():
    # return 'dev'

# @pytest.fixture
# def control():
    # return 'knowledge_config/control'

# @pytest.fixture
# def eserver():
    # return 'gl-know-ap33.lnx.lr.net:9200'

# @pytest.fixture
# def elasticsearch_version():
    # return '1.4.5'


# @pytest.fixture
# def esearch(eserver, control, index):
    # return Esearch(host='http://{}'.format(eserver),control=control)

# @pytest.fixture
# def dsl():
    # return Dsl()



# def test_buildPage(esearch, dsl):
    # """
    # page correctly populates a dictionary of request fields based on:
        # - the required page number (page)
        # - number of results to be displayed per page (size)

    # https://www.elastic.co/guide/en/elasticsearch/reference/5.1/search-request-from-size.html

    # """
    
    # assert esearch.page() == {'size': 5000}
    # assert esearch.page(page=0) == {'size': 5000}
    # assert esearch.page(page=1) == {'size': 5000}
    # assert esearch.page(page=2) == {'size': 5000}
    # assert esearch.page(size=10) == {'size': 10}
    # assert esearch.page(size=10) == {'size': 10}
    # assert esearch.page(size=10, page=0) == {'size': 10}
    # assert esearch.page(size=10, page=1) == {'size': 10}
    # assert esearch.page(size=10, page=2) == {'size': 10, 'from' : 10 }
    # assert esearch.page(size=10, page=20) == {'size': 10, 'from' : 190 }
    # assert esearch.page(size=10, page=-1) == {'size': 10}
    # assert esearch.page(size=-10, page=1) == {'size': -10} # GE : TODO is this desired?

# def test_buildSort(esearch):

    # """
    # buildSort correctly populates a dictionary of request fields based on:
        # - sort = search_type = 'score', 'date', or 'popularity'
        # - order = 'asc' or 'desc'

    # https://www.elastic.co/guide/en/elasticsearch/reference/current/search-request-sort.html

    # """

    # assert dsl.buildSort() == {'sort': [{'_score': {'order': 'desc'}}]}
    # assert dsl.buildSort(order='desc') == {'sort': [{'_score': {'order': 'desc'}}]}
    # assert dsl.buildSort(sort='score') == {'sort': [{'_score': {'order': 'desc'}}]}
    # assert dsl.buildSort(sort='score',order='desc') == {'sort': [{'_score': {'order': 'desc'}}]}
    # assert dsl.buildSort(sort='date',order='asc') == {'sort': [{'master.lastmodified': {'order': 'asc'}}]}

# def test_buildDsl(esearch, index):
    # """
    # buildDsl returns a well formed elasticsearch query

    # """
    # fields = ["id", "title", "scope", "master.document", "master.version", "sensitivity", "purpose"]
    # expected = {
        # 'fields': ['id',
        # 'title',
        # 'scope',
        # 'master.document',
        # 'master.version',
        # 'sensitivity',
        # 'purpose'],
        # 'query': {
            # 'filtered': {'filter': {'bool': {'must': []}},
            # 'query': {'bool': {'should': []}}}
            # },
        # 'size': 5000,
        # 'sort': 'id'}
    # dsl = esearch.buildDsl(fields=fields, index=index)
    # assert dsl == expected
    # # this should now work: esearch.search(index,"articles",dsl)




# def test_get_documents(esearch,index):
    # """
    # get_documents returns a whole load of articles
    # """
    # r = esearch.get_documents(type="article", index=index)
    # assert r['total'] > 1


# # TODO
# # def test_getAssociateList(esearch, index):
    # # r = esearch.getAssociateList(index, "article")
    # # pass


# def test_get_articles(esearch, index):
    # """
    # get_articles returns a whole load of articles
    # """
    # r = esearch.get_articles(index=index)
    # assert len(r) > 1


# def test_get_items(esearch,index):
    # r = esearch.get_items(index=index)
    # assert len(r) > 1


# def test_get_snippets(esearch,index):
    # """
    # """
    # r = esearch.get_snippets(index=index)
    # assert len(r) > 1


# def test_get_document(esearch, index):
    # """
    # """
    # r = esearch.get_document(index=index, type='article', id='fr_gen_reg_lra2002')
    # assert 'First registration' in r['title']


# def test_get_control(esearch):
    # """
    # """
    # r = esearch.get_control(item='styles')
    # assert 'legal_bold' in r.keys()

# def test_get_similar(esearch, index):
    # """
    # """
    # r = esearch.get_similar(index=index, keywords=['first','registration'])
    # ids = [ i['id'][0] for i in r ]
    # expected = ['admin_receiv_adrec', 'boundaries_electro', 'leases_regd_mortgage']
    # assert not set(ids).difference(set(expected))

# @pytest.mark.parametrize('id', ['work_all_tm_ji'])
# def test_get_cluster(esearch, index,id):
    # """
    # """
    # r = esearch.get_cluster(index=index, id=id, size=1)
    # assert id in r[0]['id']

# def test_get_cluster_ist(esearch, index):
    # """
    # """
    # r = esearch.get_cluster_list(index=index)
    # assert len(r) > 100

# # def test_getWhere(esearch, index):
    # # r = esearch.getWhere(index=index, item='styles')
    # # import IPython; IPython.embed()

# # def test_clearIndex ():
    # # raise Exception('TODO')

# # def test_postLog(esearch, index):
    # # seq = '' update["seq"]
    # # url = esearch.make_url(index, "commits", "{0}-{1}".format(index, seq)).strip()
    # # r = esearch.request("get", url)
    # # import IPython; IPython.embed()


# # def test_getSuccess():
    # # raise Exception('TODO')

# # def test_getStatus():
    # # raise Exception('TODO')

# # def test_postEnd():
    # # raise Exception('TODO')

# # def test_resetUp():
    # # raise Exception('TODO')

# # def test_postUp():
    # # raise Exception('TODO')

# # def test_postKM():
    # # raise Exception('TODO')

# # def test_delKM():
    # # raise Exception('TODO')

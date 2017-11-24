import requests
import json
from datetime import datetime, timezone
from time import sleep
from guide_search.__about__ import __version__

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
from posixpath import join as posixjoin

from guide_search.dsl import Dsl
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
    ValidationError,
    )


"""
guide-search

interface to the guidance index in elasticsearch

currently built for elasticseach v1.4


"""

# TODO JP - need to put dict decodes inside try-except and return an appropriate error message if elasticsearch
# responce is not as expected. Currently error message is unhelpful.


class Esearch(object):

    def __init__(self, host,  control, Requests=requests, **kwargs):
        self.init(host, control, **kwargs)
        self.Requests=Requests

    def init(self, host, control, **kwargs):
        self.host = host
        if len(control) == 0:
            self.control = 'guide_config'
        else:
            control = control.split('/')
            for x in control:
                if len(x) > 0:
                    self.control = x
                    break

        self.logger = kwargs.get("logger", None)
        self.timeout = kwargs.get("timeout", 5)
        self.retries = kwargs.get("retries", 3)
        self.reset_session()

    def reset_session(self):
        if self.logger:
            self.logger.debug("reset elasticsearch connection")

        try:
            self.session.close()
            del self.session
        except:
            pass
        sleep(0.1) # give ES some time
        self.session = requests.Session() # create a session to keep a TCP connection open
        if self.logger:
            self.logger.debug("elastic search connection reset")

# In principle we should be using the Elasticsearch maintained python library to do requests
# however this code has worked well for a long time and mitigates the ES hanging problem we saw
    def request(self, method, url, params=None, data=None, timeout=None):
        """Makes requests to elasticsearch and returns result in json format"""
        kwargs = dict({}, **{
            'headers': {},
        })
        if params:
            kwargs['params'] = params

        # note : elastic search takes a payload on
        # GET and delete requests - this is non standard
        if data:
            if isinstance(data, str): # bulk updates are newline deliminated json
                kwargs['data'] = data
                kwargs['headers']['Content-Type'] = 'application/x-ndjson'
            else:
                kwargs['data'] = json.dumps(data)
                kwargs['headers']['Content-Type'] = 'application/json'



        # this retry loop assumes that all requests are idempotent and so we can retry on fail
        retries = 0
        while True:
            try:
                if retries > 0:
                    sleep(0.01)  # reset thread scheduling 0.0001?
                if timeout == None:
                    timeout = self.timeout
                response = getattr(self.session, method)(url,timeout=timeout,**kwargs)
                break
            except Exception as e:
                if self.logger:
                    self.logger.debug("esearch retrying {0} {1} {2}".format(retries, method, url))
                retries = retries + 1
                if retries == self.retries:
                    # the underlying libraries should normally automatically re-establish a connection
                    # this is to deal with a situation where ES has hung
                    self.reset_session()
                if retries > self.retries:
                    raise e

        if response.status_code in (200, 201):
            if not response.content.strip():  # success but no response content
                return True
            try:
                return response.json()
            except (ValueError, TypeError):
                raise JSONDecodeError(response)

        elif response.status_code == 400:
            raise BadRequestError(response.text)
        elif response.status_code == 404:
            raise ResourceNotFoundError
        elif response.status_code == 409:
            raise ConflictError
        elif response.status_code == 412:
            raise PreconditionError
        elif response.status_code == 500:
            raise ElasticsearchError(response.text)
        elif response.status_code == 503:
            raise ServiceUnreachableError
        raise UnknownError(response.status_code)

    def make_url(self, index, *args):
        url = urljoin(self.host, posixjoin(index, *args))
        return url


# JP: TODO refactor this to use the smaller functions in the DSL class
# JP: TODO refactor to make the queries between delivery and management more consistent

    def buildDsl(self, **kwargs):
        dsl = Dsl().match_all()

        if "_fields" in kwargs:
            dsl.fields(kwargs["_fields"])
        dsl.size('5000').sort('id')

        if "keywords" in kwargs:
            dsl.Q_should({"terms": {"keywords": kwargs["keywords"],
                                    "minimum_should_match": "-0%"}})  # todo THINK ABOUT DOING MATCH PHRASE HERE
        if "title" in kwargs:
            dsl.Q_should({"match": {"title": {"query": kwargs["title"], "operator": "and"}}})
        if "scope" in kwargs:
            dsl.Q_should({"match": {"scope": {"query": kwargs["scope"], "operator": "and"}}})
        if "markup" in kwargs:
            dsl.Q_should({"match": {"markup": {"query": kwargs["markup"], "operator": "and"}}})
        if "id" in kwargs:
            dsl.Q_should({"match": {"id": {"query": kwargs["id"], "operator": "and"}}})

            # filters
        # JP TODO the following 2 lines were commented out because they caused the Useful Links to fail. However they are probably needed for the editor so need to get to the bottom of this
        if "purpose" in kwargs:
           dsl.Q_filter({"match": {"purpose": kwargs["purpose"]}})

            # nested into clusters # TODO should this be a filter ?
        if "cluster" in kwargs:
            clusters = [{"term": {"clusters.cluster": kwargs["cluster"]}}]
            dsl.Q_filter({"nested": {"path": "clusters", "filter": {"bool": {"must": clusters}}}})

            # nested into facets
        if "facet" in kwargs:
            facets = [{"term": {"facets.facet": kwargs["facet"]}}]
            if "focus" in kwargs:
                facets.append({"term": {"facets.foci": kwargs["focus"]}})
            facetFilter = {"nested": {"path": "facets", "filter": {"bool": {"must": facets}}}}
            dsl.Q_filter(facetFilter)

        return dsl.dsl()


# JP: TODO think about whether to return whole ES response just the hits or something more generic
# query functions
    def search(self, index, type, dsl):
        url = self.make_url(index, type, "_search")
        r = self.request("get", url, data=dsl)
        return r


    def get_documents(self, index, type, **kwargs):
        dsl = self.buildDsl(**kwargs)

        # 2017-07-19: GE : term filter
        term = kwargs.get('term')
        if term:
            dsl['query']['bool']['filter']['bool']['must'].append({"match": { "markup": term } })

        r = self.search(index, type + "s", dsl)
        try:
            results = []
            for hit in r["hits"]["hits"]:
                results.append(hit["_source"])
            return results
        except:
            raise ResultParseError

    def get_associate_list(self, index, aType):
        # JP TODO  this needs to be re-written as it no longe makes sense as associates are items !
        articles = []
        dsl = Dsl().associate_list(aType).dsl()
        res = self.search(index, "articles", dsl)
        for hit in res["hits"]["hits"]:
            articles.append(hit["_source"])
        return {"count": res["hits"]["total"], "articles": articles}

    def get_articles(self, index, **kwargs):
        r = self.get_documents(index, "article", **kwargs)
        return r

    def get_publications(self, index, page=0, per_page=100):
        url = self.make_url(index, "record", "_search")
        
        # filter out publications with 0 high significant changes and 0 low significant changes
        filter = {"bool": {"must_not": {"bool": {"filter": [{"term": {"high": 0}}, {"term": {"low": 0}}]}}}}
        query = Dsl().match_all(filter).fields(['id']).sort("id", "desc").size(per_page, page + 1)

        res = self.request("get", url, data=query.dsl())
        publications = []
        for hit in res["hits"]["hits"]:
            publications.append(hit["_source"]["id"])
        return {"count": res["hits"]["total"], "publications": publications}

    def get_publication(self, index, id):
        url = self.make_url(index, "record",  id)
        res = self.request("get", url)
        try:
            return res["_source"]
        except:
            raise ResultParseError


    def get_items(self, index, **kwargs):
        r = self.get_documents(index, "item",  **kwargs)
        return r

    def get_snippets(self, index, **kwargs):
        r = self.get_documents(index, "snippet", **kwargs)
        return r

    # TODO need to refactor to get_object
    def get_document(self, index, type, id):
        url = self.make_url(index, type + 's', id)
        res = self.request("get", url)
        try:
            return res["_source"]
        except:
            raise ResultParseError

    def get_object(self, index, type, id):
        url = self.make_url(index, type, id)
        res = self.request("get", url)
        try:
            return res["_source"]
        except:
            raise ResultParseError

    def get_control(self, folder, id):
        url = self.make_url(self.control, folder, id)
        res = self.request("get", url)
        try:
            return res["_source"][id]
        except:
            raise ResultParseError

    def get_similar(self, index, id):
        articles = []
        dsl = Dsl().more_like_this(index, id).size(5).dsl()
        url = self.make_url(index, "articles", "_search")
        r = self.request("get", url, data=dsl)
        try:
            for hit in r["hits"]["hits"]:
                articles.append(hit["_source"])
        except:
            ResultParseError
        return articles

    def get_cluster(self, index, id, size=100):
        dsl = Dsl().query_cluster(id).size(100).dsl() 
        url = self.make_url(index, 'articles', '_search')
        res = self.request("get", url, data=dsl)
        articles = []

        try:
            for hit in res["hits"]["hits"]:
                articles.append(hit["_source"])
        except:
            ResultParseError
        return articles

    def get_cluster_list(self, index, **kwargs):
        if "max" in kwargs:
            max = kwargs["max"]
        else:
            max = 10000

        dsl = Dsl().cluster_list(max).dsl()
        url = self.make_url(index, "articles", "_search")
        res = self.request("get", url, data=dsl)

        try:
            # note I need a ordered dict that contains a list of clusters and their attributes"
            cls = dict([(c["key"], {"id": c["key"], "count": c['doc_count'], "title": "_no landing page",
                                    "scope": "no landing page for cluster " + c["key"]}) for c in
                        res["aggregations"]["clusters"]["clusters"]["buckets"]])

            cls = dict([(c["key"], {"id": c["key"], "count":c['doc_count'], "title":"_no landing page",
                                    "scope":"no landing page for cluster " + c["key"],
                                    "sens":c["sens"]["sens"]["buckets"]}) for c in
                        res["aggregations"]["clusters"]["clusters"]["buckets"]])
        except:
            ResultParseError

        dsl = Dsl().landing_list().size(max).dsl()
        url = self.make_url(index, "articles", "_search")

        res = self.request("get", url, data=dsl)

        try:
            cl = res["hits"]["hits"]
            for c in cl:
                cls[c["_source"]["id"]]["title"] = c["_source"]["title"]
                cls[c["_source"]["id"]]["scope"] = c["_source"]["scope"]
        except:
            ResultParseError

        return cls

    # editing stuff
    #
    def get_item_use(self, index, id):
        dsl = Dsl().item_use(id).dsl()
        url = self.make_url(index, 'articles', '_search')
        deps = []
        res = self.request("get", url, data=dsl)
        try:
            for hit in res["hits"]["hits"]:
                deps.append(hit["_source"]["id"])
        except:
            ResultParseError
        return deps

    def get_snippet_use(self, index, snippet_type, snippet_id):
        url = self.make_url(index, "articles", "_search")
        dsl = (Dsl().
               fields(['id']).
               sort('_score', 'desc').
               Q().
               Q_must({"term": {"snips.snip_type": snippet_type}}).
               Q_must({"term": {"snips.snip_id": snippet_id}}).
               dsl())
        res = self.request("get", url, data=dsl)
        articles = []
        for hit in res["hits"]["hits"]:
            articles.append(hit["_source"]["id"])
        return {"count": res["hits"]["total"], "articles": articles}



    # publishing stuff
    #
    # clear index and set commit record to empty
    def clear_index(self, index):
        query = Dsl().match_all().sort("seq", "desc").size("1")
        url = self.make_url(index, "commits", "_search")
        res = self.request("post", url, data=query.dsl())["hits"]["hits"]
        if len(res) == 1:
            last = res[0]["_source"]
            seq = int(last["seq"]) + 1
        else:
            seq = 0

        self.get_empty(index, "content", seq=seq)  # create a reference to empty then delete all content
        self.get_empty(index, "metadata", seq=seq)  # create a reference to empty then delete all content
        self.del_object(index, "articles", "*")  # wildcard to delete all items but not the document mapping
        self.del_object(index, "items", "*")
        self.del_object(index, "snippets", "*")

    def post_log(self, index, seq, log, pub_type):
        try:
            url = self.make_url(index, "commits", "{0}-{1}-{2}".format(index, pub_type, seq)).strip()

            r = self.request("get", url)

            last = r["_source"]

            if last['state'] not in ['updating']:
                return
            up = {}
            up["log"] = last["log"]
            up["log"].append(log)
            url = self.make_url(url, "_update")
            self.request("post", url, data={"doc": up, "doc_as_upsert": "true"}, params={"refresh": "true"})
        except:
            pass

    def post_progress(self, index, seq, progress, pub_type):
        try:
            url = self.make_url(index, "commits", "{0}-{1}-{2}".format(index, pub_type, seq)).strip()

            r = self.request("get", url)

            last = r["_source"]

            if last['state'] not in ['updating']:
                return
            up = {}
            up['log'] = json.dumps(progress) # JP TODO would be nicer if this was a object but this would require a mapping change
            url = self.make_url(url, "_update")
            self.request("post", url, data={"doc": up, "doc_as_upsert": "true"}, params={"refresh": "true"})
        except:
            pass


    # TODO think about combining this with the clear function
    def get_empty(self, index, pub_type, seq=0):
        up = {}
        # create a commit pointing to empty
        up["seq"] = seq
        up["start"] = datetime.now(timezone.utc).astimezone().isoformat()
        up["finish"] = up["start"]
        up["oldcommit"] = "empty"
        up["newcommit"] = "empty"
        up["pub_type"] = pub_type
        up["state"] = "empty"
        up["log"] = ["no commit yet"]
        url = self.make_url(index, "commits", "{0}-{1}-{2}".format(index, pub_type, up["seq"]))
        self.request("post", url, data=up)
        return up

    def get_last_success(self, index, pub_type):
        # query = {"query": {
        #             "filtered": {
        #                "query": {
        #                 "match_all": {}},
        #                "filter": {"term": {"state": "complete"}}
        #                 }
        #             },
        #          "sort": {"seq": "desc"},
        #          "size": "1"}  # es1
        filter = {"bool": {"must": [{"term": {"pub_type": pub_type}}, {"term": {"state": "complete"}}]}}
                        
        query = Dsl().match_all(filter).sort("seq", "desc").size("1")
        url = self.make_url(index, "commits", "_search")
        # r = self.request("post", url, data=query)["hits"]["hits"] # es 1
        res = self.request("post", url, data=query.dsl())
        states = res["hits"]["hits"]
        if len(states) == 0:
            return self.get_empty(index, pub_type)
        else:
            return states[0]["_source"]

    def get_state(self, index, pub_type, seq=None):
        if seq:
            url = self.make_url(index, "commits", "{0}-{1}-{2}".format(index, pub_type, seq))
            res = self.request("get", url,)
            return res["_source"]
        else:
            filter = {"term": {"pub_type": pub_type}}
            query = Dsl().match_all(filter).sort("seq", "desc").size(1)
            url = self.make_url(index, "commits", "_search")
            res = self.request("post", url, data=query.dsl())
            states = res["hits"]["hits"]
            if len(states) == 0:
                return self.get_empty(index, pub_type)
            else:
                return states[0]["_source"]

    def post_end(self, index, seq, newcommit, state, pub_type, log=None):
        last = self.get_state(index, pub_type)
        if not seq == last["seq"]:
            m = "Requested seq <{0}> does not match in progress seq <{1}>".format(seq, last["seq"])

            raise CommitError(m)
        elif not last["state"] == "updating":
            m = "Latest commit <{0}> in wrong state = {1}".format(last["seq"], last['state'])

            raise CommitError(m)
        elif not last["newcommit"] == newcommit:
            m = "Requested commit <{0}> does not match in progress commit <{1}>".format(newcommit, last["newcommit"])

            raise CommitError(m)
        else:
            last["finish"] = datetime.now(timezone.utc).astimezone().isoformat()
            last["state"] = state
            # if log:
            #     last["log"] = [log]
            # else:
            #     last["log"] = ""
            url = self.make_url(index, "commits", "{0}-{1}-{2}".format(index, pub_type, seq))
            self.request("post", url, data=last, params={"refresh": "true"})
        return last

    def reset_up(self, index, seq, pub_type):
        url = self.make_url(index, "commits", "{0}-{1}-{2}".format(index, pub_type, seq))
        self.request("delete", url)

    def post_up(self, index, last, newcommit, pub_type):
        up = {}
        # start new commit
        seq = int(last["seq"]) + 1
        up["seq"] = seq
        up["start"] = datetime.now(timezone.utc).astimezone().isoformat()
        up["finish"] = datetime(1958, 7, 6, tzinfo=timezone.utc).isoformat()
        up["oldcommit"] = last["newcommit"]
        up["newcommit"] = newcommit
        up["pub_type"] = pub_type
        up["state"] = "updating"
        up["log"] = ["updating from {0} to {1} ".format(up["oldcommit"], newcommit)]
        url = self.make_url(index, "commits", "{0}-{1}-{2}".format(index, pub_type, seq), "_update")
        self.request("post", url, data={"doc": up, "doc_as_upsert": "true"}, params={"refresh": "true"})
        return up


    # POST to partially update or completetly create - not idempotent - not safe FIXME TODO
    def post_object(self, index, oType, kmj, upsert=False):
        try:
            id_value = kmj["id"]
        except:
            raise ValidationError("no id field in json structure")

        if upsert:
            # create or update changed fields
            url = self.make_url(index, oType, id_value, "_update")
            # ES5 : True was unquoted changed this to "true"  - ES1 break ?
            doc = {"doc": kmj, "doc_as_upsert": "true"}
        else:
            # completely replace
            url = self.make_url(index, oType, id_value)
            doc = kmj

        self.request("post", url, data=doc)
        return ({"act": "upsert" if upsert else "replace", "status": "200", "reason": "OK"})

    def del_object(self, index, oType, id=""):
        try:
            # es 1
            # if (id == '*'):
            #     data = {"query": {
            #         "match_all": {}}}  # note this is deprecated and cannot be done in v 2.0 onwards
            #     url = self.make_url(index, oType, "_query")
            # else:
            #     data = {}
            #     url = self.make_url(index, oType, id)

            if (id == '*'):
                delete_query = Dsl().match_all()
                url = self.make_url(index, oType, "_delete_by_query")
                res = self.request("post", url, data=delete_query.dsl())
                # TODO read the documentation and handle error conditions.
            else:
                url = self.make_url(index, oType, id)
                res = self.request("delete", url)

        except ResourceNotFoundError:
            res = self.Requests.Response()
            res.status_code = 200
            res.reason = "Resource to be deleted did not exist <{0}>".format(url)
        return res

    def post_bulk(self, channel, bulk):
        url = self.make_url(channel, "_bulk")
        res = self.request("put", url, data=bulk, timeout=3600)
        return res

# setup stuff


    def put_control(self, folder, id, control):
        url = self.make_url(self.control, folder, id)
        if id in control:
            return self.request("put", url, data=control)
        else:
            raise ValidationError("url:{0}".format(url))

    def get_info(self):
        info = {"host": self.host,
                "controls": self.control,
                "guide_search_version": __version__
                }
        try:
            url = self.host
            res = self.request("get", url)
            info["version"] = res["version"]["number"]
            info["name"] = res["name"]
            url = self.make_url("_cluster", "health")
            try:
                health = self.request("get", url)
                info["cluster_name"] = health["cluster_name"]
                info["cluster_health"] = health["status"]
                if health["status"] == "green":
                    info["status"] = "alive"
                else:
                    info["status"] = "limping"
            except:
                info["status"] = "not quite alive"
        except:
            info["status"] = "dead"
        return info

    def get_index_health(self, index):
        current = {}
        for pub_type in ['content', 'metadata']:
            try:
                publish = self.get_state(index, pub_type)
                if publish["state"] not in ["complete", "empty"]:
                    last = self.get_last_success(index)
                    if last["newcommit"] != publish["newcommit"]:
                        publish["last_successful_commit"] = last["newcommit"]
                        publish["last_successful_publish"] = last["finish"]
                del publish["log"]
                current[pub_type] = publish
                for doctype in ["articles", "items", "snippets"]:
                    url = self.make_url(index, doctype, "_count")
                    try:
                        current[doctype] = {'state': 'OK', 'count': self.request("get", url)['count']}
                    except:
                        current[doctype] = {'state': 'error'}

            except:
                current[pub_type] = {'state': 'error', 'message': 'no publication record'}
        return current


# Aliases and copying

    def get_index(self, alias):
        '''
            {'wip-a': {'aliases': {'wip': {}}}}


        '''
        url = self.make_url(alias, '_alias')
        res = self.request("get", url)
        indices = list(res.keys()) 
        return indices

    def get_aliases(self, index):
        '''
         {'index': {'aliases': {'alias1': {}}}}
        '''
        url = self.make_url(index, '_alias')
        r = self.request("get", url)
        aliases = []
        try:
            r = r[index]['aliases']
            for k in r.keys():
                aliases.append(k)
        except:
            pass   
        return aliases

    def set_alias(self, index, alias):
        if index != self.get_index(index)[0]: # make sure we don't set an alias to an alias
            raise BadRequestError("Attempt to create an alias({0}) to an alias({1})".format(alias,index))

        try:
            self.delete_alias("_all", alias)
        except ResourceNotFoundError:
            pass

        url = self.make_url(index, '_aliases', alias)
        r = self.request("post", url)
        return r

    def copy_index(self, source, dest, mapping):
        # delete to if exists
        # map to
        # copy from - to
        # need to think about conflicts and versioning
        try:
            aliases = self.get_aliases(dest)
        except ResourceNotFoundError:
            aliases = None
        if aliases:
            raise BadRequestError("Index ({0}) has an alias ({1}) assigned".format(dest,aliases[0]))

        self.put_mapping(dest, mapping, force=True)
        query = {"source": {"index": source}, "dest": {"index": dest}}
        url = self.make_url('_reindex')
        r = self.request("post", url, data=query, timeout=60)
        return r

    def delete_alias(self, index, alias):
        url = self.make_url(index, '_alias', alias)
        r = self.request("delete", url)
        return r
    
    def delete_index(self, index, force=False):
        ind_test = self.get_index(index)[0]
        if index != ind_test:
            raise BadRequestError("Attempt to delete an index ({0}) using an alias ({1})".format(ind_test,index))
        aliases = self.get_aliases(index)  
        if (len(aliases) > 0) and  not force:
            raise BadRequestError("Attempt to delete an index ({0}) which has  an alias ({1}) assigned".format(index,aliases[0]))
        url = self.make_url(index)
        r = self.request("delete", url)
        return r

    def put_mapping(self, index, mapping, force=False):
        url = self.make_url(index)
        if force:
            try:
                self.delete_index(index, force)
            except ResourceNotFoundError:
                pass

        return self.request("put", url, data=mapping)



    def count_index(self, index):
        url = self.make_url(index, '_count')
        res = self.request("get", url)
        return res['count']


    

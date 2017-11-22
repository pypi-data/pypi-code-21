
OPSLOG_MAPPING = {
    "template" : "opslog-*",
    "mappings": {
        "opslog": {
            "_all": {
                "enabled": "false"
            },
            "properties": {
                "@timestamp": {
                    "type": "date"
                },
                "envname": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 20
                        }
                    }
                },
                "errlocation": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 20
                        }
                    }
                },
                "errseverity": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 20
                        }
                    }
                },
                "errstack": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 20
                        }
                    }
                },
                "errstackidx": {
                    "type": "long"
                },
                "keywname": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 100
                        }
                    }
                },
                "keywvalue": {
                    "type": "double"
                },
                "loghost": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 20
                        }
                    }
                },
                "logtext": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "module": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 20
                        }
                    }
                },
                "procid": {
                    "type": "long"
                },
                "procname": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 20
                        }
                    }
                }
            }
        }
    },
    "settings": {
        "index.number_of_shards": "4",
        "index.number_of_replicas": "0",
        "index.query.default_field": "logtext",
        "index.write.wait_for_active_shards": "0"
    },
    "aliases": {
        "opslog": {}
    }
}


if __name__ == '__main__':
    # ELASTICSEARCH CLIENT PYTHON API BUG put_template doesn't work
    # from elasticsearch import Elasticsearch
    # es = Elasticsearch("http://134.171.189.10")
    # es.put_template(id="opslog", body=OPSLOG_MAPPING)
    # es.get_template(id="opslog")

    import requests, json

    #Delete de template
    url = "http://134.171.189.10:9200/_template/opslog"
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r = requests.delete(url, headers=headers)

    #Create the new template
    url = "http://134.171.189.10:9200/_template/opslog"
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r = requests.post(url, data=json.dumps(OPSLOG_MAPPING), headers=headers)







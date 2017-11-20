
VLTLOG_MAPPING = {
  "template" : "vltlog-*",
  "mappings": {
    "fevt": {
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
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 100
            }
          }
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
    },
    "log": {
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
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 100
            }
          }
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
    },
    "flog": {
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
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 100
            }
          }
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
    },
    "err": {
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
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 100
            }
          }
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
    },
    "fpar": {
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
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 100
            }
          }
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
    "index.number_of_shards" : "4",
    "index.number_of_replicas" : "0",
    "index.query.default_field": "logtext",
    "index.write.wait_for_active_shards": "0"
  },
  "aliases": {
    "vltlog": {}
  }
}

if __name__ == '__main__':
    #ELASTICSEARCH CLIENT PYTHON API BUG put_template doesn't work
    #from elasticsearch import Elasticsearch
    #es = Elasticsearch("http://134.171.189.10")
    #es.put_template(id="vltlog", body=VLTLOG_MAPPING)
    #es.get_template(id="vltlog")

    import requests, json
    url = "http://134.171.189.10:9200/_template/vltlog"
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r = requests.post(url, data=json.dumps(VLTLOG_MAPPING), headers=headers)


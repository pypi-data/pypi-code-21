#!flask/bin/python
from flask import Flask, jsonify, abort, make_response
import search_api
import json

def api_server():
    app = Flask('logBlizzard')
    @app.route('/todo/api/v1.0/logs/<search>/<oper>/<stype>', methods=['GET'])
    def log_search(search,oper,stype):
        search=search.split(',')
        result=search_api.apiReq(search,oper,stype)

        return(jsonify(result))
    with open('network_cfg.json','r') as nwc:
        nw=json.load(nwc)
    API_IP=nw["API_IP"]
    app.run(host=API_IP, debug=True)

if __name__ == '__main__':
    api_server()

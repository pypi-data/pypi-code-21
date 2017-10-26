# -*- coding: utf-8 -*-

import json

def check_JSON(data):
    if isinstance(data, dict):
        return 1        
    elif isinstance(data, str):
        # check if data is a json string
        try:
            line = json.loads(data)
            return 2
        except ValueError:
            return -1
    else:
        return -1

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pycoraldb
    
if __name__ == '__main__':
    client = pycoraldb.CoralDBClient('coraldb://127.0.0.1:5166')
    client.login("test", "123456789")
    rs = client.getStat()
    print rs

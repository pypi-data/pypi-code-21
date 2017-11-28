#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/TechLaProvence/lp_mongodb

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 figarocms dhardy@figarocms.fr

import base64
import gridfs
from pymongo import MongoClient
from bson.objectid import ObjectId
from tornado.concurrent import return_future

def __conn__(self):
    connection = MongoClient(
      self.config.MONGO_LP_SERVER_HOST,
      self.config.MONGO_LP_SERVER_PORT
    )
    db = connection[self.config.MONGO_LP_SERVER_DB]
    storage = db[self.config.MONGO_LP_SERVER_COLLECTION]

    return connection, db, storage

@return_future
def load(self, path, callback):
    connection, db, storage = __conn__(self)

    stored = storage.find_one({'path': path})

    if not stored:
        callback(None)
        return

    fs = gridfs.GridFS(db)

    contents = fs.get(stored['file_id']).read()

    callback(str(contents))

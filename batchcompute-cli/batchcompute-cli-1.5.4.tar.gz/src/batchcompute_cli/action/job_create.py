
# -*- coding:utf-8 -*-

from ..util import client, formater
from terminal import  green
import json


def create(jsonString=None, filePath=None):

    desc = ''
    if jsonString:
        desc = json.loads(jsonString)
    elif filePath:
        desc = getJobJSON(filePath)
    else:
        raise Exception('Invalid json string')

    #print(desc)

    result = client.create_job(desc)

    if result.StatusCode==201:
        print(green('Job created: %s' % result.Id))


def getJobJSON(filePath):
    filePath= formater.get_abs_path(filePath)
    s = ''
    with open(filePath) as f:
        s = json.loads(f.read())
    return s
#!/usr/bin/env python
import boto.swf
from boto.exception import SWFResponseError
from boto.swf.exceptions import SWFLimitExceededError
from multiprocessing import Pool

def f(x):
    try:
        conn = boto.swf.connect_to_region("eu-west-1")
        print len(conn.list_domains("REGISTERED"))
    except SWFLimitExceededError:
        print "Rate limit exceeded!"
    except SWFResponseError as e:
        print e.error_code
        raise

if __name__ == '__main__':
    p = Pool(60)
    p.map(f, xrange(1, 150))

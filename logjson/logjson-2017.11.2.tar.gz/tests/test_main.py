import logging
import logjson
import json


def test_main():

    capture = []

    class FileLike(object):
        def write(self, data):
            capture.append(data)

    logger = logging.getLogger('blah')
    logger.addHandler(logjson.JSONHandler(pretty=True, stream=FileLike()))

    logger.info('hi %s %s!', 'you', 'there')

    print(capture[0])

    d = json.loads(capture[0])

    assert d['message'] == "hi you there!"
    assert d['name'] == "blah"


def test_logstash():

    capture = []

    class FileLike(object):
        def write(self, data):
            capture.append(data)

    logger = logging.getLogger('ls')
    logger.addHandler(logjson.JSONHandler(
        pretty=True,
        logstash_mode=True,
        stream=FileLike())
    )

    logger.info('logstash test')

    print(capture[0])

    d = json.loads(capture[0])

    assert d['@message'] == 'logstash test'
    assert d['@fields']['name'] == 'ls'


def test_exc():

    capture = []

    class FileLike(object):
        def write(self, data):
            capture.append(data)

    logger = logging.getLogger('blah')
    logger.addHandler(logjson.JSONHandler(stream=FileLike()))

    try:
        raise Exception('error')
    except:
        logger.exception('Something went wrong:')

    print(capture)
    assert capture

    d = json.loads(capture[0])

    assert d['message'].startswith('Something went wrong:')
    assert d['name'] == 'blah'
    assert d['levelname'] == 'ERROR'
    assert d['levelno'] == 40
    assert 'Traceback (most recent call last)' in d['exc_text']

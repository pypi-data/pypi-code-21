#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_netuitive
----------------------------------

Tests for `netuitive` module.
"""

import unittest
import os
import json
import time
import netuitive
import datetime

try:
    from cStringIO import StringIO

except ImportError:
    try:
        from StringIO import StringIO

    except ImportError:
        from io import StringIO


def getFixtureDirPath():
    path = os.path.join(
        os.path.dirname('tests/'),
        'fixtures')
    return path


def getFixturePath(fixture_name):
    path = os.path.join(getFixtureDirPath(),
                        fixture_name)
    if not os.access(path, os.R_OK):
        print('Missing Fixture ' + path)
    return path


def getFixture(fixture_name):
    with open(getFixturePath(fixture_name), 'r') as f:
        return StringIO(f.read())


class TestClientInit(unittest.TestCase):

    def setUp(self):
        pass

    def test_custom_endpoint(self):

        # test custom endpoint url creation
        a = netuitive.Client('https://example.com/ingest', 'apikey')
        self.assertEqual(a.url, 'https://example.com/ingest')
        self.assertEqual(a.api_key, 'apikey')
        self.assertEqual(a.dataurl, 'https://example.com/ingest/apikey')
        self.assertEqual(
            a.eventurl, 'https://example.com/ingest/events/apikey')

    def test_infrastructure_endpoint(self):

        # test infrastructure endpoint url creation
        a = netuitive.Client(
            'https://example.com/ingest/infrastructure', 'apikey')
        self.assertEqual(a.url, 'https://example.com/ingest/infrastructure')
        self.assertEqual(a.api_key, 'apikey')
        self.assertEqual(
            a.dataurl, 'https://example.com/ingest/infrastructure/apikey')
        self.assertEqual(
            a.eventurl, 'https://example.com/ingest/events/infrastructure/apikey')

    def test_minimum(self):

        # test infrastructure endpoint url creation
        a = netuitive.Client(api_key='apikey')
        self.assertEqual(a.url, 'https://api.app.netuitive.com/ingest')
        self.assertEqual(a.api_key, 'apikey')
        self.assertEqual(
            a.dataurl, 'https://api.app.netuitive.com/ingest/apikey')
        self.assertEqual(
            a.eventurl, 'https://api.app.netuitive.com/ingest/events/apikey')

    def test_trailing_slash(self):

        # test negation of trailing / on the url
        a = netuitive.Client('https://example.com/ingest/', 'apikey')
        self.assertEqual(a.url, 'https://example.com/ingest')
        self.assertEqual(a.api_key, 'apikey')
        self.assertEqual(a.dataurl, 'https://example.com/ingest/apikey')
        self.assertEqual(
            a.eventurl, 'https://example.com/ingest/events/apikey')

    def test_default_agent(self):

        # test default agent string
        a = netuitive.Client('https://example.com/ingest', 'apikey')
        self.assertEqual(a.agent, 'Netuitive-Python/' + netuitive.__version__)

    def test_custom_agent(self):

        # test default agent string
        a = netuitive.Client('https://example.com/ingest', 'apikey', 'phil')
        self.assertEqual(a.agent, 'phil')

    def tearDown(self):
        pass


class TestElementInit(unittest.TestCase):

    def setUp(self):
        pass

    def test_no_args(self):
        a = netuitive.Element()
        self.assertEqual(a.type, 'SERVER')

    def test_element_type(self):
        a = netuitive.Element('NOT_SERVER')
        self.assertEqual(a.type, 'NOT_SERVER')

    def test_element_localtion(self):
        a = netuitive.Element('SERVER', 'here')
        self.assertEqual(a.location, 'here')

        b = netuitive.Element('SERVER', location='here too')
        self.assertEqual(b.location, 'here too')

    def test_post_format(self):

        a = netuitive.Element('SERVER', 'here')
        ajson = json.dumps(
            [a], default=lambda o: o.__dict__, sort_keys=True)

        self.assertEqual(ajson, getFixture(
            'TestElementInit.test_post_format').getvalue())

    def tearDown(self):
        pass


class TestElementAttributes(unittest.TestCase):

    def setUp(self):
        self.a = netuitive.Element()
        self.a.add_attribute('Test', 'TestValue')
        self.a.add_attribute('Test2', 'TestValue2')

    def test(self):
        self.assertEqual(self.a.attributes[0].name, 'Test')
        self.assertEqual(self.a.attributes[0].value, 'TestValue')
        self.assertEqual(self.a.attributes[1].name, 'Test2')
        self.assertEqual(self.a.attributes[1].value, 'TestValue2')

    def test_post_format(self):

        ajson = json.dumps(
            [self.a], default=lambda o: o.__dict__, sort_keys=True)

        self.assertEqual(ajson, getFixture(
            'TestElementAttributes.test_post_format').getvalue())

    def tearDown(self):
        pass


class TestElementRelations(unittest.TestCase):

    def setUp(self):
        self.a = netuitive.Element()
        self.a.add_relation('Test')
        self.a.add_relation('Test2')

    def test(self):
        self.assertEqual(self.a.relations[0].fqn, 'Test')
        self.assertEqual(self.a.relations[1].fqn, 'Test2')

    def test_post_format(self):

        ajson = json.dumps(
            [self.a], default=lambda o: o.__dict__, sort_keys=True)

        self.assertEqual(ajson, getFixture(
            'TestElementRelations.test_post_format').getvalue())

    def tearDown(self):
        pass


class TestElementTags(unittest.TestCase):

    def setUp(self):
        pass

    def test(self):
        a = netuitive.Element()
        a.add_tag('Test', 'TestValue')

        self.assertEqual(a.tags[0].name, 'Test')
        self.assertEqual(a.tags[0].value, 'TestValue')

    def tearDown(self):
        pass


class TestElementSamples(unittest.TestCase):

    def setUp(self):
        pass

    def test_add_sample(self):
        a = netuitive.Element()
        a.add_sample(
            'metricId', 1434110794, 1, 'COUNTER', host='hostname')

        self.assertEqual(a.id, 'hostname')
        self.assertEqual(a.name, 'hostname')

        self.assertEqual(a.metrics[0].id, 'metricId')
        self.assertEqual(a.metrics[0].type, 'COUNTER')

    def test_add_sample_with_tags(self):
        a = netuitive.Element()
        a.add_sample(
            'tagged', 1434110794, 1, 'COUNTER', host='hostname', tags=[{'utilization': 'true'}])

        self.assertEqual(a.id, 'hostname')
        self.assertEqual(a.name, 'hostname')

        self.assertEqual(a.metrics[0].id, 'tagged')
        self.assertEqual(a.metrics[0].type, 'COUNTER')
        self.assertEqual(a.metrics[0].tags[0].name, 'utilization')
        self.assertEqual(a.metrics[0].tags[0].value, 'true')

    def test_duplicate_metrics(self):
        a = netuitive.Element()

        a.add_sample(
            'metricId', 1434110794, 1, 'COUNTER', host='hostname')

        # don't allow duplicate metrics
        self.assertEqual(len(a.metrics), 1)

        self.assertEqual(a.samples[0].metricId, 'metricId')
        self.assertEqual(a.samples[0].timestamp, 1434110794000)
        self.assertEqual(a.samples[0].val, 1)

    def test_clear_samples(self):
        a = netuitive.Element()
        a.add_sample(
            'metricId', 1434110794, 1, 'COUNTER', host='hostname')
        # test clear_samples
        self.assertEqual(len(a.metrics), 1)
        a.clear_samples()
        self.assertEqual(len(a.metrics), 0)
        self.assertEqual(len(a.samples), 0)

    def test_with_sparseDataStrategy(self):
        a = netuitive.Element()

        # test sparseDataStrategy
        a.add_sample(
            'nonsparseDataStrategy', 1434110794, 1, 'COUNTER', host='hostname')
        a.add_sample(
            'sparseDataStrategy', 1434110794, 1, 'COUNTER', host='hostname', sparseDataStrategy='ReplaceWithZero')

        self.assertEqual(a.metrics[0].sparseDataStrategy, 'None')
        self.assertEqual(
            a.metrics[1].sparseDataStrategy, 'ReplaceWithZero')

        a.clear_samples()

    def test_with_unit(self):
        a = netuitive.Element()

        # test unit
        a.add_sample(
            'unit', 1434110794, 1, 'COUNTER', host='hostname', unit='Bytes')

        a.add_sample(
            'nonunit', 1434110794, 1, 'COUNTER', host='hostname')

        self.assertEqual(
            a.metrics[0].unit, 'Bytes')

        self.assertEqual(a.metrics[1].unit, '')

    def test_with_min(self):
        a = netuitive.Element()

        a.add_sample(
            'min', 1434110794, 1, 'COUNTER', host='hostname', min=0)

        self.assertEqual(
            a.samples[0].min, 0)

    def test_with_max(self):
        a = netuitive.Element()

        a.add_sample(
            'max', 1434110794, 1, 'COUNTER', host='hostname', max=100)

        self.assertEqual(
            a.samples[0].max, 100)

    def test_with_avg(self):
        a = netuitive.Element()

        a.add_sample(
            'avg', 1434110794, 1, 'COUNTER', host='hostname', avg=50)

        self.assertEqual(
            a.samples[0].avg, 50)

    def test_with_sum(self):
        a = netuitive.Element()

        a.add_sample(
            'sum', 1434110794, 1, 'COUNTER', host='hostname', sum=2)

        self.assertEqual(
            a.samples[0].sum, 2)

    def test_with_cnt(self):
        a = netuitive.Element()

        a.add_sample(
            'cnt', 1434110794, 1, 'COUNTER', host='hostname', cnt=3)

        self.assertEqual(
            a.samples[0].cnt, 3)

    def test_add_sanitize(self):
        a = netuitive.Element()
        a.add_sample(
            'mongo.wiredTiger.cache.eviction$server populating queue,:but not evicting pages', 1434110794, 1, 'COUNTER', host='hostname')

        self.assertEqual(a.metrics[
                         0].id, 'mongo.wiredTiger.cache.eviction_server_populating_queue__but_not_evicting_pages')

    def test_post_format(self):
        a = netuitive.Element()

        a.add_sample(
            'nonsparseDataStrategy', 1434110794, 1, 'COUNTER', host='hostname')
        a.add_sample(
            'sparseDataStrategy', 1434110794, 1, 'COUNTER', host='hostname', sparseDataStrategy='ReplaceWithZero')

        a.add_sample(
            'unit', 1434110794, 1, 'COUNTER', host='hostname', unit='Bytes')

        a.add_sample(
            'nonunit', 1434110794, 1, 'COUNTER', host='hostname')

        a.add_sample(
            'tagged', 1434110794, 1, 'COUNTER', host='hostname', tags=[{'utilization': 'true'}])

        a.add_sample(
            'min', 1434110794, 1, 'COUNTER', host='hostname', min=0)

        a.add_sample(
            'max', 1434110794, 1, 'COUNTER', host='hostname', max=100)

        a.add_sample(
            'avg', 1434110794, 1, 'COUNTER', host='hostname', avg=50)

        a.add_sample(
            'sum', 1434110794, 1, 'COUNTER', host='hostname', sum=2)

        a.add_sample(
            'cnt', 1434110794, 1, 'COUNTER', host='hostname', cnt=3)

        a.add_sample(
            'min.max.avg.sum.cnt', 1434110794, 1, 'COUNTER', host='hostname', min=0, max=100, avg=50, sum=2, cnt=3)

        a.add_sample(
            'cnt2', 1475158966202, 1, 'COUNTER', host='hostname', cnt=3, ts_is_ms=True)

        ajson = json.dumps(
            [a], default=lambda o: o.__dict__, sort_keys=True)

        self.assertEqual(ajson, getFixture(
            'TestElementSamples.test_post_format').getvalue())

    def test_add_sample_ms(self):
        a = netuitive.Element()
        a.add_sample(
            'metricId', 1475158966202, 1, 'COUNTER', host='hostname', ts_is_ms=True)

        self.assertEqual(a.samples[0].timestamp, 1475158966202)

    def test_add_sample_no_timestamp(self):
        a = netuitive.Element()
        c = datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
        d = c.microseconds + (c.seconds + c.days * 86400) * 10**3

        a.add_sample(
            'metricId', None, 1, 'COUNTER', host='hostname')

        e = a.samples[0].timestamp - d

        shouldbetrue = False

        # minimum.timstamp has to be within the 10 second
        if 10000 > e:
            shouldbetrue = True

        self.assertTrue(shouldbetrue)

    def tearDown(self):
        pass


class TestEvent(unittest.TestCase):

    def setUp(self):
        self.everything = netuitive.Event('elementId', 'INFO', 'title', 'message', 'INFO',
                                          [('name0', 'value0'), ('name1', 'value1')], 1434110794, 'source')

        self.notags = netuitive.Event(
            'elementId', 'INFO', 'title', 'message', 'INFO', timestamp=1434110794, source='source')

        self.minimum = netuitive.Event(
            'elementId', 'INFO', 'title', 'message', 'INFO')

        self.everythingjson = json.dumps(
            [self.everything], default=lambda o: o.__dict__, sort_keys=True)

        self.notagsjson = json.dumps(
            [self.notags], default=lambda o: o.__dict__, sort_keys=True)

        self.minimumjson = json.dumps(
            [self.minimum], default=lambda o: o.__dict__, sort_keys=True)

    def test_all_options(self):

        # test event with all options

        self.assertEqual(self.everything.type, 'INFO')
        self.assertEqual(self.everything.title, 'title')
        self.assertEqual(self.everything.timestamp, 1434110794000)
        self.assertEqual(self.everything.tags[0].name, 'name0')
        self.assertEqual(self.everything.tags[0].value, 'value0')
        self.assertEqual(self.everything.tags[1].name, 'name1')
        self.assertEqual(self.everything.tags[1].value, 'value1')

        data = self.everything.data
        self.assertEqual(data.elementId, 'elementId')
        self.assertEqual(data.level, 'INFO')
        self.assertEqual(data.message, 'message')

    def test_no_tags(self):

        # test event without tags

        self.assertEqual(self.notags.type, 'INFO')
        self.assertEqual(self.notags.title, 'title')
        self.assertEqual(self.notags.timestamp, 1434110794000)
        self.assertEqual(hasattr(self.notags, 'tags'), False)

        data = self.notags.data
        self.assertEqual(data.elementId, 'elementId')
        self.assertEqual(data.level, 'INFO')
        self.assertEqual(data.message, 'message')

    def test_minimum(self):

        # test event with minimum options

        shouldbetrue = False
        t = int(time.time()) * 1000

        # minimum.timstamp has to be within the 10 second
        if t - 10000 < int(self.minimum.timestamp):
            shouldbetrue = True

        self.assertTrue(shouldbetrue)
        self.assertEqual(self.minimum.title, 'title')
        self.assertEqual(self.minimum.type, 'INFO')

        data = self.minimum.data
        self.assertEqual(data.elementId, 'elementId')
        self.assertEqual(data.level, 'INFO')
        self.assertEqual(data.message, 'message')

    def test_post_format_everthing(self):
        # test post format for event with all options

        self.assertEqual(self.everythingjson, getFixture(
            'TestEvent.test_post_format_everthing').getvalue())

    def test_post_format_notags(self):
        # test post format for event without tags

        self.assertEqual(self.notagsjson, getFixture(
            'TestEvent.test_post_format_notags').getvalue())

    def test_post_format_minimum(self):
        # test post format for event with minimum options

        self.assertEqual(self.minimumjson, getFixture(
            'TestEvent.test_post_format_minimum').getvalue().replace('TIMESTAMP_TEMPLATE', str(self.minimum.timestamp)))

    def tearDown(self):
        pass


class TestCheck(unittest.TestCase):

    def setUp(self):
        self.check = netuitive.Check('checkName', 'elementId', 60)

    def test_check(self):

        self.assertEqual(self.check.name, 'checkName')
        self.assertEqual(self.check.elementId, 'elementId')
        self.assertEqual(self.check.interval, 60)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()

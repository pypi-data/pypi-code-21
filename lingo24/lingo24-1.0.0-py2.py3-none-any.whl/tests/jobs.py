# -*- coding: utf-8 -*-
import datetime
import json
from decimal import Decimal

import requests_mock

from lingo24.business_documents import Authenticator, Client
from lingo24.business_documents.files import File
from lingo24.business_documents.jobs import Job, JobPrice, Price, Metric
from lingo24.business_documents.locales import Locale
from lingo24.business_documents.projects import Project
from lingo24.business_documents.services import Service
from lingo24.exceptions import APIError, DoesNotExist

from .base import BaseTestCase


class JobTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)
        self.project = Project(self.client, 1, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')

    def test_equality(self):
        project2 = Project(self.client, 1, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')

        self.assertEqual(Job(self.project.jobs, 1, 'aaa', 2, 3, 4, 5, 6), Job(self.project.jobs, 1, 'aaa', 2, 3, 4, 5, 6))
        self.assertNotEqual(Job(self.project.jobs, 1, 'aaa', 2, 3, 4, 5, 6), Job(self.project.jobs, 10, 'aaa', 2, 3, 4, 5, 6))
        self.assertNotEqual(Job(self.project.jobs, 1, 'aaa', 2, 3, 4, 5, 6), Job(self.project.jobs, 1, 'bbb', 2, 3, 4, 5, 6))
        self.assertNotEqual(Job(self.project.jobs, 1, 'aaa', 2, 3, 4, 5, 6), Job(self.project.jobs, 1, 'aaa', 20, 3, 4, 5, 6))
        self.assertNotEqual(Job(self.project.jobs, 1, 'aaa', 2, 3, 4, 5, 6), Job(self.project.jobs, 1, 'aaa', 2, 30, 4, 5, 6))
        self.assertNotEqual(Job(self.project.jobs, 1, 'aaa', 2, 3, 4, 5, 6), Job(self.project.jobs, 1, 'aaa', 2, 3, 40, 5, 6))
        self.assertNotEqual(Job(self.project.jobs, 1, 'aaa', 2, 3, 4, 5, 6), Job(self.project.jobs, 1, 'aaa', 2, 3, 4, 50, 6))
        self.assertNotEqual(Job(self.project.jobs, 1, 'aaa', 2, 3, 4, 5, 6), Job(self.project.jobs, 1, 'aaa', 2, 3, 4, 5, 60))

    def test_url_path(self):
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertEqual(job.url_path, 'projects/1/jobs/123')

    def test_client(self):
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertEqual(job.client, self.client)

    @requests_mock.mock()
    def test_service(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/services/2', text=json.dumps({
            'id': 2,
            'name': 'aaa',
            'description': 'AAA',
        }))
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertEqual(job.service, Service(2, 'aaa', 'AAA'))

    @requests_mock.mock()
    def test_source_locale(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/locales/3', text=json.dumps({
            'id': 3,
            'name': 'aaa',
            'language': 'AAA',
            'country': 'xxx',
        }))
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertEqual(job.source_locale, Locale(3, 'aaa', 'AAA', 'xxx'))

    @requests_mock.mock()
    def test_target_locale(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/locales/4', text=json.dumps({
            'id': 4,
            'name': 'aaa',
            'language': 'AAA',
            'country': 'xxx',
        }))
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertEqual(job.target_locale, Locale(4, 'aaa', 'AAA', 'xxx'))

    @requests_mock.mock()
    def test_source_file(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/files/5', text=json.dumps({
            'id': 5,
            'name': 'Source.txt',
            'type': 'SOURCE',
        }))
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertEqual(job.source_file, File(self.client, 5, 'Source.txt', 'SOURCE'))

    @requests_mock.mock()
    def test_source_file_missing(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/files/5', status_code=404)
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertRaises(DoesNotExist, lambda: job.source_file)

    @requests_mock.mock()
    def test_source_file_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/files/5', status_code=500)
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertRaises(APIError, lambda: job.source_file)

    @requests_mock.mock()
    def test_target_file(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/files/6', text=json.dumps({
            'id': 6,
            'name': 'Target.txt',
            'type': 'TARGET',
        }))
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertEqual(job.target_file, File(self.client, 6, 'Target.txt', 'TARGET'))

    def test_target_file_empty(self):
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, None)
        self.assertIsNone(job.target_file)

    @requests_mock.mock()
    def test_target_file_missing(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/files/6', status_code=404)
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertRaises(DoesNotExist, lambda: job.target_file)

    @requests_mock.mock()
    def test_target_file_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/files/6', status_code=500)
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertRaises(APIError, lambda: job.target_file)

    @requests_mock.mock()
    def test_price(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/price', text=json.dumps({
            'currencyCode': 'GBP',
            'totalWoVatWDiscount': '11.11',
            'totalWVatWDiscount': '22.22',
            'totalWoVatWoDiscount': '33.33',
            'totalWVatWoDiscount': '44.44',
        }))
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertEqual(job.price, JobPrice(
            total_with_discount=Price('GBP', Decimal('11.11'), Decimal('22.22')),
            total_without_discount=Price('GBP', Decimal('33.33'), Decimal('44.44')),
        ))

    @requests_mock.mock()
    def test_price_missing(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/price', status_code=404)
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertIsNone(job.price)

    @requests_mock.mock()
    def test_price_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/price', status_code=500)
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertRaises(APIError, lambda: job.price)

    @requests_mock.mock()
    def test_metrics(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/metrics', text=json.dumps({
            'values': {
                'AAA': {'WHITE_SPACES': 1, 'SEGMENTS': 2, 'WORDS': 3, 'CHARACTERS': 4},
                'BBB': {'WHITE_SPACES': 5, 'SEGMENTS': 6, 'WORDS': 7, 'CHARACTERS': 8},
                'CCC': {'WHITE_SPACES': 9, 'SEGMENTS': 10, 'WORDS': 11, 'CHARACTERS': 12},
            }
        }))
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertDictEqual(job.metrics, {
            'AAA': Metric(1, 2, 3, 4),
            'BBB': Metric(5, 6, 7, 8),
            'CCC': Metric(9, 10, 11, 12),
        })

    @requests_mock.mock()
    def test_metrics_missing(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/metrics', status_code=404)
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertDictEqual(job.metrics, {})

    @requests_mock.mock()
    def test_metrics_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/metrics', status_code=500)
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertRaises(APIError, lambda: job.metrics)

    @requests_mock.mock()
    def test_delete(self, m):
        m.delete('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123')
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        job.delete()

    @requests_mock.mock()
    def test_delete_error(self, m):
        m.delete('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123', status_code=500)
        job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)
        self.assertRaises(APIError, job.delete)


class JobPriceTestCase(BaseTestCase):
    def test_equality(self):
        self.assertEqual(
            JobPrice(Price('GBP', 111, 222), Price('GBP', 333, 444)),
            JobPrice(Price('GBP', 111, 222), Price('GBP', 333, 444)),
        )
        self.assertNotEqual(
            JobPrice(Price('GBP', 111, 222), Price('GBP', 333, 444)),
            JobPrice(Price('USD', 111, 222), Price('GBP', 333, 444)),
        )
        self.assertNotEqual(
            JobPrice(Price('GBP', 111, 222), Price('GBP', 333, 444)),
            JobPrice(Price('GBP', 111, 222), Price('USD', 333, 444)),
        )


class PriceTestCase(BaseTestCase):
    def test_equality(self):
        self.assertEqual(Price('GBP', 123, 456), Price('GBP', 123, 456))
        self.assertNotEqual(Price('GBP', 123, 456), Price('USD', 123, 456))
        self.assertNotEqual(Price('GBP', 123, 456), Price('GBP', 111, 456))
        self.assertNotEqual(Price('GBP', 123, 456), Price('GBP', 123, 111))

    def test_tax(self):
        price = Price('GBP', 123, 456)
        self.assertEqual(price.tax, 333)

    def test_formatted_net(self):
        self.assertEqual(Price('GBP', 123, 456).formatted_net, u'£123')
        self.assertEqual(Price('EUR', 123, 456).formatted_net, u'€123')
        self.assertEqual(Price('USD', 123, 456).formatted_net, u'$123')
        self.assertEqual(Price('AUD', 123, 456).formatted_net, u'AUD 123')

    def test_formatted_gross(self):
        self.assertEqual(Price('GBP', 123, 456).formatted_gross, u'£456')
        self.assertEqual(Price('EUR', 123, 456).formatted_gross, u'€456')
        self.assertEqual(Price('USD', 123, 456).formatted_gross, u'$456')
        self.assertEqual(Price('AUD', 123, 456).formatted_gross, u'AUD 456')

    def test_formatted_tax(self):
        self.assertEqual(Price('GBP', 123, 456).formatted_tax, u'£333')
        self.assertEqual(Price('EUR', 123, 456).formatted_tax, u'€333')
        self.assertEqual(Price('USD', 123, 456).formatted_tax, u'$333')
        self.assertEqual(Price('AUD', 123, 456).formatted_tax, u'AUD 333')


class MetricTestCase(BaseTestCase):
    def test_equality(self):
        self.assertEqual(Metric(1, 2, 3, 4), Metric(1, 2, 3, 4))
        self.assertNotEqual(Metric(1, 2, 3, 4), Metric(5, 2, 3, 4))
        self.assertNotEqual(Metric(1, 2, 3, 4), Metric(1, 5, 3, 4))
        self.assertNotEqual(Metric(1, 2, 3, 4), Metric(1, 2, 5, 4))
        self.assertNotEqual(Metric(1, 2, 3, 4), Metric(1, 2, 3, 5))


class JobFileCollectionBasicTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)
        self.project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')
        self.job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)

    def test_make_item(self):
        file_obj = self.job.files.make_item(
            id=1,
            name='aaa',
            type='SOURCE',
            )
        self.assertEqual(file_obj, File(self.client, 1, 'aaa', 'SOURCE'))

    def test_equality(self):
        self.assertEqual(self.job.files, self.job.files)

    def test_clone(self):
        files = self.job.files
        clone = files.clone()
        self.assertEqual(files, clone)
        self.assertIsNot(files, clone)

    def test_item_url_path(self):
        self.assertEqual(self.job.files.item_url_path(123), 'projects/1/jobs/123/files/123')

    @requests_mock.mock()
    def test_get(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/files/12345', text=json.dumps({
            'id': 12345,
            'name': 'aaa',
            'type': 'SOURCE',
        }))
        file_obj = self.job.files.get(12345)
        self.assertEqual(file_obj, File(self.client, 12345, 'aaa', 'SOURCE'))

    @requests_mock.mock()
    def test_get_missing(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/files/123', status_code=404)
        self.assertRaises(DoesNotExist, self.job.files.get, 123)

    @requests_mock.mock()
    def test_get_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/files/123', status_code=500)
        self.assertRaises(APIError, self.job.files.get, 123)


class JobFileCollectionEmptyTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)
        self.project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')
        self.job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)

    @staticmethod
    def setup_data(m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/files?page=0&size=4', text=json.dumps({
            'content': [],
            'page': {
                'size': 0,
                'totalElements': 0,
                'totalPages': 0,
                'number': 0,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/files?page=1&size=4', status_code=404)

    @requests_mock.mock()
    def test_page_count(self, m):
        self.setup_data(m)
        self.assertEqual(self.job.files.page_count, 0)

    @requests_mock.mock()
    def test_len(self, m):
        self.setup_data(m)
        self.assertEqual(len(self.job.files), 0)

    @requests_mock.mock()
    def test_iteration(self, m):
        self.setup_data(m)
        it = iter(self.job.files)
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_iteration_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/files?page=0&size=4', status_code=500)
        it = iter(self.job.files)
        self.assertRaises(APIError, it.next)

    @requests_mock.mock()
    def test_indexing(self, m):
        self.setup_data(m)
        self.assertRaises(IndexError, lambda i: self.job.files[i], -1)
        self.assertRaises(IndexError, lambda i: self.job.files[i], 0)
        self.assertRaises(TypeError, lambda i: self.job.files[i], 'xxx')

    @requests_mock.mock()
    def test_slice_start(self, m):
        self.setup_data(m)
        it = iter(self.job.files[:5])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_middle(self, m):
        self.setup_data(m)
        it = iter(self.job.files[2:9])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_end(self, m):
        self.setup_data(m)
        it = iter(self.job.files[7:])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_step(self, m):
        self.setup_data(m)
        it = iter(self.job.files[2:9:2])
        self.assertRaises(StopIteration, it.next)


class JobFileCollectionDataTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)
        self.project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')
        self.job = Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6)

    @staticmethod
    def setup_data(m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/files', text=json.dumps({
            'links': [
                {'rel': 'next', 'href': 'https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/files?page=1&size=4'},
            ],
            'content': [
                {'id': 1, 'name': 'Name1.txt', 'type': 'SOURCE'},
                {'id': 2, 'name': 'Name2.txt', 'type': 'SOURCE'},
                {'id': 3, 'name': 'Name3.txt', 'type': 'SOURCE'},
                {'id': 4, 'name': 'Name4.txt', 'type': 'SOURCE'},
            ],
            'page': {
                'size': 4,
                'totalElements': 10,
                'totalPages': 3,
                'number': 0,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/files?page=1&size=4', text=json.dumps({
            'links': [
                {'rel': 'next', 'href': 'https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/files?page=2&size=4'},
            ],
            'content': [
                {'id': 5, 'name': 'Name5.txt', 'type': 'SOURCE'},
                {'id': 6, 'name': 'Name6.txt', 'type': 'SOURCE'},
                {'id': 7, 'name': 'Name7.txt', 'type': 'SOURCE'},
                {'id': 8, 'name': 'Name8.txt', 'type': 'SOURCE'},
            ],
            'page': {
                'size': 4,
                'totalElements': 10,
                'totalPages': 3,
                'number': 1,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/files?page=2&size=4', text=json.dumps({
            'content': [
                {'id': 9, 'name': 'Name9.txt', 'type': 'SOURCE'},
                {'id': 10, 'name': 'Name10.txt', 'type': 'SOURCE'},
            ],
            'page': {
                'size': 2,
                'totalElements': 10,
                'totalPages': 3,
                'number': 2,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123/files?page=10&size=4', status_code=404)

    @requests_mock.mock()
    def test_page_count(self, m):
        self.setup_data(m)
        self.assertEqual(self.job.files.page_count, 3)

    @requests_mock.mock()
    def test_len(self, m):
        self.setup_data(m)
        self.assertEqual(len(self.job.files), 10)

    @requests_mock.mock()
    def test_iteration(self, m):
        self.setup_data(m)
        it = iter(self.job.files)
        self.assertEqual(it.next(), File(self.client, 1, 'Name1.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 2, 'Name2.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 3, 'Name3.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 4, 'Name4.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 5, 'Name5.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 6, 'Name6.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 7, 'Name7.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 8, 'Name8.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 9, 'Name9.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 10, 'Name10.txt', 'SOURCE'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_indexing(self, m):
        self.setup_data(m)
        self.assertRaises(IndexError, lambda i: self.job.files[i], -1)
        self.assertRaises(IndexError, lambda i: self.job.files[i], 10)
        self.assertEqual(self.job.files[5], File(self.client, 6, 'Name6.txt', 'SOURCE'))

    @requests_mock.mock()
    def test_slice_start(self, m):
        self.setup_data(m)
        it = iter(self.job.files[:5])
        self.assertEqual(it.next(), File(self.client, 1, 'Name1.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 2, 'Name2.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 3, 'Name3.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 4, 'Name4.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 5, 'Name5.txt', 'SOURCE'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_middle(self, m):
        self.setup_data(m)
        it = iter(self.job.files[2:9])
        self.assertEqual(it.next(), File(self.client, 3, 'Name3.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 4, 'Name4.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 5, 'Name5.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 6, 'Name6.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 7, 'Name7.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 8, 'Name8.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 9, 'Name9.txt', 'SOURCE'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_end(self, m):
        self.setup_data(m)
        it = iter(self.job.files[7:])
        self.assertEqual(it.next(), File(self.client, 8, 'Name8.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 9, 'Name9.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 10, 'Name10.txt', 'SOURCE'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_step(self, m):
        self.setup_data(m)
        it = iter(self.job.files[2:9:2])
        self.assertEqual(it.next(), File(self.client, 3, 'Name3.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 5, 'Name5.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 7, 'Name7.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 9, 'Name9.txt', 'SOURCE'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_get_page(self, m):
        self.setup_data(m)
        it = iter(self.job.files.get_page(1))
        self.assertEqual(it.next(), File(self.client, 5, 'Name5.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 6, 'Name6.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 7, 'Name7.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 8, 'Name8.txt', 'SOURCE'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_get_page_non_existant(self, m):
        self.setup_data(m)
        it = iter(self.job.files.get_page(10))
        self.assertRaises(StopIteration, it.next)

import datetime
import json
from decimal import Decimal

import requests_mock

from lingo24.business_documents import Authenticator, Client
from lingo24.business_documents.domains import Domain
from lingo24.business_documents.files import File
from lingo24.business_documents.jobs import Job
from lingo24.business_documents.pricing import Charge, Price, TotalPrice
from lingo24.business_documents.projects import Project, ProjectCollection
from lingo24.exceptions import APIError, DoesNotExist, InvalidState

from .base import BaseTestCase


class ProjectTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)

    def test_equality(self):
        self.assertEqual(Project(self.client, 1, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc'), Project(self.client, 1, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc'))
        # self.assertNotEqual(Project(self.client, 1, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc'), Project(None, 1, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc'))
        self.assertNotEqual(Project(self.client, 1, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc'), Project(self.client, 2, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc'))
        self.assertNotEqual(Project(self.client, 1, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc'), Project(self.client, 1, 'xxx', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc'))
        self.assertNotEqual(Project(self.client, 1, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc'), Project(self.client, 1, 'aaa', 3, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc'))
        self.assertNotEqual(Project(self.client, 1, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc'), Project(self.client, 1, 'aaa', 2, 'xxx', datetime.datetime.utcfromtimestamp(123), 'ccc'))
        self.assertNotEqual(Project(self.client, 1, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc'), Project(self.client, 1, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(456), 'ccc'))
        self.assertNotEqual(Project(self.client, 1, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc'), Project(self.client, 1, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'xxx'))

    @requests_mock.mock()
    def test_domain(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/domains/123', text=json.dumps({
            'id': 123,
            'name': 'xxx',
        }))
        project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')
        self.assertEqual(project.domain, Domain(123, 'xxx'))

    def test_domain_none(self):
        project = Project(self.client, 1, 'aaa', None, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')
        self.assertIsNone(project.domain)

    def test_url_path(self):
        project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')
        self.assertEqual('projects/1', project.url_path)

    @requests_mock.mock()
    def test_price(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/price', text=json.dumps({
            'currencyCode': 'GBP',
            'totalWoVatWDiscount': '11.11',
            'totalWVatWDiscount': '22.22',
            'totalWoVatWoDiscount': '33.33',
            'totalWVatWoDiscount': '44.44',
        }))
        project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')
        self.assertEqual(project.price, TotalPrice(
            total_with_discount=Price('GBP', Decimal('11.11'), Decimal('22.22')),
            total_without_discount=Price('GBP', Decimal('33.33'), Decimal('44.44')),
        ))

    @requests_mock.mock()
    def test_price_missing(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/price', status_code=404)
        project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')
        self.assertIsNone(project.price)

    @requests_mock.mock()
    def test_price_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/price', status_code=500)
        project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')
        self.assertRaises(APIError, lambda: project.price)

    @requests_mock.mock()
    def test_refresh(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1', text=json.dumps({
            'id': 1,
            'name': 'xxx',
            'domainId': 3,
            'projectStatus': 'yyy',
            'created': 456,
            'projectCallbackUrl': 'zzz',
        }))
        project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')
        project.refresh()
        self.assertEqual(project, Project(self.client, 1, 'xxx', 3, 'yyy', datetime.datetime.utcfromtimestamp(456), 'zzz'))

    @requests_mock.mock()
    def test_request_quote(self, m):
        def text_callback(request, context):
            self.assertDictEqual(request.json(), {
                'projectStatus': 'QUOTED',
            })
            return json.dumps({})

        m.put('https://api-demo.lingo24.com/docs/v1/projects/1', text=text_callback)
        project = Project(self.client, 1, 'aaa', 123, 'CREATED', datetime.datetime.utcfromtimestamp(123), 'ccc')
        project.request_quote()
        self.assertEqual(project.status, 'PENDING')

    @requests_mock.mock()
    def test_request_quote_invalid_state(self, m):
        project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')
        self.assertRaises(InvalidState, project.request_quote)

    @requests_mock.mock()
    def test_request_quote_error(self, m):
        m.put('https://api-demo.lingo24.com/docs/v1/projects/1', status_code=400)
        project = Project(self.client, 1, 'aaa', 123, 'CREATED', datetime.datetime.utcfromtimestamp(123), 'ccc')
        self.assertRaises(APIError, project.request_quote)

    @requests_mock.mock()
    def test_cancel(self, m):
        m.delete('https://api-demo.lingo24.com/docs/v1/projects/1')
        project = Project(self.client, 1, 'aaa', 123, 'CREATED', datetime.datetime.utcfromtimestamp(123), 'ccc')
        project.cancel()
        self.assertEqual(project.status, 'CANCELLED')
        self.assertRaises(InvalidState, project.cancel)

        project.status = 'PENDING'
        project.cancel()
        self.assertEqual(project.status, 'CANCELLED')
        self.assertRaises(InvalidState, project.cancel)

        project.status = 'QUOTED'
        project.cancel()
        self.assertEqual(project.status, 'CANCELLED')
        self.assertRaises(InvalidState, project.cancel)

    @requests_mock.mock()
    def test_cancel_invalid_state(self, m):
        project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')
        self.assertRaises(InvalidState, project.cancel)

    @requests_mock.mock()
    def test_cancel_error(self, m):
        m.delete('https://api-demo.lingo24.com/docs/v1/projects/1', status_code=400)
        project = Project(self.client, 1, 'aaa', 123, 'CREATED', datetime.datetime.utcfromtimestamp(123), 'ccc')
        self.assertRaises(APIError, project.cancel)

    @requests_mock.mock()
    def test_accept_quote(self, m):
        def text_callback(request, context):
            self.assertDictEqual(request.json(), {
                'projectStatus': 'IN_PROGRESS',
            })
            return json.dumps({})

        m.put('https://api-demo.lingo24.com/docs/v1/projects/1', text=text_callback)
        project = Project(self.client, 1, 'aaa', 123, 'QUOTED', datetime.datetime.utcfromtimestamp(123), 'ccc')
        project.accept_quote()
        self.assertEqual(project.status, 'IN_PROGRESS')

    @requests_mock.mock()
    def test_accept_quote_invalid_state(self, m):
        project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')
        self.assertRaises(InvalidState, project.accept_quote)

    @requests_mock.mock()
    def test_accept_quote_error(self, m):
        m.put('https://api-demo.lingo24.com/docs/v1/projects/1', status_code=400)
        project = Project(self.client, 1, 'aaa', 123, 'QUOTED', datetime.datetime.utcfromtimestamp(123), 'ccc')
        self.assertRaises(APIError, project.accept_quote)


class ProjectCollectionBasicTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)

    def test_make_item(self):
        project = self.client.projects.make_item(
            id=1,
            name='aaa',
            domainId=2,
            projectStatus='bbb',
            created=123,
            projectCallbackUrl='ccc',
            )
        self.assertEqual(project, Project(self.client, 1, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc'))

    def test_equality(self):
        self.assertEqual(self.client.projects, self.client.projects)

    def test_clone(self):
        projects = self.client.projects
        clone = projects.clone()
        self.assertEqual(projects, clone)
        self.assertIsNot(projects, clone)

    def test_item_url_path(self):
        self.assertEqual(self.client.projects.item_url_path(123), 'projects/123')

    def test_sort(self):
        projects = self.client.projects
        projects_by_name = projects.sort('name')
        projects_by_status = projects_by_name.sort('projectStatus')
        self.assertNotEqual(projects, projects_by_name)
        self.assertNotEqual(projects_by_name, projects_by_status)
        self.assertDictEqual(projects.make_query_dict(page_index=0), {'page': 0, 'size': 4})
        self.assertDictEqual(projects_by_name.make_query_dict(page_index=0), {'page': 0, 'size': 4, 'sort': 'name'})
        self.assertDictEqual(projects_by_status.make_query_dict(page_index=0), {'page': 0, 'size': 4, 'sort': 'projectStatus'})

    @requests_mock.mock()
    def test_get(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/12345', text=json.dumps({
            'id': 12345,
            'name': 'aaa',
            'domainId': 2,
            'projectStatus': 'bbb',
            'created': 123,
            'projectCallbackUrl': 'ccc',
        }))
        project = self.client.projects.get(12345)
        self.assertEqual(project, Project(self.client, 12345, 'aaa', 2, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc'))

    @requests_mock.mock()
    def test_get_missing(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/123', status_code=404)
        self.assertRaises(DoesNotExist, self.client.projects.get, 123)

    @requests_mock.mock()
    def test_get_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/123', status_code=500)
        self.assertRaises(APIError, self.client.projects.get, 123)

    @requests_mock.mock()
    def test_create(self, m):
        def text_callback(request, context):
            self.assertDictEqual(request.json(), {
                'name': 'Name',
                'domainId': 123,
            })
            return json.dumps({
                'id': 12345,
                'name': 'Name',
                'domainId': 123,
                'projectStatus': 'xxx',
                'created': 100,
                'projectCallbackUrl': 'yyy',
            })

        m.post('https://api-demo.lingo24.com/docs/v1/projects', text=text_callback)
        project = self.client.projects.create('Name', 123)
        self.assertEqual(project, Project(self.client, 12345, 'Name', 123, 'xxx', datetime.datetime.utcfromtimestamp(100), 'yyy'))

    @requests_mock.mock()
    def test_create_error(self, m):
        m.post('https://api-demo.lingo24.com/docs/v1/projects', status_code=400)
        self.assertRaises(APIError, self.client.projects.create, 'Name', 123)


class ProjectCollectionEmptyTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)

    @staticmethod
    def setup_data(m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/?page=0&size=4', text=json.dumps({
            'content': [],
            'page': {
                'size': 0,
                'totalElements': 0,
                'totalPages': 0,
                'number': 0,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/?page=1&size=4', status_code=404)

    @requests_mock.mock()
    def test_page_count(self, m):
        self.setup_data(m)
        self.assertEqual(self.client.projects.page_count, 0)

    @requests_mock.mock()
    def test_len(self, m):
        self.setup_data(m)
        self.assertEqual(len(self.client.projects), 0)

    @requests_mock.mock()
    def test_iteration(self, m):
        self.setup_data(m)
        it = iter(self.client.projects)
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_iteration_Error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/?page=0&size=4', status_code=500)
        it = iter(self.client.projects)
        self.assertRaises(APIError, it.next)

    @requests_mock.mock()
    def test_indexing(self, m):
        self.setup_data(m)
        self.assertRaises(IndexError, lambda i: self.client.projects[i], -1)
        self.assertRaises(IndexError, lambda i: self.client.projects[i], 0)
        self.assertRaises(TypeError, lambda i: self.client.projects[i], 'xxx')

    @requests_mock.mock()
    def test_slice_start(self, m):
        self.setup_data(m)
        it = iter(self.client.projects[:5])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_middle(self, m):
        self.setup_data(m)
        it = iter(self.client.projects[2:9])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_end(self, m):
        self.setup_data(m)
        it = iter(self.client.projects[7:])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_step(self, m):
        self.setup_data(m)
        it = iter(self.client.projects[2:9:2])
        self.assertRaises(StopIteration, it.next)


class ProjectCollectionDataTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)

    @staticmethod
    def setup_data(m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/?page=0&size=4', text=json.dumps({
            'links': [
                {'rel': 'next', 'href': 'https://api-demo.lingo24.com/docs/v1/projects/?page=1&size=4'},
            ],
            'content': [
                {'id': 1, 'name': 'Name1', 'domainId': 100, 'projectStatus': 'Status1', 'created': 111, 'projectCallbackUrl': 'Callback1'},
                {'id': 2, 'name': 'Name2', 'domainId': 200, 'projectStatus': 'Status2', 'created': 222, 'projectCallbackUrl': 'Callback2'},
                {'id': 3, 'name': 'Name3', 'domainId': 300, 'projectStatus': 'Status3', 'created': 333, 'projectCallbackUrl': 'Callback3'},
                {'id': 4, 'name': 'Name4', 'domainId': 400, 'projectStatus': 'Status4', 'created': 444, 'projectCallbackUrl': 'Callback4'},
            ],
            'page': {
                'size': 4,
                'totalElements': 10,
                'totalPages': 3,
                'number': 0,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/?page=1&size=4', text=json.dumps({
            'links': [
                {'rel': 'next', 'href': 'https://api-demo.lingo24.com/docs/v1/projects/?page=2&size=4'},
            ],
            'content': [
                {'id': 5, 'name': 'Name5', 'domainId': 500, 'projectStatus': 'Status5', 'created': 555, 'projectCallbackUrl': 'Callback5'},
                {'id': 6, 'name': 'Name6', 'domainId': 600, 'projectStatus': 'Status6', 'created': 666, 'projectCallbackUrl': 'Callback6'},
                {'id': 7, 'name': 'Name7', 'domainId': 700, 'projectStatus': 'Status7', 'created': 777, 'projectCallbackUrl': 'Callback7'},
                {'id': 8, 'name': 'Name8', 'domainId': 800, 'projectStatus': 'Status8', 'created': 888, 'projectCallbackUrl': 'Callback8'},
            ],
            'page': {
                'size': 4,
                'totalElements': 10,
                'totalPages': 3,
                'number': 1,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/?page=2&size=4', text=json.dumps({
            'content': [
                {'id': 9, 'name': 'Name9', 'domainId': 900, 'projectStatus': 'Status9', 'created': 999, 'projectCallbackUrl': 'Callback9'},
                {'id': 10, 'name': 'Name10', 'domainId': 1000, 'projectStatus': 'Status10', 'created': 101010, 'projectCallbackUrl': 'Callback10'},
            ],
            'page': {
                'size': 2,
                'totalElements': 10,
                'totalPages': 3,
                'number': 2,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/?page=10&size=4', status_code=404)

    @requests_mock.mock()
    def test_page_count(self, m):
        self.setup_data(m)
        self.assertEqual(self.client.projects.page_count, 3)

    @requests_mock.mock()
    def test_len(self, m):
        self.setup_data(m)
        self.assertEqual(len(self.client.projects), 10)

    @requests_mock.mock()
    def test_iteration(self, m):
        self.setup_data(m)
        it = iter(self.client.projects)
        self.assertEqual(it.next(), Project(self.client, 1, 'Name1', 100, 'Status1', datetime.datetime.utcfromtimestamp(111), 'Callback1'))
        self.assertEqual(it.next(), Project(self.client, 2, 'Name2', 200, 'Status2', datetime.datetime.utcfromtimestamp(222), 'Callback2'))
        self.assertEqual(it.next(), Project(self.client, 3, 'Name3', 300, 'Status3', datetime.datetime.utcfromtimestamp(333), 'Callback3'))
        self.assertEqual(it.next(), Project(self.client, 4, 'Name4', 400, 'Status4', datetime.datetime.utcfromtimestamp(444), 'Callback4'))
        self.assertEqual(it.next(), Project(self.client, 5, 'Name5', 500, 'Status5', datetime.datetime.utcfromtimestamp(555), 'Callback5'))
        self.assertEqual(it.next(), Project(self.client, 6, 'Name6', 600, 'Status6', datetime.datetime.utcfromtimestamp(666), 'Callback6'))
        self.assertEqual(it.next(), Project(self.client, 7, 'Name7', 700, 'Status7', datetime.datetime.utcfromtimestamp(777), 'Callback7'))
        self.assertEqual(it.next(), Project(self.client, 8, 'Name8', 800, 'Status8', datetime.datetime.utcfromtimestamp(888), 'Callback8'))
        self.assertEqual(it.next(), Project(self.client, 9, 'Name9', 900, 'Status9', datetime.datetime.utcfromtimestamp(999), 'Callback9'))
        self.assertEqual(it.next(), Project(self.client, 10, 'Name10', 1000, 'Status10', datetime.datetime.utcfromtimestamp(101010), 'Callback10'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_indexing(self, m):
        self.setup_data(m)
        self.assertRaises(IndexError, lambda i: self.client.projects[i], -1)
        self.assertRaises(IndexError, lambda i: self.client.projects[i], 10)
        self.assertEqual(self.client.projects[5], Project(self.client, 6, 'Name6', 600, 'Status6', datetime.datetime.utcfromtimestamp(666), 'Callback6'))

    @requests_mock.mock()
    def test_slice_start(self, m):
        self.setup_data(m)
        it = iter(self.client.projects[:5])
        self.assertEqual(it.next(), Project(self.client, 1, 'Name1', 100, 'Status1', datetime.datetime.utcfromtimestamp(111), 'Callback1'))
        self.assertEqual(it.next(), Project(self.client, 2, 'Name2', 200, 'Status2', datetime.datetime.utcfromtimestamp(222), 'Callback2'))
        self.assertEqual(it.next(), Project(self.client, 3, 'Name3', 300, 'Status3', datetime.datetime.utcfromtimestamp(333), 'Callback3'))
        self.assertEqual(it.next(), Project(self.client, 4, 'Name4', 400, 'Status4', datetime.datetime.utcfromtimestamp(444), 'Callback4'))
        self.assertEqual(it.next(), Project(self.client, 5, 'Name5', 500, 'Status5', datetime.datetime.utcfromtimestamp(555), 'Callback5'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_middle(self, m):
        self.setup_data(m)
        it = iter(self.client.projects[2:9])
        self.assertEqual(it.next(), Project(self.client, 3, 'Name3', 300, 'Status3', datetime.datetime.utcfromtimestamp(333), 'Callback3'))
        self.assertEqual(it.next(), Project(self.client, 4, 'Name4', 400, 'Status4', datetime.datetime.utcfromtimestamp(444), 'Callback4'))
        self.assertEqual(it.next(), Project(self.client, 5, 'Name5', 500, 'Status5', datetime.datetime.utcfromtimestamp(555), 'Callback5'))
        self.assertEqual(it.next(), Project(self.client, 6, 'Name6', 600, 'Status6', datetime.datetime.utcfromtimestamp(666), 'Callback6'))
        self.assertEqual(it.next(), Project(self.client, 7, 'Name7', 700, 'Status7', datetime.datetime.utcfromtimestamp(777), 'Callback7'))
        self.assertEqual(it.next(), Project(self.client, 8, 'Name8', 800, 'Status8', datetime.datetime.utcfromtimestamp(888), 'Callback8'))
        self.assertEqual(it.next(), Project(self.client, 9, 'Name9', 900, 'Status9', datetime.datetime.utcfromtimestamp(999), 'Callback9'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_end(self, m):
        self.setup_data(m)
        it = iter(self.client.projects[7:])
        self.assertEqual(it.next(), Project(self.client, 8, 'Name8', 800, 'Status8', datetime.datetime.utcfromtimestamp(888), 'Callback8'))
        self.assertEqual(it.next(), Project(self.client, 9, 'Name9', 900, 'Status9', datetime.datetime.utcfromtimestamp(999), 'Callback9'))
        self.assertEqual(it.next(), Project(self.client, 10, 'Name10', 1000, 'Status10', datetime.datetime.utcfromtimestamp(101010), 'Callback10'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_step(self, m):
        self.setup_data(m)
        it = iter(self.client.projects[2:9:2])
        self.assertEqual(it.next(), Project(self.client, 3, 'Name3', 300, 'Status3', datetime.datetime.utcfromtimestamp(333), 'Callback3'))
        self.assertEqual(it.next(), Project(self.client, 5, 'Name5', 500, 'Status5', datetime.datetime.utcfromtimestamp(555), 'Callback5'))
        self.assertEqual(it.next(), Project(self.client, 7, 'Name7', 700, 'Status7', datetime.datetime.utcfromtimestamp(777), 'Callback7'))
        self.assertEqual(it.next(), Project(self.client, 9, 'Name9', 900, 'Status9', datetime.datetime.utcfromtimestamp(999), 'Callback9'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_get_page(self, m):
        self.setup_data(m)
        it = iter(self.client.projects.get_page(1))
        self.assertEqual(it.next(), Project(self.client, 5, 'Name5', 500, 'Status5', datetime.datetime.utcfromtimestamp(555), 'Callback5'))
        self.assertEqual(it.next(), Project(self.client, 6, 'Name6', 600, 'Status6', datetime.datetime.utcfromtimestamp(666), 'Callback6'))
        self.assertEqual(it.next(), Project(self.client, 7, 'Name7', 700, 'Status7', datetime.datetime.utcfromtimestamp(777), 'Callback7'))
        self.assertEqual(it.next(), Project(self.client, 8, 'Name8', 800, 'Status8', datetime.datetime.utcfromtimestamp(888), 'Callback8'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_get_page_non_existant(self, m):
        self.setup_data(m)
        it = iter(self.client.projects.get_page(10))
        self.assertRaises(StopIteration, it.next)


class ProjectChargeCollectionBasicTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)
        self.project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')

    def test_make_item(self):
        charge = self.project.charges.make_item(
            title='xxx',
            value=123,
            )
        self.assertEqual(charge, Charge(self.project.charges, 'xxx', 123))

    def test_equality(self):
        self.assertEqual(self.project.charges, self.project.charges)

    def test_clone(self):
        charges = self.project.charges
        clone = charges.clone()
        self.assertEqual(charges, clone)
        self.assertIsNot(charges, clone)


class ProjectChargeCollectionEmptyTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)
        self.project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')

    @staticmethod
    def setup_data(m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/charges?page=0&size=4', text=json.dumps({
            'content': [],
            'page': {
                'size': 0,
                'totalElements': 0,
                'totalPages': 0,
                'number': 0,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/charges?page=1&size=4', status_code=404)

    @requests_mock.mock()
    def test_page_count(self, m):
        self.setup_data(m)
        self.assertEqual(self.project.charges.page_count, 0)

    @requests_mock.mock()
    def test_len(self, m):
        self.setup_data(m)
        self.assertEqual(len(self.project.charges), 0)

    @requests_mock.mock()
    def test_iteration(self, m):
        self.setup_data(m)
        it = iter(self.project.charges)
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_iteration_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/charges?page=0&size=4', status_code=500)
        it = iter(self.project.charges)
        self.assertRaises(APIError, it.next)

    @requests_mock.mock()
    def test_indexing(self, m):
        self.setup_data(m)
        self.assertRaises(IndexError, lambda i: self.project.charges[i], -1)
        self.assertRaises(IndexError, lambda i: self.project.charges[i], 0)
        self.assertRaises(TypeError, lambda i: self.project.charges[i], 'xxx')

    @requests_mock.mock()
    def test_slice_start(self, m):
        self.setup_data(m)
        it = iter(self.project.charges[:5])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_middle(self, m):
        self.setup_data(m)
        it = iter(self.project.charges[2:9])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_end(self, m):
        self.setup_data(m)
        it = iter(self.project.charges[7:])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_step(self, m):
        self.setup_data(m)
        it = iter(self.project.charges[2:9:2])
        self.assertRaises(StopIteration, it.next)


class ProjectChargeCollectionDataTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)
        self.project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')

    @staticmethod
    def setup_data(m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/charges?page=0&size=4', text=json.dumps({
            'links': [
                {'rel': 'next', 'href': 'https://api-demo.lingo24.com/docs/v1/projects/1/charges?page=1&size=4'},
            ],
            'content': [
                {'title': 'Charge 1', 'value': 111},
                {'title': 'Charge 2', 'value': 222},
                {'title': 'Charge 3', 'value': 333},
                {'title': 'Charge 4', 'value': 444},
            ],
            'page': {
                'size': 4,
                'totalElements': 10,
                'totalPages': 3,
                'number': 0,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/charges?page=1&size=4', text=json.dumps({
            'links': [
                {'rel': 'next', 'href': 'https://api-demo.lingo24.com/docs/v1/projects/1/charges?page=2&size=4'},
            ],
            'content': [
                {'title': 'Charge 5', 'value': 555},
                {'title': 'Charge 6', 'value': 666},
                {'title': 'Charge 7', 'value': 777},
                {'title': 'Charge 8', 'value': 888},
            ],
            'page': {
                'size': 4,
                'totalElements': 10,
                'totalPages': 3,
                'number': 1,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/charges?page=2&size=4', text=json.dumps({
            'content': [
                {'title': 'Charge 9', 'value': 999},
                {'title': 'Charge 10', 'value': 101010},
            ],
            'page': {
                'size': 2,
                'totalElements': 10,
                'totalPages': 3,
                'number': 2,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/charges?page=10&size=4', status_code=404)

    @requests_mock.mock()
    def test_page_count(self, m):
        self.setup_data(m)
        self.assertEqual(self.project.charges.page_count, 3)

    @requests_mock.mock()
    def test_len(self, m):
        self.setup_data(m)
        self.assertEqual(len(self.project.charges), 10)

    @requests_mock.mock()
    def test_iteration(self, m):
        self.setup_data(m)
        it = iter(self.project.charges)
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 1', 111))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 2', 222))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 3', 333))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 4', 444))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 5', 555))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 6', 666))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 7', 777))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 8', 888))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 9', 999))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 10', 101010))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_indexing(self, m):
        self.setup_data(m)
        self.assertRaises(IndexError, lambda i: self.project.charges[i], -1)
        self.assertRaises(IndexError, lambda i: self.project.charges[i], 10)
        self.assertEqual(self.project.charges[5], Charge(self.project.charges, 'Charge 6', 666))

    @requests_mock.mock()
    def test_slice_start(self, m):
        self.setup_data(m)
        it = iter(self.project.charges[:5])
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 1', 111))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 2', 222))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 3', 333))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 4', 444))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 5', 555))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_middle(self, m):
        self.setup_data(m)
        it = iter(self.project.charges[2:9])
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 3', 333))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 4', 444))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 5', 555))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 6', 666))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 7', 777))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 8', 888))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 9', 999))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_end(self, m):
        self.setup_data(m)
        it = iter(self.project.charges[7:])
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 8', 888))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 9', 999))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 10', 101010))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_step(self, m):
        self.setup_data(m)
        it = iter(self.project.charges[2:9:2])
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 3', 333))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 5', 555))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 7', 777))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 9', 999))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_get_page(self, m):
        self.setup_data(m)
        it = iter(self.project.charges.get_page(1))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 5', 555))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 6', 666))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 7', 777))
        self.assertEqual(it.next(), Charge(self.project.charges, 'Charge 8', 888))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_get_page_non_existant(self, m):
        self.setup_data(m)
        it = iter(self.project.charges.get_page(10))
        self.assertRaises(StopIteration, it.next)


class ProjectFileCollectionBasicTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)
        self.project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')

    def test_make_item(self):
        file_obj = self.project.files.make_item(
            id=1,
            name='aaa',
            type='SOURCE',
            )
        self.assertEqual(file_obj, File(self.client, 1, 'aaa', 'SOURCE'))

    def test_equality(self):
        self.assertEqual(self.project.files, self.project.files)

    def test_clone(self):
        files = self.project.files
        clone = files.clone()
        self.assertEqual(files, clone)
        self.assertIsNot(files, clone)

    def test_item_url_path(self):
        self.assertEqual(self.project.files.item_url_path(123), 'projects/1/files/123')

    @requests_mock.mock()
    def test_get(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/files/12345', text=json.dumps({
            'id': 12345,
            'name': 'aaa',
            'type': 'SOURCE',
        }))
        file_obj = self.project.files.get(12345)
        self.assertEqual(file_obj, File(self.client, 12345, 'aaa', 'SOURCE'))

    @requests_mock.mock()
    def test_get_missing(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/files/123', status_code=404)
        self.assertRaises(DoesNotExist, self.project.files.get, 123)

    @requests_mock.mock()
    def test_get_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/files/123', status_code=500)
        self.assertRaises(APIError, self.project.files.get, 123)

    @requests_mock.mock()
    def test_add(self, m):
        def text_callback(request, context):
            self.assertDictEqual(request.json(), {
                'id': 12345,
            })
            return json.dumps({})
        m.post('https://api-demo.lingo24.com/docs/v1/projects/1/files', text=text_callback)
        file_obj = File(self.client, 12345, 'aaa', 'SOURCE')
        self.project.files.add(file_obj)

    @requests_mock.mock()
    def test_add_error(self, m):
        m.post('https://api-demo.lingo24.com/docs/v1/projects/1/files', status_code=500)
        file_obj = File(self.client, 12345, 'aaa', 'SOURCE')
        self.assertRaises(APIError, self.project.files.add, file_obj)

    @requests_mock.mock()
    def test_remove(self, m):
        m.delete('https://api-demo.lingo24.com/docs/v1/projects/1/files/12345')
        file_obj = File(self.client, 12345, 'aaa', 'SOURCE')
        self.project.files.remove(file_obj)

    @requests_mock.mock()
    def test_remove_error(self, m):
        m.delete('https://api-demo.lingo24.com/docs/v1/projects/1/files/12345', status_code=500)
        file_obj = File(self.client, 12345, 'aaa', 'SOURCE')
        self.assertRaises(APIError, self.project.files.remove, file_obj)


class ProjectFileCollectionEmptyTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)
        self.project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')

    @staticmethod
    def setup_data(m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/files?page=0&size=4', text=json.dumps({
            'content': [],
            'page': {
                'size': 0,
                'totalElements': 0,
                'totalPages': 0,
                'number': 0,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/files?page=1&size=4', status_code=404)

    @requests_mock.mock()
    def test_page_count(self, m):
        self.setup_data(m)
        self.assertEqual(self.project.files.page_count, 0)

    @requests_mock.mock()
    def test_len(self, m):
        self.setup_data(m)
        self.assertEqual(len(self.project.files), 0)

    @requests_mock.mock()
    def test_iteration(self, m):
        self.setup_data(m)
        it = iter(self.project.files)
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_iteration_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/files?page=0&size=4', status_code=500)
        it = iter(self.project.files)
        self.assertRaises(APIError, it.next)

    @requests_mock.mock()
    def test_indexing(self, m):
        self.setup_data(m)
        self.assertRaises(IndexError, lambda i: self.project.files[i], -1)
        self.assertRaises(IndexError, lambda i: self.project.files[i], 0)
        self.assertRaises(TypeError, lambda i: self.project.files[i], 'xxx')

    @requests_mock.mock()
    def test_slice_start(self, m):
        self.setup_data(m)
        it = iter(self.project.files[:5])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_middle(self, m):
        self.setup_data(m)
        it = iter(self.project.files[2:9])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_end(self, m):
        self.setup_data(m)
        it = iter(self.project.files[7:])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_step(self, m):
        self.setup_data(m)
        it = iter(self.project.files[2:9:2])
        self.assertRaises(StopIteration, it.next)


class ProjectFileCollectionDataTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)
        self.project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')

    @staticmethod
    def setup_data(m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/files?page=0&size=4', text=json.dumps({
            'links': [
                {'rel': 'next', 'href': 'https://api-demo.lingo24.com/docs/v1/projects/1/files?page=1&size=4'},
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
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/files?page=1&size=4', text=json.dumps({
            'links': [
                {'rel': 'next', 'href': 'https://api-demo.lingo24.com/docs/v1/projects/1/files?page=2&size=4'},
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
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/files?page=2&size=4', text=json.dumps({
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
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/files?page=10&size=4', status_code=404)

    @requests_mock.mock()
    def test_page_count(self, m):
        self.setup_data(m)
        self.assertEqual(self.project.files.page_count, 3)

    @requests_mock.mock()
    def test_len(self, m):
        self.setup_data(m)
        self.assertEqual(len(self.project.files), 10)

    @requests_mock.mock()
    def test_iteration(self, m):
        self.setup_data(m)
        it = iter(self.project.files)
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
        self.assertRaises(IndexError, lambda i: self.project.files[i], -1)
        self.assertRaises(IndexError, lambda i: self.project.files[i], 10)
        self.assertEqual(self.project.files[5], File(self.client, 6, 'Name6.txt', 'SOURCE'))

    @requests_mock.mock()
    def test_slice_start(self, m):
        self.setup_data(m)
        it = iter(self.project.files[:5])
        self.assertEqual(it.next(), File(self.client, 1, 'Name1.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 2, 'Name2.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 3, 'Name3.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 4, 'Name4.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 5, 'Name5.txt', 'SOURCE'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_middle(self, m):
        self.setup_data(m)
        it = iter(self.project.files[2:9])
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
        it = iter(self.project.files[7:])
        self.assertEqual(it.next(), File(self.client, 8, 'Name8.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 9, 'Name9.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 10, 'Name10.txt', 'SOURCE'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_step(self, m):
        self.setup_data(m)
        it = iter(self.project.files[2:9:2])
        self.assertEqual(it.next(), File(self.client, 3, 'Name3.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 5, 'Name5.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 7, 'Name7.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 9, 'Name9.txt', 'SOURCE'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_get_page(self, m):
        self.setup_data(m)
        it = iter(self.project.files.get_page(1))
        self.assertEqual(it.next(), File(self.client, 5, 'Name5.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 6, 'Name6.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 7, 'Name7.txt', 'SOURCE'))
        self.assertEqual(it.next(), File(self.client, 8, 'Name8.txt', 'SOURCE'))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_get_page_non_existant(self, m):
        self.setup_data(m)
        it = iter(self.project.files.get_page(10))
        self.assertRaises(StopIteration, it.next)


class ProjectJobCollectionBasicTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)
        self.project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')

    def test_make_item(self):
        file_obj = self.project.jobs.make_item(
            id=123,
            jobStatus='aaa',
            serviceId=2,
            sourceLocaleId=3,
            targetLocaleId=4,
            sourceFileId=5,
            targetFileId=6,
            )
        self.assertEqual(file_obj, Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6))

    def test_equality(self):
        self.assertEqual(self.project.jobs, self.project.jobs)

    def test_clone(self):
        jobs = self.project.jobs
        clone = jobs.clone()
        self.assertEqual(jobs, clone)
        self.assertIsNot(jobs, clone)

    def test_item_url_path(self):
        self.assertEqual(self.project.jobs.item_url_path(123), 'projects/1/jobs/123')

    @requests_mock.mock()
    def test_get(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123', text=json.dumps({
            'id': 123,
            'jobStatus': 'aaa',
            'serviceId': 2,
            'sourceLocaleId': 3,
            'targetLocaleId': 4,
            'sourceFileId': 5,
            'targetFileId': 6,
        }))
        job = self.project.jobs.get(123)
        self.assertEqual(job, Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, 6))

    @requests_mock.mock()
    def test_get_missing(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123', status_code=404)
        self.assertRaises(DoesNotExist, self.project.jobs.get, 123)

    @requests_mock.mock()
    def test_get_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs/123', status_code=500)
        self.assertRaises(APIError, self.project.jobs.get, 123)

    @requests_mock.mock()
    def test_create(self, m):
        def text_callback(request, context):
            self.assertDictEqual(request.json(), {
                'projectId': 1,
                'serviceId': 2,
                'sourceLocaleId': 3,
                'sourceFileId': 4,
                'targetLocaleId': 5,
            })
            return json.dumps({
                'id': 123,
                'jobStatus': 'aaa',
                'projectId': 1,
                'serviceId': 2,
                'sourceLocaleId': 3,
                'targetLocaleId': 4,
                'sourceFileId': 5,
                'targetFileId': None,
            })

        m.post('https://api-demo.lingo24.com/docs/v1/projects/1/jobs', text=text_callback)
        project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')
        job = project.jobs.create(service=2, source_locale=3, source_file=4, target_locale=5)
        self.assertEqual(job, Job(self.project.jobs, 123, 'aaa', 2, 3, 4, 5, None))

    @requests_mock.mock()
    def test_create_error(self, m):
        m.post('https://api-demo.lingo24.com/docs/v1/projects', status_code=400)
        self.assertRaises(APIError, self.client.projects.create, 'Name', 123)



class ProjectJobCollectionEmptyTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)
        self.project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')

    @staticmethod
    def setup_data(m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs?page=0&size=4', text=json.dumps({
            'content': [],
            'page': {
                'size': 0,
                'totalElements': 0,
                'totalPages': 0,
                'number': 0,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs?page=1&size=4', status_code=404)

    @requests_mock.mock()
    def test_page_count(self, m):
        self.setup_data(m)
        self.assertEqual(self.project.jobs.page_count, 0)

    @requests_mock.mock()
    def test_len(self, m):
        self.setup_data(m)
        self.assertEqual(len(self.project.jobs), 0)

    @requests_mock.mock()
    def test_iteration(self, m):
        self.setup_data(m)
        it = iter(self.project.jobs)
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_iteration_error(self, m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs?page=0&size=4', status_code=500)
        it = iter(self.project.jobs)
        self.assertRaises(APIError, it.next)

    @requests_mock.mock()
    def test_indexing(self, m):
        self.setup_data(m)
        self.assertRaises(IndexError, lambda i: self.project.jobs[i], -1)
        self.assertRaises(IndexError, lambda i: self.project.jobs[i], 0)
        self.assertRaises(TypeError, lambda i: self.project.jobs[i], 'xxx')

    @requests_mock.mock()
    def test_slice_start(self, m):
        self.setup_data(m)
        it = iter(self.project.jobs[:5])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_middle(self, m):
        self.setup_data(m)
        it = iter(self.project.jobs[2:9])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_end(self, m):
        self.setup_data(m)
        it = iter(self.project.jobs[7:])
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_step(self, m):
        self.setup_data(m)
        it = iter(self.project.jobs[2:9:2])
        self.assertRaises(StopIteration, it.next)


class ProjectJobCollectionDataTestCase(BaseTestCase):
    def setUp(self):
        authenticator = Authenticator('xxx', 'yyy', 'https://www.example.com/callback')
        authenticator.store.set({'access_token': 'aaa'})
        self.client = Client(authenticator, 'demo', per_page=4)
        self.project = Project(self.client, 1, 'aaa', 123, 'bbb', datetime.datetime.utcfromtimestamp(123), 'ccc')

    @staticmethod
    def setup_data(m):
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs?page=0&size=4', text=json.dumps({
            'links': [
                {'rel': 'next', 'href': 'https://api-demo.lingo24.com/docs/v1/projects/1/jobs?page=1&size=4'},
            ],
            'content': [
                {'id': 1, 'jobStatus': 'aaa', 'serviceId': 11, 'sourceLocaleId': 12, 'targetLocaleId': 13, 'sourceFileId': 14, 'targetFileId': 15},
                {'id': 2, 'jobStatus': 'bbb', 'serviceId': 21, 'sourceLocaleId': 22, 'targetLocaleId': 23, 'sourceFileId': 24, 'targetFileId': 25},
                {'id': 3, 'jobStatus': 'ccc', 'serviceId': 31, 'sourceLocaleId': 32, 'targetLocaleId': 33, 'sourceFileId': 34, 'targetFileId': 35},
                {'id': 4, 'jobStatus': 'ddd', 'serviceId': 41, 'sourceLocaleId': 42, 'targetLocaleId': 43, 'sourceFileId': 44, 'targetFileId': 45},
            ],
            'page': {
                'size': 4,
                'totalElements': 10,
                'totalPages': 3,
                'number': 0,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs?page=1&size=4', text=json.dumps({
            'links': [
                {'rel': 'next', 'href': 'https://api-demo.lingo24.com/docs/v1/projects/1/jobs?page=2&size=4'},
            ],
            'content': [
                {'id': 5, 'jobStatus': 'eee', 'serviceId': 51, 'sourceLocaleId': 52, 'targetLocaleId': 53, 'sourceFileId': 54, 'targetFileId': 55},
                {'id': 6, 'jobStatus': 'fff', 'serviceId': 61, 'sourceLocaleId': 62, 'targetLocaleId': 63, 'sourceFileId': 64, 'targetFileId': 65},
                {'id': 7, 'jobStatus': 'ggg', 'serviceId': 71, 'sourceLocaleId': 72, 'targetLocaleId': 73, 'sourceFileId': 74, 'targetFileId': 75},
                {'id': 8, 'jobStatus': 'hhh', 'serviceId': 81, 'sourceLocaleId': 82, 'targetLocaleId': 83, 'sourceFileId': 84, 'targetFileId': 85},
            ],
            'page': {
                'size': 4,
                'totalElements': 10,
                'totalPages': 3,
                'number': 1,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs?page=2&size=4', text=json.dumps({
            'content': [
                {'id': 9, 'jobStatus': 'iii', 'serviceId': 91, 'sourceLocaleId': 92, 'targetLocaleId': 93, 'sourceFileId': 94, 'targetFileId': 95},
                {'id': 10, 'jobStatus': 'jjj', 'serviceId': 101, 'sourceLocaleId': 102, 'targetLocaleId': 103, 'sourceFileId': 104, 'targetFileId': 105},
            ],
            'page': {
                'size': 2,
                'totalElements': 10,
                'totalPages': 3,
                'number': 2,
            }
        }))
        m.get('https://api-demo.lingo24.com/docs/v1/projects/1/jobs?page=10&size=4', status_code=404)

    @requests_mock.mock()
    def test_page_count(self, m):
        self.setup_data(m)
        self.assertEqual(self.project.jobs.page_count, 3)

    @requests_mock.mock()
    def test_len(self, m):
        self.setup_data(m)
        self.assertEqual(len(self.project.jobs), 10)

    @requests_mock.mock()
    def test_iteration(self, m):
        self.setup_data(m)
        it = iter(self.project.jobs)
        self.assertEqual(it.next(), Job(self.project.jobs, 1, 'aaa', 11, 12, 13, 14, 15))
        self.assertEqual(it.next(), Job(self.project.jobs, 2, 'bbb', 21, 22, 23, 24, 25))
        self.assertEqual(it.next(), Job(self.project.jobs, 3, 'ccc', 31, 32, 33, 34, 35))
        self.assertEqual(it.next(), Job(self.project.jobs, 4, 'ddd', 41, 42, 43, 44, 45))
        self.assertEqual(it.next(), Job(self.project.jobs, 5, 'eee', 51, 52, 53, 54, 55))
        self.assertEqual(it.next(), Job(self.project.jobs, 6, 'fff', 61, 62, 63, 64, 65))
        self.assertEqual(it.next(), Job(self.project.jobs, 7, 'ggg', 71, 72, 73, 74, 75))
        self.assertEqual(it.next(), Job(self.project.jobs, 8, 'hhh', 81, 82, 83, 84, 85))
        self.assertEqual(it.next(), Job(self.project.jobs, 9, 'iii', 91, 92, 93, 94, 95))
        self.assertEqual(it.next(), Job(self.project.jobs, 10, 'jjj', 101, 102, 103, 104, 105))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_indexing(self, m):
        self.setup_data(m)
        self.assertRaises(IndexError, lambda i: self.project.jobs[i], -1)
        self.assertRaises(IndexError, lambda i: self.project.jobs[i], 10)
        self.assertEqual(self.project.jobs[5], Job(self.project.jobs, 6, 'fff', 61, 62, 63, 64, 65))

    @requests_mock.mock()
    def test_slice_start(self, m):
        self.setup_data(m)
        it = iter(self.project.jobs[:5])
        self.assertEqual(it.next(), Job(self.project.jobs, 1, 'aaa', 11, 12, 13, 14, 15))
        self.assertEqual(it.next(), Job(self.project.jobs, 2, 'bbb', 21, 22, 23, 24, 25))
        self.assertEqual(it.next(), Job(self.project.jobs, 3, 'ccc', 31, 32, 33, 34, 35))
        self.assertEqual(it.next(), Job(self.project.jobs, 4, 'ddd', 41, 42, 43, 44, 45))
        self.assertEqual(it.next(), Job(self.project.jobs, 5, 'eee', 51, 52, 53, 54, 55))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_middle(self, m):
        self.setup_data(m)
        it = iter(self.project.jobs[2:9])
        self.assertEqual(it.next(), Job(self.project.jobs, 3, 'ccc', 31, 32, 33, 34, 35))
        self.assertEqual(it.next(), Job(self.project.jobs, 4, 'ddd', 41, 42, 43, 44, 45))
        self.assertEqual(it.next(), Job(self.project.jobs, 5, 'eee', 51, 52, 53, 54, 55))
        self.assertEqual(it.next(), Job(self.project.jobs, 6, 'fff', 61, 62, 63, 64, 65))
        self.assertEqual(it.next(), Job(self.project.jobs, 7, 'ggg', 71, 72, 73, 74, 75))
        self.assertEqual(it.next(), Job(self.project.jobs, 8, 'hhh', 81, 82, 83, 84, 85))
        self.assertEqual(it.next(), Job(self.project.jobs, 9, 'iii', 91, 92, 93, 94, 95))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_end(self, m):
        self.setup_data(m)
        it = iter(self.project.jobs[7:])
        self.assertEqual(it.next(), Job(self.project.jobs, 8, 'hhh', 81, 82, 83, 84, 85))
        self.assertEqual(it.next(), Job(self.project.jobs, 9, 'iii', 91, 92, 93, 94, 95))
        self.assertEqual(it.next(), Job(self.project.jobs, 10, 'jjj', 101, 102, 103, 104, 105))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_slice_step(self, m):
        self.setup_data(m)
        it = iter(self.project.jobs[2:9:2])
        self.assertEqual(it.next(), Job(self.project.jobs, 3, 'ccc', 31, 32, 33, 34, 35))
        self.assertEqual(it.next(), Job(self.project.jobs, 5, 'eee', 51, 52, 53, 54, 55))
        self.assertEqual(it.next(), Job(self.project.jobs, 7, 'ggg', 71, 72, 73, 74, 75))
        self.assertEqual(it.next(), Job(self.project.jobs, 9, 'iii', 91, 92, 93, 94, 95))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_get_page(self, m):
        self.setup_data(m)
        it = iter(self.project.jobs.get_page(1))
        self.assertEqual(it.next(), Job(self.project.jobs, 5, 'eee', 51, 52, 53, 54, 55))
        self.assertEqual(it.next(), Job(self.project.jobs, 6, 'fff', 61, 62, 63, 64, 65))
        self.assertEqual(it.next(), Job(self.project.jobs, 7, 'ggg', 71, 72, 73, 74, 75))
        self.assertEqual(it.next(), Job(self.project.jobs, 8, 'hhh', 81, 82, 83, 84, 85))
        self.assertRaises(StopIteration, it.next)

    @requests_mock.mock()
    def test_get_page_non_existant(self, m):
        self.setup_data(m)
        it = iter(self.project.jobs.get_page(10))
        self.assertRaises(StopIteration, it.next)

# coding: utf-8

from __future__ import absolute_import

from . import BaseTestCase
import mock
import couchbase
from couchbase.n1ql import N1QLQuery
import json

class TestLabelStoreFunctionsController(BaseTestCase):
    """ LabelStoreFunctionsController integration test stubs """

    @mock.patch('swagger_server.controllers.label_store_functions.get_db')
    def test_get_label(self, mock_get_db):
        """
        Test case for get

        retrieve label with label id.
        """
        # mocked bucket
        mock_get_db.return_value = mock.create_autospec(couchbase.bucket.Bucket)
        mock_bucket = mock_get_db.return_value
        # mocked bucket.get()
        mock_get = mock_bucket.get
        mock_get.return_value = mock.create_autospec(couchbase.bucket.Result)
        mock_get.return_value.value = {'id': '1', 'position':'1.2.3' ,'label': 'test label'}

        response = self.client.open('/label_store/get/{label_id}'.format(label_id='1'),
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    @mock.patch('swagger_server.controllers.label_store_functions.get_db')
    def test_get_exception(self, mock_get_db):
        """
        Test case for get

        retrieve label with label id.
        """
        # mocked bucket
        mock_get_db.return_value = mock.create_autospec(couchbase.bucket.Bucket)
        mock_bucket = mock_get_db.return_value
        # mocked bucket.get()
        mock_get = mock_bucket.get
        mock_get.side_effect = Exception()

        response = self.client.open('/label_store/get/{label_id}'.format(label_id='2'),
                                    method='GET')

        self.assert404(response, "Response body is : " + response.data.decode('utf-8'))
        mock_get_db.assert_called_once()
        mock_get.assert_called_once_with('2')

    @mock.patch('swagger_server.controllers.label_store_functions.get_db')
    def test_post(self, mock_get_db):
        """
        Test case for upload

        upload label to couchbase.
        """
        # mocked bucket
        mock_get_db.return_value = mock.create_autospec(couchbase.bucket.Bucket)
        mock_bucket = mock_get_db.return_value
        # mocked bucket.upsert()
        mock_upsert = mock_bucket.upsert
        mock_upsert.return_value = mock.create_autospec(couchbase.bucket.OperationResult)
        mock_upsert.return_value.success = True

        label = {'doc_id': '1234', 'label_id': '1', 'position': '1.2.3'}
        response = self.client.open('/label_store/post',
                                    method='POST',
                                    data=json.dumps(label),
                                    content_type='application/json')

        mock_get_db.assert_called_once()
        mock_upsert.assert_called_once_with('1', label)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    @mock.patch('swagger_server.controllers.label_store_functions.get_db')
    def test_post_failed(self, mock_get_db):
        """
        Test case for upload

        upload label to couchbase.
        """
        # mocked bucket
        mock_get_db.return_value = mock.create_autospec(couchbase.bucket.Bucket)
        mock_bucket = mock_get_db.return_value

         # mocked bucket.upsert()
        mock_upsert = mock_bucket.upsert
        mock_upsert.side_effect = KeyError()

        doc = {'label_id': '1', 'doc_id': '1'}
        response = self.client.open('/label_store/post',
                                    method='POST',
                                    data=json.dumps(doc),
                                    content_type='application/json')

        mock_get_db.assert_called_once()
        self.assert404(response, "Response body is : " + response.data.decode('utf-8'))


    @mock.patch('swagger_server.controllers.label_store_functions.get_db')
    def test_delete_success(self, mock_get_db):
        """
        Test case for delete

        delete label with label id.
        """
        # mocked bucket
        mock_get_db.return_value = mock.create_autospec(couchbase.bucket.Bucket)
        mock_bucket = mock_get_db.return_value

        # mocked bucket.delete()
        mock_delete = mock_bucket.delete
        mock_delete.return_value = mock.create_autospec(couchbase.bucket.OperationResult)
        mock_delete.return_value.success = True

        response = self.client.open('/label_store/delete/{label_id}'.format(label_id='label_id_example'),
                                    method='DELETE')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    @mock.patch('swagger_server.controllers.label_store_functions.get_db')
    def test_delete_failed(self, mock_get_db):
        """
        Test case for delete

        delete label with label id.
        """
        # mocked bucket
        mock_get_db.return_value = mock.create_autospec(couchbase.bucket.Bucket)
        mock_bucket = mock_get_db.return_value

        # mocked bucket.delete()
        mock_delete = mock_bucket.delete
        mock_delete.side_effect = Exception()

        response = self.client.open('/label_store/delete/{label_id}'.format(label_id='label_id_example'),
                                    method='DELETE')
        mock_get_db.assert_called_once()
        self.assert404(response, "Response body is : " + response.data.decode('utf-8'))

    @mock.patch('swagger_server.controllers.label_store_functions.get_db')
    def test_get_all_labels(self, mock_get_db):
        """
        Test case for get_all_labels

        retrieve all labels for a document with document id.
        """
        # mocked bucket
        mock_get_db.return_value = mock.create_autospec(couchbase.bucket.Bucket)
        mock_bucket = mock_get_db.return_value
        # mocked bucket.get()
        mock_query = mock_bucket.n1ql_query
        mock_query.return_value = mock.create_autospec(couchbase.n1ql.N1QLRequest)
        mock_query.return_value.value = [1,2,3]

        response = self.client.open('/label_store/get_all_labels/{doc_id}'.format(doc_id='1'),
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))
    

if __name__ == '__main__':
    import unittest
    unittest.main()

import unittest
import logging
from mock import MagicMock

import boto3

from dynamodbrunner import DynamoDbRunner
from falkuslib.awsutils import set_boto_logging_level


class TestIntegWithDbSupport(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)
        set_boto_logging_level(logging.WARNING)
        cls.ddbr = DynamoDbRunner(port=12001, max_port_to_try=12100)
        cls.ddbr.run()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'ddbr'):
            cls.ddbr.shutdown()

    @classmethod
    def aws_resource(cls, aws_service, region_name="eu-west-1"):
        return boto3.resource(aws_service, region_name=region_name, endpoint_url=cls.ddbr.get_endpoint())

    @classmethod
    def aws_client(cls, aws_service, region_name="eu-west-1"):
        return boto3.client(aws_service, region_name=region_name, endpoint_url=cls.ddbr.get_endpoint())

    @classmethod
    def dynamodb_table(cls, table_name):
        return cls.aws_resource("dynamodb").Table(table_name)


class TestIntegService(TestIntegWithDbSupport):

    @classmethod
    def setUpClass(cls):
        super(TestIntegService, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestIntegService, cls).tearDownClass()

    @classmethod
    def aws_format_name(cls, table_name):
        return table_name

    @classmethod
    def mock_lws_context(cls, request={}, path="/test",
                         userid="testuser@test.com",
                         usertype=""):
        lws_context_mock = MagicMock()
        lws_context_mock.get_request_path = MagicMock(return_value=path)
        lws_context_mock.get_request = MagicMock(return_value=request)
        lws_context_mock.get_user_id = MagicMock(return_value=userid)
        lws_context_mock.get_user_type = MagicMock(return_value=usertype)
        lws_context_mock.aws_resource.side_effect = cls.aws_resource
        lws_context_mock.aws_client.side_effect = cls.aws_client
        lws_context_mock.aws_format_name.side_effect = cls.aws_format_name
        lws_context_mock.dynamodb_table.side_effect = cls.dynamodb_table
        return lws_context_mock


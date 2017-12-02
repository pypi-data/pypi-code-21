#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `awssh` package."""

import pytest
import mock
import os
import boto3
import json
import sys
import botocore
import moto

from click.testing import CliRunner

from awssh import awssh


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


@pytest.fixture
def ec2_api_mock():
    def mock_api(self, serv, arg, **kwargs):
        if serv == 'DescribeInstances':
            return {'Reservations': [
                {'Instances': [
                    {
                        'State': {'Code': 16},
                        'Tags': [
                            {'Key': 'Name', 'Value': 'Name1'},
                            {'Key': 'Bunk', 'Value': 'Ugh'}
                        ],
                        'PublicIpAddress': '1.1.1.1',
                        'PrivateIpAddress': '2.2.2.2'
                    },
                    {
                        'State': {'Code': 16},
                        'Tags': [
                            {'Key': 'Name', 'Value': 'Name2'},
                            {'Key': 'Bunk', 'Value': 'Ugh'}
                        ],
                        'PublicIpAddress': '3.3.3.3',
                        'PrivateIpAddress': '4.4.4.4'
                    },
                ]},
                {'Instances': [
                    {
                        'State': {'Code': 3},
                        'Tags': [
                            {'Key': 'Name', 'Value': 'Name3'},
                            {'Key': 'Bunk', 'Value': 'Ugh'}
                        ],
                        'PublicIpAddress': '5.5.5.5',
                        'PrivateIpAddress': '6.6.6.6'
                    },
                    {
                        'State': {'Code': 16},
                        'Tags': [
                            {'Key': 'NameNope', 'Value': 'Name4'},
                            {'Key': 'Bunk', 'Value': 'Ugh'}
                        ],
                        'PublicIpAddress': '7.7.7.7',
                        'PrivateIpAddress': '8.8.8.8'
                    },
                ]},
                {'Instances': [
                    {
                        'State': {'Code': 16},
                        'Tags': [
                            {'Key': 'Name', 'Value': 'Name5'},
                            {'Key': 'Bunk', 'Value': 'Ugh'}
                        ],
                        'PublicIpAddress': '9.9.9.9',
                        'PrivateIpAddress': '10.10.10.10'
                    },
                    {
                        'State': {'Code': 16},
                        'Tags': [
                            {'Key': 'Name', 'Value': 'NoIp'},
                            {'Key': 'Bunk', 'Value': 'Ugh'}
                        ],
                        'PublicIpAddress': '',
                        'PrivateIpAddress': ''
                    },
                ]},
            ]}
        if serv == 'DescribeRegions':
            return {'Regions': [{'Endpoint': 'ec2.ap-south-1.amazonaws.com',
                                 'RegionName': 'ap-south-1'},
                                {'Endpoint': 'ec2.eu-west-2.amazonaws.com',
                                 'RegionName': 'eu-west-2'},
                                {'Endpoint': 'ec2.eu-west-1.amazonaws.com',
                                 'RegionName': 'eu-west-1'},
                                {'Endpoint': 'ec2.ap-northeast-2.amazonaws.com', # noqa
                                 'RegionName': 'ap-northeast-2'},
                                {'Endpoint': 'ec2.ap-northeast-1.amazonaws.com', # noqa
                                 'RegionName': 'ap-northeast-1'},
                                {'Endpoint': 'ec2.sa-east-1.amazonaws.com',
                                 'RegionName': 'sa-east-1'},
                                {'Endpoint': 'ec2.ca-central-1.amazonaws.com',
                                 'RegionName': 'ca-central-1'},
                                {'Endpoint': 'ec2.ap-southeast-1.amazonaws.com',  # noqa
                                 'RegionName': 'ap-southeast-1'},
                                {'Endpoint': 'ec2.ap-southeast-2.amazonaws.com',  # noqa
                                 'RegionName': 'ap-southeast-2'},
                                {'Endpoint': 'ec2.eu-central-1.amazonaws.com',
                                 'RegionName': 'eu-central-1'},
                                {'Endpoint': 'ec2.us-east-1.amazonaws.com',
                                 'RegionName': 'us-east-1'},
                                {'Endpoint': 'ec2.us-east-2.amazonaws.com',
                                 'RegionName': 'us-east-2'},
                                {'Endpoint': 'ec2.us-west-1.amazonaws.com',
                                 'RegionName': 'us-west-1'},
                                {'Endpoint': 'ec2.us-west-1.amazonaws.com',
                                 'RegionName': 'zz-iraq-1'},
                                {'Endpoint': 'ec2.us-west-2.amazonaws.com',
                                 'RegionName': 'us-west-2'}],
                    'ResponseMetadata': {'RetryAttempts': 0,
                                         'HTTPStatusCode': 200,
                                         'RequestId': '48139461-f0cf-4fc1-9da6-c55016b31d90',  # noqa
                                         'HTTPHeaders': {'transfer-encoding': 'chunked',  # noqa
                                                         'vary': 'Accept-Encoding',  # noqa
                                                         'server': 'AmazonEC2',
                                                         'content-type': 'text/xml;charset=UTF-8',  # noqa
                                                         'date': 'Thu, 19 Oct 2017 05:39:31 GMT'}}} # noqa

    return mock_api


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    # runner = CliRunner()
    # result = runner.invoke(awssh.cli.main)
    # assert result.exit_code == 0
    # # assert 'awssh.cli.main' in result.output
    # help_result = runner.invoke(awssh.cli.main, ['--help'])
    # assert help_result.exit_code == 0
    # assert '--help' in help_result.output


@moto.mock_ec2
def test_test():
    ec2 = boto3.client('ec2')

    ec2.run_instances(ImageId='ami-asdf', MinCount=10, MaxCount=10)

    print(ec2.describe_regions())


@mock.patch('awssh.awssh.boto3')
def _test_awssh_client(my_mock):

    awh = awssh.Awssh()

    awh.client("swf")
    my_mock.client.assert_called_with("swf")

    os.environ['AWS_DEFAULT_REGION'] = 'us-west-1'

    awh = awssh.Awssh()
    awh.client('rds')
    my_mock.client.assert_called_with("rds", region_name='us-west-1')

    awssh.Awssh._clients = {}
    awssh.Awssh._region = None
    del os.environ['AWS_DEFAULT_REGION']

    awssh.Awssh._clients = {}
    awssh.Awssh._region = None
    awh = awssh.Awssh(region='us-east-2')

    awh.client('sns')
    my_mock.client.assert_called_with('sns', region_name='us-east-2')

    my_mock.client.return_value = False
    with pytest.raises(Exception) as exe:
        awh.client('sqs')
    assert "Could not create" in str(exe.value)

    my_mock.client.side_effect = Exception("Test")
    with pytest.raises(Exception) as exe:
        awh.client("sts")
    assert "Unable to connect" in str(exe.value)

    awssh.Awssh._clients = {}
    awssh.Awssh._region = None


def _test_return_ec2_servers(ec2_api_mock):

    with mock.patch('botocore.client.BaseClient._make_api_call', new=ec2_api_mock): # noqa
        a = awssh.Awssh()

        res = a.return_ec2_servers()

        test_str = json.dumps(res)

        assert '5.5.5.5' not in test_str
        assert 'NoIp' not in test_str
        assert 'Name5' in test_str
        assert '9.9.9.9' in test_str


def _test_set_region(ec2_api_mock):
    return
    with mock.patch('botocore.client.BaseClient._make_api_call', new=ec2_api_mock): # noqa

        a = awssh.Awssh()

        a.set_region('zi1')
        assert awssh.Awssh.get_region() == 'zz-iraq-1'

        a.set_region('test-error')
        assert awssh.Awssh.get_region() == 'us-west-2'

        a.set_region('us-east-2')
        assert awssh.Awssh.get_region() == 'us-east-2'

import elasticsearch
import curator
import os
import json
import string, random, tempfile
import click
from click import testing as clicktest
from mock import patch, Mock

from . import CuratorTestCase
from . import testvars as testvars

import logging
logger = logging.getLogger(__name__)

host, port = os.environ.get('TEST_ES_SERVER', 'localhost:9200').split(':')
port = int(port) if port else 9200

class TestCLIIndexSettings(CuratorTestCase):
    def test_set_simple_setting(self):
        i = 'my_index'
        k = 'refresh_interval'
        v = '10s'
        ignore = False
        preserve = False

        self.create_index(i)
        self.write_config(
            self.args['configfile'], testvars.client_config.format(host, port))
        self.write_config(self.args['actionfile'],
            testvars.index_settings.format(k, v, ignore, preserve))
        test = clicktest.CliRunner()
        result = test.invoke(
                    curator.cli,
                    [
                        '--config', self.args['configfile'],
                        self.args['actionfile']
                    ],
                    )
        self.assertEqual(
            v,
            self.client.indices.get_settings(index=i)[i]['settings']['index'][k]
        )
    def test_no_change_with_preserve_existing(self):
        i = 'my_index'
        k = 'refresh_interval'
        e = '1s'
        v = '10s'
        ignore = False
        preserve = True

        body = {'index': {k:e}}
        self.create_index(i)
        self.client.indices.put_settings(index=i, body=body)
        # First set
        self.assertEqual(
            e,
            self.client.indices.get_settings(index=i)[i]['settings']['index'][k]
        )

        self.write_config(
            self.args['configfile'], testvars.client_config.format(host, port))
        self.write_config(self.args['actionfile'],
            testvars.index_settings.format(k, v, ignore, preserve))
        
        test = clicktest.CliRunner()
        result = test.invoke(
                    curator.cli,
                    [
                        '--config', self.args['configfile'],
                        self.args['actionfile']
                    ],
                    )
        self.assertEqual(
            e,
            self.client.indices.get_settings(index=i)[i]['settings']['index'][k]
        )
    def test_skip_open_index_when_ignore_is_true_with_static_setting(self):
        i = 'my_index'
        k = 'codec'
        v = 'best_compression'
        new_v = 'default'
        ignore = True
        preserve = False

        # Create index, close it, set codec to v, then open it.
        self.create_index(i)
        self.client.indices.close(index=i)
        self.client.indices.put_settings(index=i, body={'index':{k:v}})
        self.client.indices.open(index=i)

        self.write_config(
            self.args['configfile'], testvars.client_config.format(host, port))
        self.write_config(self.args['actionfile'],
            testvars.index_settings.format(k, new_v, ignore, preserve))
        test = clicktest.CliRunner()
        result = test.invoke(
                    curator.cli,
                    [
                        '--config', self.args['configfile'],
                        self.args['actionfile']
                    ],
                    )
        self.assertEqual(
            v,
            self.client.indices.get_settings(index=i)[i]['settings']['index'][k]
        )
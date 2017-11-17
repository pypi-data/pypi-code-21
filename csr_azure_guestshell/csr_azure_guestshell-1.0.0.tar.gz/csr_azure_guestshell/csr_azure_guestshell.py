#!/usr/bin/env python
from os.path import expanduser
import os
import sys
import cli
import configparser
from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings


class cag():
    def __init__(self):
        self.load_env()
        self.block_blob_service = BlockBlobService(
            account_name=os.environ['AZURE_STORAGE_NAME'], account_key=os.environ['AZURE_STORAGE_KEY'])

    def load_env(self):
        config = configparser.ConfigParser()
        config.optionxform = str
        home = expanduser("~")
        config.read(home + '/.azure/credentials')
        for key in config['default']:
            value = config.get('default', key)
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            os.environ[key] = str(value)

    def does_container_exist(self, containername):
        containers = self.block_blob_service.list_containers()

        for c in containers:
            if containername is c.name:
                return True

        return False

    def create_container_if_doesnt_exist(self, containername):
        if self.does_container_exist(containername) is False:
            self.block_blob_service.create_container(containername)

    def download_file(self, containername, filename, directory="/bootflash/"):
        try:
            self.block_blob_service.get_blob_to_path(
                containername, filename, directory + filename)
        except Exception as e:
            print "Config File Download Failed.  Error: %s" % (e)
            return False
        print "\nDownload Complete"
        return True

    def upload_file(self, containername, filename, directory="/bootflash/"):
        try:
            self.block_blob_service.create_blob_from_path(
                containername,
                filename,
                directory + filename,
                content_settings=ContentSettings(
                    content_encoding='UTF-8', content_language='en')
            )
        except Exception as e:
            print "Uploading %s Failed.  Error: %s" % (filename, e)
            sys.exit(1)

        print "Upload Complete to container %s" % (containername)

    def save_cmd_output(self, cmdlist, filename, container=None, directory="/bootflash/", print_output=False):

        with open(directory + filename, 'w') as f:
            for command in cmdlist:
                cmd_output = cli.execute(command)
                col_space = (80 - (len(command))) / 2
                if print_output is True:
                    print "\n%s %s %s" % ('=' * col_space, command, '=' * col_space)
                    print "%s \n%s" % (cmd_output, '=' * 80)

                f.write("\n%s %s %s\n" %
                        ('=' * col_space, command, '=' * col_space))
                f.write("%s \n%s\n" % (cmd_output, '=' * 80))
        if container is not None:
            self.upload_file(container, filename)

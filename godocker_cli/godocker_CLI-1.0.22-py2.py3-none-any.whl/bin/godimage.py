#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from os.path import expanduser
from terminaltables import SingleTable
import os.path
import sys

import click
import requests, json

import xml.etree.ElementTree as ET
import xml.dom.minidom as xmldom

from godockercli.auth import Auth
from godockercli.utils import Utils
from godockercli.httputils import HttpUtils

@click.group()
def run():
    pass

@click.option('--xml', '-x', is_flag=True, help="print in xml format")
@click.command()
def list(xml):
    """ list all docker images """

    Auth.authenticate()

    images = Utils.get_docker_images()

    additional_images = Utils.get_additionalImages()

    # if xml, write in a xml file
    if xml:
        images_list = ET.Element("docker_images")
        
        # default images
        default_images = ET.SubElement(images_list, "default_images")
        for image in images:
            single_image = ET.SubElement(default_images, "image")
            ET.SubElement(single_image, "name").text = str(image["name"])
            ET.SubElement(single_image, "url").text = str(image["url"])
            ET.SubElement(single_image, "interactive_mode").text = str(image["interactive"])

        # add additional images
        additional_images_xml = ET.SubElement(images_list, "additional_images")
        for image in additional_images:
            single_image = ET.SubElement(additional_images_xml, "image")
            ET.SubElement(single_image, "url").text = str(image)

        tree = ET.ElementTree(images_list)
        tree.write("/tmp/.images.xml")
        xml = xmldom.parse("/tmp/.images.xml").toprettyxml()

        # write in a final xml (pretty)
        xmlfile = open("images_result.xml", 'w')
        xmlfile.write(xml)
        xmlfile.close()

        print("Results are available in images_result.xml file")

    else:

        images_data = []
        images_data.append(['name', 'url', 'interactive mode'])
        for image in images:
            images_data.append([str(image["name"]), str(image["url"]), str(image["interactive"])])

        table_images = SingleTable(images_data, "default images")
        print("\n"+table_images.table+"\n")


        # add other table
        additional_images_data = []
        additional_images_data.append(["url"])
        for url in sorted(additional_images):
             additional_images_data.append([str(url)])

        table_additional_images = SingleTable(additional_images_data, "additional images")
        print("\n"+table_additional_images.table+"\n")


run.add_command(list)


if __name__ == "__main__":
    run()

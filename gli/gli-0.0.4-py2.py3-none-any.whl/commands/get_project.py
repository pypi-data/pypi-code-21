"""Gitlab CLI get_project Command"""


from json import dumps
from .base import Base

import gitlab

import os
import sys

import requests

import yaml
from datetime import date, time, datetime, timedelta

from pprint import pprint
import logging
import re
from subprocess import Popen, PIPE
import click

from .. import utils

from pprint import pprint

#une classe dois toujours commencer par une majuscule!!!
class Get_project(Base):

    def run(self):

	if self.options["--list"]:
            if self.utils.project_name:
                projects = self.utils.gl.projects.list(search=self.utils.project_name)
            else:
                projects = self.utils.gl.projects.list(membership=True, simple=True)

            for project in projects:
                print project.path_with_namespace+" id="+str(project.id)
        
        if self.utils.project_name:

            try:
                project = self.utils.get_project_name(self.utils.project_name)
                print (project.pretty_print())

            except gitlab.exceptions.GitlabGetError,e:
                if e.message == "404 Project Not Found":                
                    print "select valid Gitlab project --project-name"
                    quit()
                else:
                    print e.message

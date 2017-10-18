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


#une classe dois toujours commencer par une majuscule!!!
class Toggle_registry(Base):

    def run(self):

        try:
            project = self.utils.get_project_name(self.utils.project_name)
            print("Conatiner Registry Before = "+str(project.container_registry_enabled))
            if project.container_registry_enabled:
                project.container_registry_enabled = False
            else:
                project.container_registry_enabled= True
                project.save()
            print("Container Registry After = "+str(project.container_registry_enabled))

        except gitlab.exceptions.GitlabGetError,e:
            if e.message == "404 Project Not Found":                
                print("select valid Gitlab project --project-name")
                quit()
            elif e.message == "404 Variable Not Found":
                print ("the variable --key="+self.utils.key+" is not found")
                print ("add --list to see all variables"                )
            else:
                print(e.message)        



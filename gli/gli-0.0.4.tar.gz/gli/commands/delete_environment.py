"""Gitlab CLI delete_environment Command"""

from __future__ import print_function

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
class Delete_environment(Base):

    def run(self):

        #Get Project
        try:
            project = self.utils.get_project_name(self.utils.project_name)


	    environments = project.environments.list()
	
	    if self.options["--list"]:        
	        for env in environments:
	            print("list: name=" + env.name + " id=" + str(env.id) + " url=" + str(env.external_url))
	                
	    if self.utils.key:
	        for env in environments:
	            if env.name == self.utils.key:
	
	                environment = project.environments.get(env.id)
	                print("Confirm that you want to delete environment name="+ environment.name + " id=" + str(environment.id) + " url=" + str(environment.external_url) + "from project "+self.utils.project_name+" ? y/(n)")
                        print('$>', end='')	                    
	                res = raw_input()
	                if res.lower() == "y" or res.lower() == "yes":
	                    environment.delete()
	                    print("deleted")
	            

            
        except gitlab.exceptions.GitlabGetError,e:
            if e.message == "404 Project Not Found":                
                print("select valid Gitlab project --project-name")
                quit()
            else:
                print(e.message)

            


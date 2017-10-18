import gitlab
import sys
import os
from os.path import expanduser
import json
from pprint import pprint
import requests

from json import dumps

class Utils(object):
    
    R="\033[31m"
    G="\033[32m"
    B="\033[36m"
    N="\033[m"


    config_file=expanduser("~")+"/.gitlab-helper"
    config = {}

    #gitlab object
    gl = {}

    #current working project
    project = {}

    debug_flag=False
    
    session_file="./.session"
    session = {}

    gitlab=""
    
    project_name=""
    
    def __init__(self, options):
        self.options = options

        if self.options["-d"] == True:
            print('You supplied the following options:', dumps(self.options, indent=2, sort_keys=True))
            debug_flag=True
            
        #recuperation des parametres
        if options["--project-name"]:
            self.project_name = options["--project-name"]        
            self.debug("blue", "working with project-name " + self.project_name)

        self.key = ""
        if options["--key"]:
            self.key = options["--key"]

        self.value = ""
        if options["--value"]:
            self.value = options["--value"] 

        self.gitlab = "gitlab"
        if options["--gitlab"]:
            self.gitlab = options["--gitlab"]

        #Initialisation de la connection avec GitLab
        self.__init_gitlab()

            
            
    def __init_gitlab(self):
        global gl
        self.debug("blue", "using python-gitlab configuration = " + self.gitlab)
        self.gl = gitlab.Gitlab.from_config(self.gitlab)
        self.gl.auth()


########################################################################################        
## Print Messages

    def blue(self,msg):
        print self.B+msg+self.N
    def red(self,msg):
        print self.R+msg+self.N
    def green(self,msg):
        print self.G+msg+self.N

    print_color = {
        "blue"  : blue,
        "red"   : red, 
        "green" : green
    }
    def debug(self,c, msg):
        if self.debug_flag :
            self.print_color[c](self, msg)

########################################################################################        


#########################################################
## Gitlab
#########################################################


    def get_project_name(self, project_name):
        project = self.gl.projects.get(project_name)
        self.debug("blue", project.name+"="+str(project.id))
        return project

    def get_project_id(self, project_id):
        project = self.gl.projects.get(project_name)
        self.debug("blue", project.name+"="+str(project.id))        
        pprint(project)
        return project


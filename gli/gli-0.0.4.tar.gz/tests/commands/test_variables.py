"""Tests for our `pwdc info` subcommand."""


from subprocess import PIPE, Popen as popen
from unittest import TestCase

gitlab_test_repo="sallamand/test"


class TestGetProject(TestCase):
    def test_list_variable(self):
        output = popen(['gli', '--project='+gitlab_test_repo, 'get_variable', '--list'], stdout=PIPE).communicate()[0]
        lines = output.split('\n')
        self.assertTrue(len(lines) != 1)

    def test_list_variable_mavariable(self):
        output = popen(['gli', '--project='+gitlab_test_repo, 'get_variable', '--list'], stdout=PIPE).communicate()[0]
        self.assertTrue('mavariable' in output)

        
    def test_get_variable_mavariable(self):
        output = popen(['gli', '--project='+gitlab_test_repo, 'get_variable', '--key', 'mavariable'], stdout=PIPE).communicate()[0]        
        self.assertTrue('mavalue' in output)


    def test_create_variable_mavariable2(self):
        output = popen(['gli', '--project='+gitlab_test_repo, 'set_variable', '--key', 'mavariable2', '--value', 'mavalue2'], stdout=PIPE).communicate()[0]
        self.assertTrue('gitlab project('+gitlab_test_repo+') variable mavariable2=mavalue2 has been successfully updated' in output)        

        
    def test_get_variable_mavariable2(self):
        output = popen(['gli', '--project='+gitlab_test_repo, 'get_variable', '--key', 'mavariable2'], stdout=PIPE).communicate()[0]        
        self.assertTrue('mavalue2' in output)


    def test_delete_variable_mavariable2(self):
        output = popen(['gli', '--project='+gitlab_test_repo, 'delete_variable', '--key', 'mavariable2'], stdout=PIPE).communicate()[0]        
        self.assertTrue('Confirm that you want to delete variable mavariable2 from project '+gitlab_test_repo+' ? y/(n)' in output)
        #add interractive yes

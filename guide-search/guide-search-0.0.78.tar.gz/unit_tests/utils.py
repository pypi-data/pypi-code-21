# vim: foldmethod=marker:foldmarker=\ {{{,\ }}}:cms=#%s
import requests
import os
from random import Random
from termcolor import cprint

def log(s):
    cprint('%s' % s, 'cyan')
    return True


class AttrDict(dict):
    """ dictionary that exposes its keys as attributes """
    def __init__(self, *args, **kwargs):  # {{{
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self # }}}

class Helper(object):
# {{{
    RANDCHARS = [chr(i) for i in range(97,123)]
    RANDCHARS.extend( [chr(i) for i in range(48,58)] )

    def randomName(self, prefix='test_', n=6):
        r = Random()
        prefix = 'test_'
        for i in range(6):
            prefix = prefix + self.RANDCHARS[r.randint(0, len(self.RANDCHARS)-1)]
        return prefix

    def __init__(self, guide_api_host):
        # get the gitlab server details from guide-api
        self.api_host = guide_api_host
        self.info = requests.get(self.api_host+'/info').json() #  'http://hh-kng-d11.lnx.lr.net'
        self.gitlab_host = self.info['gitlab']['content']['host']
        self.project_id = self.info['gitlab']['content']['project'] # 13
        self.headers = {'PRIVATE-TOKEN': '45PpX1Y-n2Ygi6EyyuZ7'} # TODO: move into config or add a create branch endpoint to guide-api

    def get_commits(self, branch_name='master'):

        """ https://docs.gitlab.com/ee/api/branches.html#create-repository-branch  """

        url = '%s/api/v3/projects/%s/repository/commits' % (self.gitlab_host, self.project_id)
        params = {'ref_name': branch_name }
        kwargs = { 'headers':self.headers, 'params': params }
        return requests.get(url, **kwargs)


    def create_branch(self, branch_name, sha1='empty'):

        """ https://docs.gitlab.com/ee/api/branches.html#create-repository-branch """

        url = '%s/api/v3/projects/%s/repository/branches' % (self.gitlab_host, self.project_id)
        params = {'branch_name': branch_name, 'ref': sha1}
        kwargs = { 'headers':self.headers, 'params': params }
        return requests.post(url, **kwargs)


    def delete_branch(self, branch_name):

        """ https://docs.gitlab.com/ee/api/branches.html#delete-repository-branch """

        url = '%s/api/v3/projects/%s/repository/branches/%s' % (self.gitlab_host, self.project_id, branch_name)
        kwargs = { 'headers':self.headers, 'params': {} }
        return requests.delete(url, **kwargs)
    
    def list_branches(self):

        """ https://docs.gitlab.com/ee/api/branches.html#list-repository-branches """

        url = '%s/api/v3/projects/%s/repository/branches' % (self.gitlab_host, self.project_id)
        kwargs = { 'headers':self.headers, 'params': {} }
        return requests.get(url, **kwargs)


    def delete_test_branches(self):

        """ Delete all branches prefixed with 'test_' """

        for test_branch in self.get_test_branch_names():
            log('Deleting branch %s..' % test_branch)
            r = self.delete_branch(test_branch)
            if not r or r.status_code != 200:
                log('Failed to delete branch %s..' % test_branch)

    def get_test_branch_names(self):
        r = self.list_branches()
        names = [b['name'] for b in r.json()]
        return [n for n in names if n.startswith('test_')]


    def initialise_index(self, index_name):

        """ Delete all branches prefixed with 'test_' """

        Host = os.environ['GUIDE_API_HOST']
        log('HOST=%s' % host)

        # curl -X PUT http://localhost:5002/api/initialise/controls
        # upload files from git repo: dev-guidance / configuration to ES5
        url = host+'/api/initialise/controls'
        log('\nInitialising controls %s ...' % url)
        r = requests.put(url)
        for k,v in r.json().items():
            log("\t%s = %s" % (k,v))
            assert v == 'success'

        # curl -X PUT http://localhost:5002/api/initialise/index/test_a3J2/test_a3J2
        # put more stuff in ES
        url = host+'/api/initialise/index/'+index_name+'/'+index_name
        log('\nInitialising index %s ...' % url)
        r = requests.put(url)
        assert(r.json()['acknowledged'])

        # get last commit on master branch
        commits = self.get_commits(branch_name='master').json()
        sha1 = commits[0]['id']

        # create a branch of the last commit
        r = self.create_branch(index_name, sha1)

        assert r.status_code == 201
        commit=r.json()
        assert commit

        
        # curl -X PUT http://localhost:5002/api/publish/test_a3J2/_publish
        # publish the content in the above branch to ES
        url = host+'/api/publish/'+index_name+'/_publish'
        log('\nPublishing content %s ...' % url)
        r = requests.put(url)
        assert r.json()['status']=='started'

# }}}


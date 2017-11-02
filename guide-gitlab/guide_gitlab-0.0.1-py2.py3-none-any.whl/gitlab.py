# -*- coding: utf-8 -*-
import requests
import json
import time
from posixpath import join as posixjoin
from urllib.parse import quote

from .exceptions import (
    AuthError,
    ConflictError,
    ImpersonateError,
    ServerError,
    ValidationError,
    ResourceNotFoundError,
    RequestEntityTooLargeError,
    GitUnknownError,
    ForbiddenError,
    BadRequestError,
    GitLabAbortError,
    InvalidDataError,
)


class Gitlab3(object):
    """Gitlab class"""

    def api_version(self):
        return 3

    def __init__(self, host, project, token="", oauth_token="", verify_ssl=True):
        self.point_me_to(host, project, token, oauth_token, verify_ssl)

    # refactored here so we can rewire a new project ID into the urls in the unit tests
    def point_me_to(self, host, project, token="", oauth_token="", verify_ssl=True):
        """on init we setup the token used for all the api calls and all the urls

        :param host: host of gitlab
        :param token: token
        """
        if token != "":
            self.token = token
            self.headers = {"PRIVATE-TOKEN": self.token}
        if oauth_token != "":
            self.oauth_token = oauth_token
            self.headers = {"Authorization": 'Bearer {}'.format(
                self.oauth_token)}
        if not host:
            raise ValueError("host argument may not be empty")
        self.host = host.rstrip('/')
        if self.host.startswith('http://') or self.host.startswith('https://'):
            pass
        else:
            self.host = 'https://' + self.host

        self.project = project
        # self.api_url = urljoin(self.host, "/api/v3")
        # self.projects_url = posixjoin(self.api_url, "projects")
        # self.project_url = posixjoin(self.api_url, "projects", str(project))
        self.api_url = '%s/api/v%d' % (self.host, self.api_version())  # e.g. http://gitlab.com/api/v3
        self.projects_url = self.api_url + '/projects'  # e.g. http://gitlab.com/api/v3/projects
        self.project_url = self.projects_url + '/' + str(project)  # e.g. http://gitlab.com/api/v3/projects/12345
        self.users_url = self.api_url + "/users"
        self.keys_url = self.api_url + "/user/keys"
        self.groups_url = self.api_url + "/groups"
        self.search_url = self.api_url + "/projects/search"
        self.hook_url = self.api_url + "/hooks"
        self.verify_ssl = verify_ssl

        self.req = 1
        self.limit = 50
        self.period = 2
        self.start = time.clock()

    # TODO need to look at ssl verification in request call
    def request(self, method, url, params=None, data=None, raw_response=False):
        kwargs = dict({}, **{
            'headers': self.headers,
            'params': params or {}
            # ,'data': data or {}
        })
        # st = time.clock()

        self.req = self.req + 1
        if (self.req > self.limit):

            t = self.start
            self.start = time.clock()
            d = self.start - t
            self.req = 1
            if (d < self.period):
                wp = self.period - d + 1
                time.sleep(wp)

        if method in ('post', 'put'):
            kwargs['data'] = json.dumps(data)
            kwargs['headers']['Content-Type'] = 'application/json'

        response = getattr(requests, method)(url, **kwargs)

        # TODO check to see if all exceptions are being handled
        # tt = time.clock() - st

        if response.status_code in (200, 201):
            # if not response.content.strip():  # succeded but no response content
            #     return True
            try:
                return response.json()
            except (ValueError, TypeError):
                response.encoding = "UTF-8"  # seems to think its ISO-8859-1 - presumably from gitlab headers
                return response.text

        elif response.status_code == 400:
            raise BadRequestError(response.text)
        elif response.status_code == 401:
            raise AuthError
        elif response.status_code == 403:
            raise ForbiddenError
        elif response.status_code == 404:
            if data:
                msg = json.dumps(data)
            else:
                msg = json.dumps(kwargs['params'])
            raise ResourceNotFoundError(url + '-' + msg)
        elif response.status_code == 409:
            raise ConflictError
        elif response.status_code == 412 and self.impersonate is not None:
            raise ImpersonateError
        elif response.status_code == 413:
            raise RequestEntityTooLargeError
        elif response.status_code == 422:
            errors = response.json()['errors']
            raise ValidationError(str(', '.join(e if isinstance(e, str) else ': '.join(e) for e in errors)))
        elif response.status_code == 500:
            raise ServerError
        elif response.status_code == 502:
            raise GitLabAbortError
        raise GitUnknownError

# helper
    def make_url(self, index, *args):
        url = posixjoin(self.project_url, index, *args)
        return url

#
    def get_health(self):
        health = {"host": self.host, "project": self.project}
        try:
            url = posixjoin(self.api_url, "version")
            health["version"] = self.request("get", url)["version"]
            health["health"] = "alive"
        except:
            health["health"] = "dead"
        return health

    def get_tree(self, branch, path):
        """Get a list of repository files and directories in a project.

        :return: dcit with the tree
        """
        data = {"path": path, "ref_name": branch}
        url = self.make_url("repository", "tree")
        request = self.request("get", url, params=data)
        return request

    def create_merge_request(self, sourcebranch, target_branch, title,
                             target_project_id=None, assignee_id=None):
        """Create a new merge request.

        :param sourcebranch: name of the branch to merge from
        :param target_branch: name of the branch to merge to
        :param title: Title of the merge request
        :param assignee_id: Assignee user ID
        :return: dict of the new merge request
        """
        data = {"source_branch": sourcebranch,
                "target_branch": target_branch,
                "title": title}
        if assignee_id:
            data["assignee_id"] = assignee_id
        if target_project_id:
            data["target_project_id"] = target_project_id

        url = self.make_url("merge_requests")
        request = self.request("post", url, data=data)
        return request

    def accept_merge_request(self, mergerequest_id):
        """Update an existing merge request.

        :param mergerequest_id: ID of the merge request to accept
        :param merge_commit_message: Custom merge commit message
        :return: dict of the modified merge requests
        """
        url = self.make_url("merge_requests", str(mergerequest_id), "merge")
        request = self.request("put", url)
        return request

# branch
    def get_repository_branch(self, branch):
        """Get a single project repository branch.

        :param project_id: project id
        :param branch: branch
        :return: dict of the branch
        """
        url = self.make_url("repository", "branches", branch)
        request = self.request("get", url)
        return request

    # def create_branch(self, project_id, branch, ref):
    def create_branch(self, branch, ref):
        """Create branch from commit SHA or existing branch

        :param project_id:  The ID of a project
        :param branch: The name of the branch
        :param ref: Create branch from commit SHA or existing branch
        :return: True if success, False if not
        """
        data = {"branch_name": branch, "ref": ref}

        url = self.make_url("repository", "branches")  # e.g. http://gitlab.com/api/v3/projects/12345/repository/branches
        request = self.request("post", url, data=data)
        return request

    def compare_branches_tags_commits(self, from_id, to_id):
        """Compare branches, tags or commits

        :param project_id: The ID of a project
        :param from_id: the commit sha or branch name
        :param to_id: the commit sha or branch name
        :return: commit list and diff between two branches tags or commits provided by name
        """
        data = {"from": str(from_id), "to": str(to_id)}
        url = self.make_url("repository", "compare")

        request = self.request("get", url,
                               params=data)
        return request

    def get_raw_file(self, sha1, filepath):
        """Get the raw file contents for a file by commit SHA and path.

        :param project_id: The ID of a project
        :param sha1: The commit or branch name
        :param filepath: The path the file
        :return: raw file contents
        """
        data = {"filepath": filepath}
        url = self.make_url("repository", "blobs", sha1)
        request = self.request("get", url,
                               params=data)
        return request

    def get_branch(self, branch=None):
        """List one or all branches from a project

        :param project_id: project id
        :param branch: branch id
        :return: the branch
        """
        if branch:
            url = self.make_url("repository", "branches", branch)
        else:
            url = self.make_url("repository", "branches")
        request = self.request("get", url)
        return request

    def create_file(self, file_path, branch_name, content, commit_message):
        """Creates a new file in the repository

        :param project_id: project id
        :param file_path: Full path to new file. Ex. lib/class.rb
        :param branch_name: The name of branch
        :param content: File content
        :param commit_message: Commit message
        :return: true if success, false if not
        """
        data = {"file_path": file_path, "branch_name": branch_name,
                "content": content, "commit_message": commit_message}
        url = self.make_url("repository", "files")
        try:
            return self.request("post", url, data=data)
        except:
            time.sleep(5)
            return self.request("post", url, data=data)

    def update_file(self, file_path, branch_name, content, commit_message):
        """Updates an existing file in the repository

        :param project_id: project id
        :param file_path: Full path to new file. Ex. lib/class.rb
        :param branch_name: The name of branch
        :param content: File content
        :param commit_message: Commit message
        :return: true if success, false if not
        """
        data = {"file_path": file_path, "branch_name": branch_name,
                "content": content, "commit_message": commit_message}
        url = self.make_url("repository", "files")
        try:
            return self.request("put", url, data=data)
        except:
            time.sleep(5)
            return self.request("put", url, data=data)

    def create_repository_tag(self, tag_name, ref, message=None):
        """Creates new tag in the repository that points to the supplied ref
        :param project_id: project id
        :param tag_name: tag
        :param ref: sha1 of the commit or branch to tag
        :param message: message
        :return: dict
        """
        data = {"tag_name": tag_name, "ref": ref, "message": message}
        url = self.make_url("repository", "tags")
        res = self.request("post", url, data=data)
        return res

    def get_merge_requests(self, page=1, per_page=20, state=None):
        """Get all the merge requests for a project.

        :param project_id: ID of the project to retrieve merge requests for
        :param state: Passes merge request state to filter them by it
        :return: list with all the merge requests
        """
        data = {"page": page, "per_page": per_page, "state": state}
        url = self.make_url("merge_requests")
        return self.request("get", url, data=data)

    def get_merge_request(self, mergerequest_id):
        """Get information about a specific merge request.

        :param project_id: ID of the project
        :param mergerequest_id: ID of the merge request
        :return: dict of the merge request
        """
        url = self.make_url("merge_requests", str(mergerequest_id))
        return self.request("get", url)

    def get_repository_commits(self, project_id, ref_name=None, page=0, per_page=20):
        """Get a list of repository commits in a project.

        :param project_id: The ID of a project
        :param ref_name: The name of a repository branch or tag or if not given the default branch
        :return: list of commits
        """
        data = {"page": page, "per_page": per_page}
        url = self.make_url("repository", "commits")
        if ref_name is not None:
            data.update({"ref_name": ref_name})
            return self.request("get", url, params=data)
        else:
            return self.request("get", url)

    def get_projects_owned(self, page=1, per_page=20):
        """Returns a dictionary of all the projects for the current user

        :return: list with the repo name, description, last activity, web url, ssh url, owner and if its public
        """
        data = {"page": page, "per_page": per_page}

        request = requests.get("{0}/owned".format(self.projects_url), params=data,
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return request.json()
        else:
            return False
    
    def create_project(self, name, **kwargs):
        """Creates a new project owned by the authenticated user.

        :param name: new project name
        :param path: custom repository name for new project. By default generated based on name
        :param namespace_id: namespace for the new project (defaults to user)
        :param description: short project description
        :param issues_enabled:
        :param merge_requests_enabled:
        :param wiki_enabled:
        :param snippets_enabled:
        :param public: if true same as setting visibility_level = 20
        :param visibility_level:
        :param sudo:
        :param import_url:
        :return:
        """
        data = {"name": name}

        if kwargs:
            data.update(kwargs)

        request = requests.post(self.projects_url, headers=self.headers,
                                data=data, verify=self.verify_ssl)
        if request.status_code == 201:
            return request.json()
        elif request.status_code == 403:
            if "Your own projects limit is 0" in request.text:
                print(request.text)
                return False
        else:
            return False

    def get_projects(self, page=1, per_page=20):
        """Returns a dictionary of all the projects

        :return: list with the repo name, description, last activity,web url, ssh url, owner and if its public
        """
        data = {"page": page, "per_page": per_page}

        request = requests.get(self.projects_url, params=data,
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return request.json()
        else:
            return False

    def delete_project(self, project_id):
        """Delete a project

        :param project_id: project id
        :return: always true
        """
        request = requests.delete("{0}/{1}".format(self.projects_url, project_id),
                                  headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return True

    def get_repository_tags(self, project_id, page=1, per_page=20):
        """Get a list of repository tags from a project, sorted by name in reverse alphabetical order.

        :param project_id: project id
        :return: list with all the tags
        """
        data = {"page": page, "per_page": per_page}
        request = requests.get("{0}/{1}/repository/tags".format(self.projects_url, project_id), params=data,
                               verify=self.verify_ssl, headers=self.headers)
        if request.status_code == 200:
            return request.json()
        else:
            return False        

    def get_branches(self, project_id):
        """List all the branches from a project

        :param project_id: project id
        :return: the branches
        """
        request = requests.get("{0}/{1}/repository/branches".format(self.projects_url, project_id),
                               headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return request.json()
        else:
            return False
        
    def get_repository_tree(self, project_id, **kwargs):
        """Get a list of repository files and directories in a project.

        :param project_id: The ID of a project
        :param path: The path inside repository. Used to get contend of subdirectories
        :param ref_name: The name of a repository branch or tag or if not given the default branch
        :return: dcit with the tree
        """
        data = {}
        if kwargs:
            data.update(kwargs)

        request = requests.get("{0}/{1}/repository/tree".format(self.projects_url, project_id), params=data,
                               verify=self.verify_ssl, headers=self.headers)
        if request.status_code == 200:
            return request.json()
        else:
            return False

    def delete_branch(self, project_id, branch):
        """Delete branch by name

        :param project_id:  The ID of a project
        :param branch: The name of the branch
        :return: True if success, False if not
        """

        request = requests.delete("{0}/{1}/repository/branches/{2}".format(self.projects_url, project_id, branch),
                                  headers=self.headers, verify=self.verify_ssl)

        if request.status_code == 200:
            return True
        else:
            return False


############### guide specific stuff

    # channel refers to a commit/branch/tag
    # doctype: 'articles' 'items' 'snippets'
    # name: filename
    # subtype : extension
    def get_object(self, channel, doctype, name, subtype):
        fn = "{0}/{1}.{2}".format(doctype, name, subtype)

        obj = self.get_raw_file(channel, fn)

        if subtype in ['ga', 'gs']:
            if not isinstance(obj, dict):
                m = "File {0} is not valid json".format(fn)
                raise InvalidDataError(m)
            if not name == obj["id"]:
                # TODO need to raise more specific exception
                m = "File {0} does not contain the data for {1}".format(fn, name)
                raise InvalidDataError(m)
        # else:
        #     if obj == True:
        #         obj = ''
        return obj


class Gitlab4(Gitlab3):
    """
        Provides limited support for version 4 of the API.

        https://docs.gitlab.com/ce/api/v3_to_v4.html

    """
    def api_version(self):
        return 4

    def __init__(self, host, project, token="", oauth_token="", verify_ssl=True):
        super(Gitlab4, self).__init__(host, project, token, oauth_token, verify_ssl)

    def get_projects_owned(self, page=1, per_page=20):
        data = {"page": page, "per_page": per_page, "owned": True}
        response = requests.get("{0}".format(self.projects_url), params=data,
                                headers=self.headers, verify=self.verify_ssl)
        if response.status_code == 200:
            return response.json()
        else:
            return False

    def create_branch(self, branch, ref):
        data = {"branch": branch, "ref": ref}
        url = self.make_url("repository", "branches")
        response = self.request("post", url, data=data)
        return response

    def delete_project(self, project_id):
        response = requests.delete("{0}/{1}".format(self.projects_url, project_id),
                                   headers=self.headers, verify=self.verify_ssl)
        return response.status_code in (200, 202)

    def create_file(self, file_path, branch_name, content, commit_message):
        data = {"branch": branch_name, "content": content, "commit_message": commit_message}
        file_path = quote(file_path, safe='')
        url = self.make_url("repository", "files", file_path)
        try:
            return self.request("post", url, data=data)
        except:
            time.sleep(5)
            return self.request("post", url, data=data)

    def get_raw_file(self, sha1, filepath):
        data = {"ref": sha1}
        filepath = quote(filepath, safe='')  # filepath.replace('/', '%2F').replace('.', '%2E')
        url = self.make_url("repository", "files", filepath, "raw")
        request = self.request("get", url, params=data)
        return request

    def update_file(self, file_path, branch_name, content, commit_message):
        data = {"branch": branch_name, "content": content, "commit_message": commit_message}
        file_path = quote(file_path, safe='')
        url = self.make_url("repository", "files", file_path)
        try:
            return self.request("put", url, data=data)
        except:
            time.sleep(5)
            return self.request("put", url, data=data)

    def get_merge_request(self, mergerequest_id):
        url = self.make_url("merge_requests/?iid=%d" % mergerequest_id)
        return self.request("get", url)[0]

    def accept_merge_request(self, iid):
        url = self.make_url("merge_requests", str(iid), "merge")
        return self.request("put", url)

    def get_repository_commits(self, project_id, ref_name=None, page=1, per_page=20):
        data = {"page": page, "per_page": per_page}
        url = self.make_url("repository", "commits")
        if ref_name is not None:
            data.update({"ref_name": ref_name})
            return self.request("get", url, params=data)
        else:
            return self.request("get", url)

    def get_tree(self, branch, path):
        data = {"path": path, "ref": branch}
        url = self.make_url("repository", "tree")
        request = self.request("get", url, params=data)
        return request

"""
    release
    ~~~~~~~~~~~~~~~~~~~

    Make github a release using github api

    :copyright: (c) 2017 by Onni Software Ltd.
    :license: MIT License, see LICENSE for more details

"""

from gease.rest import Api
from gease.orgs import EndPoint as Orgs
from gease.repo import EndPoint as Repo
from gease.uritemplate import UriTemplate
import gease.exceptions as exceptions


RELEASE_URL = 'https://api.github.com/repos{/owner}{/repo}/releases'
KEY_HTML_URL = 'html_url'
MESSAGE_MISSING_KEY = 'No %s in github repsonse' % KEY_HTML_URL


class EndPoint(object):
    """
    Github release endpoint

    More documentation is available at
    https://developer.github.com/v3/repos/releases/
    """
    def __init__(self, owner, repo):
        self.__template = UriTemplate(RELEASE_URL)
        self.__template.owner = owner
        self.__template.repo = repo
        self.__client = Api.get_api()

    @property
    def url(self):
        return str(self.__template)

    def publish(self, **kwargs):
        """
        Publish the release

        More information at:
        https://developer.github.com/v3/repos/releases/#create-a-release

        :returns: the url to the release on github
        :throws: exception if gihub changes its api response
        """
        try:
            json_reply = self.__client.create(self.url, kwargs)
            return json_reply[KEY_HTML_URL]
        except exceptions.RepoNotFoundError:
            try:
                return self.republish(**kwargs)
            except exceptions.RepoNotFoundError:
                raise exceptions.AbnormalGithubResponse(
                    self.__template.repo + " does not exist!")
        except KeyError:
            raise exceptions.AbnormalGithubResponse(
                MESSAGE_MISSING_KEY)
        except exceptions.ReleaseExistException:
            raise exceptions.AbnormalGithubResponse(
                "Release or tag %s exists" % kwargs['tag_name'])
        except exceptions.UnhandledException as e:
            raise exceptions.AbnormalGithubResponse(str(e))

    def republish(self, **kwargs):
        repo = self.__template.repo
        org = which_org_has(repo)
        if org is None:
            raise exceptions.RepoNotFoundError()
        else:
            self.__template.owner = org
            json_reply = self.__client.create(self.url, kwargs)
            return json_reply[KEY_HTML_URL]


def which_org_has(repo):
    orgs = Orgs()
    for org_info in orgs.get_all_organisations():
        org_repo = Repo(org_info['repos_url'])
        for arepo in org_repo.get_all_repos():
            if repo == arepo['name']:
                return org_info['login']
    return None

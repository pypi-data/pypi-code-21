
import os
import json
import uuid
import requests
from porper.controllers.auth_controller import AuthController

class GithubAuthController(AuthController):

    def __init__(self, permission_connection):

        AuthController.__init__(self, permission_connection)

        self.auth_endpoint = os.environ.get('GITHUB_AUTH_ENDPOINT')
        self.api_endpoint = os.environ.get('GITHUB_API_ENDPOINT')
        self.client_id = os.environ.get('GITHUB_CLIENT_ID')
        self.client_secret = os.environ.get('GITHUB_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('GITHUB_REDIRECT_URI')

    def authenticate(self, params):

        code = params['code']
        state = params['state']
        #redirect_uri = params['redirect_uri']

        #print "code [%s], state [%s], redirect_uri [%s]" % (code, state, redirect_uri)
        print "code [%s], state [%s]" % (code, state)

        # first find the access token from the given code & state
        access_token_url = "%s/access_token" % (self.auth_endpoint)
        post_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "state": state
        }
        headers = {"Content-Type":"application/json"}
        r = requests.post(access_token_url, headers=headers, data=json.dumps(post_data), verify=False)
        print r
        print r._content
        """
        access_token=f378a5dd8da8422472d1875011db11ea9ccbd9c8&scope=&token_type=bearer
        """
        try:
            access_token = r._content.split('&')[0].split('=')[1]
        except Exception:
            raise Exception("unauthorized")

        """
        https://developer.github.com/apps/building-integrations/setting-up-and-registering-oauth-apps/about-authorization-options-for-oauth-apps/
        https://developer.github.com/v3/#authentication
        $ curl -u "username" https://api.github.com
        {
          "current_user_url": "https://api.github.com/user",
          "current_user_authorizations_html_url": "https://github.com/settings/connections/applications{/client_id}",
          "authorizations_url": "https://api.github.com/authorizations",
          "code_search_url": "https://api.github.com/search/code?q={query}{&page,per_page,sort,order}",
          "commit_search_url": "https://api.github.com/search/commits?q={query}{&page,per_page,sort,order}",
          "emails_url": "https://api.github.com/user/emails",
          "emojis_url": "https://api.github.com/emojis",
          "events_url": "https://api.github.com/events",
          "feeds_url": "https://api.github.com/feeds",
          "followers_url": "https://api.github.com/user/followers",
          "following_url": "https://api.github.com/user/following{/target}",
          "gists_url": "https://api.github.com/gists{/gist_id}",
          "hub_url": "https://api.github.com/hub",
          "issue_search_url": "https://api.github.com/search/issues?q={query}{&page,per_page,sort,order}",
          "issues_url": "https://api.github.com/issues",
          "keys_url": "https://api.github.com/user/keys",
          "notifications_url": "https://api.github.com/notifications",
          "organization_repositories_url": "https://api.github.com/orgs/{org}/repos{?type,page,per_page,sort}",
          "organization_url": "https://api.github.com/orgs/{org}",
          "public_gists_url": "https://api.github.com/gists/public",
          "rate_limit_url": "https://api.github.com/rate_limit",
          "repository_url": "https://api.github.com/repos/{owner}/{repo}",
          "repository_search_url": "https://api.github.com/search/repositories?q={query}{&page,per_page,sort,order}",
          "current_user_repositories_url": "https://api.github.com/user/repos{?type,page,per_page,sort}",
          "starred_url": "https://api.github.com/user/starred{/owner}{/repo}",
          "starred_gists_url": "https://api.github.com/gists/starred",
          "team_url": "https://api.github.com/teams",
          "user_url": "https://api.github.com/users/{user}",
          "user_organizations_url": "https://api.github.com/user/orgs",
          "user_repositories_url": "https://api.github.com/users/{user}/repos{?type,page,per_page,sort}",
          "user_search_url": "https://api.github.com/search/users?q={query}{&page,per_page,sort,order}"
        }
        """

        # now find the user info from the access token
        user_url = "%s/user?access_token=%s"%(self.api_endpoint, access_token)
        r = requests.get(user_url, verify=False)
        print r._content
        """
        {
            "login": "",
            "id": 0000,
            "avatar_url": "https://avatars.githubusercontent.com/u/....",
            "gravatar_id": "",
            "url": "https://api.github.com/users/....",
            "html_url": "https://github.com/....",
            "followers_url": "https://api.github.com/users/....",
            "following_url": "https://api.github.com/users/....",
            "gists_url": "https://api.github.com/users/....",
            "starred_url": "https://api.github.com/users/....",
            "subscriptions_url": "https://api.github.com/users/....",
            "organizations_url": "https://api.github.com/users/....",
            "repos_url": "https://api.github.com/users/....",
            "events_url": "https://api.github.com/users/....",
            "received_events_url": "https://api.github.com/users/....",
            "type": "User",
            "site_admin": false,
            "name": "  ",
            "company": null,
            "blog": null,
            "location": null,
            "email": "   ",
            "hireable": null,
            "bio": null,
            "public_repos": 11,
            "public_gists": 0,
            "followers": 4,
            "following": 0,
            "created_at": "2008-11-21T23:30:05Z",
            "updated_at": "2016-06-22T12:48:31Z"
        }
        """
        user_info = json.loads(r._content)

        # find email addresses
        if user_info['email'] is None:
            user_url = "%s/user/emails?access_token=%s"%(self.api_endpoint, access_token)
            r = requests.get(user_url, verify=False)
            print r._content
            emails = json.loads(r._content)
            primary_emails = [email['email'] for email in emails if email['primary']]
            if len(primary_emails) > 0:
                user_info['email'] = primary_emails[0]

        # find first and last names
        splitted = user_info['name'].split(' ')
        first_name = " ".join(splitted[:len(splitted)-1])
        last_name = splitted[len(splitted)-1]

        # now save the user info & tokens
        auth_params = {
            'user_id': str(user_info['id']),
            'email': user_info['email'],
            'family_name': last_name,
            'given_name': first_name,
            'name': user_info['name'],
            'auth_type': 'github',
            'access_token': access_token,
            'refresh_token': code
        }
        AuthController.authenticate(self, auth_params)

        # return the access_token if all completed successfully
        user_info['user_id'] = user_info['id']
        user_info['access_token'] = access_token
        user_info['groups'] = AuthController.find_groups(self, auth_params['user_id'])
        return user_info

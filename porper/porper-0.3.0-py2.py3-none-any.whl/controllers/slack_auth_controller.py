
import os
import json
import requests
from porper.controllers.auth_controller import AuthController

class SlackAuthController(AuthController):

    def __init__(self, permission_connection):

        AuthController.__init__(self, permission_connection)

        self.api_endpoint = os.environ.get('SLACK_API_ENDPOINT')
        self.client_id = os.environ.get('SLACK_CLIENT_ID')
        self.client_secret = os.environ.get('SLACK_CLIENT_SECRET')

    def authenticate(self, params):
        code = params.get('code')
        state = params.get('state')
        access_token = params.get('access_token')
        user_id = params.get('uid')
        team_id = params.get('tid')
        print "code [%s], state [%s], access_token [%s], user_id [%s], team_id [%s]" % (code, state, access_token, user_id, team_id)
        if access_token and user_id and team_id:
            return self.validate(access_token, user_id, team_id)
        else:
            return self.login(code, state)

    def login(self, code, state):

        """
        https://slack.com/oauth/authorize?client_id=1234&scope=identity.basic,identity.email
        https://slack.com/api/oauth.access?client_id=1234&client_secret=secretxxxx&code=codexxx
        {"ok":true,"access_token":"xxx","scope":"identify,commands,identity.basic,identity.email","user":{"name":"name","id":"id","email":"email"},"team":{"id":"tid"}}
        """
        api_url = "%s/oauth.access" % (self.api_endpoint)
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code
        }
        headers = {"Content-Type":"application/json"}
        r = requests.get(api_url, headers=headers, params=payload, verify=False)
        print r
        print r._content
        user_info = json.loads(r._content)
        user_info['refresh_token'] = code
        return self.save(user_info)


    """def find_user(self, user_id, team_id):
        uid = '%s-%s' % (team_id, user_id)
        from porper.models.user import User
        user = User(self.connection)
        user_info = user.find_by_id(uid)
        if not user_info:
            raise Exception("not authenticated")
        # now generate an access_token and save the tokens
        import uuid
        access_token = str(uuid.uuid4())
        refresh_token = access_token
        from porper.controllers.token_controller import TokenController
        token_controller = TokenController(self.connection)
        token_controller.save(access_token, refresh_token, uid)
        user_info['access_token'] = access_token
        return user_info"""


    def validate(self, access_token, user_id, team_id):
        # https://slack.com/api/users.profile.get?token=<access_token>&user=user_id
        api_url = "%s/users.profile.get" % (self.api_endpoint)
        payload = {
            "token": access_token,
            "user": user_id
        }
        headers = {"Content-Type":"application/json"}
        r = requests.get(api_url, headers=headers, params=payload, verify=False)
        print r
        print r._content
        """
        {
            "ok": true,
            "profile": {
                "first_name": "Alex",
                "last_name": "Ough",
                "avatar_hash": "e8a...",
                "image_24": "https://avatars.slack-edge.com/...",
                "image_32": "https://avatars.slack-edge.com/...",
                "image_48": "https://avatars.slack-edge.com/...",
                "image_72": "https://avatars.slack-edge.com/...",
                "image_192": "https://avatars.slack-edge.com/...",
                "image_512": "https://avatars.slack-edge.com/...",
                "image_1024": "https://avatars.slack-edge.com/...",
                "image_original": "https://avatars.slack-edge.com/...",
                "fields": [ ],
                "real_name": "Alex Ough",
                "display_name": "alexough",
                "real_name_normalized": "Alex Ough",
                "display_name_normalized": "alexough",
                "email": "alex.ough@sungardas.com"
            }
        }
        """
        if r.status_code != 200:
            raise Exception("not authenticated")
        if not json.loads(r._content).get('ok'):
            raise Exception("not authenticated")
        uid = '%s-%s' % (team_id, user_id)
        from porper.models.user import User
        user = User(self.connection)
        user_info = user.find_by_id(uid)
        if not user_info:
            # create this user
            profile = json.loads(r._content)['profile']
            user_info = {
                'id': uid,
                'auth_type': 'slack',
            }
            if profile.get('email'):
                user_info['email'] = profile['email']
            if profile.get('real_name'):
                user_info['name'] = profile['real_name']
            if profile.get('first_name'):
                user_info['given_name'] = profile['first_name']
            if profile.get('last_name'):
                user_info['family_name'] = profile['last_name']
            user.create(user_info)

            # add this user to its default group
            self.setup_group(team_id, uid)

        from porper.controllers.token_controller import TokenController
        token_controller = TokenController(self.connection)
        token_controller.save(access_token, access_token, uid)
        user_info['access_token'] = access_token
        return user_info


    def setup_group(self, team_id, uid):

        is_admin = False

        # create a default group if not exists
        from porper.models.group import Group
        group = Group(self.connection)
        group_info = group.find_by_id(team_id)
        if not group_info:
            # if this is the first user in this group, make it as admin
            is_admin = True
            group_info = {"id": team_id, "name": team_id}
            group.create(group_info)

        # now add this user to its default group
        from porper.models.user_group import UserGroup
        user_group = UserGroup(self.connection)
        user_group_info = {"user_id": uid, "group_id": team_id, "is_admin": is_admin}
        print user_group_info
        user_group.create(user_group_info)


    def save(self, user_info):

        splitted = user_info['user']['name'].split(' ')
        first_name = " ".join(splitted[:len(splitted)-1])
        last_name = splitted[len(splitted)-1]

        # now save the user info & tokens
        auth_params = {
            'user_id': '%s-%s' % (user_info['team']['id'], user_info['user']['id']),
            'email': user_info['user']['email'],
            'family_name': last_name,
            'given_name': first_name,
            'name': user_info['user']['name'],
            'auth_type': 'slack',
            'slack_team_id': user_info['team']['id'],
            #'slack_bot_name': bot_name,
            'access_token': user_info['access_token'],
            'refresh_token': user_info['refresh_token']
        }
        AuthController.authenticate(self, auth_params)

        # return the access_token if all completed successfully
        user_info['user_id'] = auth_params['user_id']
        user_info['groups'] = AuthController.find_groups(self, auth_params['user_id'])
        return user_info

'''
HipChat plugin.
'''
import requests

from lib import git
from lib.services import config
from lib.utils.destructure import destructure


class HipChatPlugin():
    '''
    HipChat Plugin. Only supports static messages for pre and post deploy lifecycle events.
    '''

    def __init__(self):
        self.hipchat_url = "https://{0}.hipchat.com/v2/room/{1}/notification?auth_token={2}"
        self.deploying_message = "{0} is deploying a {1} build from branch {2}."
        self.deployed_message = "{0} deployed a {1} {2} from branch {3}."

    def apply(self, compiler):
        ''' Register plugins. '''
        compiler.plugin('deploy/will_upload', self.pre_deploy)
        compiler.plugin('deploy/did_deploy', self.post_deploy)

    def config_data(self):
        ''' Returns hipchat config data. '''
        if not config.is_hipchat_configured():
            return

        return config.get()['hipchat']

    def notify(self, payload):
        ''' Send a notification. '''
        hipchat_details = config.get()['hipchat']
        company_name, room_id, auth_token = destructure(hipchat_details)(
            'company_name', 'room_id', 'auth_token'
        )
        requests.post(
            self.hipchat_url.format(company_name, room_id, auth_token),
            data=payload
        )

    def get_build_link(self, url):
        ''' Return an <a> tag with the build link. '''
        link = "<a href={0}>build</a>"
        return link.format(url)

    def pre_deploy(self, compilation):
        ''' Send a notification before deploying. '''
        if not config.is_hipchat_configured():
            return

        if not config.is_hipchat_config_valid():
            return

        release_type, branch = destructure(compilation)('release_type', 'branch')
        notification_data = {
            'color': 'red',
            'message': self.deploying_message.format(
                git.username(), release_type.upper(), branch
            ),
            'notify': True,
            'message_format': "html"
        }
        self.notify(notification_data)

    def post_deploy(self, compilation):
        ''' Send a notification after deploying. '''
        if not config.is_hipchat_configured():
            return

        release_type, branch, url = destructure(compilation)('release_type', 'branch', 'url')
        notification_data = {
            'color': "green",
            'message': self.deployed_message.format(
                git.username(), release_type.upper(), self.get_build_link(url), branch
            ),
            'notify': True,
            'message_format': "html"
        }
        self.notify(notification_data)

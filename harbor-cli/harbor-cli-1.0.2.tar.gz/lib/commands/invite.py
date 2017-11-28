''' Service for invite command. '''
import sys
from requests import exceptions

from lib import android
from lib.anchor import Anchor
from lib.logger import logger
from lib.utils.validators import is_valid_email
from lib.inqurires import getlogincredentials
from lib.services.firebase_service import Firebase
from lib.exceptions.UserNotFound import UserNotFoundException


ROLES = ['dev', 'qa', 'uat']


class Invite(Anchor):
    '''
    Service class for invitation. Subclasses Anchor to expose lifecycle events.
    '''
    def __init__(self, email, role=None):
        super().__init__()

        self.invitee = validate_email(email)
        self.role = sanitize_role(role)
        self.projectdetails = None

    def execute(self):
        ''' Invite a user to the current project. '''
        if not android.is_android():
            logger().error('You are not in a valid Android project.')
            sys.exit(1)

        email, password = getlogincredentials()

        try:
            Firebase().login_with_email(email, password)
        except exceptions.HTTPError:
            logger().error('Cannot login. Please verify credentials.')
            sys.exit(1)

        self.projectdetails = android.project_details()
        remoteprojectdetails = self.get_remote_details()

        if remoteprojectdetails is None:
            logger().error(
                'This project has not been registered. Please run `harbor register --help`'
            )

        self.update_database()
        logger().info('Invitation successful.')

    def update_database(self):
        ''' Add member entry to the database. '''
        path = 'members/{uid}/{project_name}'
        try:
            invitee = Firebase().get_details_for_user_by_email(self.invitee)()
        except UserNotFoundException:
            error_message = 'The email {0} is not registered'.format(self.invitee)
            logger().error(error_message)
            sys.exit(1)

        data = {
            'role': self.role,
            'notificationLevel': self.role
        }
        sanitizedpackagename = ''.join(self.projectdetails['packagename'].split('.'))

        Firebase().write_to_db(
            path.format(
                uid=invitee['uid'],
                project_name=sanitizedpackagename
            ),
            data,
            update=True
        )

    def get_remote_details(self):
        ''' Fetches the details about the current project from the server. '''
        path = 'projects/{0}'
        sanitizedpackagename = ''.join(self.projectdetails['packagename'].split('.'))

        existing = Firebase().get_from_db(path.format(sanitizedpackagename))

        return existing.val()


def sanitize_role(role):
    ''' For unpermitted incoming deploy type, fallback to 'dev'.  '''
    if role is None or role.lower() not in ROLES:
        logger().warning('Unspecified or unpermitted role - Falling back to "dev"')
        return 'dev'

    return role

def validate_email(email):
    ''' For invalid email, throw an error. '''
    error_message = '%s is not valid.'

    if not is_valid_email(email):
        message = error_message.format(email)
        logger().error(message)
        sys.exit(1)

    return email

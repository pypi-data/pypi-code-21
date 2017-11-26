''' Service for register command. '''
import sys
from requests import exceptions

from lib import android
from lib.anchor import Anchor
from lib.logger import logger
from lib.inqurires import getlogincredentials
from lib.utils.validators import is_valid_email
from lib.services.firebase_service import Firebase

class Register(Anchor):
    '''
    Service class for register command.
    '''

    def __init__(self, user_registration):
        super().__init__()

        self.user = None
        self.icon_url = None
        self.icon_path = None
        self.packagename = None
        self.projectdetails = None
        self.is_user_registration = user_registration or False

    def execute(self):
        ''' Register a user or a project. '''
        if self.is_user_registration:
            self.register_user()
            return

        if not android.is_android():
            logger().error('You are not in a valid Android project.')
            sys.exit(1)

        self.register_project()

    def register_user(self):
        ''' Register a user. '''
        # Signup credentials.
        email, password = getlogincredentials()

        if not is_valid_email(email):
            logger().error('Invalid email. Please try another one.')
            sys.exit(1)

        try:
            Firebase().signup_via_email(email, password)
        except Exception as e: #pylint: disable=broad-except
            logger().error('Could not register. Please use a valid email address and a strong password.')
            sys.exit(1)

        success = 'Signed up successfully with email "%s"' % email

        logger().info(success)

    def register_project(self):
        ''' Register a project. '''

        email, password = getlogincredentials()

        try:
            Firebase().login_with_email(email, password)
            self.user = Firebase().get_current_user_details()
        except exceptions.HTTPError:
            logger().error('Cannot login. Please verify credentials.')
            sys.exit(1)

        self.projectdetails = android.project_details()
        self.packagename = ''.join(self.projectdetails['packagename'].split('.'))

        # local path to ic_launcher icon
        self.icon_path = android.launcher_icon()

        if self.icon_path is None:
            logger().warning('Cannot find any valid icons.')
        else:
            self.icon_url = self.upload_icon()

        if self.already_exists():
            logger().error('This project has already been registered.')
            sys.exit(1)

        self.update_database()

        success = '"{0}" registered successfully.'.format(
            self.projectdetails['name'] or self.packagename
        )

        logger().info(success)

    def update_database(self):
        ''' Update database for new project. '''
        projectpath = 'projects/{packagename}'
        project = {
            'uploads': {},
            'metadata': {},
            'iconUrl': self.icon_url,
            'packageName': self.packagename,
            'name': self.projectdetails['name']
        }

        # The one registering the project is an admin by default.
        memberpath = 'members/{uid}/{packagename}'
        member = {
            'role': 'admin',
            'notificationLevel': 'all'
        }

        Firebase().write_to_db(
            projectpath.format(packagename=self.packagename),
            project
        )

        Firebase().write_to_db(
            memberpath.format(
                uid=self.user['uid'],
                packagename=self.packagename
            ),
            member
        )


    def already_exists(self):
        ''' Returns True if a project by the same package name already exists. '''
        path = 'projects/{0}'
        data = Firebase().get_from_db(
            path.format(self.packagename)
        )

        return data.val() is not None

    def upload_icon(self):
        ''' Upload an icon and get its download url. '''
        path = '{0}/icon.png'

        return Firebase().upload(
            path.format(self.packagename),
            self.icon_path
        )

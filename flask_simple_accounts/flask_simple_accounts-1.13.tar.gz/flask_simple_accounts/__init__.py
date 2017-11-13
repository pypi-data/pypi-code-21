import os
import datetime

from flask_mail import Mail, Message
import flask_login

import flask_beautiful_messages
import flask_render_specific_template
import flask_multiple_static_folders

from . config import Config
from . import helper


login_manager = flask_login.LoginManager()


@login_manager.user_loader
def user_loader(email):
    return FlaskSimpleAccounts.models.User.query.filter_by(email=email).first()


def save_db():
    FlaskSimpleAccounts.models.db.session.commit()

def delete_db_object(db_object):
    FlaskSimpleAccounts.db.session.delete(db_object)


class FlaskSimpleAccounts:

    app = None
    models = None
    db = None

    def __init__(self, models, app):
        FlaskSimpleAccounts.app = app
        FlaskSimpleAccounts.models = models
        FlaskSimpleAccounts.db = self.initialize_db()
        self.customize_app_config()
        login_manager.init_app(FlaskSimpleAccounts.app)

    def hash_matches_user_password_hash(self, hash, user):
        return hash == user.password_hash

    def password_is_correct(self, raw_password, email):
        user = self.get_user_by_email(email)

        if user is None:
            return False

        password_hash = helper.hash_password(
            raw_password,
            user.salt
        )
        return self.hash_matches_user_password_hash(password_hash, user)

    def get_package_root_dir(self):
        file_path = os.path.realpath(__file__)
        return os.path.dirname(file_path)

    def get_package_template_dir(self):
        package_dir = self.get_package_root_dir()
        return os.path.join(package_dir, 'templates')

    def get_user_by_email(self, email):
        user = FlaskSimpleAccounts.models.User.query.filter_by(email=email).first()
        return user

    def get_current_user(self):
        user_id = flask_login.current_user.get_id()
        return self.get_user_by_email(user_id)

    def user_email_is_unique(self, user_email):
        user = self.get_user_by_email(user_email)
        return user is None

    def create_new_user(self, password):
        new_user = FlaskSimpleAccounts.models.User(password)
        FlaskSimpleAccounts.models.db.session.add(new_user)
        save_db()
        return new_user

    def create_new_verification(self, code, user, unverified_email):
        new_verification = FlaskSimpleAccounts.models.EmailVerification(code, user, unverified_email)
        FlaskSimpleAccounts.models.db.session.add(new_verification)
        save_db()
        return new_verification

    def email_is_valid(self, email):
        import re
        email_regex = r"[^@]+@[^@]+\.[^@]+"
        match = re.match(email_regex, email)
        return match is not None

    def string_has_minimum_length(self, string, length):
        return len(string) >= length

    def string_has_minimum(self, string, min_count, comparison_function):
        count = 0
        for character in string:
            if comparison_function(character):
                count += 1

            if count >= min_count:
                return True

        return False

    def string_has_minimum_letters(self, string, min_count):
        def is_alpha(string):
            return string.isalpha()
        return self.string_has_minimum(string, min_count, is_alpha)

    def string_has_minimum_numbers(self, string, min_count):
        def is_digit(string):
            return string.isdigit()
        return self.string_has_minimum(string, min_count, is_digit)

    def string_has_minimum_upper_case_characters(self, string, min_count):
        def is_upper(string):
            return string.isupper()
        return self.string_has_minimum(string, min_count, is_upper)

    def string_has_minimum_lower_case_characters(self, string, min_count):
        def is_lower(string):
            return string.islower()
        return self.string_has_minimum(string, min_count, is_lower)

    def string_has_minimum_special_characters(self, string, min_count, special_characters):
        def is_special(string):
            return string in special_characters
        return self.string_has_minimum(string, min_count, is_special)

    def password_is_valid(self, password):
        requirements = FlaskSimpleAccounts.app.config['PASSWORD_REQUIREMENTS']

        if requirements['has_length']['default']:
            if self.string_has_minimum_length(password, requirements['has_length']['min_value']):
                print("Password has minimum length")
            else:
                return False

        if requirements['has_letter']['default']:
            if self.string_has_minimum_letters(password, requirements['has_letter']['min_value']):
                print("Password has minimum number of letters")
            else:
                return False

        if requirements['has_number']['default']:
            if self.string_has_minimum_numbers(password, requirements['has_number']['min_value']):
                print("Password has minimum number of numbers")
            else:
                return False

        if requirements['has_upper_case']['default']:
            if self.string_has_minimum_upper_case_characters(password, requirements['has_upper_case']['min_value']):
                print("Password has minimum number of upper case characters")
            else:
                return False

        if requirements['has_lower_case']['default']:
            if self.string_has_minimum_lower_case_characters(password, requirements['has_lower_case']['min_value']):
                print("Password has minimum number of lower case characters")
            else:
                return False

        if requirements['has_special_character']['default']:
            if self.string_has_minimum_special_characters(
                password,
                requirements['has_special_character']['min_value'],
                requirements['has_special_character']['values']
            ):
                print("Password has minimum number of special case characters")
            else:
                return False

        return True

    def generate_unique_code(self):
        import uuid
        return str(uuid.uuid4())

    def generate_email_verification_code(self):
        code = self.generate_unique_code()
        return code.replace('-','')

    def generate_site_address(self, request):
        if FlaskSimpleAccounts.app.config['SITE_ADDRESS']:
            return FlaskSimpleAccounts.app.config['SITE_ADDRESS']
        return request.environ['HTTP_HOST']

    def send_verification_email(self, request, unverified_email, user):
        print('sending verification email')
        mail = Mail(FlaskSimpleAccounts.app)
        msg = Message(
            subject=FlaskSimpleAccounts.app.config['EMAIL_VERIFICATION']['subject'],
            sender=FlaskSimpleAccounts.app.config['EMAIL_VERIFICATION']['sender'],
            recipients=[unverified_email]
        )
        site_address = self.generate_site_address(request)
        verification_code = self.generate_email_verification_code()
        verification_path = FlaskSimpleAccounts.app.config['SIMPLE_ACCOUNTS_APP_PATHS']['verify_email']
        self.create_new_verification(verification_code, user, unverified_email)

        msg.html = 'Your verification link is: {}{}?verification_code={}'.format(
            site_address,
            verification_path,
            verification_code
        )
        mail.send(msg)

    def sign_up(self, request):
        response = {
            'success': False,
            'errors': [],
        }

        email = request.values['email']
        password = request.values['password']

        # validate email
        if self.email_is_valid(email):
            print("Email is valid")
        else:
            response['errors'].append('Email is not valid')
            return response

        # check if user with email is already in system
        if self.user_email_is_unique(email):
            print('User email is unique')
        else:
            response['errors'].append('User email is not unique')
            return response

        # validate password
        if self.password_is_valid(password):
            print("Password is valid")
        else:
            response['errors'].append('Password is not valid')
            return response

        # add user to system
        new_user = self.create_new_user(password)
        response['success'] = True

        # handle verification
        if FlaskSimpleAccounts.app.config['EMAIL_VERIFICATION']['enabled']:
            self.send_verification_email(request, email, new_user)
        else:
            new_user.email = email
            new_user.is_active = True
            save_db()

        return response

    def verify_email(self, request):
        email_is_verified = False

        # extract verification code
        verification_code = request.values['verification_code']

        # use verification code to find user
        verification = FlaskSimpleAccounts.models.EmailVerification.query.filter_by(code=verification_code).first()

        if verification:
            time_difference = datetime.datetime.now() - verification.time_created
            hours_since_verification_creation = self.convert_seconds_to_hours(time_difference.seconds)

            if hours_since_verification_creation < FlaskSimpleAccounts.app.config['EMAIL_VERIFICATION']['hours_verification_is_valid']:
                user = verification.user
                user.email = verification.unverified_email
                user.email_verified = True
                user.is_active = True
                save_db()
                email_is_verified = True

        verification_config = FlaskSimpleAccounts.app.config['EMAIL_VERIFICATION_TEMPLATE']

        if email_is_verified:
            title = verification_config['success_title']
            message = verification_config['success_message']
        else:
            title = verification_config['fail_title']
            message = verification_config['fail_message']

        context = {
            'title':title,
            'message': message,
            'link_address': verification_config['return_link'],
            'link_text': verification_config['return_link_text']
        }
        context.update(verification_config)

        beautiful_messages_template = flask_beautiful_messages.get_package_template_dir()
        response = flask_render_specific_template.render_template(
            beautiful_messages_template,
            'basic-multiple.html',
            **context
        )
        return response

    def log_in(self, request):
        """
        Error messages are vague here on purpose
        """
        response = {
            'success': False,
            'errors': [],
        }

        email = request.form['email']
        password = request.form['password']

        if self.password_is_correct(password, email):
            user = self.get_user_by_email(email)
            flask_login.login_user(user)
            user.mark_user_as_authenticated(callback=save_db)
            response['success'] = True
        else:
            response['errors'].append('Invalid log in')
        return response

    def log_out(self, request):
        response = {
            'success': False,
            'errors': [],
        }
        user = self.get_current_user()
        if not user.is_authenticated:
            response['errors'].append("User is not logged in")
        else:
            user.mark_user_as_anonymous(callback=save_db)
            flask_login.logout_user()
            response['success'] = True

        return response


    def delete_account(self, request):
        """
        User must be logged in
        User must send her/his email and password combination
        """
        response = {
            'success': False,
            'errors': [],
        }

        user = self.get_current_user()
        if user is None or not user.is_authenticated:
            response['errors'].append("User is not logged in")
        elif self.password_is_correct(request.form['password'], request.form['email']):
            delete_db_object(user)
            save_db()
        else:
            response['errors'].append('Invalid email/password combination')

        return response


    def change_email(self, request):
        """
        User must be logged in
        User must send her/his new_email
        """
        response = {
            'success': False,
            'errors': [],
        }

        user = self.get_current_user()
        new_email = request.form.get('new_email')

        if user is None or not user.is_authenticated:
            response['errors'].append("User is not logged in")
        elif self.email_is_valid(new_email) and self.user_email_is_unique(new_email):

            if FlaskSimpleAccounts.app.config['EMAIL_VERIFICATION']['enabled']:
                self.send_verification_email(request, new_email, user)
            else:
                user.email = new_email
            save_db()
            response['success'] = True

        else:
            response['errors'].append('New email is invalid')

        return response

    def change_password(self, request):
        """
        User must be logged in
        User must send her/his old_password, new_password
        """
        response = {
            'success': False,
            'errors': [],
        }

        user = self.get_current_user()
        email = user.email
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        if user is None or not user.is_authenticated:
            response['errors'].append("User is not logged in")
        elif self.password_is_correct(current_password, email) and new_password:

            if self.password_is_valid(new_password):
                new_salt = helper.generate_salt()
                new_password_hash = helper.hash_password(new_password, new_salt)
                user.salt = new_salt
                user.password_hash = new_password_hash
                save_db()
                response['success'] = True
            else:
                response['errors'].append('New password is invalid')

        else:
            response['errors'].append('Invalid email/password combination')

        return response


    def convert_seconds_to_hours(self, seconds):
        seconds_per_hour = 3600
        return seconds / seconds_per_hour

    def initialize_db(self):
        db = FlaskSimpleAccounts.models.db
        db.app = FlaskSimpleAccounts.app
        db.init_app(FlaskSimpleAccounts.app)
        return db

    def set_app_static_folders(self):
        beautiful_messages_static_folder = flask_beautiful_messages.get_package_static_dir()
        FlaskSimpleAccounts.app.static_folders = [FlaskSimpleAccounts.app.static_folder, beautiful_messages_static_folder]
        return FlaskSimpleAccounts.app

    def customize_app_config(self):
        FlaskSimpleAccounts.app.config['PASSWORD_REQUIREMENTS'].update(FlaskSimpleAccounts.app.config['CUSTOM_PASSWORD_REQUIREMENTS'])
        FlaskSimpleAccounts.app.config['EMAIL_VERIFICATION'].update(FlaskSimpleAccounts.app.config['CUSTOM_EMAIL_VERIFICATION'])
        FlaskSimpleAccounts.app.config['SIMPLE_ACCOUNTS_APP_PATHS'].update(FlaskSimpleAccounts.app.config['CUSTOM_SIMPLE_ACCOUNTS_APP_PATHS'])
        FlaskSimpleAccounts.app.config['EMAIL_VERIFICATION_TEMPLATE'].update(FlaskSimpleAccounts.app.config['CUSTOM_EMAIL_VERIFICATION_TEMPLATE'])

        # delete old keys
        del FlaskSimpleAccounts.app.config['CUSTOM_EMAIL_VERIFICATION']
        del FlaskSimpleAccounts.app.config['CUSTOM_EMAIL_VERIFICATION_TEMPLATE']
        del FlaskSimpleAccounts.app.config['CUSTOM_PASSWORD_REQUIREMENTS']
        del FlaskSimpleAccounts.app.config['CUSTOM_SIMPLE_ACCOUNTS_APP_PATHS']

        FlaskSimpleAccounts.app = flask_multiple_static_folders.transform_app(FlaskSimpleAccounts.app)
        self.set_app_static_folders()

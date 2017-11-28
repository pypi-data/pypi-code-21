'''
Module to handle all inquiries that the CLI makes to the user.
'''
import click
from inquirer import Text, Password, Confirm, prompt

from lib import git
from lib.utils.validators import is_valid_email


RELEASE_LOG_TEXT = '''
# Please enter an optional CHANGELOG for this release. Everything below this line is ignored.
#
# On branch '{0}' as user '{1}'
'''


def getlogincredentials():
    ''' Inquire about login credentials from the user. '''
    questions = [
        Text(
            'email',
            validate=lambda _, email: is_valid_email(email),
            message='Enter your email address',
            default=git.email() or ''
        ),

        Password(
            'password',
            message='Enter your password'
        )
    ]

    answers = prompt(questions)

    return (answers['email'], answers['password'])


def getversionnumber():
    ''' Get version number for a release. '''
    questions = [
        Text(
            'version',
            message='Enter a version number for the release'
        )
    ]

    answers = prompt(questions)

    return answers['version']


def getchangelog():
    '''
    Opens up EDITOR, and allows user to enter changelog.
    Splits by the boilerplate text and returns user input
    '''
    branch = git.branch() or '<unavailable>'
    user = git.username() or '<unavailable>'

    data = click.edit(
        text=RELEASE_LOG_TEXT.format(branch, user),
        require_save=True
    )
    try:
        serialized = data.split(RELEASE_LOG_TEXT.format(branch, user))

        return serialized[0]
    except Exception:  # pylint: disable=broad-except
        return ''


def getdeploymentconfirmation():
    ''' Get confirmation (y/N) for deployment. '''
    questions = [
        Confirm(
            'confirm',
            message='Confirm these details to begin deployment?',
            default=True
        )
    ]

    answers = prompt(questions)

    return answers['confirm']

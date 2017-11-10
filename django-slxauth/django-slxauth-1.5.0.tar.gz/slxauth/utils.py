import logging

import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.models import Group


logger = logging.getLogger(__name__)


def get_unsaved_user_from_token(access_token):
    logger.debug('extracting user info from access-token %s' % access_token)

    extra_data = jwt.decode(access_token, verify=False)

    user_model = get_user_model()
    user, created = user_model.objects.get_or_create(email=extra_data['email'])

    logger.debug('%s user %s' % ('creating' if created else 'updating', user.email))

    user.customer_no = extra_data['customerNumber']
    user.customer_name = extra_data['customerName']
    user.last_name = extra_data['lastName']
    user.first_name = extra_data['firstName']
    user.title = extra_data['title']
    user.is_customer_admin = extra_data['isCustomerAdmin']
    user.language = extra_data['language']
    user.crm_contact_id = extra_data['crmContactId']
    user.um_id = extra_data['id']

    logger.debug('creating groups for user %s' % user.email)
    for role in extra_data['authorities']:
        group, created = Group.objects.get_or_create(name=role)
        user.groups.add(group)

    logger.debug('finished user extraction from token')
    return user

def get_unsaved_user_from_token_and_portal_config(access_token, portal_config):
    user = get_unsaved_user_from_token(access_token)

    if portal_config and 'fetch-user-info-url' in portal_config:
        logger.debug('fetching user info from portal config for %s' % user.email)
        user_profile_response = None

        try:
            user_profile_response = requests.get(portal_config['fetch-user-info-url'], headers={'Authorization': 'Bearer %s' % access_token}, timeout=0.5)
            logger.debug('user profile response: %s' % user_profile_response)
        except Exception as e:
            logger.error('could not fetch user info: %s' % e)

        if user_profile_response and user_profile_response.status_code == 200:
            user_profile = user_profile_response.json()
            user.avatar_attachment_id = user_profile['avatarAttachmentId']
            user.company_logo_attachment_id = user_profile['companyLogoAttachmentId']
            logger.debug('updated user %s from portal config' % user.email)

    return user

def login_using_token(request, access_token):

    portal_config_response = None

    logger.debug('beginning user login from token')
    try:
        # load more infos...
        portal_config_response = requests.get(settings.PORTAL_CONFIG_URL, headers={
            'Authorization': 'Bearer %s' % access_token
        }, timeout=0.5)
        logger.debug('portal config response: %s' % portal_config_response)
    except Exception as e:
        logger.error('could not load remote portal config: %s' % e)

    user = None

    if portal_config_response and portal_config_response.status_code == 200:
        try:
            logger.debug('getting user from access token and portal config')
            portal_config = portal_config_response.json()
            user = get_unsaved_user_from_token_and_portal_config(access_token, portal_config)
        except Exception as e:
            logger.error('could not get user from access token and portal config: %s' % e)

    if not user:
        logger.debug('getting user from access token without portal config')
        user = get_unsaved_user_from_token(access_token)

    logger.debug('saving user object')
    user.save()
    logger.debug('logging in user %s' % user.email)
    login(request, user)


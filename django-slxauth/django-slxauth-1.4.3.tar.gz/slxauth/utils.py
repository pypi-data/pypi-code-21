import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.models import Group


def get_unsaved_user_from_token(access_token):
    extra_data = jwt.decode(access_token, verify=False)

    user_model = get_user_model()
    user, created = user_model.objects.get_or_create(email=extra_data['email'])
    user.customer_no = extra_data['customerNumber']
    user.customer_name = extra_data['customerName']
    user.last_name = extra_data['lastName']
    user.first_name = extra_data['firstName']
    user.title = extra_data['title']
    user.is_customer_admin = extra_data['isCustomerAdmin']
    user.language = extra_data['language']
    user.crm_contact_id = extra_data['crmContactId']
    user.um_id = extra_data['id']

    for role in extra_data['authorities']:
        group, created = Group.objects.get_or_create(name=role)
        user.groups.add(group)

    return user

def get_unsaved_user_from_token_and_portal_config(access_token, portal_config):
    user = get_unsaved_user_from_token(access_token)

    user.avatar_attachment_id = portal_config['avatarAttachmentId']
    user.company_logo_attachment_id = portal_config['companyLogoAttachmentId']

    return user

def login_using_token(request, access_token, expiration_time, refresh_token):

    # load more infos...
    portal_config_response = requests.get(settings.PORTAL_CONFIG_URL, cookies={
        'access_token': access_token,
        'expiration_time': expiration_time,
        'refresh_token': refresh_token,
    })

    if portal_config_response.status_code == 200:
        portal_config = portal_config_response.json()
        user = get_unsaved_user_from_token_and_portal_config(request, access_token, portal_config)
    else:
        user = get_unsaved_user_from_token(request, access_token)
    user.save()
    login(request, user)


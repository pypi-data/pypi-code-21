import jwt
from django.contrib.auth import get_user_model
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
    user.id = extra_data['id']

    for role in extra_data['authorities']:
        group, created = Group.objects.get_or_create(name=role)
        user.groups.add(group)

    return user

def get_unsaved_user_from_token_and_portal_config(access_token, portal_config):
    user = get_unsaved_user_from_token(access_token)

    user.avatar_attachment_id = portal_config['avatarAttachmentId']
    user.company_logo_attachment_id = portal_config['companyLogoAttachmentId']

    return user

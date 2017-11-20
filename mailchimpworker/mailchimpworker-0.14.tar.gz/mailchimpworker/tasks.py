import requests
import json
import hashlib

from celery import task
from django.conf import settings
from .models import Subscriber


def post_mailchimp(email, list_id, category_id, interest_id):
    API_KEY = settings.MAILCHIMP_API_KEY
    API_ROOT = 'https://us11.api.mailchimp.com/3.0/'

    api_postfix = 'lists/{}/members'.format(list_id)
    payload = {'email_address': email, 'status': 'subscribed',
               'interests': {interest_id: True}}
    result = requests.post(
        API_ROOT + api_postfix, data=json.dumps(payload), auth=('anystring', API_KEY)).json()

    try:
        if result['title'] and result['title'] == 'Member Exists':
            subscriber_hash = hashlib.md5()
            subscriber_hash.update(email.lower().encode('utf-8'))
            result_hash = subscriber_hash.hexdigest()

            api_postfix = 'lists/{}/members/{}'.format(list_id, result_hash)
            user_info_json = requests.get(
                API_ROOT + api_postfix, auth=('anystring', API_KEY)).json()

            user_interests = user_info_json['interests']
            user_interests.update({interest_id: True})
            payload = {'interests': user_interests}
            response = requests.patch(
                API_ROOT + api_postfix, data=json.dumps(payload), auth=('anystring', API_KEY))
    except KeyError:
        pass


@task
def send_new_emails(list_id, category_id, interest_id):
    subscribers_base = Subscriber.objects.filter(status=False)
    for i in subscribers_base:
        post_mailchimp(i.email, list_id, category_id, interest_id)
        i.status = True
        i.save()

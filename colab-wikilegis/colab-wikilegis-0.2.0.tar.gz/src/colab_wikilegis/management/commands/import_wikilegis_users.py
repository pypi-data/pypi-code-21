# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.utils.text import slugify
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from colab_wikilegis.data_importer import ColabWikilegisPluginDataImporter
from random import randint
import uuid

User = get_user_model()


def set_username(username, users):
    usernames_in_db = users.filter(username=username)
    usernames_in_db = usernames_in_db.values_list('username', flat=True)
    if username in usernames_in_db:
        return set_username(username + str(randint(1, 9)), users)
    else:
        return username


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        importer = ColabWikilegisPluginDataImporter()
        users = importer.fetch_users()
        colab_users = User.objects.all()
        for user in users:
            if not user.email in colab_users.values_list('email', flat=True):
                username = set_username(slugify(user.username[:25]),
                                        colab_users)

                new_password = str(uuid.uuid4().get_hex()[0:10])
                new_user, created = User.objects.get_or_create(
                    username=username,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
                new_user.set_password(new_password)
                new_user.is_active = True
                new_user.save()

                print "Importing " + new_user.username

                if created:
                    self.send_email(new_user, new_password)

    def send_email(self, user, password):
        html = render_to_string('emails/wikilegis_new_user.html',
                                {'user': user, 'password': password})
        email_to = [user.email, ]
        subject = "Conheça o novo e-Democracia!"
        mail = EmailMultiAlternatives(subject=subject, to=email_to)
        mail.attach_alternative(html, 'text/html')
        mail.send()

# -*- coding: utf-8 -*-
from django.core import mail
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import Client
from molo.core.tests.base import MoloTestCaseMixin
from molo.commenting.tasks import send_export_email
from molo.core.models import Main, Languages, SiteLanguageRelation
from molo.commenting.models import MoloComment
from datetime import datetime


class ModelsTestCase(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.user = User.objects.create_user(
            'test', 'test@example.org', 'test'
        )

        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='admin@example.com',
            password='0000',
            is_staff=True
        )

        self.client = Client()
        self.client.login(username='superuser', password='0000')
        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.article = self.mk_article(
            title='article 1', slug='article-1', parent=self.yourmind,
            subtitle='article 1 subtitle')
        self.content_type = ContentType.objects.get_for_model(self.article)

    def mk_comment(self, comment, parent=None):
        return MoloComment.objects.create(
            content_type=self.content_type,
            object_pk=self.article.pk,
            content_object=self.article,
            site=Site.objects.get_current(),
            user=self.user,
            comment=comment,
            parent=parent,
            submit_date=datetime.now())

    def test_send_export_email(self):
        self.mk_comment('comment_text')
        send_export_email(self.user.email, {})
        message = list(mail.outbox)[0]
        self.assertEquals(message.to, [self.user.email])
        self.assertEquals(
            message.subject, 'Molo export: ' + settings.SITE_NAME)
        self.assertEquals(
            message.attachments[0],
            ('Molo_export_testapp.csv',
             'submit_date,user_name,user_email,comment,id,parent_id,'
             'article_title,article_subtitle,article_full_url,is_public,'
             'is_removed,parent,wagtail_site\r\n' + str(
                 datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")) +
             ',,,comment_text,1,,article 1,article 1 subtitle,'
             'http://main-1.localhost:8000/sections-main-1/your-mind/'
             'article-1/,1,0,,1\r\n',
             'text/csv'))

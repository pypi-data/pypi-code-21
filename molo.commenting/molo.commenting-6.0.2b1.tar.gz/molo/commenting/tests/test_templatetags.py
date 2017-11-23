import re

from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from django.template import Template, Context

from molo.commenting.models import MoloComment
from molo.commenting.forms import MoloCommentForm
from molo.core.models import Main, Languages, SiteLanguageRelation
from molo.core.tests.base import MoloTestCaseMixin


class GetMoloCommentsTest(TestCase, MoloTestCaseMixin):

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
            'test', 'test@example.org', 'test')
        self.content_type = ContentType.objects.get_for_model(self.user)

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.article1 = self.mk_article(
            title='article 1', slug='article-1', parent=self.yourmind)

        for i in range(10):
            MoloComment.objects.create(
                content_type=self.content_type,
                object_pk=self.article1.pk,
                content_object=self.user,
                site=Site.objects.get_current(),
                user=self.user,
                comment='comment %s' % (i,),
                submit_date=datetime.now())

    def test_template_tags_default(self):
        template = Template("""
        {% load molo_commenting_tags mptt_tags %}
        {% get_molo_comments for object as comments %}
        {% for comment in comments %}
            {% recursetree comment %}
                {{ node.comment }}
                {{ children }}
            {% endrecursetree %}
        {% endfor %}
        """)
        output = template.render(Context({
            'object': self.user,
        }))
        expected_output = [
            'comment 9\s+',
            'comment 8\s+',
            'comment 7\s+',
            'comment 6\s+',
            'comment 5\s+',
        ]
        self.assertNotEqual(re.search(''.join(expected_output), output), None)
        self.assertFalse('comment 4' in output)

    def test_template_tags_limits(self):
        template = Template("""
        {% load molo_commenting_tags mptt_tags %}
        {% get_molo_comments for object as comments limit 2 %}
        {% for comment in comments %}
            {% recursetree comment %}
                {{ node.comment }}
                {{ children }}
            {% endrecursetree %}
        {% endfor %}
        """)
        output = template.render(Context({
            'object': self.user,
        }))
        expected_output = [
            'comment 9\s+',
            'comment 8\s+',
        ]
        self.assertNotEqual(re.search(''.join(expected_output), output), None)
        self.assertFalse('comment 7' in output)

    def test_template_tags_unlimited(self):
        template = Template("""
        {% load molo_commenting_tags mptt_tags %}
        {% get_molo_comments for object as comments limit -1 %}
        {% for comment in comments %}
            {% recursetree comment %}
                {{ node.comment }}
                {{ children }}
            {% endrecursetree %}
        {% endfor %}
        """)
        output = template.render(Context({
            'object': self.user,
        }))
        expected_output = [
            'comment 9\s+',
            'comment 8\s+',
            'comment 7\s+',
            'comment 6\s+',
            'comment 5\s+',
            'comment 4\s+',
            'comment 3\s+',
            'comment 2\s+',
            'comment 1\s+',
            'comment 0\s+',
        ]
        self.assertNotEqual(re.search(''.join(expected_output), output), None)


class GetCommentsContentObjectTest(TestCase, MoloTestCaseMixin):

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
            'test', 'test@example.org', 'test')
        self.content_type = ContentType.objects.get_for_model(self.user)

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.article1 = self.mk_article(
            title='article 1', slug='article-1', parent=self.yourmind)

        for i in range(10):
            MoloComment.objects.create(
                content_type=self.content_type,
                object_pk=self.article1.pk,
                content_object=self.user,
                site=Site.objects.get_current(),
                user=self.user,
                comment='comment %s' % (i,),
                submit_date=datetime.now())

    def test_get_comments_content_object(self):
        template = Template("""
        {% load molo_commenting_tags %}
        {% get_comments_content_object for form as the_object %}
        {{ the_object.email }}
        """)
        output = template.render(Context({
            'form': MoloCommentForm(self.user, data={
                'content_type': 'auth.user',
                'object_pk': self.user.pk,
            }),
        }))
        self.assertTrue('test@example.org' in output)

# -*- coding: utf-8 -*-

import re

from bs4 import BeautifulSoup
from datetime import datetime
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase, Client, override_settings

from molo.commenting.models import MoloComment, CannedResponse
from molo.core.models import Main, Languages, SiteLanguageRelation
from molo.core.tests.base import MoloTestCaseMixin


class CommentingAdminTest(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.section = self.mk_section(
            self.section_index, title='section')
        self.article = self.mk_article(self.section, title='article 1',
                                       subtitle='article 1 subtitle',
                                       slug='article-1')
        self.user = User.objects.create_superuser(
            'testadmin', 'testadmin@example.org', 'testadmin')
        self.content_type = ContentType.objects.get_for_model(self.article)
        self.client = Client()
        self.client.login(username='testadmin', password='testadmin')

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

    def test_reply_link_on_comment(self):
        '''Every root comment should have the "Add reply" text and icon that
        has a link to the reply view for that comment.'''
        comment = self.mk_comment('comment text')
        changelist = self.client.get(
            reverse('admin:commenting_molocomment_changelist'))
        self.assertContains(
            changelist,
            '<img src="%s" alt="add" />' % (
                static('admin/img/icon_addlink.gif')),
            html=True)
        self.assertContains(
            changelist,
            '<a href="%s">Add reply</a>' % (
                reverse(
                    'admin:commenting_molocomment_reply',
                    kwargs={'parent': comment.pk})),
            html=True)

    def test_nested_replies(self):
        '''Replies to comments should be indented and ordered chronologically
        directly under the parent comment.'''
        comment = self.mk_comment('comment text')
        reply1 = self.mk_comment('reply 1 text 😁', parent=comment)
        reply2 = self.mk_comment('reply 2 text', parent=comment)
        changelist = self.client.get(
            reverse('admin:commenting_molocomment_changelist'))
        self.assertContains(changelist, reply1.comment)
        html = BeautifulSoup(changelist.content, 'html.parser')
        table = html.find(id='result_list')
        [commentrow, reply1row, reply2row] = table.tbody.find_all('tr')
        self.assertTrue(comment.comment in commentrow.prettify())
        self.assertEqual(
            len(commentrow.find_all(style='padding-left:8px')), 1)
        self.assertTrue(reply2.comment in reply2row.prettify())
        self.assertEqual(
            len(reply1row.find_all(style='padding-left:18px')), 1)
        self.assertEqual(
            len(reply2row.find_all(style='padding-left:18px')), 1)

    def test_comments_reverse_chronological_order(self):
        '''The admin changelist view should display comments in reverse
        chronological order.'''
        comment1 = self.mk_comment('comment1')
        comment2 = self.mk_comment('comment2')
        comment3 = self.mk_comment('comment3')
        changelist = self.client.get(
            reverse('admin:commenting_molocomment_changelist'))

        html = BeautifulSoup(changelist.content, 'html.parser')
        table = html.find(id='result_list')
        [c3, c2, c1] = table.tbody.find_all('tr')
        self.assertTrue(comment3.comment in c3.prettify())
        self.assertTrue(comment2.comment in c2.prettify())
        self.assertTrue(comment1.comment in c1.prettify())

    def test_reply_to_comment_view(self):
        '''A get request on the comment reply view should return a form that
        allows the user to make a comment in reply to another comment.'''
        comment = self.mk_comment('comment')
        formview = self.client.get(
            reverse('admin:commenting_molocomment_reply', kwargs={
                'parent': comment.pk,
            }))
        self.assertTemplateUsed(formview, 'admin/reply.html')

    def test_reply_to_comment(self):
        '''A valid form should create a new comment that is a reply to an
        existing comment.'''
        comment = self.mk_comment('comment')
        formview = self.client.get(
            reverse('admin:commenting_molocomment_reply', kwargs={
                'parent': comment.pk,
            }))

        html = BeautifulSoup(formview.content, 'html.parser')
        data = {
            i.get('name'): i.get('value') or ''
            for i in html.form.find_all('input') if i.get('name')
        }
        data['comment'] = 'test reply text'

        response = self.client.post(
            reverse('admin:commenting_molocomment_reply', kwargs={
                'parent': comment.pk,
            }), data=data)
        comment = MoloComment.objects.get(pk=comment.pk)
        [reply] = comment.get_children()
        self.assertEqual(reply.comment, 'test reply text')
        self.assertRedirects(
            response, '%s?c=%d' % (
                reverse('admin:commenting_molocomment_changelist'),
                reply.pk),
            target_status_code=302)

    def test_reply_to_comment_ignore_fields(self):
        '''The form for replying to the comment should ignore certain fields
        in the request, and instead set them using user information.'''
        comment = self.mk_comment('comment')
        formview = self.client.get(
            reverse('admin:commenting_molocomment_reply', kwargs={
                'parent': comment.pk,
            }))

        html = BeautifulSoup(formview.content, 'html.parser')
        data = {
            i.get('name'): i.get('value') or ''
            for i in html.form.find_all('input') if i.get('name')
        }
        data['comment'] = 'test reply text'
        data['name'] = 'foo'
        data['url'] = 'http://bar.org'
        data['email'] = 'foo@bar.org'

        self.client.post(
            reverse('admin:commenting_molocomment_reply', kwargs={
                'parent': comment.pk,
            }), data=data)
        comment = MoloComment.objects.get(pk=comment.pk)
        [reply] = comment.get_children()

        self.assertEqual(reply.user_name, 'testadmin')
        self.assertEqual(reply.user_email, 'testadmin@example.org')
        self.assertEqual(reply.user_url, '')

    def test_canned_response_appears_in_reply_template(self):
        comment = self.mk_comment('comment')

        canned_response = CannedResponse.objects.create(
            response_header='Test Canned Response',
            response='Canned response text'
        )

        formview = self.client.get(
            reverse('admin:commenting_molocomment_reply', kwargs={
                'parent': comment.pk,
            }))

        html = BeautifulSoup(formview.content, 'html.parser')

        selects = html.form.find_all('select')

        self.assertEqual(1, len(selects))

        self.assertEqual('canned_response', selects[0].get('name'))

        options = selects[0].find_all('option')

        self.assertEqual(2, len(options))
        self.assertEqual(canned_response.response_header,
                         options[1].contents[0])
        self.assertEqual(canned_response.response, options[1]['value'])

    def test_admin_can_duplicate_replies(self):
        comment = self.mk_comment('comment')

        formview = self.client.get(
            reverse('admin:commenting_molocomment_reply', kwargs={
                'parent': comment.pk,
            }))

        html = BeautifulSoup(formview.content, 'html.parser')
        data = {
            i.get('name'): i.get('value') or ''
            for i in html.form.find_all('input') if i.get('name')
        }
        data['comment'] = 'test duplication'

        self.client.post(
            reverse('admin:commenting_molocomment_reply', kwargs={
                'parent': comment.pk,
            }), data=data)

        self.client.post(
            reverse('admin:commenting_molocomment_reply', kwargs={
                'parent': comment.pk,
            }), data=data)

        changelist = self.client.get(
            reverse('admin:commenting_molocomment_changelist'))

        self.assertContains(changelist, 'test duplication', count=2)


class TestMoloCommentsAdminViews(TestCase, MoloTestCaseMixin):
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

        self.mk_main2()
        self.main2 = Main.objects.all().last()
        self.language_setting2 = Languages.objects.create(
            site_id=self.main2.get_site().pk)
        self.english2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='en',
            is_active=True)
        self.french2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='fr',
            is_active=True)
        self.yourmind2 = self.mk_section(
            self.section_index2, title='Your mind2')
        self.article2 = self.mk_article(
            title='article 2', slug='article-2', parent=self.yourmind2,
            subtitle='article 2 subtitle')

        self.mk_main2(title='main3', slug='main3', path=00010003)
        self.client2 = Client(HTTP_HOST=self.main2.get_site().hostname)

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

    def test_correct_comment_appears_in_admin_view(self):
        comment1 = self.mk_comment('the comment')
        comment2 = MoloComment.objects.create(
            content_type=self.content_type,
            object_pk=self.article2.pk,
            content_object=self.article2,
            site=Site.objects.first(),
            user=self.user,
            comment='second site comment',
            parent=None,
            submit_date=datetime.now())
        response = self.client.get(
            '/admin/commenting/molocomment/'
        )
        self.assertContains(response, comment1.comment)
        self.assertNotContains(response, comment2.comment)

        User.objects.create_superuser(
            username='superuser2', password='password2',
            email='super2@email.com', is_staff=True)
        self.client2.login(username='superuser2', password='password2')
        response = self.client2.get(
            self.site2.root_url + '/admin/commenting/molocomment/')
        self.assertNotContains(response, comment1.comment)
        self.assertContains(response, comment2.comment)

    def test_canned_response_appears_in_canned_responses_admin_view(self):
        canned_response = CannedResponse.objects.create(
            response_header='Test Canned Response',
            response='Canned response text'
        )

        response = self.client.get(
            '/admin/commenting/cannedresponse/'
        )

        self.assertContains(response, canned_response.response_header)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_download_csv_per_site_redirects(self):
        self.mk_comment('export comment')
        MoloComment.objects.create(
            content_type=self.content_type,
            object_pk=self.article2.pk,
            content_object=self.article2,
            site=Site.objects.first(),
            user=self.user,
            comment='second site comment',
            parent=None,
            submit_date=datetime.now())
        response = self.client.post(
            '/admin/commenting/molocomment/'
        )

        # substitute the datetime component to avoid intermittent test failures
        # due to crossing a second boundary
        response.content = re.sub('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
                                  'datetime',
                                  response.content)

        self.assertEquals(response.status_code, 302)

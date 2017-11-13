from bs4 import BeautifulSoup
from datetime import datetime

from django.conf.urls import patterns, url, include
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import Group

from molo.commenting.models import MoloComment
from molo.commenting.forms import MoloCommentForm
from molo.core.models import SiteLanguageRelation, Languages, Main
from molo.core.tests.base import MoloTestCaseMixin

from notifications.models import Notification

urlpatterns = patterns(
    '',
    url(r'^commenting/',
        include('molo.commenting.urls', namespace='molo.commenting')),
    url(r'', include('django_comments.urls')),
    url(r'', include('molo.core.urls')),
    url(r'', include('wagtail.wagtailcore.urls')),
)


@override_settings(ROOT_URLCONF='molo.commenting.tests.test_views')
class ViewsTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        # Creates main page
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
        self.client = Client()
        self.client.login(username='test', password='test')
        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.article1 = self.mk_article(
            title='article 1', slug='article-1', parent=self.yourmind)

    def mk_comment(self, comment):
        return MoloComment.objects.create(
            content_type=self.content_type,
            object_pk=self.user.pk,
            content_object=self.user,
            site=Site.objects.get_current(),
            user=self.user,
            comment=comment,
            submit_date=datetime.now())

    def test_reporting_without_removal(self):
        comment = self.mk_comment('the comment')
        response = self.client.get(
            reverse('molo.commenting:molo-comments-report',
                    args=(comment.pk,)))
        self.assertEqual(response.status_code, 302)
        [flag] = comment.flags.all()
        self.assertEqual(flag.comment, comment)
        self.assertEqual(flag.user, self.user)
        self.assertFalse(MoloComment.objects.get(pk=comment.pk).is_removed)
        self.assertTrue('The comment has been reported.'
                        in response.cookies['messages'].value)

    def test_reporting_with_removal(self):
        comment = self.mk_comment('the comment')
        with self.settings(COMMENTS_FLAG_THRESHHOLD=1):
            response = self.client.get(
                reverse('molo.commenting:molo-comments-report',
                        args=(comment.pk,)))
        self.assertEqual(response.status_code, 302)
        [flag] = comment.flags.all()
        self.assertEqual(flag.comment, comment)
        self.assertEqual(flag.user, self.user)
        self.assertTrue(MoloComment.objects.get(pk=comment.pk).is_removed)
        self.assertTrue('The comment has been reported.'
                        in response.cookies['messages'].value)

    def test_molo_post_comment(self):
        data = MoloCommentForm(self.user, {}).generate_security_data()
        data.update({
            'name': 'the supplied name',
            'comment': 'Foo',
        })
        self.client.post(
            reverse('molo.commenting:molo-comments-post'), data)
        [comment] = MoloComment.objects.filter(user=self.user)
        self.assertEqual(comment.comment, 'Foo')
        self.assertEqual(comment.user_name, 'the supplied name')

    def test_molo_post_comment_anonymous(self):
        data = MoloCommentForm(self.user, {}).generate_security_data()
        data.update({
            'name': 'the supplied name',
            'comment': 'Foo',
            'submit_anonymously': '1',
        })
        self.client.post(
            reverse('molo.commenting:molo-comments-post'), data)
        [comment] = MoloComment.objects.filter(user=self.user)
        self.assertEqual(comment.comment, 'Foo')
        self.assertEqual(comment.user_name, 'Anonymous')
        self.assertEqual(comment.user_email, self.user.email)

    def test_molo_post_comment_without_email_address(self):
        self.user.email = ''
        self.user.save()

        data = MoloCommentForm(self.user, {}).generate_security_data()
        data.update({
            'name': 'the supplied name',
            'comment': 'Foo',
        })
        self.client.post(
            reverse('molo.commenting:molo-comments-post'), data)
        [comment] = MoloComment.objects.filter(user=self.user)
        self.assertEqual(comment.comment, 'Foo')
        self.assertEqual(comment.user_name, 'the supplied name')
        self.assertEqual(comment.user_email, 'blank@email.com')

    def test_report_response(self):
        article = self.article1
        comment = MoloComment.objects.create(
            content_object=article, object_pk=article.id,
            content_type=ContentType.objects.get_for_model(article),
            site=Site.objects.get_current(), user=self.user,
            comment='comment 1', submit_date=datetime.now())
        response = self.client.get(reverse('molo.commenting:report_response',
                                   args=(comment.id,)))
        self.assertContains(
            response,
            "This comment has been reported."
        )

    def test_commenting_closed(self):
        article = self.article1
        article.save()
        initial = {
            'object_pk': article.id,
            'content_type': "core.articlepage"
        }
        data = MoloCommentForm(article, {},
                               initial=initial).generate_security_data()
        data.update({
            'comment': "This is another comment"
        })
        response = self.client.post(
            reverse('molo.commenting:molo-comments-post'), data)
        self.assertEqual(response.status_code, 302)

    def test_commenting_open(self):
        article = self.article1
        initial = {
            'object_pk': article.id,
            'content_type': "core.articlepage"
        }
        data = MoloCommentForm(article, {},
                               initial=initial).generate_security_data()
        data.update({
            'comment': "This is a second comment",
        })
        response = self.client.post(
            reverse('molo.commenting:molo-comments-post'), data)
        self.assertEqual(response.status_code, 302)


@override_settings(ROOT_URLCONF='molo.commenting.tests.test_views')
class ViewMoreCommentsTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        # Creates main page
        self.mk_main()
        self.user = User.objects.create_user(
            'test', 'test@example.org', 'test')
        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.article = self.mk_article(
            title='article 1', slug='article-1', parent=self.yourmind)

        self.client = Client()

    def create_comment(self, comment, parent=None, user=None):
        commenter = user or self.user
        return MoloComment.objects.create(
            content_type=ContentType.objects.get_for_model(self.article),
            object_pk=self.article.pk,
            content_object=self.article,
            site=Site.objects.get_current(),
            user=commenter,
            comment=comment,
            parent=parent,
            submit_date=datetime.now())

    def test_view_more_comments(self):
        for i in range(50):
            self.create_comment('comment %d' % i)
        response = self.client.get(
            reverse('molo.commenting:more-comments',
                    args=[self.article.pk, ],))
        self.assertContains(response, 'Page 1 of 3')
        self.assertContains(response, '&rarr;')
        self.assertNotContains(response, '&larr;')

        response = self.client.get('%s?p=2' % (reverse(
            'molo.commenting:more-comments', args=[self.article.pk, ],),))
        self.assertContains(response, 'Page 2 of 3')
        self.assertContains(response, '&rarr;')
        self.assertContains(response, '&larr;')

        response = self.client.get('%s?p=3' % (reverse(
            'molo.commenting:more-comments', args=[self.article.pk, ],),))
        self.assertContains(response, 'Page 3 of 3')
        self.assertNotContains(response, '&rarr;')
        self.assertContains(response, '&larr;')

    def test_view_page_not_integer(self):
        '''If the requested page number is not an integer, the first page
        should be returned.'''
        response = self.client.get('%s?p=foo' % reverse(
            'molo.commenting:more-comments', args=(self.article.pk,)))
        self.assertContains(response, 'Page 1 of 1')

    def test_view_empty_page(self):
        '''If the requested page number is too large, it should show the
        last page.'''
        for i in range(40):
            self.create_comment('comment %d' % i)
        response = self.client.get('%s?p=3' % reverse(
            'molo.commenting:more-comments', args=(self.article.pk,)))
        self.assertContains(response, 'Page 2 of 2')

    def test_view_nested_comments(self):
        comment1 = self.create_comment('test comment1 text')
        comment2 = self.create_comment('test comment2 text')
        comment3 = self.create_comment('test comment3 text')
        reply1 = self.create_comment('test reply1 text', parent=comment2)
        reply2 = self.create_comment('test reply2 text', parent=comment2)
        response = self.client.get(
            reverse('molo.commenting:more-comments', args=(self.article.pk,)))

        html = BeautifulSoup(response.content, 'html.parser')
        [c3row, c2row, reply1row, reply2row, c1row] = html.find_all(
            class_='comment-list__item')
        self.assertTrue(comment3.comment in c3row.prettify())
        self.assertTrue(comment2.comment in c2row.prettify())
        self.assertTrue(reply1.comment in reply1row.prettify())
        self.assertTrue(reply2.comment in reply2row.prettify())
        self.assertTrue(comment1.comment in c1row.prettify())

    def test_view_replies_report(self):
        '''If a comment is a reply, there should only be a report button
        if the reply is not made by an admin'''
        comment = self.create_comment('test comment1 text')
        reply = self.create_comment('test reply text', parent=comment)

        response = self.client.get(
            reverse('molo.commenting:more-comments', args=(self.article.pk,)))

        html = BeautifulSoup(response.content, 'html.parser')
        [crow, replyrow] = html.find_all(class_='comment-list__item')
        self.assertTrue(comment.comment in crow.prettify())
        self.assertTrue('report' in crow.prettify())
        self.assertTrue(reply.comment in replyrow.prettify())
        self.assertTrue('report' in replyrow.prettify())

        comment2 = self.create_comment('test comment2 text')
        superuser = User.objects.create_superuser(
            username='superuser',
            email='superuser@email.com',
            password='password'
        )
        reply2 = self.create_comment('test reply2 text',
                                     parent=comment2,
                                     user=superuser)

        response = self.client.get(
            reverse('molo.commenting:more-comments', args=(self.article.pk,)))
        html = BeautifulSoup(response.content, 'html.parser')
        [crow2, replyrow2, crow, replyrow] = html.find_all(
            class_='comment-list__item')
        self.assertTrue(comment2.comment in crow2.prettify())
        self.assertTrue('report' in crow2.prettify())
        self.assertTrue(reply2.comment in replyrow2.prettify())
        self.assertFalse('report' in replyrow2.prettify())


class TestFrontEndCommentReplies(TestCase, MoloTestCaseMixin):

    def create_comment(self, article, comment, user, parent=None):
        return MoloComment.objects.create(
            content_type=ContentType.objects.get_for_model(article),
            object_pk=article.pk,
            content_object=article,
            site=Site.objects.get_current(),
            user=user,
            comment=comment,
            parent=parent,
            submit_date=datetime.now())

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.client = Client()

        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='superuser@email.com',
            password='password'
        )

        self.moderator_group, _created = Group.objects.get_or_create(
            name='Moderator')
        self.comment_moderator_group, _created = Group.objects.get_or_create(
            name='Comment Moderator')
        self.expert_group, _created = Group.objects.get_or_create(
            name='Expert')

        self.moderator = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='password',
        )
        self.moderator.groups.set([self.moderator_group])

        self.comment_moderator = User.objects.create_user(
            username='comment_moderator',
            email='comment_moderator@example.com',
            password='password',
        )
        self.comment_moderator.groups.set([self.comment_moderator_group])

        self.expert = User.objects.create_user(
            username='expert',
            email='expert@example.com',
            password='password',
        )
        self.expert.groups.set([self.expert_group])

        # create ordinary user
        self.bob = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='password',
        )

        self.section = self.mk_section(
            self.section_index, title='section')
        self.article = self.mk_article(self.section, title='article 1',
                                       subtitle='article 1 subtitle',
                                       slug='article-1')
        self.comment = self.create_comment(
            article=self.article,
            comment="this_is_comment_content",
            user=self.bob
        )

    def check_reply_exists(self, client):
        response = client.get(
            reverse('molo.commenting:more-comments',
                    args=[self.article.pk, ],))
        self.assertTrue(response.status_code, 200)

        html = BeautifulSoup(response.content, 'html.parser')
        [comment] = html.find_all(class_='comment-list__item')
        self.assertTrue(comment.find('p', string='this_is_comment_content'))
        self.assertTrue(comment.find('a', string='Reply'))

        comment_reply_url = comment.find('a', string='Reply')['href']

        response = self.client.get(comment_reply_url)
        self.assertTrue(response.status_code, 200)

    def test_expert_can_reply_to_comments_on_front_end(self):
        client = Client()
        client.login(
            username=self.expert.username, password='password')
        self.check_reply_exists(client)

    def test_moderator_can_reply_to_comments_on_front_end(self):
        client = Client()
        client.login(
            username=self.moderator.username, password='password')
        self.check_reply_exists(client)

    def test_comment_moderator_can_reply_to_comments_on_front_end(self):
        client = Client()
        client.login(
            username=self.comment_moderator.username, password='password')
        self.check_reply_exists(client)

    def test_superuser_can_reply_to_comments_on_front_end(self):
        client = Client()
        client.login(
            username=self.superuser.username, password='password')
        self.check_reply_exists(client)

    def test_ordinary_user_can_reply_to_comments_on_front_end(self):
        client = Client()
        client.login(
            username=self.bob.username, password='password')
        self.check_reply_exists(client)

    def test_user_cannot_reply_to_comments_when_logged_out(self):
        response = self.client.get(
            reverse('molo.commenting:more-comments',
                    args=[self.article.pk, ],))

        self.assertTrue(response.status_code, 200)
        html = BeautifulSoup(response.content, 'html.parser')
        [comment] = html.find_all(class_='comment-list__item')
        self.assertTrue(comment.find('p', string='this_is_comment_content'))
        self.assertFalse(comment.find('a', string='Reply'))


class TestThreadedComments(TestCase, MoloTestCaseMixin):

    def setUp(self):
        # Creates main page
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

        self.section = self.mk_section(
            self.section_index, title='section')
        self.article = self.mk_article(self.section, title='article 1',
                                       subtitle='article 1 subtitle',
                                       slug='article-1')

        self.client = Client()

    def create_comment(self, comment, parent=None, user=None):
        commenter = user or self.user
        return MoloComment.objects.create(
            content_type=ContentType.objects.get_for_model(self.article),
            object_pk=self.article.pk,
            content_object=self.article,
            site=Site.objects.get_current(),
            user=commenter,
            comment=comment,
            parent=parent,
            submit_date=datetime.now())

    def test_restrict_article_comment_count(self):
        for i in range(3):
            self.create_comment('comment %d' % i)

        response = self.client.get(self.article.url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "comment 2")
        self.assertContains(response, "comment 1")
        self.assertNotContains(response, "comment 0")

    def test_restrict_article_comment_reply_count(self):
        comment = self.create_comment('Original Comment')
        for i in range(3):
            self.create_comment('reply %d' % i, parent=comment)
        response = self.client.get(self.article.url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Original Comment")
        self.assertContains(response, "reply 2")
        self.assertContains(response, "reply 1")
        self.assertNotContains(response, "reply 0")

    def test_restrict_article_comment_reply_truncation(self):
        comment = self.create_comment('Original Comment')
        comment_text = "Lorem ipsum dolor sit amet, consectetur adipisicing \
            tempor incididunt ut labore et dolore magna aliqua. Ut enim ad \
            quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea \
            consequat. Duis aute irure dolor in reprehenderit in voluptate \
            cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat \
            proident, sunt in culpa qui officia deserunt mollit anim id est"
        self.create_comment(comment_text, parent=comment)

        response = self.client.get(self.article.url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Original Comment")
        truncated_text = "Lorem ipsum dolor sit amet, consectetur adipisicing"
        self.assertContains(response, truncated_text)
        self.assertNotContains(response, "officia deserunt mollit anim id est")

    def test_comment_reply_list(self):
        comment = self.create_comment('Original Comment')

        for i in range(3):
            self.create_comment('Reply %d' % i, parent=comment)

        response = self.client.get(
            reverse('molo.commenting:molo-comments-reply',
                    args=(comment.pk, )))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Original Comment')
        self.assertContains(response, 'Reply 0')
        self.assertContains(response, 'Reply 1')
        self.assertContains(response, 'Reply 2')

    def test_reply_pagination(self):
        comment = self.create_comment('Original Comment')
        for i in range(15):
            self.create_comment('Reply %d' % i, parent=comment)

        response = self.client.get(
            reverse('molo.commenting:molo-comments-reply',
                    args=[comment.pk, ],))

        self.assertContains(response, 'Original Comment')
        self.assertContains(response, 'Page 1 of 3')
        self.assertContains(response, '&rarr;')
        self.assertNotContains(response, '&larr;')

        response = self.client.get('%s?p=2' % (reverse(
            'molo.commenting:molo-comments-reply',
            args=[comment.pk, ],),))
        self.assertContains(response, 'Page 2 of 3')
        self.assertContains(response, '&rarr;')
        self.assertContains(response, '&larr;')

        response = self.client.get('%s?p=3' % (reverse(
            'molo.commenting:molo-comments-reply',
            args=[comment.pk, ],),))
        self.assertContains(response, 'Page 3 of 3')
        self.assertNotContains(response, '&rarr;')
        self.assertContains(response, '&larr;')


@override_settings(ROOT_URLCONF='molo.commenting.tests.test_views')
class ViewNotificationsRepliesOnCommentsTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        # Creates main page
        self.mk_main()
        self.user = User.objects.create_user(
            'test', 'test@example.org', 'test')

        self.section = self.mk_section(
            self.section_index, title='section')
        self.article = self.mk_article(self.section, title='article 1',
                                       subtitle='article 1 subtitle',
                                       slug='article-1')

        self.client = Client()
        self.client.login(username='test', password='test')

    def create_comment(self, comment, parent=None):
        return MoloComment.objects.create(
            content_type=ContentType.objects.get_for_model(self.article),
            object_pk=self.article.pk,
            content_object=self.article,
            site=Site.objects.get_current(),
            user=self.user,
            comment=comment,
            parent=parent,
            submit_date=datetime.now())

    def test_notification_reply_list(self):
        self.client = Client()
        self.client.login(username='test', password='test')

        data = MoloCommentForm(self.user, {}).generate_security_data()
        data.update({
            'name': 'the supplied name',
            'comment': 'Foo',
        })
        self.client.post(
            reverse('molo.commenting:molo-comments-post'), data)
        [comment] = MoloComment.objects.filter(user=self.user)
        self.assertEqual(comment.comment, 'Foo')
        self.assertEqual(comment.user_name, 'the supplied name')

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Unread replies: 0')

        data = MoloCommentForm(self.user, {}).generate_security_data()
        data.update({
            'name': 'the supplied name',
            'comment': 'Foo reply',
            'parent': comment.pk
        })
        self.client.post(
            reverse('molo.commenting:molo-comments-post'), data)
        self.assertEqual(Notification.objects.unread().count(), 1)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = BeautifulSoup(response.content, 'html.parser')
        [ntfy] = html.find_all("div", class_='reply-notification')
        self.assertEqual(ntfy.find("p").get_text().strip(),
                         'You have 1 unread replies')

        # Unread notifications
        response = self.client.get(
            reverse('molo.commenting:reply_list'))
        self.assertContains(response, 'You have 1 unread replies')
        n = Notification.objects.filter(recipient=self.user).first()
        n.mark_as_read()
        self.assertEqual(Notification.objects.unread().count(), 0)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Unread replies: 0')

        # Read notifications
        response = self.client.get(
            reverse('molo.commenting:reply_list'))
        self.assertEqual(Notification.objects.read().count(), 1)
        self.assertNotContains(response, 'You have 0 unread replies')
        self.assertContains(response, 'Read')

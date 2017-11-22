from bs4 import BeautifulSoup

from django.core.urlresolvers import reverse

from molo.core.models import (
    Main,
    SectionIndexPage,
    SectionPage,
)

from molo.yourwords.tests.base import BaseYourWordsTestCase
from molo.yourwords.models import (
    YourWordsCompetition,
    YourWordsCompetitionEntry,
)


class TestYourWordsViewsTestCase(BaseYourWordsTestCase):

    def test_yourwords_competition_page(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description',
            slug='test-competition')
        self.competition_index.add_child(instance=comp)
        comp.save_revision().publish()
        self.competition_index.save()

        comp = YourWordsCompetition.objects.get(slug='test-competition')

        response = self.client.get(comp.url)
        self.assertContains(response, 'Test Competition')
        self.assertContains(response, 'This is the description')

    def test_translated_yourwords_competition_page_exists_section(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        section = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='test-section',
            slug='test-section',
        )

        comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description',
            slug='test-competition')

        section.add_child(instance=comp)
        comp.save_revision().publish()

        self.client.post(reverse(
            'add_translation', args=[comp.id, 'fr']))
        page = YourWordsCompetition.objects.get(
            slug='french-translation-of-test-competition')
        page.save_revision().publish()

        response = self.client.get(section.url)
        self.assertContains(response, 'Test Competition')
        self.assertContains(response, 'This is the description')

        response = self.client.get('/')
        self.assertContains(response, 'Test Competition')
        self.assertContains(response, 'This is the description')

        self.client.get('/locale/fr/')

        response = self.client.get(section.url)
        self.assertContains(response, page.title)

        response = self.client.get('/')
        self.assertContains(response, page.title)

    def test_yourwords_validation_for_fields(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description',
            slug='test-competition')
        self.competition_index.add_child(instance=comp)
        comp.save_revision().publish()

        comp = YourWordsCompetition.objects.get(slug='test-competition')

        self.client.get(
            reverse('molo.yourwords:competition_entry', args=[comp.slug]))

        response = self.client.post(
            reverse('molo.yourwords:competition_entry', args=[comp.slug]), {})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'This field is required')

        response = self.client.post(
            reverse('molo.yourwords:competition_entry', args=[comp.slug]),
            {'story_name': 'this is a story'})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'This field is required')

        response = self.client.post(
            reverse('molo.yourwords:competition_entry', args=[comp.slug]),
            {'story_name': 'This is a story', 'story_text': 'The text'})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'This field is required')

        response = self.client.post(
            reverse('molo.yourwords:competition_entry', args=[comp.slug]), {
                'story_name': 'This is a story',
                'story_text': 'The text',
                'terms_or_conditions_approved': 'true'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(YourWordsCompetitionEntry.objects.all().count(), 1)

        response = self.client.post(
            reverse('molo.yourwords:competition_entry', args=[comp.slug]), {
                'story_name': 'This is a story',
                'story_text': 'The text',
                'terms_or_conditions_approved': 'true',
                'hide_real_name': 'true'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(YourWordsCompetitionEntry.objects.all().count(), 2)

    def test_yourwords_thank_you_page(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description',
            slug='test-competition')
        self.competition_index.add_child(instance=comp)
        comp.save_revision().publish()

        response = self.client.post(
            reverse('molo.yourwords:competition_entry', args=[comp.slug]), {
                'story_name': 'This is a story',
                'story_text': 'The text',
                'terms_or_conditions_approved': 'true'})
        self.assertEqual(
            response['Location'],
            '/yourwords/thankyou/test-competition/')

    def test_translated_yourwords_competition_page_exists(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description',
            slug='test-competition')
        self.competition_index.add_child(instance=comp)
        comp.save_revision().publish()

        self.client.post(reverse(
            'add_translation', args=[comp.id, 'fr']))
        page = YourWordsCompetition.objects.get(
            slug='french-translation-of-test-competition')
        page.save_revision().publish()

        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.competition_index.id]))
        page = YourWordsCompetition.objects.get(
            slug='french-translation-of-test-competition')
        self.assertContains(response,
                            '<a href="/admin/pages/%s/edit/"'
                            % page.id)

    def test_competition_multisite(self):
        section = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='test-section',
            slug='test-section',
        )

        comp = YourWordsCompetition(
            title='Test Competition Main1',
            description='This is the description')
        section.add_child(instance=comp)
        comp.save_revision().publish()

        section_main2 = self.mk_section(
            SectionIndexPage.objects.child_of(self.main2).first(),
            title='test-section',
            slug='test-section',
        )
        comp_main2 = YourWordsCompetition(
            title='Test Competition Main2',
            description='This is the description')
        section_main2.add_child(instance=comp_main2)
        comp_main2.save_revision().publish()

        self.assertEquals(2, SectionPage.objects.count())

        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )
        response = self.client.get(section.url)
        self.assertContains(response, 'Test Competition Main1')
        self.assertNotContains(response, 'Test Competition Main2')

        self.client2.login(
            username=self.superuser_name,
            password=self.superuser_password
        )
        response = self.client2.get(section_main2.url)

        self.assertContains(response, 'Test Competition Main2')
        self.assertNotContains(response, 'Test Competition Main1')

    def test_translated_competition_entry_stored_against_the_main_lang(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        en_comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description',
            slug='test-competition')
        self.competition_index.add_child(instance=en_comp)
        en_comp.save_revision().publish()

        self.client.post(reverse(
            'add_translation', args=[en_comp.id, 'fr']))
        fr_comp = YourWordsCompetition.objects.get(
            slug='french-translation-of-test-competition')
        fr_comp.save_revision().publish()

        self.client.post(
            reverse('molo.yourwords:competition_entry', args=[fr_comp.slug]), {
                'story_name': 'this is a french story',
                'story_text': 'The text',
                'terms_or_conditions_approved': 'true'})

        entry = YourWordsCompetitionEntry.objects.all().first()
        self.assertEqual(entry.story_name, 'this is a french story')
        self.assertEqual(entry.competition.id, en_comp.id)

    def test_yourwords_wagtail_competition_view(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description')
        self.competition_index.add_child(instance=comp)
        comp.save_revision().publish()

        response = self.client.get(
            '/admin/yourwords/yourwordscompetition/'
        )

        self.assertContains(response, comp.title)

    def test_yourwords_wagtail_multisite_competition_view(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        self.client2.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        comp = YourWordsCompetition(
            title='Test Competition Main1',
            description='This is the description')
        self.competition_index.add_child(instance=comp)
        comp.save_revision().publish()

        comp_main2 = YourWordsCompetition(
            title='Test Competition Main2',
            description='This is the description')
        self.competition_index_main2.add_child(instance=comp_main2)
        comp_main2.save_revision().publish()

        response = self.client.get(
            '/admin/yourwords/yourwordscompetition/'
        )

        self.assertContains(response, comp.title)
        self.assertNotContains(response, comp_main2.title)

        response = self.client2.get(
            '/admin/yourwords/yourwordscompetition/'
        )

        self.assertNotContains(response, comp.title)
        self.assertContains(response, comp_main2.title)

    def test_yourwords_wagtail_entries_view(self):

        comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description')
        self.competition_index.add_child(instance=comp)
        comp.save_revision().publish()

        YourWordsCompetitionEntry.objects.create(
            competition=comp,
            user=self.user,
            story_name='test',
            story_text='test body',
            terms_or_conditions_approved=True,
            hide_real_name=True
        )

        entry = YourWordsCompetitionEntry.objects.all().first()

        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        response = self.client.get(
            '/admin/yourwords/yourwordscompetitionentry/'
        )

        self.assertContains(response, entry.story_name)

    def test_yourwords_multisite_wagtail_entries_view(self):

        comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description')
        self.competition_index.add_child(instance=comp)
        comp.save_revision().publish()

        comp_main2 = YourWordsCompetition(
            title='Test Competition Main2',
            description='This is the description')
        self.competition_index_main2.add_child(instance=comp_main2)
        comp_main2.save_revision().publish()

        YourWordsCompetitionEntry.objects.create(
            competition=comp,
            user=self.user,
            story_name='test main1',
            story_text='test body main1',
            terms_or_conditions_approved=True,
            hide_real_name=True
        )
        entry_main1 = YourWordsCompetitionEntry.objects.all().first()

        YourWordsCompetitionEntry.objects.create(
            competition=comp_main2,
            user=self.user,
            story_name='test main2',
            story_text='test body main2',
            terms_or_conditions_approved=True,
            hide_real_name=True
        )
        entry_main2 = YourWordsCompetitionEntry.objects.all().last()

        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        response = self.client.get(
            '/admin/yourwords/yourwordscompetitionentry/'
        )

        self.assertContains(response, entry_main1.story_name)
        self.assertNotContains(response, entry_main2.story_name)

        self.client2.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        response = self.client2.get(
            '/admin/yourwords/yourwordscompetitionentry/'
        )
        self.assertContains(response, entry_main2.story_name)
        self.assertNotContains(response, entry_main1.story_name)


class TestDeleteButtonRemoved(BaseYourWordsTestCase):

    def test_delete_btn_removed_for_yr_wrds_comp_index_page_in_main(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        main_page = Main.objects.first()
        response = self.client.get('/admin/pages/{0}/'
                                   .format(str(main_page.pk)))
        self.assertEquals(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        index_page_rows = soup.find_all('tbody')[0].find_all('tr')

        for row in index_page_rows:
            if row.h2.a.string == self.competition_index.title:
                self.assertTrue(row.find('a', string='Edit'))
                self.assertFalse(row.find('a', string='Delete'))

    def test_delete_button_removed_from_dropdown_menu(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        response = self.client.get('/admin/pages/{0}/'
                                   .format(str(self.competition_index.pk)))
        self.assertEquals(response.status_code, 200)

        delete_link = ('<a href="/admin/pages/{0}/delete/" '
                       'title="Delete this page" class="u-link '
                       'is-live ">Delete</a>'
                       .format(str(self.competition_index.pk)))
        self.assertNotContains(response, delete_link, html=True)

    def test_delete_button_removed_in_edit_menu(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        response = self.client.get('/admin/pages/{0}/edit/'
                                   .format(str(self.competition_index.pk)))
        self.assertEquals(response.status_code, 200)

        delete_button = ('<li><a href="/admin/pages/{0}/delete/" '
                         'class="shortcut">Delete</a></li>'
                         .format(str(self.competition_index.pk)))
        self.assertNotContains(response, delete_button, html=True)

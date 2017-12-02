import warnings

from trunity_migrator import settings
from trunity_migrator.trunity_2_client import Client as Trunity2Client
from trunity_migrator.fixers import *
from trunity_migrator.html_fixer import HTMLFixer
from trunity_migrator.glossary import Glossary
from trunity_migrator.questionnaires.uploaders import upload_question_pool
from trunity_migrator.self_assessments.uploaders import upload_self_assessment

from trunity_3_client import (
    initialize_session_from_creds,
    TopicsClient,
    ContentsClient,
    ContentType,
    ResourceType,
    SitesClient,
    SiteType,
    TermsClient,
)


CONTENT_TYPES = [  # TODO: make global settings object
    "article",
    "questionpool",
    # "exam"
    # "news",
    "video",
    # "podcast",
    # "gallery",
    "game",
    # "assignment",
    # "whitepaper",
    # "casestudy",
    # "presentation",
    # "lecture",
    # "exercise",
    # "teachingunit",
]


class RootTopicIdError(IOError):
    """
    Raise when can't find root topic in Trunity 2
    """
    pass


class Vertex(object):

    def __init__(self, uploaded_topic_id, join):
        self.uploaded_topic_id = uploaded_topic_id
        self.join = join


class Migrator(object):

    def __init__(self, trunity_2_login, trunity_2_password,
                 trunity_3_login, trunity_3_password,
                 t2_book_title, t3_book_title,
                 html_fixer: HTMLFixer=None):

        self._t2_client = Trunity2Client(
            trunity_2_login, trunity_2_password
        )

        self._t3_session = initialize_session_from_creds(
            trunity_3_login, trunity_3_password
        )
        self._t3_json_session = initialize_session_from_creds(
            trunity_3_login, trunity_3_password,
            content_type='application/json'
        )
        self._topics_client = TopicsClient(self._t3_session)
        self._contents_client = ContentsClient(self._t3_session)

        self._t3_site_id = self._create_new_site(t3_book_title)

        self._t2_root_topic_id, self._t2_site_id = \
            self._get_trunity_2_site_info(t2_book_title)

        self._queue = []

        self._html_fixer = html_fixer

        self._glossary = Glossary(
            self._t3_site_id,
            self._t3_session
        )

        self._t3_terms_client = TermsClient(self._t3_session)

        self._no_definition_terms = []

    def print_no_definition_terms(self):
        print()
        print("\t\t TERMS WITHOUT DEFINITIONS")

        for term_list, article in self._no_definition_terms:
            print('--> ', ', '.join(term_list), ' in ', article)

    def _create_new_site(self, title: str):
        """
        Create new book (site) on Trunity 3 and return site_id.
        :param title:
        :return: site_id
        """
        print("Creating new book: {}".format(title), end='')

        sites_client = SitesClient(self._t3_session)
        site_id = sites_client.list.post(
            name=title,
            site_type=SiteType.TEXTBOOK,
            description=''
        )

        # TODO: make description argument optional.

        print('\t\t[SUCCESS!]')
        return site_id

    def _get_trunity_2_site_info(self, site_name):
        """
        Returns root_topic_id and site_id.
        :param site_name:
        :return:
        """
        sites = self._t2_client.get_user_sites('All')
        for site in sites:
            if site['name'] == site_name:
                return site['rootTopic'], site['siteId']

        raise RootTopicIdError(
            "Can't retrieve Trunity 2 book info by book name!"
        )

    def _upload_glossary_terms(self, article_title, article_body):
        article_body = self._glossary.fix_tags(html=article_body)

        # track glossary terms without definitions:
        if self._glossary.no_definition_terms:
            self._no_definition_terms.append([
                self._glossary.no_definition_terms,
                article_title
            ])
            del self._glossary.no_definition_terms
        return article_body

    def upload_article(self, join, topic_id=None):
        title = join['title']
        body = join['body']

        print("Uploading Article: {}".format(title), end='')

        if self._html_fixer:
            body = self._html_fixer.apply(body)

        body = self._upload_glossary_terms(title, body)

        content_id = self._contents_client.list.post(
            site_id=self._t3_site_id,
            content_title=title,
            content_type=ContentType.ARTICLE,
            text=body,
            topic_id=topic_id,
        )

        # update tmp content terms:
        uploaded_term_ids = self._glossary.uploaded_term_ids

        # TODO: move this to Glossary class:
        for term_id in uploaded_term_ids:
            try:
                self._t3_terms_client.update_tmp_content_term.put(
                    tmp_content_term_id=term_id,
                    content_id=content_id,
                    content_type='articles'
                )
            except KeyError:
                print("[Warning] Trunity API can't accept temp content term!")

        print('\t\t[SUCCESS!]')

    def upload_question_pool(self, join, topic_id=None):
        title = join['title']
        description = join['body']

        print("Uploading Question Pool: {}".format(title))

        t2_question_pool = self._t2_client.get_content(
            site_id=self._t2_site_id,
            content_id=join['_id']
        )

        content_id = self._contents_client.list.post(
            site_id=self._t3_site_id,
            content_title=title,
            content_type=ContentType.QUESTIONNAIRE,
            text=description,
            topic_id=topic_id,
            resource_type=ResourceType.QUESTION_POOL,
        )

        questions = t2_question_pool['content']['questions']

        upload_question_pool(
            session=self._t3_json_session,
            questionnaire_id=content_id,
            t2_questions=questions
        )

    def upload_self_assessment(self, join, topic_id=None):
        """
        Check if Article has Self-Assessment and uploads it.
        """
        article = self._t2_client.get_content(
            site_id=self._t2_site_id,
            content_id=join['_id']
        )

        check_on_learning_questions = article['content'].get('checkOnLearning')

        if check_on_learning_questions:
            title = join['title']

            print('SelfAssessment for "{}"'.format(title), end=': ')

            content_id = self._contents_client.list.post(
                site_id=self._t3_site_id,
                content_title=title.strip() + ' - Self Assessment',
                content_type=ContentType.QUESTIONNAIRE,
                text='',
                topic_id=topic_id,
                resource_type=ResourceType.SELF_ASSESSMENTS,
            )

            upload_self_assessment(
                session=self._t3_json_session,
                questionnaire_id=content_id,
                t2_questions=check_on_learning_questions
            )

    def upload_content(self, join, topic_id=None):

        content_type = self._get_type_of_join(join)

        if content_type in ['article', 'game', 'video']:

            self.upload_article(join, topic_id)
            self.upload_self_assessment(join, topic_id)

        elif content_type == 'questionpool':
            self.upload_question_pool(join, topic_id)

    def _get_chapter_info(self, t2_chapter_id):
        topic = self._t2_client.get_a_topic(
            site_id=self._t2_site_id,
            topic_id=t2_chapter_id,
        )
        return topic.get('shortName', None), topic.get('description', None)

    def _create_chapter(self, title, topic_id=None,
                        short_name=None, description=None):
        print('Creating new chapter: {}'.format(title), end='')

        if description:  # apply html fixers:
            if self._html_fixer:
                description = self._html_fixer.apply(description)

        new_chapter_id = self._topics_client.list.post(
            site_id=self._t3_site_id,
            name=title,
            topic_id=topic_id,
            short_name=short_name,
            description=description,
        )

        print('\t\t[SUCCESS!]')

        return new_chapter_id

    def _get_topic_joins(self, topic_id):
        return self._t2_client.get_topic_joins(
            self._t2_site_id, topic_id
        )

    @staticmethod
    def _get_type_of_join(join):
        return join.get('type', None)

    def _is_join_is_content(self, join):

        content_type = self._get_type_of_join(join)

        if content_type in CONTENT_TYPES:
            return True
        else:
            return False

    def _is_join_is_chapter(self, join):

        content_type = self._get_type_of_join(join)

        if content_type == 'topics':
            return True
        else:
            return False

    def _update_queue_by_joins(self, topic_id, topic_joins):
        queue = [
            Vertex(uploaded_topic_id=topic_id, join=join)
            for join in topic_joins
        ]
        self._queue.extend(queue)

    def _upload_topic_joins(self):

        while self._queue:
            vertex = self._queue.pop(0)

            if self._is_join_is_content(vertex.join):

                self.upload_content(
                    join=vertex.join,
                    topic_id=vertex.uploaded_topic_id
                )

            elif self._is_join_is_chapter(vertex.join):

                short_name, description = self._get_chapter_info(
                    vertex.join['_id']
                )

                new_topic_id = self._create_chapter(
                    title=vertex.join['title'],
                    topic_id=vertex.uploaded_topic_id,
                    short_name=short_name,
                    description=description,
                )

                topic_joins = self._get_topic_joins(vertex.join['_id'])
                self._update_queue_by_joins(
                    topic_id=new_topic_id,
                    topic_joins=topic_joins,
                )

    def migrate_book(self):
        root_topic_joins = self._get_topic_joins(self._t2_root_topic_id)

        self._update_queue_by_joins(
            topic_id=None,
            topic_joins=root_topic_joins
        )
        self._upload_topic_joins()

        self.print_no_definition_terms()


if __name__ == '__main__':

    migrator = Migrator(
        trunity_2_login='',
        trunity_2_password='',
        trunity_3_login='',
        trunity_3_password='',
        t2_book_title='Integrating Concepts in Biology',
        t3_book_title='Integrating Concepts in Biology v19'
    )

    migrator.migrate_book()


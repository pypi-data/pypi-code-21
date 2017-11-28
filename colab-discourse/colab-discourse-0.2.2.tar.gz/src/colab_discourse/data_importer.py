from colab_discourse import models
from colab.plugins.data import PluginDataImporter
from colab.plugins import helpers
from django.db.models.fields import DateTimeField
from django.utils.dateparse import parse_datetime
from django.contrib.auth import get_user_model
from pydiscourse.client import DiscourseClient
User = get_user_model()


class ColabDiscoursePluginDataImporter(PluginDataImporter):
    app_label = 'colab_discourse'

    def __init__(self):
        plugin_config = helpers.get_plugin_config('colab_discourse')
        self.client = DiscourseClient(
            plugin_config['upstream'],
            api_key=plugin_config['api_key'],
            api_username=plugin_config['api_username']
        )

    def fill_object_data(self, model_class, data):
        try:
            obj = model_class.objects.get(id=data['id'])
        except model_class.DoesNotExist:
            obj = model_class()

        for field in obj._meta.fields:
            try:
                if field.name == 'badge_type':
                    obj.badge_type_id = data['badge_type_id']
                    continue

                if field.name == 'category':
                    obj.category_id = data['category_id']
                    continue

                if field.name == 'author':
                    user = User.objects.get(username=data['username'])
                    obj.author = user
                    continue

                if field.name == 'topic':
                    obj.topic_id = data['topic_id']
                    continue

                if isinstance(field, DateTimeField):
                    value = parse_datetime(data[field.name])
                else:
                    value = data[field.name]

                setattr(obj, field.name, value)
            except KeyError:
                continue

        return obj

    def fetch_data(self):
        models.DiscourseCategory.objects.all().delete()
        models.DiscourseTopic.objects.all().delete()
        models.DiscoursePost.objects.all().delete()
        models.DiscourseBadgeType.objects.all().delete()
        models.DiscourseBadge.objects.all().delete()

        self.fetch_categories()
        self.fetch_badges()
        self.fetch_topics()
        self.fetch_posts()

    def fetch_topics(self):
        topics_data = self.get_all_topics()
        for topic_data in topics_data:
            topic = self.fill_object_data(models.DiscourseTopic, topic_data)
            topic = self.complete_topic_informations(topic)

    def complete_topic_informations(self, topic):
        topic_data = self.client.topic(topic.slug, topic.id)
        created_by = topic_data['details']['created_by']['username']
        topic.created_by = User.objects.get(username=created_by)
        topic.participant_count = topic_data['participant_count']
        topic.save()

        for user_data in topic_data['details']['participants']:
            participant = User.objects.get(username=user_data['username'])
            topic.participants.add(participant)

        return topic

    def fetch_posts(self):
        topics = models.DiscourseTopic.objects.all()
        for topic in topics:
            self.fetch_posts_by_topic(topic)

    def fetch_posts_by_topic(self, topic):
        topic_info = self.client.posts(topic.id)
        posts_data = topic_info['post_stream']['posts']
        for post_data in posts_data:
            post = self.fill_object_data(models.DiscoursePost, post_data)
            post.save()

    def get_all_topics(self, page=0):
        topics = self.client.latest_topics(page=page)
        topics = topics['topic_list']['topics']
        all_topics = []
        all_topics.extend(topics)

        if topics:
            page += 1
            all_topics.extend(self.get_all_topics(page=page))

        return all_topics

    def fetch_categories(self):
        categories = self.client.categories()
        for category_data in categories:
            if category_data['slug'] != 'uncategorized':
                category = self.fill_object_data(models.DiscourseCategory,
                                                 category_data)
                category.save()

    def fetch_badges(self):
        badges_data = self.client.badges()
        self.fetch_badge_types(badges_data['badge_types'])
        for data in badges_data['badges']:
            badge = self.fill_object_data(models.DiscourseBadge, data)
            badge.save()

    def fetch_badge_types(self, data):
        for badge_type_data in data:
            badge_type = self.fill_object_data(models.DiscourseBadgeType,
                                               badge_type_data)
            badge_type.save()

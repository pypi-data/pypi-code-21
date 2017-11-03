import json

from actable.utils import get_gfk
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction


def get_events(instance, key, start=None, end=None):
    kwargs = get_gfk(instance)
    results = ActableRelation.objects.filter(**kwargs)
    return results.order_by('-date').values(key, 'date')


class ActableBase(models.Model):
    '''
    Base object shared by both the ActableEvent and ActableRelation, so that
    the cached data is available in both.
    '''
    class Meta:
        abstract = True
        get_latest_by = '-date'

    # Related object
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey()

    cached_html = models.TextField(
        help_text='Cached HTML snippet',
        null=True,
        blank=True,
    )

    cached_json = models.TextField(
        help_text='Cached JSON representation of context',
        null=True,
        blank=True,
    )

    date = models.DateTimeField(
        help_text='Date that this event occurred',
        auto_now_add=True,
        db_index=True,
    )

    is_cache_outdated = models.BooleanField(
        help_text='Mark if it is known that this cache needs updating',
        default=False,
    )


class ActableEvent(ActableBase):
    '''
    Represents a singular event: Generated one of these constitutes generating
    an event, and the content_object related to this is the "principle object".
    Useful for generating a global stream, and regenerating Relations if
    anything changes.
    '''
    cache_updated_date = models.DateTimeField(
        help_text='Date that the cache of this event was last updated',
        auto_now=True,
    )

    is_creation = models.BooleanField(
        help_text='Mark if this event is the creation of the principle object',
        default=False,
    )

    def save(self, **kwargs):
        relation_context = self.get_relation_context()
        is_new = not self.id
        self.regenerate_cache(relation_context)
        with transaction.atomic():
            super().save()  # Ensure get ID first

            if not is_new:
                # Delete all existing associated
                ActableRelation.objects.filter(event=self).delete()
            self.create_relations_from_self(relation_context)

    def get_principle_object(self):
        return self.content_object

    def create_relations_from_self(self, relation_context):
        '''
        Given a relation_context dictionary, create in the database all
        relevant relations for this event
        '''
        # Loop through context items
        relations = [
            ActableRelation(
                relation=relation_name,
                cached_html=self.cached_html,
                cached_json=self.cached_json,
                date=self.date,
                event=self,
                **get_gfk(content_object),
            )
            for relation_name, content_object in relation_context.items()
        ]
        ActableRelation.objects.bulk_create(relations)

    def get_relation_context(self):
        '''
        Gets all related objects to this event, as determined by the principle
        object.
        '''
        return self.content_object.get_actable_relations(self)

    def get_json(self, relation_context):
        '''
        Generates the JSON object from the principle object given the (assumed
        pre-fetched) relation context.
        '''
        if not hasattr(self.content_object, 'get_actable_json'):
            return None
        return self.content_object.get_actable_json(self)

    def get_html(self, relation_context):
        '''
        Generates the HTML from the principle object given the (assumed
        pre-fetched) relation context.
        '''
        if not hasattr(self.content_object, 'get_actable_html'):
            return None
        return self.content_object.get_actable_html(self)

    def regenerate_cache(self, relation_context):
        '''
        Update cached HTML and JSON dict (for this event only)
        '''
        self.cached_html = self.get_html(relation_context)
        json_dict = self.get_json(relation_context)
        self.cached_json = json.dumps(json_dict) if json_dict else None


class ActableRelation(ActableBase):
    '''
    Relates a single event to all related objects, storing a copy of the cached
    HTML or JSON snippets for each one.
    '''
    event = models.ForeignKey(ActableEvent)
    relation = models.CharField(
        help_text='Description of grammatical or topical relation (e.g. '
                  '"subject", "target", or "project_context")',
        max_length=64,
        db_index=True,
    )

    def get_principle_object(self):
        return self.event.content_object

    def __str__(self):
        return '%s: %s (%s)' % (self.relation, str(self.content_object), self.date)

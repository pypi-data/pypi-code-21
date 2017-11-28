from django import template
from django.contrib.contenttypes.models import ContentType

from molo.commenting.models import MoloComment

# NOTE: heavily inspired by
#       https://github.com/santiagobasulto/django-comments-utils


register = template.Library()


def get_molo_comments(parser, token):
    """
    Get a limited set of comments for a given object.
    Defaults to a limit of 5. Setting the limit to -1 disables limiting.
    Set the amount of comments to

    usage:

        {% get_molo_comments for object as variable_name %}
        {% get_molo_comments for object as variable_name limit amount %}
        {% get_molo_comments for object as variable_name limit amount child_limit amount %} # noqa

    """
    keywords = token.contents.split()
    if len(keywords) != 5 and len(keywords) != 7 and len(keywords) != 9:
        raise template.TemplateSyntaxError(
            "'%s' tag takes exactly 2,4 or 6 arguments" % (keywords[0],))
    if keywords[1] != 'for':
        raise template.TemplateSyntaxError(
            "first argument to '%s' tag must be 'for'" % (keywords[0],))
    if keywords[3] != 'as':
        raise template.TemplateSyntaxError(
            "first argument to '%s' tag must be 'as'" % (keywords[0],))
    if len(keywords) > 5 and keywords[5] != 'limit':
        raise template.TemplateSyntaxError(
            "third argument to '%s' tag must be 'limit'" % (keywords[0],))
    if len(keywords) == 7:
        return GetMoloCommentsNode(keywords[2], keywords[4], keywords[6])
    if len(keywords) > 7 and keywords[7] != 'child_limit':
        raise template.TemplateSyntaxError(
            "third argument to '%s' tag must be 'child_limit'"
            % (keywords[0],))
    if len(keywords) > 7:
        return GetMoloCommentsNode(keywords[2], keywords[4],
                                   keywords[6], keywords[8])
    return GetMoloCommentsNode(keywords[2], keywords[4])


class GetMoloCommentsNode(template.Node):

    def __init__(self, obj, variable_name, limit=5, child_limit=0):
        self.obj = obj
        self.variable_name = variable_name
        self.limit = int(limit)
        self.child_limit = int(child_limit) * (-1)

    def render(self, context):
        try:
            obj = template.Variable(self.obj).resolve(context)
        except template.VariableDoesNotExist:
            return ''

        qs = MoloComment.objects.for_model(obj.__class__).filter(
            object_pk=obj.pk, parent__isnull=True)
        if self.limit > 0:
            qs = qs[:self.limit]

        qs = [[c] + list(c.get_descendants())[self.child_limit:] for c in qs]
        context[self.variable_name] = qs
        return ''


def get_comments_content_object(parser, token):
    """
    Get a limited set of comments for a given object.
    Defaults to a limit of 5. Setting the limit to -1 disables limiting.

    usage:

        {% get_comments_content_object for form_object as variable_name %}

    """
    keywords = token.contents.split()
    if len(keywords) != 5:
        raise template.TemplateSyntaxError(
            "'%s' tag takes exactly 2 arguments" % (keywords[0],))
    if keywords[1] != 'for':
        raise template.TemplateSyntaxError(
            "first argument to '%s' tag must be 'for'" % (keywords[0],))
    if keywords[3] != 'as':
        raise template.TemplateSyntaxError(
            "first argument to '%s' tag must be 'as'" % (keywords[0],))
    return GetCommentsContentObject(keywords[2], keywords[4])


class GetCommentsContentObject(template.Node):

    def __init__(self, obj, variable_name):
        self.obj = obj
        self.variable_name = variable_name

    def render(self, context):
        try:
            form = template.Variable(self.obj).resolve(context)
        except template.VariableDoesNotExist:
            return ''

        app_label, model = form['content_type'].value().split('.')
        object_pk = form['object_pk'].value()

        content_type = ContentType.objects.get(app_label=app_label,
                                               model=model)

        context[self.variable_name] = content_type.get_object_for_this_type(
            pk=object_pk)

        return ''


def is_in_group(user, group_name):
    """
    Check if a user in a group named ``group_name``.
    :param user User:
        The auth.User object
    :param group_name str:
        The name of the group
    :returns: bool
    """
    return user.groups.filter(name__exact=group_name).exists()


def is_in_admin_group(person):
    return (
        person.is_superuser or
        is_in_group(person, 'Moderator') or
        is_in_group(person, 'Comment Moderator') or
        is_in_group(person, 'Expert')
    )


def get_number_replies(comment):
    # TODO include reported/banned comments?
    return comment.get_children().count()


@register.inclusion_tag(
    'notifications/tags/notification_banner.html',
    takes_context=True)
def display_unread_notifications(context):
    user = context['request'].user

    number_unread_notifications = 0

    if user.is_authenticated():
        number_unread_notifications = len(user.notifications.unread())

    return {
        'user': user,
        'number_unread_notifications': number_unread_notifications,
    }


register.filter('is_in_group', is_in_group)
register.tag('get_molo_comments', get_molo_comments)
register.tag('get_comments_content_object', get_comments_content_object)
register.filter('get_number_replies', get_number_replies)
register.filter('is_in_admin_group', is_in_admin_group)


from django.apps import apps
from django import template

from misc.utils import get_ip, get_session_key

from ..forms import VoteForm


register = template.Library()


@register.inclusion_tag('poll/index.html', takes_context=True)
def render_latest_poll(context):

    context = context.__dict__.copy()

    request = context['request']

    poll_model = apps.get_model('poll', 'Poll')

    try:
        poll = poll_model.objects.latest()
    except poll_model.DoesNotExist:
        return {}

    is_poll_voted = poll.is_voted(
        request.user, get_ip(request), get_session_key(request))

    form = VoteForm(initial={'poll': poll})

    context.update({
        'poll': poll,
        'form': form,
        'is_poll_voted': is_poll_voted
    })

    return context

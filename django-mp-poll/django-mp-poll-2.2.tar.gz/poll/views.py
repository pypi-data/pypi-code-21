
from django.shortcuts import redirect, render
from django.views.generic import FormView
from django.http.response import (
    HttpResponseBadRequest, JsonResponse, HttpResponse)
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from misc.utils import get_ip, get_session_key

from poll.forms import VoteForm
from poll.models import Poll


def get_latest_poll(request):

    try:
        poll = Poll.objects.latest()
    except Poll.DoesNotExist:
        return HttpResponse(_('No poll found'))

    is_poll_voted = poll.is_voted(
        request.user, get_ip(request), get_session_key(request))

    form = VoteForm(initial={'poll': poll})

    context = {
        'poll': poll,
        'form': form,
        'is_poll_voted': is_poll_voted
    }

    return render(request, 'poll/index.html', context)


class VoteView(FormView):

    form_class = VoteForm

    def form_valid(self, form):

        request = self.request
        user = request.user
        user_ip = get_ip(request)

        vote = form.save(commit=False)

        session_key = get_session_key(request)

        poll = vote.poll

        if poll.is_voted(user, user_ip, session_key):
            return HttpResponseBadRequest('Already voted')

        vote.ip = user_ip
        vote.session = session_key
        vote.user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]

        if user.is_authenticated():
            vote.user = user

        vote.save()

        vote.choice.votes += 1
        vote.choice.save()

        poll.votes += 1
        poll.save()

        if request.is_ajax():
            return JsonResponse({
                'message': _('Vote was successfully created'),
                'result': render_to_string('poll/result.html', {
                    'poll': poll,
                    'is_poll_voted': True
                })
            })

        return redirect(request.GET.get('referrer', 'home'))

    def form_invalid(self, form):
        return HttpResponseBadRequest('Invalid request')

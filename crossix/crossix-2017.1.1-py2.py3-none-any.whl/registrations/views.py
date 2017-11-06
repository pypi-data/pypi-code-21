# -*- coding: utf-8 -*-

import datetime

from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.shortcuts import render_to_response

from . import models


class ParticipantForm(forms.ModelForm):
    class Meta:
        model = models.Participant
        exclude = ('last_edition', )


def register(request):
    """Display the register form."""
    # CSRF protection
    ctxt = {
        'categories': models.Category.objects.all(),
    }
    ctxt.update(csrf(request))

    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            ctxt['participant'] = form.save()
            return render_to_response('registrations/register_success.html', ctxt)
    else:
        form = ParticipantForm()
    ctxt['form'] = form
    return render_to_response('registrations/register.html', ctxt)


def index(request):
    """Display the index page."""
    next_edition = models.Edition.objects.next()
    last_edition = models.Edition.objects.last()
    ctxt = {
        'next_edition': next_edition,
        'last_edition': last_edition,
        }
    return render_to_response('registrations/index.html', ctxt)


def access(request):
    """Display the 'access' page."""
    edition = models.Edition.objects.next() or models.Edition.objects.last()
    ctxt = {
        'edition': edition,
    }
    return render_to_response('registrations/access.html', ctxt)


def list_participants(request):
    """Display the list of participants."""
    parts = {}
    next_edition = models.Edition.objects.next()
    for cat in models.Category.objects.filter():
        parts[cat] = models.Participant.objects.filter(category=cat, last_edition=next_edition)
    ctxt = {
            'categories': parts
            }
    return render_to_response('registrations/list.html', ctxt)


@login_required
def list_participants_full(request):
    """Display data about all participants."""
    ctxt = {
            'participants': models.Participant.objects.all()
            }
    return render_to_response('registrations/list_all.html', ctxt)

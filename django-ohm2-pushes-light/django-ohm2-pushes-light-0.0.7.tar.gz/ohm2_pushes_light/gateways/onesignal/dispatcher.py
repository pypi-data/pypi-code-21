from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.db.models import Q
from ohm2_handlers_light import utils as h_utils
from ohm2_handlers_light.definitions import RunException
from . import settings
from . import utils as onesignal_utils
from .decorators import onesignal_safe_request
import os, time, random


@onesignal_safe_request
def index(request, params):
	p = h_utils.cleaned(params, (
					 	))
	
	
	ret = {
	}
	return ret
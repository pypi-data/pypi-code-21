from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from ohm2_handlers_light.parsers import get_as_or_get_default
from . import dispatcher


def index(request):
	keys = (
	)
	ret, error = dispatcher.index(request, get_as_or_get_default(request.GET, keys))
	if error:
		return HttpResponse("error")	
	return render(request, "onesignal/index.html", {"ret" : ret})

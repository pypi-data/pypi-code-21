from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from ohm2_handlers_light.parsers import get_as_or_get_default
from . import dispatcher


@login_required
def logout(request):
	keys = (
		("next", "next", "/"),
	)
	ret, error = dispatcher.logout(request, get_as_or_get_default(request.GET, keys))
	if error:
		return redirect("/")
	return redirect(ret.get("next", "/"))
	
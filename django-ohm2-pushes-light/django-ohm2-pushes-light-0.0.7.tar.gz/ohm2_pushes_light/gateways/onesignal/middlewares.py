from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
try:
	from django.utils.deprecation import MiddlewareMixin
except ImportError:
	MiddlewareMixin = object
from . import utils as onesignal_utils



class OnesignalMiddleware(MiddlewareMixin):
	
	def process_request(self, request):
		
		if request.user.is_authenticated():

			is_staff = request.user.is_staff
			is_superuser = request.user.is_superuser
			
			if is_superuser or is_staff:
				return None

				
		return None
	
	
	def process_response(self, request, response):
		
		return response
	

import logging
logger = logging.getLogger(__name__)

from django import forms

from .models import Visit, Ip, Path, UserAgent

from django.core.exceptions import ObjectDoesNotExist


class IpForm(forms.ModelForm):
	
	class Meta:
		model = Ip
		fields = ['address',]
		
def add_ip(address):
	try:
		ip = Ip.objects.get(address=address)
		if ip:
			ip.save()
	except ObjectDoesNotExist:
		form = IpForm({'address':address})
		if form.is_valid():
			ip = form.save()
		else:
			logger.info(form.errors)
			ip = None
	return ip.id
		
class PathForm(forms.ModelForm):
	
	class Meta:
		model = Path
		fields = ['path',]
		
def add_path(path):
	try:
		path = Path.objects.get(path=path)
		if path:
			path.save()
	except ObjectDoesNotExist:
		form = PathForm({'path':path})
		if form.is_valid():
			path = form.save()
		else:
			logger.info(form.errors)
			path = None
	return path.id

class UserAgentForm(forms.ModelForm):
	
	class Meta:
		model = UserAgent
		fields = ['string',]
		
def add_user_agent(string):
	try:
		agent = UserAgent.objects.get(string=string)
		if agent:
			agent.save()
	except ObjectDoesNotExist:
		form = UserAgentForm({'string':string})
		if form.is_valid():
			agent = form.save()
		else:
			logger.info(form.errors)
			agent = None
	return agent.id

class VisitForm(forms.ModelForm):
	
	class Meta:
		model=Visit
		fields=['useragent','path','ip','method','content_type','encoding']
		
def add_visit(useragent,path,ip,method=None,content_type=None,encoding=None):
	try:
		useragent_obj = add_user_agent(useragent)
		path_obj = add_path(path)
		ip_obj = add_ip(ip)
	except:
		return
	
	form = VisitForm({
		'useragent':useragent_obj,
		'path':path_obj,
		'ip':ip_obj,
		'method':method,
		'content_type':content_type,
		'encoding':encoding,
	})
	if form.is_valid():
		visit = form.save()
	else:
		logger.info(form.errors)
		visit = None
	return visit
	

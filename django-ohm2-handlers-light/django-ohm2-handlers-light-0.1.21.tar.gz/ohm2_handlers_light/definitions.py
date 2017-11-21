from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import UploadedFile
from . import settings
from . import errors as ohm2_handlers_light_errors
from . import models as ohm2_handlers_light_models

try:
	from django.utils.deprecation import MiddlewareMixin
except ImportError:
	MiddlewareMixin = object

try:
	import simplejson as json
except Exception:
	import json

import random, string, time, tempfile

class BaseException(Exception):
	
	def __init__(self, *args, **kwargs):
		self.app = kwargs.get("app", "ohm2_handlers_light")
		self.code = kwargs.get("code")
		if self.code is None:
			self.code = settings.DEFAULT_EXCEPTION_CODE

		self.message = kwargs.get("message")
		if self.message is None:
			self.message = settings.DEFAULT_EXCEPTION_MESSAGE

		self.original = kwargs.get("original", None)
			
		self.ins_filename = kwargs.get("ins_filename", "")
		self.ins_lineno = kwargs.get("ins_lineno", -1)
		self.ins_function = kwargs.get("ins_function", "")
		self.ins_code_context = kwargs.get("ins_code_context", "")
		


	def __str__(self):
		return "code: {0}; message: {1}".format(self.code, self.message)
	
	def regroup(self):
		return {
			"code" : self.code,
			"message" : self.message,
		}

class RunException(BaseException):
	
	def __init__(self, code, message, **kwargs):
		kwargs["code"] = code
		kwargs["message"] = message
		super(RunException, self).__init__(**kwargs)
	



class RequestException(BaseException):
	
	def __init__(self, app, code, message, original, **kwargs):
		kwargs["app"] = app
		kwargs["code"] = code
		kwargs["message"] = message
		kwargs["original"] = original
		super(RequestException, self).__init__(**kwargs)
		

	


class MiddlewareContext(MiddlewareMixin):

	def __init__(self, *args, **kwargs):
		pass

	@property
	def as_dict(self):
		return self.__dict__


class Device(object):

	is_ios = False
	is_android = False
	is_mobile = False

	is_pc = False
	is_bot = False

	def __init__(self, *args, **kwargs):
		for k, v in kwargs.items():
			setattr(self, k, v)

		if self.is_ios or self.is_android:
			self.is_mobile = True



class EmailHandler(object):

	def __init__(self, to_email, from_email, subject, content, **kwargs):
		
		self.to_email = to_email
		self.from_email = from_email
		self.subject = subject
		self.content = content

		self.provider = kwargs.get("provider", "Unknown")
		
		self.sent = False
		self.read = False
		

	

class PermanentUploadedFile(UploadedFile):

	def __init__(self, name, content_type, size, charset, content_type_extra = None):
		file = tempfile.NamedTemporaryFile(suffix = '.upload', dir = settings.FILE_UPLOAD_TEMP_DIR, delete = False)
		super(PermanentUploadedFile, self).__init__(file, name, content_type, size, charset, content_type_extra)

	def close(self):
		try:
			return self.file.close()
		except OSError as e:
			pass

			
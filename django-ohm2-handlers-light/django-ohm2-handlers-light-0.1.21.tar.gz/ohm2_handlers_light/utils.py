from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.utils import timezone, timesince
from django.template.response import SimpleTemplateResponse
from . import settings
from . import definitions as ohm2_handlers_light_definitions
from . import errors as ohm2_handlers_light_errors
from . import models as ohm2_handlers_light_models

if settings.MAILGUN_DOMAIN and settings.MAILGUN_API_KEY:
	from ohm2_handlers_light.email_handlers.mailgun import Mailgun

if settings.DATEUTIL_ENABLED:
	from dateutil.relativedelta import relativedelta
	from dateutil import parser as date_parser

if settings.ENCRYPTION_ENABLED:
	from Crypto.PublicKey import RSA
	from Crypto.Cipher import XOR, AES

if settings.PILL_ENABLED:
	from PIL import Image

if settings.UNIDECODE_ENABLED:
	from unidecode import unidecode

if settings.HTMLMIN_MINIFY_ENABLED:
	from htmlmin.minify import html_minify

if settings.CREATE_QR_CODES:
	import qrcode	

if settings.CREATE_BARCODES:
	import barcode

if settings.SLUGIFLY_ENABLED:
	from slugify import slugify

import html.parser as HTLMParser
import time, random, datetime, os, string, re, sys
import hashlib, sqlite3, ipaddress, tempfile, base64, mimetypes, urllib.request



def safe_run(function_to_run, on_exception_return, *args, **kwargs):
	try:
		return function_to_run(*args, **kwargs)
	except Exception as e:
		return on_exception_return

def db_get(obj, **kwargs):
	return obj.objects.get( **kwargs )

def db_get_or_none(obj, **kwargs):
	try:
		return db_get(obj, **kwargs )
	except ObjectDoesNotExist:
		return None	

def db_create(obj, **kwargs):
	return obj.objects.create( **kwargs )

def db_get_or_create(obj, **kwargs):
	return obj.objects.get_or_create( **kwargs )

def db_delete(entry, **kwargs):
	return entry.delete()

def db_update(entry, **kwargs):
	for param, value in kwargs.items():
		setattr(entry, param, value)
	setattr(entry, "last_update", timezone.now())	
	entry.save()	
	return entry

def db_filter(obj, **kwargs):
	return obj.objects.filter( **kwargs )

def db_q(obj, q):
	return obj.objects.filter(q)

def db_unique_random(obj, initial_length = 10, max_length = 32, attribute = "identity", post_prefix = "", post_suffix = ""):
	string = get_random_string(max_length)
	for up_to in range(initial_length, max_length + 1):
		tmp_string = string[:up_to]
		if db_get_or_none(obj, **{attribute: tmp_string}):
			continue
		return post_prefix + tmp_string + post_suffix
	raise ohm2_handlers_light_definitions.RunException(**ohm2_handlers_light_errors.NO_UNIQUE_RANDOM_FOUND)

def db_unique_string(pattern, db_obj, initial_length = 20, attribute = "identity", to_int = False, post_prefix = "", post_suffix = ""):
	
	if to_int == True:
		string = '{}'.format(int( hashlib.sha256( pattern.encode('utf-8') ).hexdigest(), 16))
	else:
		string = hashlib.sha256( pattern.encode('utf-8') ).hexdigest()
	
	max_length = len(string)
	for up_to in range(initial_length, max_length + 1):

		tmp_string = string[:up_to]

		try:
			obj = db_obj.objects.get( **{ attribute: tmp_string } )
		except ObjectDoesNotExist:
			obj = None
		except Exception as e:
			raise ohm2_handlers_light_definitions.RunException(**ohm2_handlers_light_errors.QUERY_SET)
		
		if obj == None:
			string = tmp_string
			break
	else:
		raise ohm2_handlers_light_definitions.RunException(**ohm2_handlers_light_errors.NO_UNIQUE_STRING_FOUND)

	return post_prefix + string + post_suffix

def db_unique_string_hashed(*args, **kwargs):
	return db_unique_string(*args, **kwargs)	

def generic_unique_string(db_obj, initial_length = 20, pattern = None, attribute = "identity"):
	if pattern == None:
		pattern = "{}{}{}".format(get_random_string(5), time.time(), get_random_string(5))
	return db_unique_string(pattern = pattern,
							initial_length = initial_length,
							db_obj = db_obj,
							attribute = attribute)

def db_generic_unique_string(*args, **kwargs):
	return generic_unique_string(*args, **kwargs)

def db_unique_random_number(obj, initial_length = 10, max_length = 32, attribute = "identity", post_prefix = "", post_suffix = ""):
	string = get_random_string_number(max_length)
	for up_to in range(initial_length, max_length + 1):
		tmp_string = string[:up_to]
		if db_get_or_none(obj, **{attribute: tmp_string}):
			continue
		return post_prefix + tmp_string + post_suffix
	else:
		raise definitions.HandlersRunError(**HandlersErrors.NO_UNIQUE_RANDOM_FOUND)		

def get_random_string(length = 5):
	return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(length))
	
def random_string(length = 10):
	return get_random_string(length)

def get_random_string_number(length = 10):
	return ''.join(random.choice(string.digits) for x in range(length))

def random_string_number(length = 10):
	return get_random_string_number(length)

def random_string_hexdigits(length = 10):
	return ''.join(random.choice(string.hexdigits) for x in range(length))

def to_unicode(string, replace_empty = True, by_ch = "_"):
	text = unidecode(string)
	if replace_empty:
		text = text.replace(" ", by_ch)
		
	return text

def get_context(request):
	context = ohm2_handlers_light_definitions.MiddlewareContext()

	context.debug = settings.DEBUG
	context.current_path = request.get_full_path()
	context.current_language = request.LANGUAGE_CODE
	context.now = timezone.now()
	context.address = request.META.get("REMOTE_ADDR", None)
	context.media_root = settings.MEDIA_ROOT
	context.host = settings.HOST
	context.subdomains = settings.SUBDOMAINS
	context.protocol = settings.PROTOCOL
	context.hostname = settings.HOSTNAME
	context.website_url = settings.WEBSITE_URL


	return context	


def is_string(string, min_length = 0):

	if type(string) != str:
		return False
		
	string = string.strip()	
	if not len(string) >= min_length:
		return False	
	return True	

def is_email_valid(email):
	regex = r'^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
	if re.match(regex, email) == None:
		return False
	return True
		
def is_content_harmful(string):
	return False

def is_url_safe(url):
	if not len(url) > 0:
		return False	
	return True

def is_file_safe(file_name):
	if not len(file_name) > 0:
		return False
	return True


file_safe_list = [ InMemoryUploadedFile, TemporaryUploadedFile]
def is_upload_file_safe(u_file):
	if not type(u_file) in file_safe_list:
		return False
	
	elif not len(u_file._name) > 0:
		return False
	
	elif not len(u_file.content_type) > 0:
		return False

	else:
		return True


def is_password_safe(password, **kwargs):		
	if not len(password) >= kwargs.get('length', 1):
		return False

	elif kwargs.get('lowercase', False) == True and re.search(r"[a-z]", password) == None:
		return False

	elif kwargs.get('uppercase', False) == True and re.search(r"[A-Z]", password) == None:
		return False

	elif kwargs.get('digits', False) == True and re.search(r"[0-9]", password) == None:
		return False

	return True	


def is_ip_address(ip):

	try:
		ipaddress.IPv4Address(ip)
	except Exception as e:
		pass
	else:
		return True

	try:
		ipaddress.IPv6Address(ip)
	except Exception as e:
		pass
	else:
		return True
	
	return False


def is_request(request):
	
	if hasattr(request, 'user') == False:
		return False

	elif hasattr(request, 'META') == False:
		return False

	elif hasattr(request, 'GET') == False:
		return False

	elif hasattr(request, 'POST') == False:
		return False	

	elif callable(getattr(request.user, 'is_authenticated')) == False:
		return False

	return True


def is_mix_type(var, types):
	o_type = type(var)
	for t in types:
		if o_type == t:
			return True
	return False

number_list = [int, float]
def is_number(num):
	if type(num) in number_list:
		return True
	return False


def is_valid_device(device):
	if device in settings.SUPPORTED_DEVICES:
		return True
	return False
	

def mix_cleaned_data(params, vars):
	t_params = {}
	for var in vars:
		v_type, v_name, v_value = var[0], var[1], var[2]
		value = params[v_name]
		
		if v_type == 'string':

			if is_string(value, v_value):
				t_params[v_name] = value.strip()
			else:
				code, message = ohm2_handlers_light_errors.INVALID_STRING["code"], ohm2_handlers_light_errors.INVALID_STRING["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)

		elif v_type == 'email':

			if is_email_valid(email = value):
				t_params[v_name] = value.strip()
			else:
				code, message = ohm2_handlers_light_errors.INVALID_EMAIL["code"], ohm2_handlers_light_errors.INVALID_EMAIL["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)

		elif v_type == 'password':
			
			if is_password_safe(value, **v_value) == True:
				t_params[v_name] = value.strip()
			else:
				code, message = ohm2_handlers_light_errors.INVALID_PASSWORD["code"], ohm2_handlers_light_errors.INVALID_PASSWORD["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)

		elif v_type == 'bool':

			for_true = v_value['True']
			for_false = v_value['False']

			if value == for_true:
				t_params[v_name] = True
			elif value == for_false:
				t_params[v_name] = False
			else:
				code, message = ohm2_handlers_light_errors.INVALID_BOOL["code"], ohm2_handlers_light_errors.INVALID_BOOL["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)
		
		elif v_type == 'type':

			if type(value) == v_value:
				t_params[v_name] = value
			else:
				code, message = ohm2_handlers_light_errors.WRONG_TYPE["code"], ohm2_handlers_light_errors.WRONG_TYPE["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)

		elif v_type == 'url':

			if is_url_safe(url = value) == True:
				t_params[v_name] = value
			else:
				code, message = ohm2_handlers_light_errors.INVALID_URL["code"], ohm2_handlers_light_errors.INVALID_URL["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)
		
		elif v_type == 'file':

			if is_file_safe(file_name = value) == True:
				t_params[v_name] = value.strip()
			else:
				code, message = ohm2_handlers_light_errors.INVALID_FILE["code"], ohm2_handlers_light_errors.INVALID_FILE["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)

		elif v_type == 'u_file':
			
			if is_upload_file_safe(u_file = value) == True:
				t_params[v_name] = value
			else:
				code, message = ohm2_handlers_light_errors.INVALID_UPLOAD_FILE["code"], ohm2_handlers_light_errors.INVALID_UPLOAD_FILE["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)

		elif v_type == 'ip':
			
			if is_ip_address(ip = value) == True:				
				t_params[v_name] = value			
			else:
				code, message = ohm2_handlers_light_errors.INVALID_IP_ADDRESS["code"], ohm2_handlers_light_errors.INVALID_IP_ADDRESS["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)

		elif v_type == 'request':
			
			if is_request(request = value) == True:
				t_params[v_name] = value			
			else:				
				code, message = ohm2_handlers_light_errors.INVALID_REQUEST["code"], ohm2_handlers_light_errors.INVALID_REQUEST["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)
		
		elif v_type == 'c_request':
			
			if is_custom_request(request = value, to_check = v_value) == True:
				t_params[v_name] = value			
			else:
				raise ohm2_handlers_light_definitions.RunException(**ohm2_handlers_light_errors.INVALID_CUSTOM_REQUEST)

		elif v_type == 'username':
			
			if v_value == 'email':

				if is_email_valid(email = value) == True:

					t_params[v_name] = value.strip()
				else:

					raise ohm2_handlers_light_definitions.RunException(**ohm2_handlers_light_errors.INVALID_USERNAME)

			elif v_value == 'string':

				t_params[v_name] = value.strip()[:settings.MAX_USERNAME_LENGTH]
										
			else:

				raise ohm2_handlers_light_definitions.RunException(**ohm2_handlers_light_errors.INVALID_USERNAME)
				
		elif v_type == 'mix':

			if is_mix_type(var = value,types = v_value) == True:
				t_params[v_name] = value

			else:
				code, message = ohm2_handlers_light_errors.INVALID_MIX_TYPE["code"], ohm2_handlers_light_errors.INVALID_MIX_TYPE["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)
		
		elif v_type == 'regex':

			if re.match(v_value, v_name):
				t_params[v_name] = value
			else:
				raise ohm2_handlers_light_definitions.RunException(**ohm2_handlers_light_errors.INVALID_REGEX)

		elif v_type == 'integer':

			if type(value) == int:
				t_params[v_name] = value

			else:
				code, message = ohm2_handlers_light_errors.INVALID_INTEGER["code"], ohm2_handlers_light_errors.INVALID_INTEGER["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)

		elif v_type == 'float':

			if type(value) == float:
				t_params[v_name] = value

			else:
				code, message = ohm2_handlers_light_errors.INVALID_FLOAT["code"], ohm2_handlers_light_errors.INVALID_FLOAT["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)	
				
		elif v_type == 'number':

			if is_number(value):
				t_params[v_name] = value
			else:
				raise ohm2_handlers_light_definitions.RunException(**ohm2_handlers_light_errors.INVALID_NUMBER)
		
		elif v_type == 'device':

			if is_valid_device(value):
				t_params[v_name] = value
			else:
				raise ohm2_handlers_light_definitions.RunException(**ohm2_handlers_light_errors.INVALID_DEVICE)

		elif v_type == 'dict':

			if type(value) == dict:
				for key in v_value:
					if value.get(key, settings.DICT_STOP_WORD) == settings.DICT_STOP_WORD:
						code, message = ohm2_handlers_light_errors.INVALID_DICT["code"], ohm2_handlers_light_errors.INVALID_DICT["message"] + ": %s, missing key '%s'" % (v_name, key)
						raise ohm2_handlers_light_definitions.RunException(code, message)
				t_params[v_name] = value
			else:
				code, message = ohm2_handlers_light_errors.INVALID_DICT["code"], ohm2_handlers_light_errors.INVALID_DICT["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)

		elif v_type == 'def_dict':

			if type(value) == dict:
				for key, def_value in v_value:
					value[key] = value.get(key, def_value)
				t_params[v_name] = value
			
			else:
				code, message = ohm2_handlers_light_errors.INVALID_DICT["code"], ohm2_handlers_light_errors.INVALID_DICT["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)

		elif v_type == 'struct':

			if type(value) == dict:
				t_params[v_name] = VALUE
			
			else:
				code, message = ohm2_handlers_light_errors.INVALID_STRUCTURE["code"], ohm2_handlers_light_errors.INVALID_STRUCTURE["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)

		elif v_type == 'address':

			if type(value) == dict:
				address_candidate = value
				address, structure = {}, v_value
				if structure is None:
					structure = settings.OHM2_ADDRESS_LIGHT_STRUCTURE

				
				for a_key, a_conf in structure.items():
					optional, a_vars = a_conf["optional"], a_conf["validation"]
					if optional and a_key not in address_candidate:
						continue

					try:
						a_p = cleaned({a_key: address_candidate.get(a_key, None)}, a_vars)
					except Exception as e:
						code, message = ohm2_handlers_light_errors.INVALID_OHM2_ADDRESS_LIGHT["code"], ohm2_handlers_light_errors.INVALID_OHM2_ADDRESS_LIGHT["message"] + ": missing or invalid key '%s'" % (a_key)
						raise ohm2_handlers_light_definitions.RunException(code, message)

					address[a_key] = a_p[a_key]

				t_params[v_name] = address
			
			else:
				code, message = ohm2_handlers_light_errors.INVALID_OHM2_ADDRESS_LIGHT["code"], ohm2_handlers_light_errors.INVALID_OHM2_ADDRESS_LIGHT["message"] + ": %s" % (v_name)
				raise ohm2_handlers_light_definitions.RunException(code, message)

		else:
			raise ohm2_handlers_light_definitions.RunException(**ohm2_handlers_light_errors.INVALID_TYPE)
				
	return t_params

def cleaned(params, vars):
	return mix_cleaned_data(params, vars)


def create_dictionary(**kwargs):
	dictionary = {}
	for k, v in kwargs.items():	
		dictionary[k] = v
	else:
		return dictionary

def _dict(**kwargs):
	return create_dictionary(**kwargs)

def join_dictionaries(*args):
	joined_dictionary = {}
	for dict_value in args:	
			
		for k, v in dict_value.items():
			joined_dictionary[k] = v

	else:
		return joined_dictionary

def join_dicts(*args):
	return join_dictionaries(*args)


def is_older_than_now(date, **kwargs):
	if timezone.now() > date + relativedelta( **kwargs ):
		return True
	return False

def generate_RSA(bits = 2048, rand = os.urandom):
	key = RSA.generate(bits,  rand, e = 65537) 
	public_key = key.publickey().exportKey("PEM")
	private_key = key.exportKey("PEM") 
	return private_key, public_key


def render_template(template, context, **kwargs):
	return SimpleTemplateResponse(template, context).render()

def template_response(template, context, **kwargs):
	rendered = render_template(template, context)
	content = rendered.content.replace(b'\n', b'')
	content = content.replace(b'\t', b'')

	html = HTLMParser.unescape( content.decode('utf-8') )
	if kwargs.get("minify"):
		return html_minify(html)
	return html


def create_qr(text, **kwargs):
	dst = tempfile.NamedTemporaryFile(suffix = '.png', delete = False)

	qr = qrcode.QRCode(
		version = kwargs.get("version", 1),
		error_correction = qrcode.constants.ERROR_CORRECT_L,
		box_size = kwargs.get("box_size", 10),
		border = kwargs.get("border", 4),
	)

	qr.add_data(text)
	qr.make(fit = kwargs.get("fit", True))
	img = qr.make_image()
	img.save(dst.name)

	return dst.name

def create_barcode(text, **kwargs):
	dst = tempfile.NamedTemporaryFile(delete = False)
	ean = barcode.get(kwargs.get('format','ean13'), text, writer = barcode.writer.ImageWriter())
	return ean.save(dst.name)

def guess_mimetype(filename):
	return mimetypes.guess_type(filename)[0]
	
def get_local_image(path, dst_suffix = ".jpg", dst_format = "JPEG", dst_quality = 95):

	with open(path, 'rb') as image:
		content = image.read()
	
	filename = path.rsplit("/", 1)[-1]
	name, extension = filename.rsplit(".", 1)
	f1 = tempfile.NamedTemporaryFile(suffix="." + extension, delete = False)
	f1.write(content)
	f1.close()

	im = Image.open(f1.name)
	f2 = tempfile.NamedTemporaryFile(suffix = dst_suffix)
	im.save(f2.name, format = dst_format, quality = dst_quality, optimize = True)


	mimetype = guess_mimetype(filename)
	if not mimetype:
		mimetype = "image/"
		
	tp = ohm2_handlers_light_definitions.PermanentUploadedFile(f2.name,
															   mimetype,
															   0,
															   None)
	
	tp.write(f2.read())
	tp.open('rb')
	return tp

def process_uploaded_image(image, **kwargs):
	image.open('rb')
	content = image.read()
	image.close()


	f1 = tempfile.NamedTemporaryFile(suffix = "." + image.name.rsplit(".", 1)[-1], delete = False)
	f1.write(content)
	
	im = Image.open(f1.name)
	
	max_width, max_height = kwargs.get("max_width"), kwargs.get("max_height")
	if (max_width is not None and max_height is not None) and (im.width > max_width or im.height > max_height):
		im.thumbnail((max_width, max_height), Image.ANTIALIAS)
	

	f2 = tempfile.NamedTemporaryFile(suffix = kwargs.get("suffix", ".jpg"), delete = False)
	im.save(f2.name,
			format = kwargs.get("format", "JPEG"),
			quality = kwargs.get("quality", 75),
			optimize = kwargs.get("optimize", True),
			fill_color = kwargs.get("fill_color", ""))


	
	tp = ohm2_handlers_light_definitions.PermanentUploadedFile(f2.name,
															   kwargs.get("mime", "image/jpg"),
															   0,
															   image.charset)
		
	tp.write(f2.read())
	tp.open('rb')
	return tp

def download_file(url, **kwargs):
	url_f = url.split("?", 1)[0]
	rest, filename = url_f.rsplit("/", 1)
	name, extension = filename.rsplit(".", 1)

	dst = tempfile.NamedTemporaryFile(suffix = '.' + extension, delete = False)
	urllib.request.urlretrieve(url, dst.name)
	return dst.name

def download_and_get_local_image(url, **kwargs):
	path = download_file(url)
	return get_local_image(path)


def mailgun_send(to_email, from_email, subject, content, **kwargs):
	handler = Mailgun(settings.MAILGUN_DOMAIN, settings.MAILGUN_API_KEY,
				      to_email = to_email, from_email = from_email,
				      subject = subject, content = content)


	return handler.send()

def get_base_error_code():
	return int(random_string_hexdigits(3), 16) * 2**6

def encrypt_aes_cfb(key_16, iv_16, message):
	obj = AES.new(key_16, AES.MODE_CFB, base64.b64decode(iv_16))
	return obj.encrypt(message)

def decrypt_aes_cfb(key_16, iv_16, encrypted):
	obj = AES.new(key_16, AES.MODE_CFB, base64.b64decode(iv_16))
	return obj.decrypt(encrypted)

def get_file_extension(path):
	split = path.rsplit(".", 1)
	if len(split) == 2:
		return split[1].strip()
	return None

def new_local_file(path, **options):
	extension = get_file_extension(path)
	if extension:
		suffix = "." + extension.lower()
	else:
		suffix = None

	tmp = NamedTemporaryFile(delete = False, suffix = suffix)
	with open(path, "rb") as f:
		
		keep_reading = True
		while keep_reading:
			content = f.read(32)
			if content == b"":
				keep_reading = False
			else:
				tmp.write(content)
	tmp.flush()
	tmp.seek(0)
	return File(tmp)

def convert_image(path, **options):
	im = Image.open(path)
	max_width, max_height = options.get("max_width"), options.get("max_height")
	if (max_width is not None and max_height is not None) and (im.width > max_width or im.height > max_height):
		im.thumbnail((max_width, max_height), Image.ANTIALIAS)
	
	extension = get_file_extension(path)
	if extension:
		suffix = "." + extension.lower()
	else:
		suffix = None

	tmp = NamedTemporaryFile(delete = False, suffix = suffix)
	
	save_options = options.get("save_options", {})
	im.save(tmp.name, **save_options)
	return tmp.name

def process_uploaded_image_2(image, **options):
	extension = get_file_extension(image.name)
	if extension:
		suffix = "." + extension.lower()
	else:
		suffix = None

	tmp = NamedTemporaryFile(delete = True, suffix = suffix)
	image.open('rb')

	keep_reading = True
	while keep_reading:
		content = image.read(64)
		if len(content) == 0:
			keep_reading = False
		else:
			tmp.write(content)
	else:
		tmp.flush()
		tmp.seek(0)
	image.close()


	convert_image_options = {
		"save_options": options.get("save_options", {})
	}
	img_src = convert_image(tmp.name, **convert_image_options)

	uploaded_image = new_local_file(img_src)

	return uploaded_image


def process_image_with_default(image, **options):
	extension = get_file_extension(image.name)
	if extension is None:
		return image
	else:
		extension = extension.lower()
	

	save_options = {}
	
	max_width = options.get("max_width", None)
	if max_width:
		save_options["max_width"] = max_width

	max_height = options.get("max_height", None)
	if max_width:
		save_options["max_height"] = max_height	


	if extension in ["jpg", "jpeg"]:
		save_options["format"] = "JPEG"
		save_options["quality"] = 95
		save_options["optimize"] = True

	elif extension == "png":
		save_options["format"] = "PNG"
		save_options["quality"] = 95
		save_options["optimize"] = True
	
	else:
		pass

	kw_options = {
		"save_options": save_options,
	}
	return process_uploaded_image_2(image, **kw_options)	
	

def download_and_get_local_image_2(url, **kwargs):
	path = download_file(url)
	return new_local_file(path)

def unique_model_slug(obj, texts, max_tries = 10, slug_attribute = "slug", prefix = "", suffix = ""):
	slug_base, extension = slugify(prefix + "-".join(texts) + suffix), ""
	attempts = 0
	while attempts < max_tries:
		attempts += 1
		slug = slug_base + extension
		if db_get_or_none(obj, **{slug_attribute: slug}):
			extension = "-%s" % (attempts)
			continue
		return slug
	raise ohm2_handlers_light_definitions.RunException(**ohm2_handlers_light_errors.NO_UNIQUE_SLUG_FOUND)

from ohm2_handlers_light import utils as h_utils
from . import settings
import os


def country_flag_small_upload_to(instance, filename):	
	filename_full = instance.alpha_3.lower() + "." + filename.rsplit(".", 1)[-1]
	return os.path.join(settings.UPLOAD_TO, filename_full)


"""
def post_delete(sender, **kwargs):	
	try:
		instance = kwargs['instance']
		os.remove( os.path.join(settings.MEDIA_ROOT, instance.avatar.name) )
	except Exception as e:
		pass
"""
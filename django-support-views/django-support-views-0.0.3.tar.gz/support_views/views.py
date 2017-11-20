import logging
import os
import random
from binascii import a2b_base64
from os import path

import six
from django.conf import settings
from . import settings as app_settings
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.views.generic import View

from user_agents import parse
from rest_framework.views import APIView


class SupportLogView(APIView):
    logger_name = "slack"

    def post(self, request):
        log = logging.getLogger(self.logger_name)

        message = self.format_message(self.get_support_data())
        log.info(message)

        return self.generate_response()

    def format_message(self, data):
        return """Message from {user}
using {browser_family} {browser_version}
on {os_family} {os_version}

> {message}

{image}""".format(**data)

    def generate_response(self):
        return HttpResponse("{\"ok\": true}")

    def _dot_version(self, version):
        if isinstance(version, (list, tuple)):
            return ".".join([six.text_type(v) for v in version])
        return version

    def get_support_data(self):
        """ gets all data that will be used to format the support message """
        agent = parse(self.request.META.get("HTTP_USER_AGENT", ""))

        image = self.request.POST.get("image", "")
        if image:
            image = self.save_image(image)

        data = dict(
            user=unicode(getattr(self.request, "user", "Anonymous")),
            browser_family=agent.browser.family,
            browser_version=self._dot_version(agent.browser.version),
            os_family=agent.os.family,
            os_version=self._dot_version(agent.os.version),
            image=image,
            message=self.request.POST.get("message")
        )
        data.update(app_settings.SUPPORT_EXTRA_CONTEXT(self.request))
        return data

    def support_image_filename(self):
        return 'support_image-{}.jpeg'.format(random.randint(0, 10))

    def save_image(self, image_data):
        """ takes a raw data_url and saves it as an image
            @return the saved image URL
        """
        filename = self.support_image_filename()
        image_data = image_data.split(",", 1)[1]
        binary_data = a2b_base64(image_data)
        fd = default_storage.open(filename, 'wb')
        fd.write(binary_data)
        fd.close()
        return path.join(settings.MEDIA_URL, filename)

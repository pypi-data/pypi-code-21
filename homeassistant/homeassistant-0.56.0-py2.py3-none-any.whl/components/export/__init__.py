"""
Support for exporting data.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/export/
"""
import asyncio
import logging
import os
from functools import partial

import voluptuous as vol

from homeassistant.setup import async_prepare_setup_platform
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv
from homeassistant.config import load_yaml_config_file
from homeassistant.const import CONF_NAME, CONF_PLATFORM
from homeassistant.helpers import config_per_platform
from homeassistant.util import slugify
from homeassistant.loader import bind_hass

_LOGGER = logging.getLogger(__name__)

# Platform specific data
ATTR_DATA = 'data'

# Text to notify user of
ATTR_MESSAGE = 'message'

# Target of the notification (user, device, etc)
ATTR_TARGET = 'target'

# Title of notification
ATTR_TITLE = 'title'
ATTR_TITLE_DEFAULT = "Home Assistant"

DOMAIN = 'export'

SERVICE_EXPORT = 'export'

PLATFORM_SCHEMA = vol.Schema({
    vol.Required(CONF_PLATFORM): cv.string,
    vol.Optional(CONF_NAME): cv.string,
}, extra=vol.ALLOW_EXTRA)

EXPORT_SERVICE_SCHEMA = vol.Schema({
    vol.Required(ATTR_MESSAGE): cv.template,
    vol.Optional(ATTR_TITLE): cv.template,
    vol.Optional(ATTR_TARGET): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(ATTR_DATA): dict,
})


@bind_hass
def send_event(hass, message, title=None, data=None):
    """Send an event message."""
    info = {
        ATTR_MESSAGE: message
    }

    if title is not None:
        info[ATTR_TITLE] = title

    if data is not None:
        info[ATTR_DATA] = data

    hass.services.call(DOMAIN, SERVICE_EXPORT, info)


@asyncio.coroutine
def async_setup(hass, config):
    """Set up the Export services."""
    descriptions = yield from hass.async_add_job(
        load_yaml_config_file,
        os.path.join(os.path.dirname(__file__), 'services.yaml'))

    targets = {}

    @asyncio.coroutine
    def async_setup_platform(p_type, p_config=None, discovery_info=None):
        """Set up an export platform."""
        if p_config is None:
            p_config = {}
        if discovery_info is None:
            discovery_info = {}

        platform = yield from async_prepare_setup_platform(
            hass, config, DOMAIN, p_type)

        if platform is None:
            _LOGGER.error("Unknown export service specified")
            return

        _LOGGER.info("Setting up %s.%s", DOMAIN, p_type)
        export_service = None
        try:
            if hasattr(platform, 'async_get_service'):
                export_service = yield from \
                    platform.async_get_service(hass, p_config, discovery_info)
            elif hasattr(platform, 'get_service'):
                export_service = yield from hass.async_add_job(
                    platform.get_service, hass, p_config, discovery_info)
            else:
                raise HomeAssistantError("Invalid export platform")

            if export_service is None:
                _LOGGER.error(
                    "Failed to initialize export service %s", p_type)
                return

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Error setting up platform %s", p_type)
            return

        export_service.hass = hass

        # @asyncio.coroutine
        # def async_export_event(service):
        #     """Handle sending notification message service calls."""
        #     kwargs = {}
        #     message = service.data[ATTR_MESSAGE]
        #     title = service.data.get(ATTR_TITLE)
        #
        #     if title:
        #         title.hass = hass
        #         kwargs[ATTR_TITLE] = title.async_render()
        #
        #     if targets.get(service.service) is not None:
        #         kwargs[ATTR_TARGET] = [targets[service.service]]
        #     elif service.data.get(ATTR_TARGET) is not None:
        #         kwargs[ATTR_TARGET] = service.data.get(ATTR_TARGET)
        #
        #     message.hass = hass
        #     kwargs[ATTR_MESSAGE] = message.async_render()
        #     kwargs[ATTR_DATA] = service.data.get(ATTR_DATA)
        #
        #     yield from export_service.async_send_message(**kwargs)
        #
        # if hasattr(export_service, 'targets'):
        #     platform_name = (
        #         p_config.get(CONF_NAME) or discovery_info.get(CONF_NAME) or
        #         p_type)
        #     for name, target in export_service.targets.items():
        #         target_name = slugify('{}_{}'.format(platform_name, name))
        #         targets[target_name] = target
        #         hass.services.async_register(
        #             DOMAIN, target_name, async_export_event,
        #             descriptions.get(SERVICE_EXPORT),
        #             schema=EXPORT_SERVICE_SCHEMA)
        #
        # platform_name = (p_config.get(CONF_NAME) or SERVICE_EXPORT)
        # platform_name_slug = slugify(platform_name)
        #
        # hass.services.async_register(
        #     DOMAIN, platform_name_slug, async_export_event,
        #     descriptions.get(SERVICE_EXPORT), schema=EXPORT_SERVICE_SCHEMA)
        #
        # return True

    setup_tasks = [async_setup_platform(p_type, p_config) for p_type, p_config
                   in config_per_platform(config, DOMAIN)]

    if setup_tasks:
        yield from asyncio.wait(setup_tasks, loop=hass.loop)

    return True


class BaseExportService(object):
    """An abstract class for export services."""

    hass = None

    def send_event(self, message, **kwargs):
        """Send an event.

        kwargs can contain ATTR_TITLE to specify a title.
        """
        raise NotImplementedError()

    def async_send_event(self, message, **kwargs):
        """Send an event.

        kwargs can contain ATTR_TITLE to specify a title.
        This method must be run in the event loop and returns a coroutine.
        """
        return self.hass.async_add_job(
            partial(self.send_event, message, **kwargs))

from django.conf import settings
import os

# Path to the service worker implementation.
PWA_SERVICE_WORKER_PATH = getattr(settings, 'PWA_SERVICE_WORKER_PATH',
                                  os.path.join(os.path.abspath(
                                               os.path.dirname(__file__)),
                                               'templates',
                                               'serviceworker.js'))

# App parameters to include in manifest.json and appropriate meta tags
PWA_NAME = getattr(settings, 'PWA_NAME', 'Molo')
PWA_DESCRIPTION = getattr(settings, 'PWA_DESCRIPTION',
                          'Molo Progressive Web App')
PWA_ROOT_URL = getattr(settings, 'PWA_ROOT_URL', '/')
PWA_THEME_COLOR = getattr(settings, 'PWA_THEME_COLOR', '#000')
PWA_DISPLAY = getattr(settings, 'PWA_DISPLAY', 'standalone')
PWA_START_URL = getattr(settings, 'PWA_START_URL', '/')
PWA_ICONS = getattr(settings, 'PWA_ICONS', [
    {
        'src': '/',
        'sizes': '160x160'
    }
])
PWA_FCM_API_KEY = getattr(settings, 'PWA_FCM_API_KEY', '')
PWA_FCM_MSGSENDER_ID = getattr(settings, 'PWA_FCM_MSGSENDER_ID', '')

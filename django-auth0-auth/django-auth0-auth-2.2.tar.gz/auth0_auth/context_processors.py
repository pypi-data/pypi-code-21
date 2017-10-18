from django.conf import settings
from django.core.urlresolvers import reverse
import uuid


def auth0(request):
    state = request.session.get('state', str(uuid.uuid4()))
    request.session['state'] = state

    return {
        'AUTH0_DOMAIN': getattr(settings, 'AUTH0_DOMAIN'),
        'AUTH0_CLIENT_ID': getattr(settings, 'AUTH0_CLIENT_ID'),
        'AUTH0_CLIENT_SECRET': getattr(settings, 'AUTH0_CLIENT_SECRET'),
        'AUTH0_SCOPE': getattr(settings, 'AUTH0_SCOPE', 'openid email'),
        'AUTH0_CALLBACK_URL': request.build_absolute_uri(reverse('auth0_callback')),
        'AUTH0_STATE': state,
    }

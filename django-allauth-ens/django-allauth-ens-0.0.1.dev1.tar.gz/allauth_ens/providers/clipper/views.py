# -*- coding: utf-8 -*-
from allauth_cas import views

from .provider import ClipperProvider


class ClipperCASAdapter(views.CASAdapter):
    provider_id = ClipperProvider.id
    url = 'https://cas.eleves.ens.fr'
    version = 3


login = views.CASLoginView.adapter_view(ClipperCASAdapter)
callback = views.CASCallbackView.adapter_view(ClipperCASAdapter)
logout = views.CASLogoutView.adapter_view(ClipperCASAdapter)

from django.conf import settings


def recaptcha_site_key(request):
    print('olaaar')
    return {'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY}

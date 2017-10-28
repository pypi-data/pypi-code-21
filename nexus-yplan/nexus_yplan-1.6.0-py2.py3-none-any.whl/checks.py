from django.conf import settings
from django.core.checks import Error, Tags, register


def register_checks():
    register(Tags.compatibility)(check_requirements)


def check_requirements(app_configs, **kwargs):
    errors = []

    if getattr(settings, 'NEXUS_SKIP_INSTALLED_APPS_REQUIREMENTS', False):
        reqs = ()
    else:
        reqs = ('django.contrib.admin', 'django.contrib.auth', 'django.contrib.sessions')

    for req in reqs:
        if req not in settings.INSTALLED_APPS:
            errors.append(Error(
                "Nexus depends on '{}'".format(req),
                id='nexus.E001',
                hint="Add '{}' to INSTALLED_APPS or set NEXUS_SKIP_INSTALLED_APPS_REQUIREMENTS = True.".format(req)
            ))

    return errors

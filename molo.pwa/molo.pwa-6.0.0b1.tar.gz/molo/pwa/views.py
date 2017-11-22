import json
from django.views.generic import View
from django.http import HttpResponse
from django.shortcuts import render
from fcm_django.models import FCMDevice

from . import app_settings


class RegistrationTokenView(View):
    def post(self, request, *args, **kwargs):
        if hasattr(request.user, 'profile'):
            data = json.loads(request.body)
            profile = request.user.profile
            profile.fcm_registration_token = data['registration_id']
            profile.save()
            device, created = FCMDevice.objects.get_or_create(
                registration_id=data['registration_id'], defaults={
                    'user': request.user,
                    'name': request.user.username, 'type': 'web'})
            return HttpResponse('Token Updated')
        return HttpResponse('User has no profile')


def service_worker(request):
    response = HttpResponse(open(app_settings.PWA_SERVICE_WORKER_PATH).read(),
                            content_type='application/javascript')
    return response


def manifest(request):
    return render(request, 'manifest.json', {
        setting_name: getattr(app_settings, setting_name)
        for setting_name in dir(app_settings)
        if setting_name.startswith('PWA_')
    })


def fcm(request):
    return render(request, 'fcm.js',
                  content_type='application/javascript')


def toast(request):
    return render(request, 'toast.min.js',
                  content_type='application/javascript')

from django.shortcuts import render
import re

from django.contrib.auth import get_user_model
User = get_user_model()

def wlogin(request):

    if request.user.is_authenticated:
        return render(request, 'wlogged.html', {'data': 'wixot_user'})
    else:
        return render(request, 'wlogin.html')


def wlogged(request):
    user = request.user


    mail_adress = re.split('@' , user.email)

    if mail_adress[1] == 'wixot.com':
        user.is_staff = True
        user.save()
        return render(request, 'wlogged.html', {'data' :'wixot_user'})
    else:
        db_user = User.objects.get(username = user.username)
        db_user.delete()
        return render(request , 'wlogged.html' ,{'data' :'google_user'})

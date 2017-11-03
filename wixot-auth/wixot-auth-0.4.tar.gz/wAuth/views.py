from django.shortcuts import render
import re
from django.contrib.auth.models import User

def wlogin(request):

    if request.user.is_authenticated:
        return render(request, 'wlogged.html', {'data': 'wixot_user'})
    else:
        return render(request, 'wlogin.html')


def wlogged(request):
    user = request.user

    try:
        mail_adress = re.split('@' , user.email)

        db_user = User.objects.get(username = user.username)
        if mail_adress[1] == 'wixot.com':
            user.is_staff = True
            user.save()
            return render(request, 'wlogged.html', {'data' :'wixot_user'})
        else:
            db_user.delete()
            return render(request , 'wlogged.html' ,{'data' :'google_user'})
    except:
        return render(request,'wlogin.html')
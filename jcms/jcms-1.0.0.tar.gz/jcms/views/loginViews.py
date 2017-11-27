from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from jcms.forms import LoginForm
from django.contrib import messages


class LoginView(TemplateView):
    template_name = 'jcms-admin/login/login.html'

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)

            if user is None:
                messages.error(self.request, 'Username or Password are incorrect')
                return render(request, self.template_name, {'form': form})
            elif not user.is_active:
                messages.success(self.request, 'User not active. Please activate the user or contact the admin')
                return render(request, self.template_name, {'form': form})
            else:
                login(request, user)
                return redirect('jcms:optionList')


def logout_user(request):
    logout(request)
    return redirect('jcms:login')

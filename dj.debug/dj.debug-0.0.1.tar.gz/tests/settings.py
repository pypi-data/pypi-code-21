
SECRET_KEY = "NOTSOSECRET"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'ATOMIC_REQUESTS': True,
    }
}

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth"]

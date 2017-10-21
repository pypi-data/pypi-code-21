import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '7nti!w-x$i=twbb=rwqg-u@un(!&^jzt7dhu(q-pnk2f4h2sau'

DEBUG = True

ALLOWED_HOSTS = [
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

INSTALLED_APPS = [
    'cosmicdb',
    'dal',
    'dal_select2',
    'crispy_forms',
    'django_tables2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

ROOT_URLCONF = 'cosmicdb.urls'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATIC_URL = '/static/'

COSMICDB_SITE_TITLE = 'CosmicDB'
COSMICDB_ALLOW_SIGNUP = False
AUTH_USER_MODEL = 'cosmicdb.User'
LOGIN_URL = '/login/'
CRISPY_TEMPLATE_PACK = 'bootstrap3'
DJANGO_TABLES2_TEMPLATE = 'django_tables2/bootstrap-responsive.html'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'test@test.com'
EMAIL_HOST_PASSWORD = 'testpassword'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL_NAME = COSMICDB_SITE_TITLE

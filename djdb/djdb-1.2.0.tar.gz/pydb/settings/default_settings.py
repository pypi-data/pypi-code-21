import os
dir = os.getcwd()
prepath = os.getcwd()
while not os.path.exists('db'):
    dir = os.path.abspath(os.path.join(dir,'..'))
    os.chdir(dir)

DB_DIR = os.path.join(os.getcwd(),'db')
os.chdir(prepath)
SECRET_KEY = 'g3qn)wlmzlm%e_9i7&9k%3zche#3%a42rq@ls1gg^!))qihpq&'

INSTALLED_APPS = ['db', ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DB_DIR, 'db.sqlite3'),
    }
}





import os
import webbrowser
from threading import Timer
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

if __name__ == "__main__":
    try:
        import rxncon_site.settings
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rxncon_site.settings")
    except ImportError:
        import src.rxncon_site.settings
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.rxncon_site.settings")

application = get_wsgi_application()
t = Timer(4, webbrowser.open, args=['http://127.0.0.1:8000/'], kwargs=None)
t.start()
call_command('runserver',  '127.0.0.1:8000')



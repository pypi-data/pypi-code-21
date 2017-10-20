#Generated with django-for-android

""" Start Django in multithreaded mode

It allows for debugging Django while serving multiple requests at once in
multi-threaded mode.

"""

import sys
import os

try:
    from jnius import autoclass
    JNIUS = True
except:
    JNIUS = False
    pass

if not '--nodebug' in sys.argv:
    log_path = os.path.abspath("{{APP_LOGS}}")

    if not os.path.exists(log_path):
        os.mkdir(log_path)
        #os.makedirs(log_path, exist_ok=True)

    print("Logs in {}".format(log_path))
    sys.stdout = open(os.path.join(log_path, "stdout.log"), "w")
    sys.stderr = open(os.path.join(log_path, "stderr.log"), "w")

    os.environ['STDOUT'] = os.path.join(log_path, "stdout.log")
    os.environ['STDERR'] = os.path.join(log_path, "stderr.log")


print("Starting Django Server")
from wsgiref import simple_server
from django.core.wsgi import get_wsgi_application

sys.path.append(os.path.join(os.path.dirname(__file__), "{{NAME}}"))


#----------------------------------------------------------------------
def django_wsgi_application():
    """"""
    print("Creating WSGI application...")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{NAME}}.settings")
    application = get_wsgi_application()
    return application


#----------------------------------------------------------------------
def main():
    """"""

    if JNIUS:
        # Create INTENT_FILTERS in environ
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        intent = activity.getIntent()
        intent_data = intent.getData()
        try:
            file_uri= intent_data.toString()
            os.environ["INTENT_FILTERS"] = file_uri
        except AttributeError:
            pass


    if {{APP_MULTITHREAD}}:
        import socketserver
        class ThreadedWSGIServer(socketserver.ThreadingMixIn, simple_server.WSGIServer):
            pass
        httpd = simple_server.make_server('{{IP}}' , {{PORT}}, django_wsgi_application(), server_class=ThreadedWSGIServer)
    else:
        httpd = simple_server.make_server('{{IP}}' , {{PORT}}, django_wsgi_application())

    httpd.serve_forever()
    print("Django for Android serving on {}:{}".format(*httpd.server_address))


main()

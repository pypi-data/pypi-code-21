"""A2D-Diary web app. Create and encode paper diaries automatically"""
__version__ = '0.1'

#from subprocess import call
import threading
import webbrowser
import time
from marking_server import app
import waitress


def launch_browser():
    """Launches the app"""
    time.sleep(3)
    webbrowser.open("http://localhost:8000/static/index.html", new=0, autoraise=True)


if __name__ == "__main__":
    LAUNCH_THREAD = threading.Thread(target=launch_browser)
    LAUNCH_THREAD.start()
    waitress.serve(app, port=8000)
    LAUNCH_THREAD.join()

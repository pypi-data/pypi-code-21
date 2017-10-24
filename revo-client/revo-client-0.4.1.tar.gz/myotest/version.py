import os

version_py = os.path.join(os.path.dirname(__file__), '../VERSION.txt')

try:
    with open(version_py, 'r') as fh:
        version_txt = open(
            version_py).read().strip().split('=')[-1].replace('"', '').strip()
except Exception:
    version_txt = "dev"
VERSION = version_txt

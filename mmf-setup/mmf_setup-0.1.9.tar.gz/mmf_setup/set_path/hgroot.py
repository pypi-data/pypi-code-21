"""Importing this module will insert HGROOT to the start of sys.path."""
import subprocess
import sys

try:
    HGROOT = subprocess.check_output(['hg', 'root']).strip()
    if HGROOT not in sys.path:
        sys.path.insert(0, HGROOT)
    import mmf_setup
    mmf_setup.HGROOT = HGROOT
except subprocess.CalledProcessError:
    # Could not run hg or not in a repo.
    pass

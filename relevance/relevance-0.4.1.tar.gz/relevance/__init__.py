"""
Content pipeline manager.

Relevance is a software suite that aims to address the common and recurring problem
of ingesting content, delivering it, searching it with relevant results and analyzing
its usage by the end-users, acting on the analytic data to provide the best results
possible.
"""

# Package version
__version__ = '0.4.1'


def init_app():
    """
    Initialize the application.
    """
    import os
    import sys

    base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    for path in ['./var', '/var/lib/relevance']:
        full_path = '{0}/{1}'.format(base_path, path)
        if full_path not in sys.path:
            sys.path.append(full_path)


# Bootstrap
init_app()

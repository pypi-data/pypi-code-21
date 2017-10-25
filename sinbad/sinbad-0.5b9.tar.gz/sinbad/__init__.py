'''Automated Structure Inference and Binding of Data'''

from sinbad.datasource import DataSource, Data_Source
from sinbad.version import __version__
from sinbad.cacher import NEVER_CACHE, NEVER_RELOAD

from sinbad import prefs
from sinbad import comm

prefs.increment_run_count()
__rc = int(prefs.get_pref("run_count"))
if __rc == 1:
    comm.register_install()
    print("Welcome to Sinbad (version {}).\n".format(__version__) + 
          "For help and documentation, visit {}".format(
                prefs.get_pref("server_base")))
elif __rc == 10:
    prefs.set_pref("share_usage", True)
    prefs.preferences(first_time = True)
elif __rc % 250 == 0:
    comm.register_milestone()


prefs.apply_preferences()

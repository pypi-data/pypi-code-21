## Command line interface to analysis runner
import sys
import os

import analysis_template_runner

# Note this string in stdout is used by the template launcher to signal a valid startup. Don't change!
print "Nutonian Analysis Template Launcher"
sys.stdout.flush() # ensure our watcher sees it

runner = analysis_template_runner.analysis_template_runner()

runner.run_args(sys.argv[1:])

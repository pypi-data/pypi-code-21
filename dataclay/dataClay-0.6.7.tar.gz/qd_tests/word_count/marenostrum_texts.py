from dataclay import runtime
from dataclay.api import init
import gevent
import itertools
import os
import sys

from WordCount import Text, TextCollection


print "<marenostrum_texts.py> Pre-init"
storage_properties_path = sys.argv[1]
init(storage_properties_path)
print "<marenostrum_texts.py> Post-init"



__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2016 Barcelona Supercomputing Center (BSC-CNS)'


if __name__ == "__main__":
    print "<marenostrum_texts.py> In __main__"

    print " # Initializing TextCollection"

    text_collection = TextCollection()

    # Read basic information from command arguments
    text_files_path = sys.argv[2]

    spawned = list()
    exec_envs = runtime.get_execution_environments_info().keys()
    print " # Using the following Execution Environments: %s" % ", ".join(map(str, exec_envs))

    for f, eeid in zip(os.listdir(text_files_path),
                       itertools.cycle(exec_envs)):
        current_text_file = os.path.join(text_files_path, f)
        new_text = Text()
        new_text.make_persistent(dest_ee_id=eeid)

        print " # Ready to put contents of %s into Text %s which has been made persistent on %s" % \
              (current_text_file, Text, eeid)
        spawned.append(gevent.spawn(
            new_text.populate_from_file, current_text_file))
        text_collection.add_text(new_text)

    print " # Spawned everything, let's wait for all gevent threads..."
    for i, glet in enumerate(spawned):
        print " ## greenlet #%d returned %d" % (i, glet.get())

    for t in text_collection.texts:
        print " ## A Text has %d words in it" % len(t.words)

    text_collection.make_persistent("wordcount_source")
    print " # TextCollection has been made persistent (hopefully) with alias `wordcount_source`"

    print "<marenostrum_text.py> FINISH __main__"

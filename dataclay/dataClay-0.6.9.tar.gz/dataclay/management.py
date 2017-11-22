from dataclay import runtime
from dataclay.conf import settings
from dataclay.core import constants
from dataclay.core.management.stubs import babel_stubs_load
from dataclay.core.paraver import trace_function
from dataclay.managers.classes.filesystem import deploy_class
import logging
import os
import yaml


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

_babel_data = None
logger = logging.getLogger(__name__)


def prepare_storage(stubs_folder=None):
    """Ensure (force creation if not exists) the STUB_STORAGE folder.

    By default, the settings.stubs_folder is used. You can override by providing
    the stubs_folder argument.
    """
    if not stubs_folder:
        stubs_folder = settings.stubs_folder

    if not os.path.exists(stubs_folder):
        os.mkdir(stubs_folder)

    if not os.path.isdir(stubs_folder):
        raise IOError("The `StubsClasspath` is not a folder --check file and permissions")


@trace_function
def load_babel_data(stubs_folder=None):
    """Load all Babel Stub data from the cached file.

    By default, the settings.stubs_folder is used. You can override by providing
    the stubs_folder argument.

    :return: A dictionary (the parsed YAML).
    """
    global _babel_data
    if _babel_data is None:
        with open(os.path.join(stubs_folder or settings.stubs_folder,
                               "babelstubs.yml"),
                  'rb') as f:
            _babel_data = babel_stubs_load(f)

    return _babel_data


@trace_function
def prepare_stubs(contracts):
    """Prepare the internal stub files (at <StubsClassPath>/*)

    :param collections.Iterable contracts: UUID for all the contracts. Will be used to contact LogicModule.
    :return: Nothing, the file is created but there is no return.

    Upon execution of this, the babelstubs.yml will contain the Babel data,
    and all the stubs (not the babel ones) will have their own files in the
    same folder.
    """
    client = runtime.ready_clients["@LM"]

    babel_data = client.get_babel_stubs(settings.current_id,
                                        settings.current_credential, contracts)

    with open(os.path.join(settings.stubs_folder, "babelstubs.yml"), 'wb') as f:
        f.write(babel_data)

    all_stubs = client.get_stubs(settings.current_id, settings.current_credential,
                                 constants.lang_codes.LANG_PYTHON,
                                 contracts)

    # Parsing both this file and the StubInfo classes is costly,
    # but there is no workaround in order to reach the namespace.
    babel_parsed = yaml.load(babel_data)

    for key, value in all_stubs.iteritems():
        if key.endswith("Yaml"):
            # We decide to ignore the Babel stubs returned by get_stubs, because we have
            # already done the get_babel_stubs call and are using that instead
            continue
        stub_info = yaml.load(babel_parsed[key])
        namespace = stub_info.namespace
        with open(os.path.join(settings.stubs_folder, "%s" % key), 'wb') as f:
            f.write(value)


@trace_function
def deploy_stubs(stubs_folder=None):
    """Perform the actual deployment of classes (python files).

    By default, the settings.stubs_folder is used. You can override by providing
    the stubs_folder argument.
    """
    if not stubs_folder:
        stubs_folder = settings.stubs_folder

    # Use the stored StubInfo (which is a YAML)
    babel_data = load_babel_data(stubs_folder)
    source_deploy = os.path.join(stubs_folder, 'sources')
    try:
        os.makedirs(source_deploy)
    except OSError as e:
        if e.errno != 17:
            # Not the "File exists" expected error, reraise it
            raise

    for class_data in babel_data:
        namespace = class_data.namespace
        full_name = class_data.className

        logger.debug("Deploying stub for %s::%s" % (namespace, full_name))
    
        try:
            # ToDo: to avoid clashes, in the future, maybe the full name should include the namespace
            # like: ... stubs_folder, "%s.%s" % (namespace, full_name ...
            with open(os.path.join(stubs_folder, full_name), 'rb') as f:
                source = f.read()
        except IOError:
            source = ""
    
        deploy_class(namespace, full_name, source, "", source_deploy)


@trace_function
def track_local_available_classes():
    """Track the available classes into the runtime.local_available_classes.

    Note that no deployment is done in this function: the deployment should be
    done beforehand through the deploy_stubs function.

    This function returns all the contracts that have been found.
    """
    babel_data = load_babel_data()
    contracts = set()

    for class_data in babel_data:
        contracts.update(class_data.contracts)
        namespace = class_data.namespace
        full_name = class_data.className

        runtime.local_available_classes[class_data.classID] = \
            "%s.%s" % (namespace, full_name)

    logger.info("Using the following contracts: %s", contracts)
    return contracts

from tempfile import mkdtemp
from dataclay.core import constants
from dataclay.api import init
from dataclay.managers.classes.factory import MetaClassFactory
import dataclay
from dataclay.debug.utils import prepare_namespace, create_users, prepare_dataclay_contrib
import model
import inspect
import unittest
import yaml
from dataclay.conf import settings
import sys
import os
import uuid


"""Tests for the dataClay LogicModule."""
__author__ = 'Enrico La Sala <enrico.lasala@bsc.es>'
__copyright__ = '2017 Barcelona Supercomputing Center (BSC-CNS)'

client_properties_path = "./client.properties"
storage_properties_path = "./storage.properties"
stubs_path = mkdtemp()
init(client_properties_path, minimal=True)

# FIXME: Correcting all the tests (Don't really test nothing at the moment)


class LogicModuleTestsContainer(unittest.TestCase):
        client = dataclay.runtime.ready_clients["@LM"]

        users = create_users()
        print "users:", users

        # Start by the public contract
        public_contract = prepare_dataclay_contrib(users.registrator, "consumer")
        print "public_contract:", public_contract

        populate_data = prepare_namespace(users.registrator, "consumer", namespace="KMeans")
        print "populate_data:", populate_data

        def test_new_class(self):

                try:

                    consumer_id = self.client.get_account_id("consumer")
                    consumer = (consumer_id,
                                "consumer".encode('utf-16-be'))

                    print "consumer_id:", consumer_id
                    print "consumer:", consumer

                    registrator_id = self.client.get_account_id("registrator")
                    registrator = (registrator_id,
                                   "registrator".encode('utf-16-be'))

                    mfc = MetaClassFactory(namespace="KMeans",
                                           responsible_account="registrator")
                    mfc.add_class(model.Board)
                    mfc.add_class(model.Fragment)
                    print "mfc:", mfc

                    result = self.client.new_class(registrator_id, registrator,
                                                   constants.lang_codes.LANG_PYTHON, mfc.classes)
                    print "result:", result
                    # Classes are created and stored in result that is a dict with name as key and Metaclass as value

                    # result['Fragment'].abstract = True
                    # print inspect.getmembers(result['Fragment'], lambda a: not (inspect.isroutine(a)))
                    self.assertEqual(result['Fragment'].namespace, 'KMeans')
                    self.assertEqual(result['Fragment'].name, 'Fragment')
                    self.assertEqual(result['Fragment'].parentType, None)
                    self.assertEqual(type(result['Fragment'].properties), list)
                    self.assertEqual(type(result['Fragment'].operations), list)
                    self.assertFalse(result['Fragment'].isAbstract)

                    print result['Fragment'].languageDepInfos
                    print result['Fragment'].namespaceID

                    if len(result) > 1:
                        board_info = result['Board']
                        print "board_info, res len >1:", board_info
                        fragment_info = result['Fragment']
                    elif len(result) == 0:
                        print "Seems that the classes they had already been registered"
                        board_info = self.client.get_class_info(registrator, registrator_id, 'Board')
                        fragment_info = self.client.get_class_info(registrator, registrator_id, 'Fragment')
                        print "board_info, res len == 0:", board_info
                    else:
                        print " ERROR: Didn't expect that number of elements, received:"
                        print "---------------------------------------------------------"
                        print result
                        raise RuntimeError("Could not initialize registered classes successfully")

                finally:
                    pass

        def test_get_stubs(self):
            try:
                registrator_id = self.users.registrator[0]
                consumer_id = self.users.consumer[0]

                get_stubs = self.client.get_stubs(registrator_id, self.users.registrator,
                                                  constants.lang_codes.LANG_PYTHON, [self.public_contract])
                get_babel_stubs = self.client.get_babel_stubs(registrator_id, self.users.registrator,
                                                              [self.public_contract])

                print "get_stubs: "
                print get_stubs
                print type(get_stubs)

                print "get_babel_stubs: "
                print type(get_babel_stubs)
                print get_babel_stubs
            finally:
                pass

        @unittest.skip("To correct")
        def test_new_session(self):
            try:

                babel_stubs = self.client.get_babel_stubs(self.users.registrator[0],
                                                          self.users.registrator, [self.public_contract])

                config_file = os.path.expanduser(storage_properties_path)

                settings.load_properties(config_file)

                # print babel_stubs
                # deploy_stubs(settings.stubs_folder)

                # In all cases, track (done through babelstubs YAML file)
                # track_local_available_classes()

                # Ensure they are in the path (high "priority")
                sys.path.insert(0, os.path.join(settings.stubs_folder, 'sources'))

                print "settings.datasets:", settings.datasets
                print "settings.dataset_for_store:", settings.dataset_for_store

                session_id = self.client.new_session(self.users.registrator[0], self.users.registrator,
                                                     [self.public_contract], settings.datasets,
                                                     settings.dataset_for_store,constants.lang_codes.LANG_PYTHON)

                print "session_id: ", session_id
            finally:
                pass

        def test_perform_set_of_new_accounts(self):
            try:

                self.assertIsNotNone(self.users)

                registrator_id = self.users.registrator[0]
                consumer_id = self.users.consumer[0]

                reg_username = self.users.registrator[1]
                cons_username = self.users.consumer[1]

                self.assertEqual(registrator_id, self.client.get_account_id("registrator"))
                self.assertEqual(consumer_id, self.client.get_account_id("consumer"))
                self.assertEqual(reg_username, "registrator")
                self.assertEqual(cons_username, "consumer")

                # ToDo: Try to perform an assertEqual for the role

            finally:
                pass


if __name__ == '__main__':
    unittest.main()

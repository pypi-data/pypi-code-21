

import requests
import arrow
import copy
import unittest

from django.test import Client

from datetime import datetime


from django_framework.django_helpers.manager_helpers import get_manager
from django_framework.django_helpers.serializer_helpers import get_serializer

class BasicRunTest(unittest.TestCase):
    model_name = 'basic_test_run'

    @classmethod
    def setUpClass(cls):
        cls.manager = get_manager(manager_name = cls.model_name)
        cls.serializer = get_serializer(serializer_name = cls.model_name)
        cls.admin_serializer = get_serializer(serializer_name = cls.model_name, version = 'admin')

        cls.model_field_names = ["id", "created_at", "last_updated", "uuid",
                                 
                                 "basic_profile_run_fk_field", "basic_profile_run", "normal_text_field", "write_once_text_field", "read_only_text_field", "hidden_text_field", "encrypted_text_field", "encrypted_text_strict_field", "epoch_time_field", "choices_field"]


        cls.payload = {
            "basic_profile_run_fk_field": None,
            "basic_profile_run" : None, 
            "write_once_text_field" :  "write_once",
            "read_only_text_field" :  "read_only",
            "hidden_text_field" :     "hidden",
            "encrypted_text_field" :  "encrypted_me",
            "encrypted_text_strict_field" : "encrypt_me_but_you_cant_read",
            "epoch_time_field" : 1,
            "choices_field" : 0,

            }

    def tests_get_manager(self):
        '''Getting the manager from various names'''
        manager = get_manager(manager_name = self.model_name)
        self.assertEqual(manager.__name__, "BasicTestRunManager", "Did not get correct manager: basic_test_run")
        self.assertEqual(manager, self.manager, "The manager we get for the class setup is not equal!")


        manager = get_manager(manager_name = 'BasicTestRun')
        self.assertEqual(manager.__name__, "BasicTestRunManager", "Did not get correct manager: BasicTestRun")    
        
        manager = get_manager(manager_name = 'BasicTestRunManager')
        self.assertEqual(manager.__name__, "BasicTestRunManager", "Did not get correct manager: BasicTestRunManager")    
        
        manager = get_manager(manager_name = 'basic_test_run_manager')
        self.assertEqual(manager.__name__, "BasicTestRunManager", "Did not get correct manager: basic_test_run_manager")    

    def tests_manager_create_empty(self):
        '''Test the manager create!'''
        payload = {}
        objs = self.manager.create(Serializer=self.serializer, data=payload)
        
        
        # make sure it has all the proper attributes:
        for field in self.model_field_names:
            self.assertEqual(hasattr(objs[0], field), True, 'We are missing a field: ' + field)
        
        self.assertEqual(hasattr(objs[0], 'this_is_not_a_field'), False, '(sanity check) Found a field that shouldnt be here: ' + field)

    
    def tests_manager_create_default(self):
        payload = self.payload
            
        objs = self.manager.create(Serializer=self.serializer, data=payload)
        model = objs[0]
        self.assertEqual(getattr(model, 'basic_profile_run_fk_field'), None)
        self.assertEqual(getattr(model, 'basic_profile_run').all().exists(), False)
        self.assertEqual(getattr(model, 'write_once_text_field'), "write_once")
        self.assertEqual(getattr(model, 'read_only_text_field'), None)
        self.assertEqual(getattr(model, 'hidden_text_field'), None)
#         self.assertEqual(getattr(model, 'encrypted_text_field'), "encrypted_me")
        self.assertGreater(len(getattr(model, 'encrypted_text_field')), 30, 'Encrypted stirngs should be longer!')

#         self.assertEqual(getattr(model, 'encrypted_text_strict_field'), "encrypt_me_but_you_cant_read")
        self.assertGreater(len(getattr(model, 'encrypted_text_strict_field')), 30, 'Encrypted strings should be longer!')

        self.assertIsInstance(getattr(model, 'epoch_time_field'), datetime)
        self.assertEqual(getattr(model, 'choices_field'), 0)

    def tests_manager_create_admin(self):
        payload = self.payload
        
        objs = self.manager.create(Serializer=self.admin_serializer, data=payload)
        model = objs[0]
        self.assertEqual(getattr(model, 'basic_profile_run_fk_field'), None)
        self.assertEqual(getattr(model, 'basic_profile_run').all().exists(), False)
        self.assertEqual(getattr(model, 'write_once_text_field'), "write_once")
        self.assertEqual(getattr(model, 'read_only_text_field'), "read_only")
        self.assertEqual(getattr(model, 'hidden_text_field'), "hidden")
#         self.assertEqual(getattr(model, 'encrypted_text_field'), "encrypted_me")
        self.assertGreater(len(getattr(model, 'encrypted_text_field')), 30, 'Encrypted stirngs should be longer!')

#         self.assertEqual(getattr(model, 'encrypted_text_strict_field'), "encrypt_me_but_you_cant_read")
        self.assertGreater(len(getattr(model, 'encrypted_text_strict_field')), 30, 'Encrypted strings should be longer!')

        self.assertIsInstance(getattr(model, 'epoch_time_field'), datetime)
        self.assertEqual(getattr(model, 'choices_field'), 0)

    def tests_manager_update_no_errors(self):
        payload = self.payload
        
        objs = self.manager.create(Serializer=self.admin_serializer, data=payload)
        model = objs[0]
        
        
        update_payload = {"choices_field" : 1, "epoch_time_field" : 30}
        objs = self.manager.update(Serializer=self.serializer, data=update_payload, model = model)
        model_updated = objs[0]
        
        self.assertEqual(getattr(model_updated, 'basic_profile_run_fk_field'), None)
        self.assertEqual(getattr(model_updated, 'basic_profile_run').all().exists(), False)
        self.assertEqual(getattr(model_updated, 'write_once_text_field'), "write_once")
        
        self.assertEqual(getattr(model_updated, 'read_only_text_field'), "read_only")
        self.assertEqual(getattr(model_updated, 'hidden_text_field'), "hidden")
#         self.assertEqual(getattr(model, 'encrypted_text_field'), "encrypted_me")
        self.assertGreater(len(getattr(model_updated, 'encrypted_text_field')), 30, 'Encrypted stirngs should be longer!')

#         self.assertEqual(getattr(model, 'encrypted_text_strict_field'), "encrypt_me_but_you_cant_read")
        self.assertGreater(len(getattr(model_updated, 'encrypted_text_strict_field')), 30, 'Encrypted strings should be longer!')

        self.assertEqual(arrow.get(getattr(model_updated, 'epoch_time_field')).timestamp, 30)
        self.assertEqual(getattr(model_updated, 'choices_field'), 1)
        
    def tests_manager_update_write_once(self):
        payload = self.payload
        
        objs = self.manager.create(Serializer=self.admin_serializer, data=payload)
        model = objs[0]
        
        update_payload = {"write_once_text_field" : 1}
        try:
            objs = self.manager.update(Serializer=self.serializer, data=update_payload, model = model)
            is_valid = False
        except Exception:
            # this is good. its supposed to go here!
            is_valid = True
        finally:
            if is_valid == False:
                self.assertEqual(False, True, 'Did not raise a proper exception when setting write once text field!')

    def test_manager_delete(self):
        payload = self.payload
        
        objs = self.manager.create(Serializer=self.admin_serializer, data=payload)
        model = objs[0]
        
        response = self.manager.delete(model = objs)
        
        self.assertEqual(response, [{'status': True}])
        
        try:
            model.refresh_from_db()
        except Exception as e:
            if str(e).find('matching query does not exist.') < 0:
                raise Exception('Did not properly delete!')
        
    
    def test_manager_get(self):
        
        payload = copy.copy(self.payload)
        payload['normal_text_field'] = 'get1'
        objs = self.manager.create(Serializer=self.admin_serializer, data=payload)
        model1 = objs[0]
        
        objs = self.manager.create(Serializer=self.admin_serializer, data=payload)
        model2 = objs[0]
        
        # testing the filters
        objs = self.manager.get_by_query(query_params = {'filter' : {'normal_text_field' : 'get1'}})  # so we start with 0. at least true last few times!
        
        self.assertEqual(len(objs), 2, 'Do you have the correct number?')
    
        
        objs = self.manager.get_by_query(query_params = {'filter' : {'normal_text_field' : 'getaksdfasdf'}})  # so we start with 0. at least true last few times!
        self.assertEqual(len(objs), 0, 'Do you have the correct number?')
        
        # testing the order_by
        objs = self.manager.get_by_query(query_params = {'filter' : {'normal_text_field' : 'get1'}, 'order_by' : ['-created_at']})  # so we start with 0. at least true last few times!
        self.assertEqual(len(objs), 2, 'Do you have the correct number?')
        
        starttime = objs[0].created_at
        
        for x in objs:
            if x.created_at < starttime:
                raise ValueError('this isnt sorted correct')
            starttime = x.created_at


def main():
    
    pass


if __name__ == '__main__':
    main()
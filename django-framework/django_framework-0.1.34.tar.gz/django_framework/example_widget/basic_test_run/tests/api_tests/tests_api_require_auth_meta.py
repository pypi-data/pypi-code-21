

import requests
import arrow
import copy
import unittest
import json

from django.test import Client

from datetime import datetime


from django_framework.django_helpers.manager_helpers import get_manager
from django_framework.django_helpers.serializer_helpers import get_serializer
from __builtin__ import True


class BasicApiTest(unittest.TestCase):
    model_name = 'basic_test_run'
#     base_url = 'http://localhost:8000'
    base_url = ''
    
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
            "normal_text_field" :  "basic_api_test",
            "write_once_text_field" :  "write_once",
            "read_only_text_field" :  "read_only",
            "hidden_text_field" :     "hidden",
            "encrypted_text_field" :  "encrypted_me",
            "encrypted_text_strict_field" : "encrypt_me_but_you_cant_read",
            "epoch_time_field" : 1,
            "choices_field" : 0,
            }

        cls.session = Client()


    def tests_get(self):
        
        # lots of things to test on get!!
        response = self.session.get('/{model_name}/models/'.format(model_name = self.model_name), MODEL_META='BasicTestRunRequireAuthMeta')
        self.assertGreater(response.status_code, 300) # could be anything but in the 400 and 500 range!
        
    def tests_put(self):
        
        # lots of things to test on get!!
        response = self.session.put('/{model_name}/models/'.format(model_name = self.model_name), MODEL_META='BasicTestRunRequireAuthMeta')
        self.assertGreater(response.status_code, 300) # could be anything but in the 400 and 500 range!
    
    def tests_post(self):
        
        # lots of things to test on get!!
        response = self.session.post('/{model_name}/models/'.format(model_name = self.model_name), MODEL_META='BasicTestRunRequireAuthMeta')
        self.assertGreater(response.status_code, 300) # could be anything but in the 400 and 500 range!
    

    def tests_delete(self):
        
        # lots of things to test on get!!
        response = self.session.get('/{model_name}/models/'.format(model_name = self.model_name), MODEL_META='BasicTestRunRequireAuthMeta')
        self.assertGreater(response.status_code, 300) # could be anything but in the 400 and 500 range!
    

    
def main():
    
    pass


if __name__ == '__main__':
    main()
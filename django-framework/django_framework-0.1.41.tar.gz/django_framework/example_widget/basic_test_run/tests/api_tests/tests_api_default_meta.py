

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
        response = self.session.get('/{model_name}/models/'.format(model_name = self.model_name))
        
        self.assertEqual(response.status_code, 200)
        response = response.json()
    
    def test_post(self):
        response = self.session.post('/{model_name}/models/'.format(model_name = self.model_name), data = self.payload)
        
        self.assertEqual(response.status_code, 200)
        response = response.json()
        
        self.assertEqual(len(response['data']), 1)
        
        model = response['data'][0]
        
# {u'choices_field_alt': u'Constant', u'encrypted_text_field': u'encrypted_me', u'last_updated': 1497589275, u'uuid': u'9caf2991-6475-452e-ad62-27489e753ccf', u'epoch_time_field_alt': u'1970-01-01 00:00:01', u'normal_text_field': u'basic_api_test', u'created_at': 1497589275, u'encrypted_text_strict_field': u'**DES**b75dab1ce5b142fe9122488345574ccbfbe70a4a693a7eb62f15820d297d97c3c3cdbe0a8c802a2b857d8e57c9e764c9ab76fb7b8591307be6b88a36acfdb92a2b74e7232912404954bbbb41d8886cdd', u'basic_profile_run_fk_field_id': None, u'write_once_text_field': u'write_once', u'choices_field': 0, u'created_at_alt': u'2017-06-16 05:01:15', u'last_updated_alt': u'2017-06-16 05:01:15', u'basic_profile_run_ids': [], u'read_only_text_field': None, u'type': u'BasicTestRun', u'id': 1, u'epoch_time_field': 1}

        self.assertEqual(model['basic_profile_run_fk_field_id'], None)
        self.assertEqual(model['basic_profile_run_ids'], [])
        self.assertEqual(model['write_once_text_field'], "write_once")
        
        self.assertEqual(model['read_only_text_field'], None) # cause it is read only
        self.assertEqual(model.get('hidden_text_field'), None) # shouldnt even show up
        self.assertEqual(model['encrypted_text_field'], "encrypted_me")

        self.assertEqual(model['encrypted_text_strict_field'].find('**DES**') >= 0, True)
        self.assertEqual(model['epoch_time_field'], 1)
        self.assertEqual(model['epoch_time_field_alt'], '1970-01-01 00:00:01')

        self.assertEqual(model['choices_field'], 0)
        self.assertEqual(model['choices_field_alt'], 'Constant')

        time_difference = arrow.utcnow() - arrow.get(model['last_updated'])
        self.assertLessEqual(time_difference.total_seconds(), 5)
        
        
        model['last_updated_alt'] # make sure it exists
        self.assertEqual(len(model['uuid']), 36 )

        time_difference2 = arrow.utcnow().timestamp - arrow.get(model['created_at']).timestamp
        self.assertLessEqual(time_difference2, 5)
        model['created_at_alt'] # make sure it exists
        
        model['id'] # make sure it exists
    
    def test_put(self):
        
        response = self.session.post('/{model_name}/models/'.format(model_name = self.model_name), data = self.payload)
        
        self.assertEqual(response.status_code, 200)
        response = response.json()
        model = response['data'][0]
        
        payload = copy.copy(self.payload)
        payload['epoch_time_field'] = 15
        payload.pop('write_once_text_field')
        ## uuid version isnt working for the models!
        response = self.session.put('/{model_name}/models/{uuid}/'.format(model_name = self.model_name, uuid = model['uuid']), data = json.dumps(payload), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        response = response.json()
        model_updated = response['data'][0]
        
# {u'choices_field_alt': u'Constant', u'encrypted_text_field': u'encrypted_me', u'last_updated': 1497589275, u'uuid': u'9caf2991-6475-452e-ad62-27489e753ccf', u'epoch_time_field_alt': u'1970-01-01 00:00:01', u'normal_text_field': u'basic_api_test', u'created_at': 1497589275, u'encrypted_text_strict_field': u'**DES**b75dab1ce5b142fe9122488345574ccbfbe70a4a693a7eb62f15820d297d97c3c3cdbe0a8c802a2b857d8e57c9e764c9ab76fb7b8591307be6b88a36acfdb92a2b74e7232912404954bbbb41d8886cdd', u'basic_profile_run_fk_field_id': None, u'write_once_text_field': u'write_once', u'choices_field': 0, u'created_at_alt': u'2017-06-16 05:01:15', u'last_updated_alt': u'2017-06-16 05:01:15', u'basic_profile_run_ids': [], u'read_only_text_field': None, u'type': u'BasicTestRun', u'id': 1, u'epoch_time_field': 1}

        self.assertEqual(model_updated['basic_profile_run_fk_field_id'], None)
        self.assertEqual(model_updated['basic_profile_run_ids'], [])
        self.assertEqual(model_updated['write_once_text_field'], "write_once")
        
        self.assertEqual(model_updated['read_only_text_field'], None) # cause it is read only
        self.assertEqual(model_updated.get('hidden_text_field'), None) # shouldnt even show up
        self.assertEqual(model_updated['encrypted_text_field'], "encrypted_me")

        self.assertEqual(model_updated['encrypted_text_strict_field'].find('**DES**') >= 0, True)
        self.assertEqual(model_updated['epoch_time_field'], 15)
        self.assertEqual(model_updated['epoch_time_field_alt'], '1970-01-01 00:00:15')

        self.assertEqual(model_updated['choices_field'], 0)
        self.assertEqual(model['choices_field_alt'], 'Constant')

        time_difference = arrow.utcnow() - arrow.get(model['last_updated'])
        self.assertLessEqual(time_difference.total_seconds(), 5) # should be newly updated!
        
        model_updated['last_updated_alt'] # make sure it exists
        self.assertEqual(len(model_updated['uuid']), 36 )

        self.assertEqual(model_updated['created_at'], model['created_at'])
        model_updated['created_at_alt'] # make sure it exists
        
        model_updated['id'] # make sure it exists
        
        
    def test_delete(self):
        
        response = self.session.post('/{model_name}/models/'.format(model_name = self.model_name), data = self.payload)
        
        self.assertEqual(response.status_code, 200)
        response = response.json()
        model = response['data'][0]
        
        response = self.session.delete('/{model_name}/models/{uuid}/'.format(model_name = self.model_name, uuid = model['uuid']))

        self.assertEqual(response.status_code, 200)
        response = response.json()
        
        response['meta_data'] # we make sure it has the key!
        self.assertEqual(response['meta_data']['type'], 'BasicTestRun')
        self.assertEqual(response['meta_data']['total_query_results'], 1)
        self.assertEqual(response['data'], [{u'status': True}])

    def test_get_filters(self):
        response = self.session.post('/{model_name}/models/'.format(model_name = self.model_name), data = self.payload)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        model = response['data'][0]
        
        response = self.session.get('/{model_name}/models/?filter[uuid]={uuid}'.format(model_name = self.model_name, uuid = model['uuid']))

        self.assertEqual(response.status_code, 200)
        response = response.json()
        
        self.assertEqual(len(response['data']), 1)
        

    
def main():
    
    pass


if __name__ == '__main__':
    main()
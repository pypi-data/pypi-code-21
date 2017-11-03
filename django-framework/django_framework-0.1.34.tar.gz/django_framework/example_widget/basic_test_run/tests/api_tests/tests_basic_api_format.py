
import unittest

def fun(x):
    return x + 1
from django.test import Client


class BasicAPIFormat(unittest.TestCase):
    '''The goal is to test basic response Error Response and Model data responses are correct!'''
    
    model_name = 'basic_test_run'
#     base_url = 'http://localhost:8000'
    base_url = ''
    
    @classmethod
    def setUpClass(cls):
        cls.session = Client()

    def test_meta_no_login(self):
        '''The meta file has been set to allow not logged in users to request data! We expect to see data!'''
        url = self.model_name + '/models/'
        url = self.url_formatter(url)
        response = self.session.get(path = url, params = {'format' : 'json'})

        self.assertEqual(response.status_code, 200)

    def test_valid_response_format(self):
        '''We test that for valid responses, it sends the correct information!'''
        url = self.model_name + '/models/'
        url = self.url_formatter(url)
        response = self.session.get(path = url, params = {'format' : 'json'})

        self.assertEqual(response.status_code, 200)
        
        response = response.json()
        self.assertEqual(type(response), dict)
        
        self.assertNotEqual(response.get('meta_data'), None)
        
        meta_data = response.get('meta_data')
        self.assertNotEqual(meta_data.get('type'), None)
        self.assertNotEqual(meta_data.get('total_query_results'), None)
        
        self.assertNotEqual(response.get('data'), None)
        data = response.get('data')
        self.assertEqual(type(data), list)
        
    def test_not_valid_response_format(self):
        url = self.url_formatter('testing/raise_error/')
        print(url)
#         url = self.url_formatter(url)
#         url = 'http://localhost:8000/testing/raise_error/'

        response = self.session.get(path = url, params = {'format' : 'json'})

        self.assertEqual(response.status_code, 500)
        
        try:
            response = response.json()
        except:
            raise Exception('Issue converting to JSON, is Debug mode set to False?')

        self.assertEqual(type(response), dict)
        
        self.assertNotEqual(response.get('meta_data'), None)
        
        
        self.assertNotEqual(response.get('error'), None)
        
        error = response.get('error')
        self.assertEqual(type(error), dict)
        self.assertNotEqual(error.get('status_code'), None)
        self.assertNotEqual(error.get('message'), None)
        self.assertNotEqual(error.get('traceback'), None)
        self.assertNotEqual(error.get('error_code'), None)
        

    def url_formatter(self, url):
        return '{base_url}/{url}'.format(base_url = self.base_url, url = url)
    

def main():
    
    pass


if __name__ == '__main__':
    main()
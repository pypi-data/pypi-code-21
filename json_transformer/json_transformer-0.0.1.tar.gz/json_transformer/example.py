from parser import JsonTransformer

if __name__ == '__main__':

    class FieldMixin(object):

        @staticmethod
        def name(value, dict_key='name'):
            return 'new_name', 'Peter'

        @staticmethod
        def id(value, dict_key='id'):
            return 'new_id', value

    class RandomTransormer(JsonTransformer, FieldMixin):
        _keep_undeclared_methods = False


    payload = {'name': 'John', 'id': '1', 'email': 'john@ueni.com'}
    print(payload)
    print('\n\n')
    print(RandomTransormer(**payload)._new_json)

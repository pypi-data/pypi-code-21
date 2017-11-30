


class BaseVariable(object):
    
    def assert_is_url(self, value):
        self.assert_not_blank(value = value)
        
        if value.find('http') < 0:
            raise ValueError('The send job url must be a url with http')
    
        if value.find(':') < 0:
            raise ValueError('The send job url must be a url with colons')
        
        return value
    def assert_not_blank(self, value):
        
        if value in ['', None]:
            raise ValueError('The value cannot be blank or None')
        
        
    def assert_boolean(self, value):
        
        if value not in [True, False]:
            
            raise ValueError('The value must be true/false')
        
        
    def assert_type(self, value, expected_type):
        
        if type(value) != expected_type:
            
            raise ValueError('We expected a certain type and didnt get it')
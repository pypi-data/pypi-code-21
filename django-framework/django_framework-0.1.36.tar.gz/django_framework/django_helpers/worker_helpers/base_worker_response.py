import arrow
import json

class BaseWorkerResponse(object):
    
    def __init__(self, **kwargs):
        
        # really just checking to make sure all the fields are properly written
        # for a response!
        
        self._kwargs = kwargs

        self.response_payload = kwargs.get('response_payload')
        self.response_at = kwargs.get('response_at')
        self.status = kwargs.get('status')
        self.status_alt = kwargs.get('status_alt')

        self.command = kwargs.get('command')
        self.action = kwargs.get('action')
        
        self.initial_payload = kwargs.get('initial_payload')
        if self.initial_payload is not None:
            self.initial_payload = json.loads(self.initial_payload)

    ## Getting and setting for response_payload ##
    @property
    def response_payload(self):
        return self._response_payload

    @response_payload.setter
    def response_payload(self, value):
        if hasattr(self, '_response_payload') == False:
            self._response_payload = None
        
        if type(value) != dict:
            raise ValueError('The response must be a dictionary!')
        self._response_payload = value
    ## Getting and setting for response_payload ##

    ## Getting and setting for response_at ##
    @property
    def response_at(self):
        return self._response_at

    @response_at.setter
    def response_at(self, value):
        if hasattr(self, '_response_at') == False:
            self._response_at = None

        self._response_at = arrow.get(value)
    ## Getting and setting for response_at ##


    ## Getting and setting for status ##
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if hasattr(self, '_status') == False:
            self._status = None
        
        try:
            int(value)
        except:
            raise ValueError('The status of a response must be a valid integer.  0 means success!')
        
        self._status = value
    ## Getting and setting for status ##

    ## Getting and setting for status_alt ##
    @property
    def status_alt(self):
        return self._status_alt

    @status_alt.setter
    def status_alt(self, value):
        if hasattr(self, '_status_alt') == False:
            self._status_alt = None
        self._status_alt = value
    ## Getting and setting for status_alt ##

    ## Getting and setting for command ##
    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        if hasattr(self, '_command') == False:
            self._command = None
            
        if value is None:
            value = self.response_payload.get('command')
        
        if value is None:
            raise ValueError('command must specified!')
        self._command = value
    ## Getting and setting for command ##

    ## Getting and setting for command ##
    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        if hasattr(self, '_action') == False:
            self._action = None
            
        if value is None:
            value = self.response_payload.get('action')
        
        if value is None:
            raise ValueError('action must specified!')
        self._action = value
    ## Getting and setting for action ##


    
    
    def to_dict(self, is_json = False):
        
        return dict( response_payload = json.dumps(self.response_payload),
                     response_at = self.response_at.timestamp,
                     status = self.status,
                     status_alt = self.status_alt)
def main():
    
    bwr = BaseWorkerResponse(response_payload = {'asdf': 'test'}, status = 0)
    
    print(bwr.response_payload)
    
    bwr.response = 'asfd'
    print(bwr.to_dict())
    
    
if __name__ == '__main__':
    main()
class GenericException(Exception):
    HTTP_STATUS = 500
    def __init__(self, message="Error message not set!", error_code=5000, http_status=None, notes = None):
        self.error_code = error_code
        
        self.http_status = self.HTTP_STATUS
        if http_status != None:
            self.http_status = http_status
            
        self.notes = notes

        super(GenericException, self).__init__(message)

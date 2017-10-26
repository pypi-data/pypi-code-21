class EmbedException(Exception):
    status_code = 0
    message = "Unexpected error occurred"

    def __init__(self, code, message):
        self.status_code = code
        self.message = message

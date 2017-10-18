class BlockException(Exception):
    def __init__(self, response):
        self.response = response

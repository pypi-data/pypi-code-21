class ESIErrorLimitReached(Exception):
    error = 'ESI error limit hit, please wait'

    def __init__(self, remaining_time):
        self.remaining_time = remaining_time

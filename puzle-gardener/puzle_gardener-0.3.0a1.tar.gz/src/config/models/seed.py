class Seed:
    def __init__(self, name, location="", fields: dict=None):

        self.name = name
        self.location = location
        self.required_values = ['name', 'location']
        self.fields = fields or {}

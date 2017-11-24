class Field:

    def __init__(self, label: str, required: bool = False, default= "", user_text=""):
        self.label = label
        self.required = required
        self.default = default
        self.text = user_text
        if required:
            self.value = None
        else:
            self.value = default

    def __getitem__(self, attr):
        return getattr(self, attr)
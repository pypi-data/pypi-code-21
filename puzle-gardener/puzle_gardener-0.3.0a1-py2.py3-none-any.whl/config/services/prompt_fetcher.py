from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError


class NoEmptyValidator(Validator):
    def validate(self, document):
        text = document.text

        if not text or text == "":
            raise ValidationError(message='This input must not be empty')

class PromptFetcher:

    @staticmethod
    def run(required_values: dict, default_values: dict= None)-> dict:
        data = {}

        for key, item in required_values.items():
            user_input = prompt(item['text'], validator=NoEmptyValidator())
            data[key] = user_input
            print(user_input)

        if default_values:
            for key, item in default_values.items():
                user_input = prompt(item['text'], default=item['default'])
                data[key] = user_input
                print(user_input)

        return data

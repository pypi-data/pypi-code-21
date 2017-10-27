import re
import codecs

from hivemindplus.validation import validate


class InstanceConfig:
    def __init__(
        self,
        connection_string,
        query,
        key,
        name,
        tags,
        instructions_template,
        instructions_template_values,
        schema_template,
        schema_template_values,
        qualifications_query
    ):
        self.connection_string = connection_string
        self.query = query
        self.key = key
        self.name = name
        self.tags = tags
        self.instructions_template = instructions_template
        self.instructions_template_values = instructions_template_values
        self.schema_template = schema_template
        self.schema_template_values = schema_template_values
        self.qualifications_query = qualifications_query


class ConfigBuilder:
    def __init__(self):
        self._connection_string = None
        self._query = None
        self._key = None
        self._name = None
        self._tags = []
        self._instructions_template = None
        self._instructions_template_values = None
        self._schema_template = None
        self._schema_template_values = None
        self._qualifications_query = None

    def with_connection_string(self, connection_string):
        """
        A pypyodbc SQL connection string that is used to execute the query

        E.g. 'DRIVER={SQL Server};SERVER=localhost;UID=sa;PWD=password'
        """
        self._connection_string = connection_string
        return self

    def with_query(self, query):
        """
        A SQL query that will be used to select data for each instance
        """
        self._query = query
        return self

    def with_key(self, key):
        """
        The name of a column that provides a unique key for each instance
        """
        self._key = key.lower()
        return self

    def with_name(self, name):
        """
        The name of a column that provides a name for each instance
        """
        self._name = name.lower()
        return self

    def with_tags(self, tags):
        """
        (Optional) list of columns to tag instances with
        """
        self._tags = [tag.lower() for tag in tags]
        return self

    def with_instructions(self, instructions_template, instructions_template_values):
        """
        Template is the path to a template markdown file to be used as instructions.
        Template values is a list of column names whose values will be inserted into the template.

        Variables should be referenced in the markdown in the same way as Python's format() function requires

        e.g.

        instructions.md
        ---------------
        What is {0} divided by {1}?

        script.py
        ---------
        with_instructions('instructions.md', ['Numerator', 'Denominator'])
        """
        with codecs.open(instructions_template, 'r', encoding='utf-8') as file:
            self._instructions_template = file.read()
            self._instructions_template_values = [value.lower() for value in instructions_template_values]

        return self

    def with_instructions_table(self, instructions_values):
        """
        List of columns to generate an instructions table with

        e.g.
        call
        ----
        with_instruction_table(['Numerator', 'Denominator'])

        markdown
        --------
        | Numerator | Denominator |
        | --------- | ----------- |
        | x         | y           |

        """
        header = u'|'
        divider = u'|'
        body = u'|'

        for i, value in enumerate(instructions_values):
            header += u' {} |'.format(value)
            divider += u' - |'
            body += u' {{{}}} |'.format(i)

        self._instructions_template = u'\n'.join([header, divider, body])
        self._instructions_template_values = [value.lower() for value in instructions_values]

        return self

    def with_schema(self, schema_template, schema_template_values):
        """
        Template is the path to a template JSON file to be used as an override schema.
        Template values is a list of column names whose values will be inserted into the template.

        Variables should be referenced in the JSON in the same way as Python's format() function requires

        e.g.

        schema.json
        ---------------
        {
          "q": {
            "type": "string",
            "enum": [{0}, {1}]
          }
        }

        script.py
        ---------
        with_schema('schema.json', ['Numerator', 'Denominator'])
        """
        with codecs.open(schema_template, 'rb', encoding='utf-8') as file:
            contents = file.read()
            # Duplicate occurrences of { and } so they do not interfere with string format values e.g. {0}
            contents = re.sub(r'({)[^0-9]', r'{\1', contents)
            contents = re.sub(r'[^0-9](})', r'}\1', contents)
            self._schema_template = contents
            self._schema_template_values = [value.lower() for value in schema_template_values]

        return self

    def with_qualifications_query(self, qualifications_query):
        """
        (Optional) A SQL query to generate instance qualifications from. The first column must be the instance key
        and the second must contain the name of a qualification. It is possible to have n qualifications for each
        instance key.
        """
        self._qualifications_query = qualifications_query
        return self

    def build(self):
        validate(self, [['_connection_string'], ['_query'], ['_key'], ['_name']])

        return InstanceConfig(
            self._connection_string,
            self._query,
            self._key,
            self._name,
            self._tags,
            self._instructions_template,
            self._instructions_template_values,
            self._schema_template,
            self._schema_template_values,
            self._qualifications_query
        )

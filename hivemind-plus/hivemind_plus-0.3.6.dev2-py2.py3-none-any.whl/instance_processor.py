import pypyodbc
import json

from hivemindplus.consts import KEY_PREFIX
from hivemindplus.exceptions import QualificationNotFoundException


class InstanceProcessor:
    def __init__(self, config):
        self._config = config

    def process(self, api):
        if not self._config:
            return

        existing = api.existing_instances()
        existing_tags = {tag for instance in existing for tag in instance['tags']}

        qualifications = self._get_qualifications(api)

        for instance in self._get_instances():
            if instance.key_tag in existing_tags:
                print('Skipping instance with key={} as it has already been created'.format(instance.key))
            else:
                print('Creating instance with key={}'.format(instance.key))
                self._create_instance(instance, qualifications, api)

    def _get_instances(self):
        config = self._config
        connection = pypyodbc.connect(config.connection_string, unicode_results=True)
        cursor = connection.cursor()
        cursor.execute(config.query)
        columns = [column[0] for column in cursor.description]

        while True:
            row = cursor.fetchone()

            if not row:
                cursor.close()
                break
            else:
                yield self._get_instance(dict(zip(columns, row)))

        connection.close()

    def _get_instance(self, row):
        config = self._config
        key = row[config.key]
        name = row[config.name]
        tags = [str(row[tag]) for tag in config.tags]
        instruction = None
        schema = None

        if config.instructions_template is not None:
            template_values = [row[col] for col in config.instructions_template_values]
            instruction = config.instructions_template.format(*template_values)

        if config.schema_template is not None:
            template_values = [row[col] for col in config.schema_template_values]
            schema = config.schema_template.format(*template_values)

        return Instance(key, name, tags, instruction, schema)

    def _get_qualifications(self, api):
        config = self._config

        if not config.qualifications_query:
            return {}

        qualifications = {q['name']: q['id'] for q in api.get_qualifications()}

        connection = pypyodbc.connect(config.connection_string, unicode_results=True)
        cursor = connection.cursor()
        cursor.execute(config.qualifications_query)
        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        instance_qualifications = {}

        for row in rows:
            key = row[0]
            qual_name = row[1]

            try:
                qual_id = qualifications[qual_name]
                quals = instance_qualifications.setdefault(key, [])
                quals.append(qual_id)
            except KeyError:
                raise QualificationNotFoundException('Qualification {} not found'.format(qual_name))

        return instance_qualifications

    def _create_instance(self, instance, qualifications, api):
        persisted = api.create_instance(instance)
        key = instance.key

        if key in qualifications:
            id = persisted['id']
            for qual_id in qualifications[key]:
                print('Adding qual_id={0} to instance={1}'.format(qual_id, id))
                api.add_qualification(id, qual_id)


class Instance:
    def __init__(self, key, name, tags, instruction, schema):
        self.key = key
        self.name = name
        self.tags = tags
        self.instruction = instruction
        self.schema = schema

        # Unique Hivemind identifier
        self.key_tag = KEY_PREFIX + str(key)
        self.tags.append(self.key_tag)

    def as_dict(self):
        result = {
            'name': self.name,
            'tags': self.tags,
        }

        if self.instruction is not None:
            result['instruction'] = self.instruction

        if self.schema is not None:
            result['overrideSchema'] = json.loads(self.schema)

        return result

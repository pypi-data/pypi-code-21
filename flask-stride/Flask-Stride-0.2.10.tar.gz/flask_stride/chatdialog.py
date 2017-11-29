from .module import Module

class ChatDialog(Module):
    type = 'chat:dialog'

    def __init__(self, key, title, url, size=None, filter=None, hint=None, primary_action=None, secondary_actions=None):
        super().__init__(key)
        self.add_property('title', {'value': title})
        self.add_property('url', url)
        if size is not None:
            self.size = size

        if hint is not None:
            self.hint = hint

        if filter is not None:
            self.filter = filter

        if primary_action is not None:
            self.primary_action = primary_action

        if secondary_actions is not None:
            self.secondary_actions = secondary_actions

    def add_option(self, name, value):
        if 'options' not in self.properties:
            self.add_property('options', {})

        self.properties['options'][name] = value

    def del_option(self, name):
        if 'options' in self.properties:
            if name in self.properties['options']:
                del(self.properties['options'][name])

        if self.properties['options'] == {}:
            self.del_property('options')

    @property
    def size(self):
        try:
            return self.properties['options']['size']
        except:
            return None

    @size.setter
    def size(self, value):
        """Specify the size of the dialog box.
           Accepts either a string or a dict.
           If `value` is a string, it must a modal dialog size supported by the Atlassian Design Guidelines
           If `value` is a dict, it must have exactly two fields: `width` and `height`. Each field value is a string representing a number followed by 'px' or '%'."""
        if isinstance(value, str):
            valid_sizes = ['small', 'medium', 'large', 'xlarge']
            if value not in valid_sizes:
                raise ValueError('{} is not a valid size.'.format(value))
        elif isinstance(value, dict):
            if (len(value) != 2) or ('width' not in value) or ('height' not in value):
                raise ValueError('Custom dialog size is not valid.')

            if not value['width'].endswith(('px', '%')):
                raise ValueError('Width must be in pixels (px) or as a percentage (%).')

            if not value['height'].endswith(('px', '%')):
                raise ValueError('Height must be in pixels (px) or as a percentage (%).')
        else:
            raise ValueError('Invalid size data.')

        self.add_option('size', value)

    @property
    def hint(self):
        try:
            return self.properties['options']['hint']
        except:
            return None

    @hint.setter
    def hint(self, value):
        """Set the hint for the dialog."""
        if isinstance(value, str):
            self.add_option('hint', {'value': value})
        elif isinstance(value, dict):
            self.add_option('hint', {'value': value['value'], 'i18n': value['i18n']})
        else:
            raise ValueError('Invalid hint value.')

    @property
    def filter(self):
        try:
            return self.properties['options']['filter']
        except:
            return None

    @filter.setter
    def filter(self, value):
        if not isinstance(value, dict):
            raise ValueError('Invalid filter data type. Expecting a dict.')

        placeholder = {}
        placeholder['value'] = value['placeholder']['value']
        if 'i18n' in value['placeholder']:
            placeholder['i18n'] = value['placeholder']['i18n']

        self.add_option('filter', {'placeholder': placeholder})


    @property
    def primary_action(self):
        try:
            return self.properties['options']['primaryAction']
        except:
            return None

    @primary_action.setter
    def primary_action(self, value):
        """Set the primary action"""
        default_key = 'primary-action-selected'

        if not isinstance(value, ChatDialogAction):
            raise ValueError('Invalid data type for Primary Action. Expecting a ChatDialogAction. Received {}'.format(type(value)))

        if getattr(value, 'key', None) is None:
            value.key = default_key

        self.add_option('primaryAction', value)

    @property
    def secondary_actions(self):
        try:
            return self.properties['options']['secondaryActions']
        except:
            return None

    @secondary_actions.setter
    def secondary_actions(self, actions):
        if isinstance(actions, ChatDialogAction):
            actions = [actions]

        if not isinstance(actions, list):
            raise ValueError('Expecting a list. Received {}.'.format(type(actions)))

        for act in actions:
            if not isinstance(act, ChatDialogAction):
                raise ValueError('Expected a list of ChatDialogAction. Found list with element of type {}.'.format(type(act)))

        self.add_option('secondaryActions', actions)

    def add_secondary_action(self, action):
        """Add an action to the list of secondary actions."""
        if ('options' not in self.properties) or ('secondaryActions' not in self.properties['options']):
            self.add_option('secondaryActions', [])
        self.properties['options']['secondaryActions'].append(action)

    def del_secondary_action(self, name):
        """Remove a secondary action based on a name."""
        new_actions_list = [ a for a in self.secondary_actions if a.properties['name']['value'] != name ]

        if len(new_actions_list) == 0:
            self.del_option('secondaryActions')
        else:
            self.add_option('secondaryActions', new_actions_list)

class ChatDialogAction(Module):
    def __init__(self, name, key=None, enabled=True, i18n=None):
        super().__init__(key)
        self.add_property('name', {'value': name})
        self.add_property('enabled', enabled)

        if i18n is not None:
            self.properties['options']['name']['i18n'] = i18n

from actappliance.models import ActResponse

# Categorize keywords so dynamic keyword generation decisions can be made
# Basic conversion table to change CLI commands into english
keyword_prefixes = {'make': 'mk', 'add': 'mk',
                    'change': 'ch', 'set': 'ch',
                    'remove': 'rm', 'absent': 'rm',
                    'find': 'ls', 'search': 'ls',
                    'execute': '', 'do': '',
                    'info': '', 'perform': ''}

# Udstask keywords
task_keywords = ('make', 'add',
                 'change', 'set',
                 'remove', 'absent',
                 'execute', 'do')

# Udsinfo keywords
info_keywords = ('find', 'search',
                 'info', 'perform')

# Keywords that can be entirely generated
dynamic_keywords = ('make',
                    'change',
                    'remove',
                    'find',
                    'execute',
                    'info')

# Keywords that need human interaction to function. Either with error handlers if the action is not-idempotent or
# with retries if it is idempotent
idempotent_keywords = ('add',
                       'set',
                       'absent',
                       'search',
                       'do',
                       'perform')


class APIHelper(object):
    def __init__(self, appliance_obj):
        self.a = appliance_obj

    def __getattr__(self, name):
        """
        Create simple API helpers which send the call and (by default) check for errors.

        :param name: dynamic keyword
        :return: method
        """
        method = self.keyword_gen(name)

        if method:
            return self.keyword_gen(name)
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name))

    def keyword_gen(self, name):
        """
        Creates a keyword method based on it's name.

        Will only function on low level non-idempotent keywords.
        This will generate a method that sends a command, ensures no error occurred and return the unparsed
        response.

        :param name: low level keyword name
        :return: method
        """
        # the split argument is a nonplussed face (>'_')>[giff methods plz]
        keyword = name.split('_')
        keyword_prefix = keyword[0]
        if keyword_prefix.lower() in dynamic_keywords:
            if keyword_prefix.lower() in task_keywords:
                command_action = 'udstask'
            elif keyword_prefix.lower() in info_keywords:
                command_action = 'udsinfo'
            else:
                raise RuntimeError('Unsupported dynamic method. Supported methods are {}'.format(dynamic_keywords))

            # acquire the body of the action i.e. workflow in udsinfo lsworkflow
            command_body = ''.join(keyword[1:])
            # manufacture the whole command
            command = command_action + ' ' + keyword_prefixes[keyword_prefix] + command_body

            def method(raise_for_error=True, **update_cmds):
                r = self.a.cmd(command, **update_cmds)
                assert issubclass(type(r), ActResponse)
                if raise_for_error:
                    r.raise_for_error()

                return r

            method.__name__ = name
            setattr(self, name, method.__get__(self))

            return method

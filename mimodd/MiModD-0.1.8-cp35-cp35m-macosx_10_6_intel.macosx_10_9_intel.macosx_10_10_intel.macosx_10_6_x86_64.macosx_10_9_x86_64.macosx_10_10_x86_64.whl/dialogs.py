# The function run_dialogs of this module can run a role of user dialogs
# populating a settings dictionary with gathered information.
# A dialog role is a list of dictionaries that describe individual dialogs
# with the user to get a value for a specific setting.
# Each dialog dictionary must define a 'title' and may define an 'intro'
# to be displayed at the beginning of the dialog.
# In additon, it must define a 'target_param' that names a valid config
# setting that should be set as the outcome of the dialog, and it may
# define a 'default_value' that will be used if the user does not provide
# a value. Specifying a 'default_value' of the module global NO_DEFAULT will
# force the user to provide a value during the dialog. Specifying
# USE_CFG_DEFAULT signals that the respective default setting from the passed
# in config object should be used as the default, which is the same as not
# providing a 'default_value'.
# Finally, the dialog must define a list of (one or more) 'questions' that
# will be asked during the dialog. Each question is, in turn, a dictionary
# defining the actual 'question', an optional 'choices' list of valid user
# inputs, possibly specifying its own 'default_value' that overrides the one
# defined for the dialog and an optional 'conditional', which must be a
# callable that determines at dialog runtime whether the question should
# actually be asked. This callable must accept one argument, which will be the
# answer to the preceding question (or None if this is the first question in
# the dialog). It should return the module global ASK_QUESTION to indicate that
# the question should be asked or, otherwise, a suitable value that the target
# parameter will be set to if this is the last question in the dialog or that
# will be passed to the next question if it is a conditional question itself.


ASK_QUESTION = object()
USE_CFG_DEFAULT = object()
NO_DEFAULT = object()


def run_dialogs (role, args, config):
    for n, dialog in enumerate(role, 1):
        print()
        if not dialog['target_param'] in args:
            print(
                'Question {0}/{1} - {2}'
                .format(n, len(role), dialog['title'])
                )
            print()
            if 'intro' in dialog:
                print(dialog['intro'])
                print()
            choice = None
            for question in dialog['questions']:
                if question.get('conditional'):
                    choice = question['conditional'](choice)
                    if choice is not ASK_QUESTION:
                        continue
                if 'default_value' in question:
                    default = question['default_value']
                    if default is USE_CFG_DEFAULT:
                        default = getattr(config, dialog['target_param'])
                elif 'default_value' in dialog:
                    default = dialog['default_value']
                    if default is USE_CFG_DEFAULT:
                        default = getattr(config, dialog['target_param'])
                else:
                    default = getattr(config, dialog['target_param'])
                if default is NO_DEFAULT:
                    q = question['question'].format('') + ' '
                else:
                    q = question['question'].format(
                        '[{}]'.format(default)
                        ) + ' '

                while True:
                    choice = input(q)
                    if choice == '' and default is NO_DEFAULT:
                        print(
                            'No reasonable default response is available so '
                            'you need to provide this input.'
                            )
                        continue
                    choice = choice or default
                    if not question.get('choices') or choice in question['choices']:
                        break
                    print('Could not understand your answer:', choice)           
            args[dialog['target_param']] = choice
        else:
            print(
                'Skipping question {0}/{1} - {2}.'
                .format(n, len(role), dialog['title'])
                )
            print('    Using provided argument as setting instead.')
        print()

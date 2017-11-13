#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import readline


def prompt(the_prompt, the_type='str'):
    py3 = sys.version_info[0] > 2

    if py3:
        response = input(the_prompt)
    else:
        response = raw_input(the_prompt)

    if the_type == 'bool':
        if response == 'true':
            return True
        else:
            return False
    elif the_type == 'int':
        return int(response)
    elif the_type == 'FLOAT':
        return float(response)

    # Default is str
    return response


def prompt_user(question, answer_type=None, required=True, default=None,
                are_sure=False, complete=None, old_completer=None, editor=False):
    '''
    Prompt the user with a single question.
    @param editor (Optional): If set to True, open the user's $EDITOR and get the answer from there.
    '''
    question = [
        {
            'key': 'the_answer',
            'answer_type': answer_type,
            'question': question,
            'required': required,
            'default': default,
            'complete': complete
        }
    ]

    if editor:
        # Make a tempfile, add the question, and a space for people to write.
        import tempfile
        fd, filename = tempfile.mkstemp(suffix='.md', text=True)
        default = default if default else ''
        default_content = '# {0}\n\n{1}'.format(question[0]['question'], default)
        f = os.fdopen(fd, 'w')
        f.write(default_content)
        f.close()

        # Fire up Vim for people to write in.
        os.system("{editor} {filename}".format(editor=os.getenv("EDITOR", "vi"), filename=filename))
        with open(filename, 'r') as f:
            answer = {'the_answer': ''.join([l for dex, l in enumerate(f.readlines()) if dex])}
    else:
        answer = get_input(question, are_sure=are_sure, old_completer=old_completer)

    if answer:
        return answer['the_answer']
    else:
        print('Aborting!')
        # Return something we shouldn't be seeing anywhere else...
        return (None, 'Abort!')


def get_input(question_list, are_sure=True, old_completer=None, **kwargs):
    '''Yeah, this is ugly but it works for now. :)'''

    # If you pass in the kwarg: auto=True get input will return all answers
    # with the defaults selected automatically.
    auto = kwargs.get('auto', False)

    answers = {'are_sure': True}
    for question in question_list:
        while True:
            formatted_question = ''

            # If the question has a "complete" key, use the list as the auto-complete options
            if question.get('complete'):
                def complete(text, state):
                    for cmd in question['complete']:
                        if cmd.startswith(text):
                            if not state:
                                return cmd
                            else:
                                state -= 1

                readline.parse_and_bind("tab: complete")
                readline.set_completer(complete)

            # Add stars in front of the required questions
            if question['required']:
                formatted_question += '* '

            # If the question has a default answer, strip the hint from the front of it.
            # This is deprecated but I think some of the shell is still using it.
            if question['default'] is not None:
                if str(question['default']).startswith('ANSWER:'):
                    question['default'] = answers[str(question['default']).replace('ANSWER:', '')]

            # If there is a "default" key, reformat the question to show the default answer.
            if question['default'] is None:
                formatted_question += question['question']
            else:
                formatted_question += "(%s) %s" % (str(question['default']), question['question'])

            # If we are returning all questions with auto, do that now.
            if auto:
                if question['default'] is not None:
                    result = question['default']
                else:
                    result = None
            else:
                # Prompt the user for the answer to the question
                try:
                    result = prompt(formatted_question)
                except (KeyboardInterrupt, EOFError):
                    # Abort utility
                    sys.exit(0)

            # Allow the user to break out of the questions and just return none.
            if result in ['exit', 'quit', 'halt', 'cease', 'desist', 'abort']:
                return None
            else:
                if result:
                    if question.get('answer_type'):
                        answers[question['key']] = question['answer_type'](result)
                        break
                    else:
                        answers[question['key']] = result
                        break
                else:
                    # If the question is required and no answer is given, prompt the user to answer the question
                    if question['required'] and question['default'] is None and not auto:
                        print("The question is required.")
                    else:
                        # If the 'answer_type' has been set, we need to call the function with that name on the answer the user has given us.
                        if question['default'] is not None:
                            if question.get('answer_type'):
                                answers[question['key']] = question['answer_type'](question['default'])
                                break
                            else:
                                answers[question['key']] = question['default']
                                break
                        else:
                            answers[question['key']] = None
                        break
    # Restore the old completer function to readline, if passed.
    if old_completer:
        readline.parse_and_bind("tab: complete")
        readline.set_completer(old_completer)

    if are_sure:
        try:
            result = prompt("Are you sure you want to do this? ")
        except (KeyboardInterrupt, EOFError):
            # Abort utility
            sys.exit(0)

        if result.lower() == 'n':
            return None

    return answers


def main():
    pass


if __name__ == '__main__':
    main()

from __future__ import unicode_literals, print_function

import sys
import errno
import logging
import os

log = logging.getLogger('qordoba')

PY3 = sys.version_info[0] == 3


def ask_select(question_list, prompt='Select: '):
    """

    :param question_list: Excpect list of tuples with 2 elements - ID and TEXT
    :param prompt: First message.
    :return: ID or TEXT
    """

    valid_answers = list((el + 1 for el in range(len(question_list))))

    question_list_text = []
    for el_num, question in enumerate(question_list, start=1):
        try:
            _, text = question
        except ValueError:
            text = question

        question_list_text.append('{}) {}'.format(el_num, text))

    promt_message = '\n'.join(question_list_text + [prompt, ])
    answer = None
    while answer not in valid_answers:
        try:
            answer = int(ask_simple(promt_message))
        except (TypeError, ValueError):
            promt_message = prompt

    return question_list[answer - 1]


def ask_select_multiple(question_list, prompt="Select: "):
    """

    :param question_list: Expect list of tuples with 2 elements - ID and TEXT
    :param prompt: First message.
    :return: list of answers ID and TEXT
    """

    valid_answers = set()
    question_list_text = []
    for el_num, question in enumerate(question_list, start=1):
        try:
            question_id, text = question
        except ValueError:
            text = question

        question_list_text.append('{}) {}'.format(el_num, text))
        valid_answers.add(el_num)

    promt_message = '\n'.join(question_list_text + [prompt, ])
    answer = None
    while not answer or not valid_answers.issuperset(answer):
        answer = ask_simple(promt_message)
        # convert values splitted by space or command
        try:
            answer = set(map(lambda x: int(x.strip()), answer.split(',') if ',' in answer else answer.split(' ')))
        except (TypeError, ValueError):
            answer = None

        promt_message = prompt

    return [q for ix, q in enumerate(question_list, start=1) if ix in answer]


def ask_bool(question='[y/n]?'):
    """
    Ask user a question in intercative mode
    """
    yes = ['Y', 'y', 'Yes', 'yes', ]
    no = ['N', 'n', 'No', 'no', ]
    valid = yes + no

    answer = None
    while answer not in valid:
        answer = ask_simple(question)
        question = '[y/n]'

    return answer in yes


def ask_simple(question):
    if PY3:
        answer = input(question)
    else:
        answer = raw_input(question)

    return answer


def ask_question(question, answer_type=str, exceptions=(TypeError, )):
    """
    Ask user a question in intercative mode and wait for answer.
    """

    valid = False
    answer = None

    while not valid:
        answer = ask_simple(question)
        try:
            answer = answer_type(answer)
            valid = True
        except exceptions:
            pass

    return answer


def mkdirs(path):
    try:
        if path:
            os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise

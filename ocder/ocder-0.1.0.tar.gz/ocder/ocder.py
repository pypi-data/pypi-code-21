from __future__ import print_function

import ast
import codecs
import logging
import os
import token
from functools import partial
from multiprocessing import Pool

from asttokens import asttokens, util

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)

log = logging.getLogger(__name__)

verbosity = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}

CHECK_NODES = (ast.Dict, ast.List, ast.Tuple, ast.Set)


def check_target(pth, fix=False, jobs=1, verbose=0):
    """
    Main function performing check on chosen path.

    :param pth: target file/directory to check
    :param fix: check-only or fix
    :param jobs: number of workers
    :param verbose: show extra information
    """
    log.setLevel(verbosity.get(min(max(verbose, 0), 2)))

    log.info('collecting files')
    targets = collect_targets(pth)
    log.info('files collected: {}'.format(len(targets)))

    pool = Pool(jobs)

    log.info('starting check, workers:'.format(jobs))
    # .get(9999999) fixes workers capturing KeyboardInterrupt
    res = pool.map_async(partial(check_file, fix), targets).get(9999999)
    return all(res)


def collect_targets(pth):
    """
    Collect and return all files in chosen path.
    """
    targets = []
    if os.path.isdir(pth):
        for root, dirs, files in os.walk(pth):
            for dir_ in dirs:
                targets += collect_targets(os.path.join(root, dir_))
            for file_ in files:
                if file_.endswith('.py'):
                    targets.append(os.path.join(root, file_))
    elif os.path.isfile(pth):
        if pth.endswith('.py'):
            targets.append(pth)
    else:
        raise ValueError('invalid target: {}'.format(pth))

    return targets


def check_file(fix, pth):
    """
    OCD-check a single file.

    File is expected to be utf-8.
    """
    log.info('checking {}'.format(pth))
    try:
        with codecs.open(pth, encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        log.error('skipping {}\n - {}'.format(pth, e))
        return True

    if not lines:
        return True

    header = ''
    if '# -*- coding:' in lines[0]:
        header = lines[0]
        lines = lines[1:]

    source_text = u''.join(lines)

    try:
        valid, source_text = check_content(source_text, fix)
    except Exception as e:
        log.error('skipping {}\n - {}'.format(pth, e))
        return True

    if not valid and fix:
        log.info('fixing {}'.format(pth))
        with codecs.open(pth, 'wb', encoding='utf-8') as f:
            f.write(header + source_text)

    return valid


def check_content(source_text, fix=False):
    """
    Perform OCD-check on a single file.

    :param source_text: source to be checked.
    :param fix: if false, file won't be modified, only report the issues.
    """
    atok = asttokens.ASTTokens(source_text, parse=True)
    changeset = set()

    for node in ast.walk(atok._tree):
        if isinstance(node, CHECK_NODES):
            tokens = list(atok.get_tokens(node, include_extra=True))[::-1]
            if not check_node(tokens, changeset, node.__class__):
                if not fix:
                    log.error('OCD node:, line {}\n{}\n'.format(node.lineno, atok.get_text(node)))
    if fix and changeset:
        return False, util.replace(source_text, [(change, change, ',') for change in changeset])
    return not len(changeset), source_text


def check_node(tokens, changes, node_type):
    """
    Check if AST node is properly trailed by comma.
    Only multiline collections are checked.

    Approach:
    - walk tokens in AST node in reversal order
    - if no newline is found, comma not required
    - if no content is found, comma not required
    - if comma isn't found before any content token, comma required

    - tuples are special somehow, closing bracket is not included in tokens

    :param node: AST node being checked
    :param tokens: tokens contained in AST node
    :param changes: collecting set of changes to be fixed
    :return: true if node is comma-trailed properly
    """
    index = int(node_type is not ast.Tuple)
    valid = False
    multiline = False
    content_index = None

    last_index = len(tokens) - 1

    while True:
        pointed = tokens[index]

        log.debug('pointed node: {}'.format(pointed))

        # first node reached, could be empty
        if index == last_index:
            log.debug('node is very last')
            valid = True
            break

        # newline, move one token further
        if pointed.type == 54 and '\n' in pointed.string:
            log.debug('node is newline')
            multiline = True
            index += 1
            continue

        # comment, move one token further
        if pointed.type == token.N_TOKENS and pointed.string.startswith('#'):
            log.debug('node is comment')
            index += 1
            continue

        # we got comma before anything else, valid
        if pointed.type == token.OP and pointed.string == ',':
            log.debug('node is comma')
            valid = True
            break

        if not valid and multiline:
            log.debug('content node, multiple lines')
            if content_index is None:
                log.debug('setting content node index: {}'.format(index))
                content_index = index
            break
        else:
            log.debug('found a node before comma, probably not valid')
            if content_index is None:
                log.debug('setting content node index: {}'.format(index))
                content_index = index
            index += 1
            # we dont know if it's multiline yet
            continue

    if not multiline:
        return True

    valid = content_index is None and valid
    if not valid:
        if content_index is None:
            content_index = index
        changes.add(tokens[content_index].endpos)
    return valid

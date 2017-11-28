from i18n_base import get_files_in_dir_with_subdirs, save_to_jsonfile, get_root_path

import codecs
import re

import datetime
now = datetime.datetime.now()
date = now.strftime("%Y%m%d%H%M")
from collections import defaultdict
import logging


import pygments
import os
from pygments.lexers import get_lexer_by_name, guess_lexer, get_all_lexers, \
    load_lexer_from_file, get_lexer_for_filename, find_lexer_class_for_filename


"""
 The Extract Handler takes in a directory and extracts stringliterals file by file
 input: Directory of the files
 optional input: custom lexer. Either specify a pygments lexer (e.g. "html", "python" or call one of qordobas custom Lexers eg. "NonJunk")
 output: location where the JSON report is stored

 """

 
 # ["Token.Literal.String", "Token.Text"]

LEXER_STRINGS = dict()
LEXER_STRINGS['pygments.lexers.html.HtmlLexer'] = ("Token.Text",)
LEXER_STRINGS["<pygments.lexers.HtmlLexer with {'stripall': True}>"] = ("Token.Text",)
LEXER_STRINGS["<pygments.lexers.CustomLexer with {'stripall': True}>"] = ("Token.Text",)

IGNOREFILES = [
    ".DS_Store",
    ".gitignore",
    ".git"
]


def get_lexer(file_name, code, lexer_custom=None):
    # finding the right lexer for filename 
    lexer = find_lexer_class_for_filename(file_name)
    rel_path = "../pygments_custom/" + lexer_custom + ".py"
    path_to_custom_lexer_wrong = get_root_path(rel_path)
    path_to_custom_lexer_file = path_to_custom_lexer_wrong.replace("commands/../", '')

    if lexer is None:
        lexer = get_lexer_for_filename(file_name)
    if lexer is None:
        lexer = guess_lexer(file_name)
    
    if lexer_custom: # if custom lexer is given e.g. pygments "html" or custom e.g. "nonjunk"
        try:
            lexer = get_lexer_by_name(lexer_custom, stripall=True)
        except pygments.util.ClassNotFound:
            lexer = load_lexer_from_file(path_to_custom_lexer_file, stripall=True)
        except NameError:
            lexer = load_lexer_from_file(path_to_custom_lexer_file, stripall=True)
        except AttributeError:
            lexer = load_lexer_from_file(path_to_custom_lexer_file, stripall=True)
    
    if lexer_custom:
        logging.info("Custom Lexer defined: `{lexer_custom}`. File `{file}`.".format(lexer_custom=lexer_custom, file=file_name))
    logging.info("Lexer is {lexer}.".format(lexer=lexer))

    return lexer



def extract(curdir, input=None, output=None, lexer_custom=None, bulk_report=False):

    absolute_path = get_root_path(input)

    files = get_files_in_dir_with_subdirs(absolute_path)
    files = [file for file in files if file.split("/")[-1] not in IGNOREFILES]

    if bulk_report: #if True, the report will reflect all files in the directory
        json_report = defaultdict(dict)

    for file_ in files:
        if not bulk_report:
            json_report = defaultdict(dict)

        f = codecs.open(file_, 'r')
        code = f.read()
        file_name = file_.split('/')[-1]

        lexer = get_lexer(file_name, code, lexer_custom=lexer_custom)
        results_generator = lexer.get_tokens_unprocessed(code)

        for item in results_generator: #unpacking content of generator
            pos, token, value = item
            #filter for stringliterals
            lexer_stringliteral_def = str(lexer)
            if str(token) in LEXER_STRINGS[lexer_stringliteral_def] and not re.match(r'\n', value) and value.strip() != '':
                
                pos_start, token, value = item
                # calculating fileline of string based on charcter position of entire file
                file_chunk = code[:pos_start]
                start_line = file_chunk.count("\n")
                multilinestring = value.count("\n")
                end_line = start_line + multilinestring

                value = value.strip()
                json_report[file_][value] = {"start_line": start_line+1, "end_line": end_line+1}
        if not bulk_report:
            file_path = output + '/qordoba-report-' + file_name + "-" + date +'.json'
            save_to_jsonfile(file_path, json_report)
            logging.info("Report saved for file and reportname in: `{}`".format(file_path))

    # creating report file for bulk
    if bulk_report:
        file_path = output + '/qordoba-bulkreport-' + date +'.json'
        save_to_jsonfile(file_path, json_report)
        logging.info("Report saved in bulk for all files in: `{}`".format(file_path))


extract('curdir', input="/Users/franzi/Workspace/artifacts_stringExtractor/directory_cloudflare", output="/Users/franzi/Workspace/artifacts_stringExtractor/directory_cloudflare", lexer_custom="NonJunk", bulk_report=False)

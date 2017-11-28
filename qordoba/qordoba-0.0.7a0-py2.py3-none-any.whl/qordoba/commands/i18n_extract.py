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
#HTML
LEXER_STRINGS["<class 'pygments.lexers.html.HtmlLexer'>"] = ("Token.Text",)
LEXER_STRINGS["<pygments.lexers.HtmlLexer with {'stripall': True}>"] = ("Token.Text",)
#Python
LEXER_STRINGS["<class 'pygments.lexers.python.PythonLexer'>"] = ("Token.Text",)
LEXER_STRINGS["<pygments.lexers.PythonLexer with {'stripall': True}>"] = ("Token.Text",)
#JS
LEXER_STRINGS["<class 'pygments.lexers.javascript.JavascriptLexer'>"] = ("Token.Literal.String.Single",)
LEXER_STRINGS["<pygments.lexers.JavascriptLexer with {'stripall': True}>"] = ("Token.Literal.String.Single",)
#Scala
LEXER_STRINGS["<class 'pygments.lexers.scala.ScalaLexer'>"] = ("Token.Literal.String",)
LEXER_STRINGS["<pygments.lexers.ScalaLexer with {'stripall': True}>"] = ("Token.Literal.String",)
#Ruby
LEXER_STRINGS["<class 'pygments.lexers.ruby.RubyLexer'>"] = ("Token.Literal.String.Other", "Token.Literal.String.Double")
LEXER_STRINGS["<pygments.lexers.RubyLexer with {'stripall': True}>"] = ("Token.Literal.String.Other","Token.Literal.String.Double",)
#Nonjucks
LEXER_STRINGS["<pygments.lexers.Nonjucks with {'stripall': True}>"] = ("Token.Text",)


IGNOREFILES = [
    ".DS_Store",
    ".gitignore",
    ".git"
]

def get_lexer(file_name, code, lexer_custom=None):
    # finding the right lexer for filename otherwise guess
    lexer = find_lexer_class_for_filename(file_name)
    if lexer is None:
        lexer = get_lexer_for_filename(file_name)
    if lexer is None:
        lexer = guess_lexer(file_name)
    
    if lexer_custom: # if custom lexer is given e.g. pygments "html" or custom e.g. "nonjunk"
        rel_path = "../pygments_custom/" + lexer_custom + ".py"
        path_to_custom_lexer = get_root_path(rel_path)
        path_to_custom_lexer_clean = path_to_custom_lexer.replace("commands/../", '')
        
        try:
            lexer = get_lexer_by_name(lexer_custom, stripall=True)
        except pygments.util.ClassNotFound:
            lexer = load_lexer_from_file(path_to_custom_lexer_clean, lexer_custom, stripall=True)
        except NameError:
            lexer = load_lexer_from_file(path_to_custom_lexer_clean, lexer_custom, stripall=True)
        except AttributeError:
            lexer = load_lexer_from_file(path_to_custom_lexer_clean, lexer_custom, stripall=True)
    
        logging.info("Custom Lexer defined: `{lexer_custom}`. File `{file}`.".format(lexer_custom=lexer_custom, file=file_name))
    
    logging.info("Lexer is {lexer}.".format(lexer=lexer))
    return lexer


def extract(curdir, input=None, output=None, lexer_custom=None, bulk_report=False):
    # first getting all files in directory, than iteration 
    absolute_path = get_root_path(input)

    files = get_files_in_dir_with_subdirs(absolute_path)
    files = [file for file in files if file.split("/")[-1] not in IGNOREFILES]

    if bulk_report: #if True, the report will reflect all files as bulk. no single report per file
        json_report = defaultdict(dict)

    for file_ in files:
        if not bulk_report:
            json_report = defaultdict(dict)

        f = codecs.open(file_, 'r')
        code = f.read()
        file_name = file_.split('/')[-1]

        lexer = get_lexer(file_name, code, lexer_custom=lexer_custom)
        #dependend on lexer class it has to be called or not (e.lexer() vs lexer)
        try:
            results_generator = lexer.get_tokens_unprocessed(code)
        except TypeError:
            results_generator = lexer().get_tokens_unprocessed(code)

        for item in results_generator: #unpacking content of generator
            pos, token, value = item
            #filter for stringliterals. Distinguish here as for Scala the token is e.g. Stringliteral but for python it is token.text
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


# from console:
# python cli.py i18n-extract -i /Users/franzi/Workspace/artifacts_stringExtractor/directory_cloudflare -o /Users/franzi/Workspace/artifacts_stringExtractor/report_cloudflare --traceback

# within script: 
# extract('curdir', input="/Users/franzi/Workspace/artifacts_stringExtractor/directory_cloudflare", output="/Users/franzi/Workspace/artifacts_stringExtractor/directory_cloudflare", lexer_custom="NonJunk", bulk_report=False)

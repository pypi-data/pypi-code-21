#!/usr/bin/python3

"""
Pandoc filter to check for syntax errors 
"""

#
RULES={}
RULES[1]="" # YOU DO NOT TALK ABOUT FIGHT CLUB
RULES[2]="" # YOU DO NOT TALK ABOUT FIGHT CLUB
RULES[3]="TOO MANY ITEMS IN BULLET LIST"
RULES[4]="CODEBLOCK IN BULLET LIST"

from panflute import *
import sys


def prepare(doc):
    #
    # dwgc means Dalibo Writing Guidelines Checks
    #
    doc.dwgc_current_header=''
    doc.dwgc_total_checks=0
    # load config
    doc.dgwc_strict_mode=doc.get_metadata('dalibo_guidelines.strict_mode', default='False')
    # init all errors counters
    doc.dwgc_errors = {}
    for k,v in RULES.items():
        doc.dwgc_errors[k]=0

def checks(elem, doc):
    if type(elem) == Header:
        doc.dwgc_current_header=stringify(elem)

    if type(elem) == BulletList:
            elem.walk(bulletlist_has_too_many_items)
            elem.walk(no_codeblocks_in_bulletlists)

#
# RULE 3 : No more than 8 items in a bullet list in slide
#
def bulletlist_has_too_many_items(elem,doc):
    doc.dwgc_total_checks+=1

#
# RULE 4 : Do not put code blocks into a bullet list
#
def no_codeblocks_in_bulletlists(elem, doc):
    doc.dwgc_total_checks+=1
    if isinstance(elem, CodeBlock):
        debug("found {0} in slide '{1}'".format(RULES[4],doc.dwgc_current_header))
        doc.dwgc_errors[4]+=1 


def finalize(doc):
    total_errors=0
    debug("------- RUNNED %d CHECKS -------" % doc.dwgc_total_checks)
    for k,v in RULES.items():
        total_errors+=doc.dwgc_errors[k]
        if doc.dwgc_errors[k]>0:
             debug("{0} : {1} errors found".format(RULES[k], doc.dwgc_errors[k]))

    if total_errors>0:
        debug("------- {0} ERRORS FOUND -------".format(total_errors))
        if doc.dgwc_strict_mode:
            sys.exit(3)
    else:
        debug("------- NO ERROR FOUND ! -------")

def main(doc=None):
    return run_filter(checks, prepare=prepare, finalize=finalize, doc=doc)

if __name__ == "__main__":
    main()

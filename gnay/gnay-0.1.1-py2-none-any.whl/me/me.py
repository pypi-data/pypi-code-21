# -*- coding: utf-8 -*-
import sys,argparse

APP_DESC="""
yang test
"""

def main():
    print(APP_DESC)

    if len(sys.argv) == 1:
        sys.argv.append("--help")

    parser = argparse.ArgumentParser()
    parser.add_argument('-v','--verbose', default=0,help="print more debuging information")
    parser.add_argument('guest_name', help="guest name")
    args = parser.parse_args()
    # 获取对应参数只需要args.guest_name之类.
    print("I am Yang! Nice to meet you %s" %args.guest_name)

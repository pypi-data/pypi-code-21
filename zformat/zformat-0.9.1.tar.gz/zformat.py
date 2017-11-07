#!/usr/bin/env python3
# encoding: utf-8
"""Command Line entry point and main script.
"""

# Standard Python Library Imports
import os.path
import argparse
import sys
import re

# 3rd Party Imports
import jsbeautifier
import cssformatter
from jsmin import jsmin

# 1st Party Imports


def remove_css_variables(css_content):
    """Remove CSS variables from the CSS and replace each usage of the variable with its value (via RegEx).

    - Useful for IE 11, which does not support CSS variables: http://caniuse.com/#feat=css-variables
    """
    # Find all of the CSS variable declarations
    css_var_definitions = re.compile(r"--(?P<var_name>[\w-]+?):\s+?(?P<var_val>.+?);")
    variables = re.findall(css_var_definitions, css_content)
    # Some CSS variables use other nested CSS variables in their definition. Replace each by working backwards.
    for var_name, var_value in reversed(variables):
        css_content = css_content.replace("var(--" + var_name + ")", var_value)
    # Remove the :root{} section with all of the CSS variable declarations
    css_content = css_content.replace(re.match(r":root \{[\s\S]*?\}", css_content).group(0), "")
    return css_content


def format_file(path, minify, check_format):
    """Unified formatting function for files.
    """
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        sys.exit("Error: file does not exist {}".format(path))
    content = open(path, 'r').read()
    root, extension = os.path.splitext(path)


    if minify and check_format:
        sys.exit("Error: cannot minify and check the file's formatting")


    result = ""
    bad_formatting = False  # Used as return code for check_format
    if extension == '.js':
        if check_format:
            result = cssformatter.format_css(content, 'expand-bs', '    ')
            if result != content:
                bad_formatting = True
                print("{} not formatted correctly".format(path))
        elif minify:
            result = jsmin(content, quote_chars="""'\"`""")
        else:  # Format in-place
            result = jsbeautifier.beautify(content)
    elif extension == '.css':
        if check_format:
            result = cssformatter.format_css(content, 'expand-bs', '    ')
            if result != content:
                bad_formatting = True
                print("{} not formatted correctly".format(path))
        elif minify:
            result = remove_css_variables(content)
            result = cssformatter.format_css(result, 'compress')
        else:  # Format in-place
            result = cssformatter.format_css(content, 'expand-bs', '    ')
    else:
        sys.exit("Error: unknown file extension {}".format(extension))


    if check_format:
        return bad_formatting
    elif minify:
        path = root + ".min" + extension
        open(path, 'w').write(result)
    else:  # Format in-place
        open(path, 'w').write(result)


def main():
    """Command Line entry point.
    """
    arg_parser = argparse.ArgumentParser(
        description="An opinionated CLI formatter for JavaScript and CSS (check formatting, format, or minimize). "
                    "If the file is being beautified, the file's contents are replaced with the new "
                    "formatting. If the file is being minimized, we create a new file with `.min` "
                    "before the normal file extensions (e.g. `.min.js` or `.min.css`).\n\n For CSS "
                    "minification, this will remove CSS variables by using search and replace to "
                    "support IE 11."
    )
    arg_parser.add_argument('path', type=str, help="file's path to format")
    arg_parser.add_argument('-m', '--minify', default=False, action="store_true",
        help="minimize the file's content instead of beautifying")
    arg_parser.add_argument('-c', '--check', default=False, action="store_true",
        help="check the file's formatting only (print and return error code if incorrect)")
    args = arg_parser.parse_args()

    format_file(args.path, args.minify, args.check)


if __name__ == "__main__":
    main()

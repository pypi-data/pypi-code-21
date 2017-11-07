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


def format_css(content, minify):
    if minify:
        content = remove_css_variables(content)
        return cssformatter.format_css(content, 'compress')
    else:
        return cssformatter.format_css(content, 'expand-bs', '    ')


def format_js(content, minify):
    if minify:
        return jsmin(content, quote_chars="""'\"`""")
    else:
        return jsbeautifier.beautify(content)


def format_file(path, minify):
    """Unified formatting function for files.
    """
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        sys.exit("Error: file does not exist {}".format(path))
    content = open(path, 'r').read()
    root, extension = os.path.splitext(path)

    formatters = {
        ".js": format_js,
        ".css": format_css,
    }

    if extension not in formatters.keys():
        sys.exit("Error: unknown file extension {}".format(extension))

    fm_func = formatters[extension]
    result = fm_func(content, minify)

    if minify:
        path = root + ".min" + extension
    open(path, 'w').write(result)


def main():
    """Command Line entry point.
    """
    arg_parser = argparse.ArgumentParser(
        description="An opinionated CLI formatter for JavaScript and CSS (beautify or minimize).\n\n "
                    "If the file is being beautified, the file's contents are replaced with the new "
                    "formatting. If the file is being minimized, we create a new file with `.min` "
                    "before the normal file extensions (e.g. `.min.js` or `.min.css`).\n\n For CSS "
                    "minification, this will remove CSS variables by using search and replace to "
                    "support IE 11."
    )
    arg_parser.add_argument('path', type=str, help="file's path to format")
    arg_parser.add_argument('-m', '--minify', default=False, action="store_true",
        help="minimize the file's content instead of beautifying")
    args = arg_parser.parse_args()

    format_file(args.path, args.minify)


if __name__ == "__main__":
    main()

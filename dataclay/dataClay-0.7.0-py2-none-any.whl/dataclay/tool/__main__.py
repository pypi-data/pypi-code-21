"""Entrypoint for tool execution.

This module can be executed with `python -m dataclay.tool <parameters>`.
"""
import sys
import functions


if len(sys.argv) < 2:
    # We need at least a parameter
    print >> sys.stderr, "dataclay.tool requires at least the function parameter"
    exit(1)

func_name = sys.argv[1]
func = getattr(functions, func_name)

if not func:
    print >> sys.stderr, "Unknown dataclay.tool function '%s'" % func_name
    exit(2)

func(*sys.argv[2:])

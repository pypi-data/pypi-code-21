from __future__ import print_function
import sys, os

this_path = os.path.join(os.path.dirname(__file__), '.')
sys.path.insert(0, this_path)

c = get_config()

c.Exporter.filters = {
    'pretty_quotes': 'filters.pretty_quotes',
    'output_snapshots': 'filters.output_snapshots'
}

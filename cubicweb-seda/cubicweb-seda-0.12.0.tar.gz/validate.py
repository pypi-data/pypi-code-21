from os.path import join, dirname
import sys

from lxml import etree

schema_fpath = join(dirname(__file__), 'test', 'data', 'relaxng.rng')
print 'loading', schema_fpath
with open(schema_fpath) as stream:
    schema = etree.RelaxNG(etree.parse(stream))

for fpath in sys.argv[1:]:
    print 'checking', fpath
    with open(fpath) as stream:
        root = etree.parse(stream)
    schema.assert_(root)
    etree.RelaxNG(root)

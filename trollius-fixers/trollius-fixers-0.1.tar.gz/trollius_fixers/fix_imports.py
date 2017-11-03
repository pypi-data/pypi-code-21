import lib2to3.fixes.fix_imports


# We have to specify more than one module here, otherwise the code
# in lib2to3 gets a Leaf instead of a list. We use asyncio to pad out the
# list.
MAPPING = {'trollius': 'asyncio', 'asyncio': 'asyncio'}


class FixImports(lib2to3.fixes.fix_imports.FixImports):
    mapping = MAPPING

# Import pyesdoc
# ... pip install pyesdoc before running notebook
import pyesdoc

# Initialise data request.
# ... loads, parses & maps dreq.xml & dreqDefn.xml
pyesdoc.drq.initialize()

# Set helper pointers.
DRQ_DEFN = pyesdoc.drq.definition
DRQ = pyesdoc.drq.content

for table in DRQ_DEFN:
    for attribute in table:
        pass

# Iterate section item properties.
# for section in DRQ:
#     for item in section:
#     	print item.links.__dict__
#         # print section, item
#         for attr, value in item:
#             pass

# for section in DRQ:
#     for item in section:
#         for attr, value in item:
#             if not isinstance(value, (attr.type_python, type(None))):
#                 print section, item, attr, value, attr.type_python

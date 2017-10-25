import pyesdoc

print pyesdoc.search("cmip5", "models")
print pyesdoc.search("cmip5", "models", document_version="*")
print pyesdoc.search("cmip5", "models", institute="ipsl")
print pyesdoc.search("cmip6", "experiments")
print pyesdoc.search("cmip6", "experiments", sub_project="damip")
print pyesdoc.search("cmip6", "simulations")
print pyesdoc.search("cmip6", "machines")
print pyesdoc.search("cmip6", "performances")



UID = "ec9243df-26b7-4ed5-ba77-beb65bc13276"

d = pyesdoc.retrieve(UID)

d.name += "-666"
pyesdoc.publish(d)
d = pyesdoc.retrieve(UID)
assert d.name.endswith("-666")

pyesdoc.unpublish(d.meta.id, d.meta.version)
d = pyesdoc.retrieve(UID, d.meta.version)
assert d is None

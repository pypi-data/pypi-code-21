from cubicweb_compound import utils, CompositeGraph

graph = CompositeGraph(schema)
structure = graph.parent_structure('ConceptScheme')

optionals = utils.optional_relations(schema, structure)
for child, relations in structure.iteritems():
    sync_schema_props_perms(child, syncprops=False)

for rdef, parent_role in utils.mandatory_rdefs(schema, structure):
    sync_schema_props_perms((str(rdef.subject), str(rdef.rtype), str(rdef.object)),
                            syncprops=False)

sync_schema_props_perms('SEDAArchiveUnit', syncprops=False)

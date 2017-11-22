d = { "db_password": "localpass",
      "db_path"    : "/Users/martinrusilowicz/ext-apps/neo4j330",
      "owl_path"   : "/Users/martinrusilowicz/mnt/milstore/go/go.owl",
      "system"     : "unix",
      "tax_nodes"  : "/Users/martinrusilowicz/mnt/milstore/taxonomy/nodes.dmp",
      "tax_names"  : "/Users/martinrusilowicz/mnt/milstore/taxonomy/names.dmp",
      }

script = """
new.connection    test.my.local.db NEO4JV1 localhost neo4j "{db_password}" "{db_path}" +{system}
new.parcel        test.my.parcel
import.go         endpoints/test.my.parcel "{owl_path}"
import.taxonomy   endpoints/test.my.parcel "{tax_nodes}" "{tax_names}"
close             test.my.local.db
"""

for k, v in d.items():
    script = script.replace( "{" + k + "}", v )

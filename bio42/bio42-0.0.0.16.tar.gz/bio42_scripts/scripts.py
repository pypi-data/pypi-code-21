"""
These are the scripts available to the user within $(APP_NAME).
They could be considered as small "apps" that run on the database.
Scripts can also be defined in Scripts.cypher.

(Note that some of these scripts are internal and are not visible to the user)


*** Please see the Script class's constructor documentation in Script.py for the description of how scripts are specified. ***
"""
from intermake import register
from neocommand.helpers.special_types import TEdgeLabel, TNodeLabel, TNodeProperty, TNodeUid
from neocommand.extensions.plugin_classes.script import Script, HDbParam as DP, HScriptParam as SP
from bio42 import constants


__author__ = "Martin Rusilowicz"

DELETE_LIMIT = constants.DEFAULT_DELETE_LIMIT
BATCH_LIMIT = 1
MASS_LIMIT = 5000
DISPLAY_LIMIT = 10
LIST_LIMIT = 15

register( Script( name = "Get edge labels",
                  description = "Gets the distinct relationship types in the database",
                  cypher = "MATCH ()-[r]->() RETURN DISTINCT TYPE(r)" ) )

register( Script( name = "Count all nodes",
                  description = "Counts the number of nodes in the database",
                  cypher = "MATCH (n) RETURN COUNT(n)" ) )

register( Script( name = "Count all edges",
                  description = "Counts the number of edges in the database",
                  cypher = "MATCH ()-[r]->() RETURN COUNT(r)" ) )

register( Script( name = "Count nodes with a specified label",
                  description = "Counts the number of nodes with a specific label",
                  cypher = "MATCH (n:<LABEL>) RETURN COUNT(n)",
                  arguments = { "label": SP[ TNodeLabel ] } ) )

register( Script( name = "Count edges of type",
                  description = "Counts the number of edges with a specific type",
                  cypher = "MATCH ()-[r:<LABEL>]->() RETURN COUNT(r)",
                  arguments = { "label": SP[ TEdgeLabel ] } ) )

register( Script( name = "Join taxa",
                  description = "Joins together the taxa imported from the database to form the taxonomy tree.",
                  cypher = """MATCH (n:Sequence), (t:Taxon {scientific_name: n.`/organism`})
                                     MERGE (t)-[r:Contains]->(n)
                                     """ ) )

register( Script( name = "Create BLAST nodes",
                  description = """Creates a BlastNode with two Target edges for every Blast edge. Returns the number of new nodes (0 when done)""",
                  cypher = """MATCH (query:<LABEL>)
                              WHERE query.`<PROPERTY>` IS NULL
                              WITH query LIMIT <LIMIT>
                              
                              MATCH path = (query)-[blast:Blast]->(subject:Sequence)
                              CREATE (query)<-[queryRel:Target]-(blastNode:<CREATED>)-[subjectRel:Target]->(subject)
                              SET blastNode = blast
                              SET subjectRel = {subject: true, start: blast.subject_start, end: blast.subject_end}
                              SET queryRel = {subject: false, start: blast.query_start, end: blast.query_end}
                              SET query.`<PROPERTY>` = true
                              
                              RETURN COUNT(path)""",
                  arguments = { "label"   : [ SP[ TNodeLabel ], constants.NODE_SEQUENCE ],
                                "limit"   : [ SP[ int ], BATCH_LIMIT ],
                                "property": [ SP[ TNodeProperty ], constants.PROP_TRACKER_BLAST_NODES ],
                                "created" : [ SP[ TNodeLabel ], constants.NODE_BLAST ] } ) )

register( Script( name = "Count nodes with property set",
                  description = "Counts the number of nodes with a specific label and property set (the property must be set, it doesn't matter to what value).",
                  cypher = """MATCH (n:<LABEL>)
                              WHERE NOT (n.`<PROPERTY>` IS NULL)
                              RETURN COUNT(n)""",
                  arguments = { "label": SP[ TNodeLabel ]
                      , "property"     : SP[ TNodeProperty ] } ) )

register( Script( name = "Find seed nodes for batch-wise scripts",
                  description = "Finds unprocessed nodes for batch-wise scripts based on whether a specific marker property has been set. Also allows multiple threads to process different sets of nodes.",
                  cypher = """MATCH (<NAME>:<LABEL>)
                              WHERE <NAME>.`<PROPERTY>` IS NULL
                              AND ( ( ID(<NAME>) % <THREAD_COUNT> ) = <THREAD> )
                              WITH <NAME> LIMIT <LIMIT>
                              SET <NAME>.`<PROPERTY>` = True
                              WITH <NAME>""",
                  arguments = { "name": SP[ str ]
                      , "label"       : SP[ TNodeLabel ]
                      , "property"    : SP[ TNodeProperty ]
                      , "limit"       : [ DP[ int ], BATCH_LIMIT ]
                      , "thread_count": [ SP[ int ], 1 ]
                      , "thread"      : [ SP[ int ], 0 ] } ) )

register( Script( name = "Find non-transitive triplets",
                  description = "Finds all non-transitive triplets",
                  cypher = """MATCH p = (n1:Sequence)-[r1:Blast]-(n2:Sequence)-[r2:Blast]-(n3:Sequence)
                              where (not (n1:Sequence)-[:Blast]-(n3:Sequence))
                              return p limit <LIMIT>""",
                  arguments = { "limit": [ SP[ int ], DISPLAY_LIMIT ] } ) )

register( Script( name = "Find non-transitive chains of 5",
                  description = "Finds non-transitive chains of 5",
                  cypher = """MATCH p = (n1:Sequence)-[r1:Blast]-(n2:Sequence)-[r2:Blast]-(n3:Sequence)-[r3:Blast]-(n4:Sequence)-[r4:Blast]-(n5:Sequence)
                              where (not (n1:Sequence)--(n3:Sequence))
                              and (not (n1:Sequence)--(n4:Sequence))
                              and (not (n1:Sequence)--(n5:Sequence))
                              and (not (n2:Sequence)--(n4:Sequence))
                              and (not (n2:Sequence)--(n5:Sequence))
                              and (not (n3:Sequence)--(n5:Sequence))
                              and (abs(r1.position_delta) > 50)
                              and (abs(r2.position_delta) > 50)
                              and (abs(r3.position_delta) > 50)
                              and (abs(r4.position_delta) > 50)
                              return p limit 1
                              """ ) )

register( Script( name = "Find links between plasmids",
                  description = "Given two plasmids, finds the sequences they share in common",
                  cypher = """MATCH (a:Plasmid), (b:Plasmid)
                              WHERE a <> b
                              MATCH path = (a)-->(as:Sequence)-[:Blast]-(bs:Sequence)<--(b)
                              RETURN path LIMIT <LIMIT>""",
                  arguments = { "limit": [ SP[ int ], DISPLAY_LIMIT ] } ) )

register( Script( name = "Find links between organisms",
                  description = "Given two organisms, finds the sequences they share in common",
                  cypher = """MATCH (a:Taxon), (b:Taxon)
                              WHERE a <> b
                              AND NOT (a)<--(:Taxon)
                              AND NOT (b)<--(:Taxon)
                              AND (a)-->(:Sequence)
                              AND (b)-->(:Sequence)
                              WITH a, b LIMIT 1
                              MATCH path = (a)-->(as:Sequence)-[:Blast]-(bs:Sequence)<--(b)
                              RETURN path""" ) )

register( Script( name = "Lookup a node",
                  description = "Returns a specific property from a specific node",
                  cypher = "MATCH (a:<LABEL> {uid:\"<UID>\"}) RETURN a.`<PROPERTY>`",
                  arguments = { "uid"     : SP[ TNodeUid ],
                                "label"   : SP[ TNodeLabel ],
                                "property": SP[ TNodeProperty ],
                                "limit"   : [ SP[ int ], LIST_LIMIT ] } ) )

register( Script( name = "Find leaf taxa",
                  description = "Returns the list of leaf taxa",
                  cypher = "MATCH (a:Taxon) WHERE NOT (a)<--(:Taxon) RETURN a LIMIT <LIMIT>",
                  arguments = { "limit": [ SP[ int ], LIST_LIMIT ] } ) )

register( Script( name = "Find organism links between sequences",
                  description = """Given a sequence, finds all related (BLAST) sequences
                                   Draws the graph showing the full organism taxonomy of these sequences""",
                  cypher = """MATCH (n:Sequence)
                              WITH n LIMIT 1
                              MATCH p = (n:Sequence)-[:Blast]-(m:Sequence)-[:Contains]-(o:Taxon)-[:Inherits*]->(q:Taxon {name:"1"})
                              RETURN p
                              """ ) )

register( Script( name = "Join taxa to plasmids",
                  description = "Joins taxa to plasmids if the taxa have sequence data for that plasmid.",
                  cypher = """MATCH (a:Taxon)
            WHERE NOT (a)<--(:Taxon) AND (a)--(:Sequence)
            WITH a
            MATCH (a)--(b:Sequence)--(c:Plasmid)
            MERGE (a)-[:HasDataFor]->(c)""" ) )

register( Script( name = "Most related taxa",
                  description = "Finds the taxa which are most related based on sequence similarity",
                  cypher = """MATCH p = (a:Taxon)-[r:HasSimilarSequences]-(b:Taxon)
                              RETURN p, r.count
                              ORDER BY r.count DESC
                              LIMIT <LIMIT>
                              """,
                  arguments = { "limit": [ SP[ int ], DISPLAY_LIMIT ] } ) )

register( Script( name = "Find taxa with sequence data",
                  description = "Finds the set of taxa for which sequence data is present",
                  cypher = """MATCH (taxon:Taxon)
                              WHERE (taxon)-[:Contains]->(:Sequence)
                              RETURN taxon
                              """ ) )

register( Script( name = "Find nodes by search text in name (primary key)",
                  description = "Finds the nodes by text in their primary key",
                  cypher = """MATCH (node:<LABEL>)
                              WHERE node.<PROPERTY> CONTAINS "<SEARCH_TEXT>"
                              RETURN node
                              LIMIT <LIMIT>
                              """,
                  arguments = { "label"      : SP[ TNodeLabel ],
                                "search_text": SP[ str ],
                                "property"   : (SP[ TNodeProperty ], "name"),
                                "limit"      : [ SP[ int ], DISPLAY_LIMIT ] } ) )

register( Script( name = "Find nodes by search text anywhere",
                  description = "Finds the nodes with the specified search-text anywhere in their properties. Unfortunately doesn't work if there are nodes with esoteric property types.",
                  cypher = """MATCH (node:<LABEL>)
                              WHERE (ANY(property in KEYS(node) WHERE TOSTRING(node[property]) CONTAINS "<SEARCH_TEXT>"))
                              RETURN node
                              LIMIT <LIMIT>
                              """,
                  arguments = { "label"      : SP[ TNodeLabel ],
                                "search_text": SP[ str ],
                                "limit"      : [ SP[ int ], DISPLAY_LIMIT ] } ) )

register( Script( name = "(Test) Find \"Escherichia\" sequences",
                  description = "Test procedure that finds Escherichia sequences",
                  cypher = """MATCH (node:<LABEL>)
                              WHERE node._organism CONTAINS "<SEARCH_TEXT>"
                              RETURN node
                              LIMIT <LIMIT>
                              """,
                  arguments = { "label"      : (SP[ TNodeLabel ], "Sequence"),
                                "search_text": (SP[ str ], "Escherichia"),
                                "limit"      : [ SP[ int ], DISPLAY_LIMIT ] } ) )

register( Script( name = "Test connection",
                  description = "Returns the integer \"1\" from the server",
                  cypher = """RETURN 1""" ) )

register( Script( name = "(Test) Match any path",
                  description = "Test procedure that matches any path of length 5 in the database.",
                  cypher = """MATCH p = ()-[]->()-[]->() RETURN p LIMIT 1""" ) )

register( Script( name = "All sequences",
                  description = "Obtains full data for all sequences",
                  cypher = "MATCH (s:Sequence) return s" ) )

register( Script( name = "All sequence UIDs",
                  description = "Obtains the UIDs of all sequences",
                  cypher = "MATCH (s:Sequence) return s.uid" ) )

register( Script( name = "Find composite genes",
                  description = "Attempt at finding composite genes",
                  cypher = """MATCH (a:Sequence)-[ab:Blast]-(b:Sequence)
                              MATCH (a)-[ac:Blast]-(c:Sequence)
                              WHERE a <> b
                              AND b <> c
                              AND ab.end < ac.start
                              RETURN a, ab, b, ac, c
                              LIMIT <LIMIT>
                              """,
                  arguments = { "limit": [ SP[ int ], LIST_LIMIT ] } ) )

register( Script( name = "Unfold taxa",
                  description = "Given a taxon, shows how it inherits from the root.",
                  cypher = """MATCH p = (a:Taxon { uid:{uid} })<-[:Contains*]-(:Taxon { uid:"1" })
                              return p
                              """,
                  arguments = { "uid": SP[ TNodeUid ] } ) )

register( Script( name = "Relate taxa",
                  description = "Given two taxa, {a} and {b}, shows how they are related.",
                  cypher = """MATCH p = shortestpath( (a:Taxon { uid:{a} })-[:Contains*]-(b:Taxon { uid:{b} }) )
                              return p
                              """,
                  arguments = { "a": DP[ TNodeUid ],
                                "b": DP[ TNodeUid ] } ) )

register( Script( name = "Relate sequences",
                  description = "Given two sequences, {a} and {b}, shows how they are related.",
                  cypher = """MATCH p = shortestpath( (a:Sequence { uid:{a} })-[:Like*]-(b:Sequence { uid:{b} }) )
                               return p
                               """,
                  arguments = { "a": DP[ TNodeUid ],
                                "b": DP[ TNodeUid ] } ) )

register( Script( name = "Relate lemons",
                  description = "Given two lemons, {a} and {b}, shows how they are related.",
                  cypher = """MATCH p = shortestpath( (a:Lemon { uid:{a} })-[:Likes*]-(b:Lemon { uid:{b} }) )
                              return p
                              """,
                  arguments = { "a": DP[ TNodeUid ],
                                "b": DP[ TNodeUid ] } ) )

register( Script( name = "Find duplicate UIDs",
                  cypher = """match (n:<LABEL>), (m:<LABEL>) where n.uid = m.uid and n <> m return n.uid""",
                  description = "Finds nodes with duplicate UIDs.",
                  arguments = { "label": SP[ TNodeLabel ] } ) )

import cluster_searcher.commands as cs


cs.cluster_regex( "cluster([0-9]+)(untagged|\.fasta)" )
cs.load_leca( "/Users/martinrusilowicz/mnt/milstore-shared/LECA/conservedclustergeneannotationsfixed.txt" )
cs.load_kegg( "/Users/martinrusilowicz/mnt/milstore-shared/kegg/cell_cycle(hsa04110).xml" )
cs.load_blast( "/Users/martinrusilowicz/mnt/milstore-shared/allgenes.out" )
cs.resolve( silent = True, report = "/Users/martinrusilowicz/tmp/report.report" )
cs.translate( colour = cs.EResolveColour.BLAST )
cs.translate( colour = cs.EResolveColour.COMBINED )
cs.translate( colour = cs.EResolveColour.TEXT )
cs.describe()

print( "please confirm the files have been written to «/Users/martinrusilowicz/tmp/» and then delete the files" )
user = input( "confirm: " )

if user.lower() not in ("yes", "y"):
    raise ValueError( "Test failed." )

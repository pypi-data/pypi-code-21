from biothings_client import get_client
from BioThingsExplorer import pathViewer

t = pathViewer ()

mv = get_client("variant")
print (mv)

print (mv.getvariant("chr7:g.140453134T>C"))

mg = get_client("gene")
print (mg)

mg.getgene(1017, 'name,symbol,refseq')

md = get_client("drug")
print (md)

md.getdrug("ATBDZSAENDYQDW-UHFFFAOYSA-N", fields="pubchem")

mt = get_client("taxon")
print (mt)

print (mt.gettaxon(9606))


t.find_path ('drugname', 'wikipathways', excluded_nodes=['dbsnp', 'hgvs'])
             

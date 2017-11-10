species_synonyms = {
                    # Worm
                    '6239' : '6239',
                    'Caenorhabditis elegans' : '6239',
                    'C. elegans' : '6239',
                    'C.elegans' : '6239',

                    # Yeast
                    '1196866' : '1196866',
                    'Saccharomyces cerevisiae' : '1196866',
                    'S. cerevisiae' : '1196866',
                    'S.cerevisiae' : '1196866',

                    # Synechocystis
                    '1148' : '1148',
                    'Synechocystis sp. PCC 6803' : '1148',
                    'Synechocystis PCC 6803' : '1148',
                    'Synechocystis' : '1148',
                    'PCC 6803' : '1148',

                    # Fly
                    '7227' : '7227',
                    'Drosophila melanogaster' : '7227',
                    'D. melanogaster' : '7227',
                    'D.melanogaster' : '7227',

                    # Zebrafish
                    '7955' : '7955',
                    'Danio rerio' : '7955',
                    'D. rerio' : '7955',
                    'D.rerio' : '7955',
                    'Brachydanio rerio' : '7955',
                    
                    # Arabidopsis
                    '3702' : '3702',
                    'Arabidopsis thaliana' : '3702',
                    'A. thaliana' : '3702',
                    'A.thaliana' : '3702',
                    
                    # Tetrahymena
                    '5911' : '5911',
                    'Tetrahymena thermophila' : '5911',
                    'T.thermophila' : '5911',
                    'T. thermophila' : '5911'
                    }
links = {
        # Worm
        '6239' :
            {
            'gene' : 'http://www.wormbase.org/species/c_elegans/gene/{gene}',
            'pos'  : 'http://www.wormbase.org/tools/genome/gbrowse/'
                     'c_elegans_PRJNA13758'
                     '?name={chromosome.barename}%3A{start}..{stop}'
            },
        #Tetrahymena
        '5911' :
            {
            'gene' :'http://tet.ciliate.org/index.php/feature/details/{gene}',
            'pos' : 'http://www.jcvi.org/jbrowse/?data=tta2mic'
                    '&loc={chromosome.shortname}%3A{start}..{stop}'
		    '&tracks=DNA%2Cmac.scaffolds.nucmer&highlight='
            },
        # Yeast
        '1196866' :
            {
            'gene' : 'https://www.yeastgenome.org/locus/{gene}',
            'pos'  : 'https://browse.yeastgenome.org/'
                     '?loc={chromosome.shortname}%3A{start}..{stop}'
            },
        # Synechocystis
        '1148' :
            {
            'gene' : 'http://genome.microbedb.jp/cyanobase/GCA_000009725.1'
                     '/genes/{gene}',
            'pos'  : 'http://genome.microbedb.jp/jbrowse/index.html'
                     '?tracklist=1&nav=1&overview=1&tracks=CyanoBase'
                     '&data=cyanobase%2FGCA_000009725.1'
                     '&loc={chromosome.name}%3A{start}..{stop}'
            },
        # Fly
        '7227' :
            {
            'gene' : 'http://flybase.org/reports/{transcript}.html',
            'pos'  : 'http://flybase.org/cgi-bin/gbrowse2/dmel/'
                     '?name={chromosome.barename}%3A{start}..{stop}'
            },
        # Zebrafish
        '7955' :
            {
            'gene' : 'http://www.ensembl.org/Danio_rerio/Gene/Matches'
                     '?db=core;t={transcript}',
            'pos'  : 'http://zfin.org/gb2/gbrowse/zfin_ensembl/'
                     '?name={chromosome.barename}%3A{start}..{stop}'
            },
        # Arabidopsis
        '3702' :
            {
            'gene' : 'http://www.arabidopsis.org/servlets/TairObject'
                     '?name={transcript.basename}&type=locus',
            'pos'  : 'https://gbrowse.arabidopsis.org/cgi-bin/gb2/gbrowse/'
                     'arabidopsis/'
                     '?name={chromosome.shortname}%3A{start}..{stop}'
            }
        }

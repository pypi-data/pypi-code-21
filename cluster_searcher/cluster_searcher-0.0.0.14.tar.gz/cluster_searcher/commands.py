import urllib.request
import hashlib
import re
from enum import Enum
from collections import Counter, defaultdict
from typing import List, Dict, Optional, Set, Iterable
from xml.etree import ElementTree

from colorama import Fore, Back, Style
from os import path
from mhelper import ByRef, MOptional, array_helper, Dirname

from intermake import MCMD, MENV, command

from mhelper import io_helper, string_helper, SwitchError, file_helper, Filename, colours, ansi


# User responses
_USER_HELP = "help"
_USER_LECA_SHOW = "leca.show"
_USER_LECA_SUMMARISE = "leca.summarise"
_USER_KEGG_SHOW = "kegg.show"
_USER_KEGG_SUMMARISE = "kegg.summarise"
_USER_REMOVE_ONCE = "filter"
_USER_REMOVE = "remove"
_USER_STOP = "stop_asking"
_USER_UNSURE = "unsure"
_USER_NO = "no"
_USER_DOMAIN = "domain"
_USER_YES = "yes"

# Regular expressions
_RE_GENE_SYMBOL = re.compile( "gene_symbol:([^ ]+)", re.IGNORECASE )
_RE_DESC = re.compile( "description:([^[]*)", re.IGNORECASE )
_RE_CLUSTER = re.compile( "cluster([0-9]+)(?:untagged|\.fasta)", re.IGNORECASE )

# Garbage in the LECA file we need to remove
_GARBAGE = { "ESP", "universal homolog", "archaeal homolog", "bacterial homolog", "pattern match error" }

# Open files
_blast_file: "BlastFile" = None
_leca_file: "LecaFile" = None
_kegg_file: "KeggFile" = None
_last_report: List[str] = []
_last_report_file: str = None

# File extensions
__EXT_TXT = ".txt"
__EXT_KEGG = ".xml"
__EXT_LECA = ".txt"
__EXT_BLAST = ".tsv"
__EXT_REPORT = ".report"
__EXT_UDM = ".udm"
__EXT_FASTA = ".fasta"


class Settings:
    """
    :data last_blast: Last BLAST file loaded
    :data last_leca: Last LECA file loaded
    :data last_kegg: Last KEGG file loaded
    :data last_kegg_permit: Last KEGG permit settings
    """
    
    
    def __init__( self ):
        self.last_blast = None
        self.last_leca = None
        self.last_kegg = None
        self.last_kegg_permit = None


__settings = Settings()
settings = MENV.local_data.store.bind( "settings", __settings )


class BlastFile:
    def __init__( self, file_name: str ) -> None:
        self.contents: List[BlastLine] = []
        self.lookup_by_kegg: Dict[str, List[BlastLine]] = defaultdict( list )
        
        with MCMD.action( "Loading BLAST" ) as action:
            with open( file_name, "r" ) as file_in:
                for line in file_in:
                    blast_line = BlastLine( line.strip() )
                    self.lookup_by_kegg[blast_line.query_id].append( blast_line )
                    self.contents.append( blast_line )
                    action.still_alive()


class BlastLine:
    def __init__( self, line ) -> None:
        def ___fix_david( text ):
            return text.split( "|", 1 )[1].split( "_" )[1]
        
        
        elements = line.split( "\t" )
        
        self.query_id = elements[0]
        self.subject_id = ___fix_david( elements[1] )
        self.percentage_identity = float( elements[2] )
        self.alignment_length = int( elements[3] )
        self.mismatches = int( elements[4] )
        self.gap_opens = int( elements[5] )
        self.query_start = int( elements[6] )
        self.query_end = int( elements[7] )
        self.subject_start = int( elements[8] )
        self.subject_end = int( elements[9] )
        self.e_value = float( elements[10] )
        self.bit_score = float( elements[11] )
        self.__leca_gene = None
        self.__leca_gene_file = None
    
    
    def lookup_leca_gene( self ) -> "LecaGene":
        if self.__leca_gene_file != _leca_file:
            self.__leca_gene_file = _leca_file
            self.__leca_gene = _leca_file.lookup_by_leca.get( self.subject_id.lower() ) if _leca_file else None
            
            if not self.__leca_gene:
                if not _leca_file.blast_mismatch_warning:
                    _leca_file.blast_mismatch_warning = True
                    MCMD.warning( "One or more BLAST genes (e.g. «{}») do not match any gene from the LECA set.".format( self.subject_id ) )
        
        return self.__leca_gene


class LecaGene:
    """
    Represents a gene in the LECA file.
    """
    
    
    def __init__( self, cluster: "LecaCluster", text: str ) -> None:
        """
        Constructor
        :param text: Raw text from the LECA file, representing this gene 
        """
        self.clusters = set()
        self.clusters.add( cluster )
        self.text = text.strip().lower()
        self.name = self.text.split( " ", 1 )[0]
        
        m = _RE_GENE_SYMBOL.search( text )
        
        if m:
            self.gene_symbol = str( m.group( 1 ) ).strip( " ." ).lower()
        else:
            self.gene_symbol = ""
        
        m = _RE_DESC.search( text )
        if m:
            self.description = str( m.group( 1 ) ).strip( " ." ).lower()
        else:
            self.description = ""
    
    
    def removed_text( self, remove: List[str] ):
        text = self.text
        
        if remove:
            for to_remove in remove:
                text = text.lower().replace( to_remove.lower(), "..." )
        
        return text
    
    
    def __str__( self ):
        return "(LECA)" + Fore.YELLOW + (self.gene_symbol or "~{}".format( id( self ) )) + Fore.RESET


class LecaCluster:
    def __init__( self, name: str ):
        self.name: str = name
        self.genes: List[LecaGene] = []
        self.organisms = set()
    
    
    def finalise( self ):
        for gene in self.genes:
            self.organisms.add( gene.text[:3] )
    
    
    @property
    def xml( self ):
        return 'name="{}" num_genes="{}" num_organisms="{}" organisms="{}"'.format( self.name,
                                                                                    len( self.genes ),
                                                                                    len( self.organisms ),
                                                                                    ",".join( sorted( self.organisms ) ) )


class LecaFile:
    """
    Reads and parses the LECA file.
    """
    
    
    def __init__( self, file_name: str ):
        self.blast_mismatch_warning = False
        self.clusters: List[LecaCluster] = []
        self.lookup_by_leca: Dict[str, LecaGene] = { }
        current_cluster = None
        multi_warning = False
        self.num_duplicates = 0
        
        with open( file_name, "r" ) as file:
            with MCMD.action( "Loading" ) as action:
                for line in file:
                    action.increment( text = "{} clusters and {} genes".format( len( self.clusters ), len( self.lookup_by_leca ) ) )
                    line = line.strip()
                    
                    if line in _GARBAGE:
                        continue
                    
                    if line:
                        cluster_result = _RE_CLUSTER.search( line )
                        
                        if cluster_result:
                            cluster_name = cluster_result.group( 1 )
                            current_cluster = LecaCluster( cluster_name )
                            self.clusters.append( current_cluster )
                        else:
                            if current_cluster is None:
                                MCMD.warning( "Gene rejected because there is no cluster: «{}».".format( line ) )
                            else:
                                gene = LecaGene( current_cluster, line )
                                
                                if gene.name in self.lookup_by_leca:
                                    if gene.text != self.lookup_by_leca[gene.name].text:
                                        raise ValueError( "There are two genes with the same name «{}» but they have different content:\n«{}»\n«{}»".format( gene.name, gene.text, self.lookup_by_leca[gene.name].text ) )
                                    
                                    if not multi_warning:
                                        multi_warning = True
                                        MCMD.warning( "At least one gene (e.g. «{}») appears in multiple clusters.".format( gene.name ) )
                                    
                                    gene = self.lookup_by_leca[gene.name]
                                    gene.clusters.add( current_cluster )
                                    
                                    if len( gene.clusters ) == 2:
                                        self.num_duplicates += 1
                                
                                else:
                                    self.lookup_by_leca[gene.name] = gene
                                
                                current_cluster.genes.append( gene )
        
        for cluster in self.clusters:
            cluster.finalise()


class KeggClass:
    def __init__( self, id: int ) -> None:
        self.index: int = id
        self.genes: "Set[KeggGene]" = set()
        self.unique_gene: Optional[KeggGene] = None
    
    
    def __str__( self ) -> str:
        return "{}".format( self.index )
    
    
    def complete( self, wrn_unique: ByRef[bool] ) -> bool:
        for gene in self.genes:
            if len( gene.kegg_classes ) == 1:
                self.unique_gene = gene
                gene.unique_class = self
                return True
        
        if not wrn_unique.value:
            wrn_unique.value = True
            MCMD.warning( "There is no gene uniquely identifying one or more KEGG classes (e.g. «{}»).".format( self ) )
        
        return False


class KeggGene:
    """
    Represents a gene (or ortholog) in the KEGG file.
    
    :data gene_ids: KEGG ID(s) for this gene
    :data symbols:  KEGG symbols for this gene
    :data aaseq:    Amino acid sequence for this gene
    """
    
    
    def __init__( self, gene_id: str ):
        """
        CONSTRUCTOR
        See class comments for parameter meanings. 
        """
        self.gene_id: str = gene_id
        self.symbols: Set[str] = set()
        self.aaseq: str = ""
        self.full_info: str = ""
        self.kegg_classes: Set[KeggClass] = set()
        self.kegg_classes_indices: Set[int] = set()
        self.unique_class: Optional[KeggClass] = None
    
    
    def __str__( self ):
        """
        OVERRIDE 
        """
        return self.gene_id


class KeggFile:
    """
    Reads and parses the KEGG (KGML) file.
    """
    
    
    def __init__( self, file_name: str, permit: List[str] ) -> None:
        """
        CONSTRUCTOR 
        """
        # Create the container
        self.file_name: str = file_name
        self.genes: List[KeggGene] = []
        self.classes: Set[KeggClass] = set()
        self.genes_lookup_by_gene_id: Dict[str, KeggGene] = { }
        self.num_genes_rejected: int = 0
        
        # Parse the XML
        tree = ElementTree.parse( file_name )
        root = tree.getroot()
        entries = [x for x in root if x.tag == "entry"]
        
        # Keep track of what we've used
        used_names = set()
        repeated_names = set()
        warn_symbol = False
        warn_aaseq = False
        wrn_unique = ByRef[bool]( False )
        wrn_drop = False
        
        # Cache HTTP records for speed
        cache_folder = MENV.local_data.local_folder( "caches" )
        file_helper.delete_file( path.join( cache_folder, "cached.pickle" ) )  # update old file
        cache_fn = path.join( cache_folder, "cached2.pickle" )
        cached = io_helper.load_binary( cache_fn, { } )
        
        # Iterate over the XML
        for entry in MCMD.iterate( entries, "Resolving names via HTTP" ):
            # Get the gene ID list
            gene_ids = [x for x in entry.attrib["name"].split( " " ) if _is_gene_permitted( x, permit )]
            
            if not gene_ids:
                self.num_genes_rejected += 1
                continue
            
            # Create the class (one class per entry)
            kegg_class = KeggClass( entry.attrib["id"] )
            self.classes.add( kegg_class )
            
            # Iterate over genes in the class
            for gene_id in gene_ids:
                # Have we found this gene already?
                kegg_gene = self.genes_lookup_by_gene_id.get( gene_id )
                
                if kegg_gene is not None:
                    kegg_gene.kegg_classes.add( kegg_class )
                    kegg_gene.kegg_classes_indices.add( kegg_class.index )
                    kegg_class.genes.add( kegg_gene )
                    continue
                
                # Create the gene and add to the class
                kegg_gene = KeggGene( gene_id )
                kegg_gene.kegg_classes.add( kegg_class )
                kegg_gene.kegg_classes_indices.add( kegg_class.index )
                kegg_class.genes.add( kegg_gene )
                self.genes.append( kegg_gene )
                self.genes_lookup_by_gene_id[gene_id] = kegg_gene
                
                # Get the data via HTTP
                link = "http://rest.kegg.jp/get/{}".format( gene_id )
                kegg_gene.full_info = _get_url( cached, link )
                data_array = kegg_gene.full_info.split( "\n" )
                
                # Get the symbols
                for line in data_array:
                    if line.startswith( "NAME" ):
                        for y in [x.strip() for x in line[4:].split( "," ) if x]:
                            kegg_gene.symbols.add( y )
                
                # Get the AA sequence
                aa_seq = ""
                
                for index, line in enumerate( data_array ):
                    if line.startswith( "AA" ):
                        for i in range( index + 1, len( data_array ) ):
                            if not (data_array[i].startswith( "NT" )):
                                aa_seq = aa_seq + data_array[i]
                            else:
                                break
                
                kegg_gene.aaseq = aa_seq.replace( " ", "" )
                kegg_gene.aaseq_hexdigest = hashlib.sha256( kegg_gene.aaseq.encode( "utf-8" ) ).hexdigest()
                
                # Warnings?
                if not kegg_gene.symbols and not warn_symbol:
                    warn_symbol = True
                    MCMD.warning( "There is at least one gene (e.g. «{}») without at least one symbol.".format( kegg_gene ) )
                
                if not kegg_gene.aaseq and not warn_aaseq:
                    warn_aaseq = True
                    MCMD.warning( "There is at least one gene (e.g. «{}») with no AA sequence.".format( kegg_gene ) )
                
                if kegg_gene.gene_id in used_names:
                    repeated_names.add( kegg_gene.gene_id )
                else:
                    used_names.add( kegg_gene.gene_id )
        
        to_drop = set()
        kegg_classes = list( sorted( self.classes, key = lambda x: x.index ) )
        
        for index, kegg_class in enumerate( kegg_classes ):
            for kegg_class_2 in kegg_classes[index + 1:]:
                if kegg_class.genes == kegg_class_2.genes:
                    if not wrn_drop:
                        wrn_drop = True
                        MCMD.warning( "One or more KEGG classes (e.g. «{}») will be dropped because they are identical to another KEGG class (e.g. «{}»).".format( kegg_class_2, kegg_class ) )
                    
                    to_drop.add( kegg_class_2 )
        
        self.num_classes_dropped = len( to_drop )
        
        for kegg_class in to_drop:
            for kegg_gene in kegg_class.genes:
                kegg_gene.kegg_classes.remove( kegg_class )
            
            self.classes.remove( kegg_class )
        
        kegg_classes = list( sorted( self.classes, key = lambda x: x.index ) )
        
        self.num_classes_not_unique = 0
        
        for kegg_class in kegg_classes:
            if not kegg_class.complete( wrn_unique ):
                self.num_classes_not_unique += 1
        
        # Save the HTTP cache
        io_helper.save_binary( cache_fn, cached )
        
        # Warn about repeated names
        if repeated_names:
            MCMD.warning( "There is at least one gene name (e.g. «{}») that is used by more than one gene. Do not continue. Please change the naming strategy.".format( array_helper.first( repeated_names ) ) )


class EConfidence( Enum ):
    """
    Confidence level of the match.
    
    The target set comprises all LECA genes (when the `combine` flag is set) or a cluster of LECA genes (when the `combine` flag is not set).
    
    See the `COLOURS` field for the corresponding colours.
    
    :data NO_MATCH:         Level 1. Gene not found in the target set
    :data ERROR:            Level 2. Gene found or not found, we can't report because the gene does not possess a viable UID.
    :data TEXT_CONTAINS:    Level 3. Gene found in the text of a gene of the target set.
    :data NAME_NUMERIC:     Level 4. Gene found in the name of a a gene in the target set, but suffixed with a number. The gene name itself does not end with a number.
    :data USER_NOT_FOUND:   Level 5. User reported gene as not found ("no").
    :data USER_FOUND:       Level 6. User reported gene as found ("yes")
    :data USER_AMBIGUOUS:   Level 7. User reported gene as ambiguous ("unsure")
    :data USER_DOMAIN:      Level 8. User reported gene domain as present ("domain")
    :data NAME_EXACT:       Level 9. Exact gene name found.
    """
    NO_MATCH = 1
    TEXT_CONTAINS = 3
    NAME_NUMERIC = 4
    USER_NOT_FOUND = 5
    USER_FOUND = 6
    USER_AMBIGUOUS = 7
    USER_DOMAIN = 8
    NAME_EXACT = 9


class EBlastConfidence( Enum ):
    """
    Confidence level of a BLAST match.
    
    See the `COLOURS` field for the corresponding colours.
    
    :data NO_MATCH:     No BLAST match
    :data SINGLE:       One cluster OR the `combine` flag is set
    :data MULTIPLE:     Multiple clusters (not applicable when the `combine` flag is set)
    """
    NO_MATCH = 0
    SINGLE = 1
    MULTIPLE = 2


# Colours of the confidence levels:
# These translate a confidence level into a colour tuple
# The colour tuple is:  [0]: Priority (if a class contains two genes with different colours either the highest or lowest priority colour will be used, depending on the settings)
#                       [1]: Text (foreground)
#                       [2]: Fill (background)
COLOURS_TEXT = { EConfidence.NAME_EXACT    : (0, colours.BLACK, colours.GREEN),
                 EConfidence.NAME_NUMERIC  : (1, colours.BLACK, colours.YELLOW),
                 EConfidence.USER_FOUND    : (2, colours.BLACK, colours.DARK_GREEN),
                 EConfidence.USER_NOT_FOUND: (3, colours.BLACK, colours.DARK_RED),
                 EConfidence.USER_AMBIGUOUS: (4, colours.BLACK, colours.DARK_BLUE),
                 EConfidence.USER_DOMAIN   : (5, colours.BLACK, colours.DARK_CYAN),
                 EConfidence.TEXT_CONTAINS : (6, colours.BLACK, colours.BLUE),
                 EConfidence.NO_MATCH      : (8, colours.BLACK, colours.RED) }

COLOURS_BLAST = { EBlastConfidence.NO_MATCH: (0, colours.BLACK, colours.ORANGE),
                  EBlastConfidence.SINGLE  : (1, colours.BLACK, colours.LIME),
                  EBlastConfidence.MULTIPLE: (2, colours.BLACK, colours.SPRING_GREEN) }

BLAST_SUCCESS_1A = colours.LIME
BLAST_SUCCESS_2P = colours.SPRING_GREEN
BLAST_NO_SUCCESS = colours.RED

TERMS_AMBIGUOUS = colours.GRAY
TERMS_MATCH = colours.BLACK
TERMS_MISMATCH = colours.MAGENTA

COLOURS_COMBINED = { (EConfidence.NAME_EXACT, EBlastConfidence.NO_MATCH)    : (0, TERMS_MISMATCH, BLAST_NO_SUCCESS),
                     (EConfidence.NAME_EXACT, EBlastConfidence.SINGLE)      : (1, TERMS_MATCH, BLAST_SUCCESS_1A),
                     (EConfidence.NAME_EXACT, EBlastConfidence.MULTIPLE)    : (2, TERMS_MATCH, BLAST_SUCCESS_2P),
                     (EConfidence.NAME_NUMERIC, EBlastConfidence.NO_MATCH)  : (3, TERMS_AMBIGUOUS, BLAST_NO_SUCCESS),
                     (EConfidence.NAME_NUMERIC, EBlastConfidence.SINGLE)    : (4, TERMS_AMBIGUOUS, BLAST_SUCCESS_1A),
                     (EConfidence.NAME_NUMERIC, EBlastConfidence.MULTIPLE)  : (5, TERMS_AMBIGUOUS, BLAST_SUCCESS_2P),
                     (EConfidence.USER_FOUND, EBlastConfidence.NO_MATCH)    : (6, TERMS_MISMATCH, BLAST_NO_SUCCESS),
                     (EConfidence.USER_FOUND, EBlastConfidence.SINGLE)      : (7, TERMS_MATCH, BLAST_SUCCESS_1A),
                     (EConfidence.USER_FOUND, EBlastConfidence.MULTIPLE)    : (8, TERMS_MATCH, BLAST_SUCCESS_2P),
                     (EConfidence.USER_NOT_FOUND, EBlastConfidence.NO_MATCH): (9, TERMS_MATCH, BLAST_NO_SUCCESS),
                     (EConfidence.USER_NOT_FOUND, EBlastConfidence.SINGLE)  : (10, TERMS_MISMATCH, BLAST_SUCCESS_1A),
                     (EConfidence.USER_NOT_FOUND, EBlastConfidence.MULTIPLE): (11, TERMS_MISMATCH, BLAST_SUCCESS_2P),
                     (EConfidence.USER_AMBIGUOUS, EBlastConfidence.NO_MATCH): (12, TERMS_AMBIGUOUS, BLAST_NO_SUCCESS),
                     (EConfidence.USER_AMBIGUOUS, EBlastConfidence.SINGLE)  : (13, TERMS_AMBIGUOUS, BLAST_SUCCESS_1A),
                     (EConfidence.USER_AMBIGUOUS, EBlastConfidence.MULTIPLE): (14, TERMS_AMBIGUOUS, BLAST_SUCCESS_2P),
                     (EConfidence.USER_DOMAIN, EBlastConfidence.NO_MATCH)   : (15, TERMS_AMBIGUOUS, BLAST_NO_SUCCESS),
                     (EConfidence.USER_DOMAIN, EBlastConfidence.SINGLE)     : (16, TERMS_AMBIGUOUS, BLAST_SUCCESS_1A),
                     (EConfidence.USER_DOMAIN, EBlastConfidence.MULTIPLE)   : (17, TERMS_AMBIGUOUS, BLAST_SUCCESS_2P),
                     (EConfidence.TEXT_CONTAINS, EBlastConfidence.NO_MATCH) : (18, TERMS_AMBIGUOUS, BLAST_NO_SUCCESS),
                     (EConfidence.TEXT_CONTAINS, EBlastConfidence.SINGLE)   : (19, TERMS_AMBIGUOUS, BLAST_SUCCESS_1A),
                     (EConfidence.TEXT_CONTAINS, EBlastConfidence.MULTIPLE) : (20, TERMS_AMBIGUOUS, BLAST_SUCCESS_2P),
                     (EConfidence.NO_MATCH, EBlastConfidence.NO_MATCH)      : (24, TERMS_MATCH, BLAST_NO_SUCCESS),
                     (EConfidence.NO_MATCH, EBlastConfidence.SINGLE)        : (25, TERMS_MISMATCH, BLAST_SUCCESS_1A),
                     (EConfidence.NO_MATCH, EBlastConfidence.MULTIPLE)      : (26, TERMS_MISMATCH, BLAST_SUCCESS_2P) }


class Result:
    """
    Represents a LECA-KEGG gene match.
    """
    
    
    def __init__( self, symbol: str, leca_gene: LecaGene, confidence: EConfidence ):
        """
        CONSTRUCTOR
        :param symbol:          Symbol the match was made under 
        :param leca_gene:       Matching gene in the LECA set 
        :param confidence:      Confidence of the match 
        """
        self.gene_symbol = symbol
        self.leca_gene = leca_gene
        self.confidence = confidence
    
    
    def __repr__( self ):
        return "{} ({}) {}".format( self.leca_gene, Fore.BLUE + str( self.confidence ) + Fore.RESET, Fore.YELLOW + str( self.gene_symbol ) + Fore.RESET )


class ConfidenceQuery:
    """
    :data gene_symbols:    Aliases for this gene 
    :data interactive:     Permit interactive searching 
    :data remove:          Exclude these text literals when searching descriptions 
    :data verbose:         Provide more information when interactively searching
    """
    
    
    def __init__( self, *, gene_symbols: Iterable[str], ref_interactive: ByRef[bool], remove: Optional[List[str]], show_leca: bool, show_kegg: bool, by_cluster: bool ):
        self.gene_symbols = gene_symbols
        self.__interactive = ref_interactive
        self.remove = remove if remove is not None else []
        self.show_leca = show_leca
        self.show_kegg = show_kegg
        self.by_cluster = by_cluster
    
    
    @property
    def interactive( self ) -> bool:
        return self.__interactive.value
    
    
    @interactive.setter
    def interactive( self, value: bool ):
        self.__interactive.value = value
    
    
    def copy( self ):
        return ConfidenceQuery( gene_symbols = list( self.gene_symbols ), ref_interactive = self.__interactive, remove = list( self.remove ), show_leca = self.show_leca, show_kegg = self.show_kegg, by_cluster = self.by_cluster )


@command()
def draw_kgml( file_name: str ):
    """
    Draws the KGML file using BioPython.
    At the time of writing this isn't very good.
    :param file_name:   File to draw
    """
    from Bio.Graphics import KGML_vis
    from Bio.KEGG.KGML import KGML_parser
    pathway = KGML_parser.read( file_helper.read_all_text( file_name ) )
    kgml_map = KGML_vis.KGMLCanvas( pathway )
    kgml_map.draw( file_name + '_drawing.png' )


def _is_gene_permitted( lst, permitted ):
    """
    Obtains if the KEGG type of the entity is permitted.
    For instance we allow orthologies (ko:xxx) to pass, but not compounds (cpd:xxx) or things we don't understand (blah:xxx).
    """
    if permitted is None:
        return True
    
    if " " in lst:
        lst = lst.split( " ", 1 )[0]
    
    if not ":" in lst:
        return False
    
    type_ = lst.split( ":" )[0]
    
    return type_.lower() in permitted


def _get_url( cached: Dict[str, str], link: str ):
    """
    Gets the URL, from the cache if available.
    """
    result = cached.get( link )
    
    if result is None:
        try:
            result = urllib.request.urlopen( link ).read().decode( "utf-8" )
        except Exception as ex:
            MCMD.warning( "Bad response from «{}»: {}".format( link, ex ) )
            return ""
        
        cached[link] = result
    
    return result


@command()
def load_blast( file_name: MOptional[Filename[__EXT_BLAST]] = None ):
    """
    Loads the LECA clusters file.
    
    :param file_name:   File to load, or `None` for the last file.
                        If this is `None` the last file will be loaded.
    """
    if not file_name:
        file_name = settings.last_blast
    
    if not file_name:
        raise ValueError( "load_blast: A filename must be specified if there is no recent file." )
    
    global _blast_file
    _blast_file = BlastFile( file_name )
    MCMD.print( "{} BLASTs loaded.".format( len( _blast_file.contents ) ) )
    
    if not _blast_file.contents:
        raise ValueError( "The BLAST file has been loaded but no entries were found." )
    
    settings.last_blast = file_name


@command()
def load_leca( file_name: MOptional[Filename[__EXT_LECA]] = None ):
    """
    Loads the LECA clusters file.
    
    :param file_name:   File to load or `None` for the last file.
                        If this is `None` the last file will be loaded.
    """
    if not file_name:
        file_name = settings.last_leca
    
    if not file_name:
        raise ValueError( "load_leca: A filename must be specified if there is no recent file." )
    
    global _leca_file
    _leca_file = LecaFile( file_name )
    MCMD.print( "{} clusters and {} genes loaded. {} genes appear in more than one cluster.".format( len( _leca_file.clusters ),
                                                                                                     len( _leca_file.lookup_by_leca ),
                                                                                                     _leca_file.num_duplicates ) )
    
    if not _leca_file.clusters:
        raise ValueError( "The LECA file has been loaded but no clusters were identified." )
    
    settings.last_leca = file_name


@command()
def load_kegg( file_name: MOptional[Filename[__EXT_KEGG]], permit: Optional[List[str]] = None ):
    """
    Loads the KEGG (KGML) file.
    
    :param permit:      List of gene types permitted, e.g. `hsa` for human or `eco` for E-coli.
                        If filename is `None` then, unless specified, the last used `permit` value is used. 
    :param file_name:   File to load.
                        Obtain this by selecting `download KGML` from a KEGG pathway. The `Reference Pathway (KO)` is recommended.
                        If this is `None` the last file will be loaded.
    """
    global _kegg_file
    
    if not file_name:
        file_name = settings.last_kegg
        
        if not permit:
            permit = settings.last_kegg_permit
    
    if not file_name:
        raise ValueError( "load_kegg: A filename must be specified if there is no recent file." )
    
    _kegg_file = KeggFile( file_name, permit )
    msg = "{} genes. {} names. {} sequences. {} genes rejected. {} classes were duplicates. {} classes are non-identifiable."
    MCMD.print( msg.format( len( _kegg_file.genes ),
                            sum( len( gene.symbols ) for gene in _kegg_file.genes ),
                            sum( 1 for gene in _kegg_file.genes if gene.aaseq ),
                            _kegg_file.num_genes_rejected,
                            _kegg_file.num_classes_dropped,
                            _kegg_file.num_classes_not_unique ) )
    
    if not _kegg_file.genes:
        raise ValueError( "The KEGG file has been loaded but no permissible genes were found." )
    
    settings.last_kegg = file_name
    settings.last_kegg_permit = permit


@command()
def write_leca_names( file_name: Filename[__EXT_TXT] = "stdout", overwrite: bool = False ) -> None:
    """
    Writes the LECA names to a file
    :param file_name:   File to write to
    :param overwrite:   Overwrite without prompt
    """
    
    overwrite_all = ByRef[bool]( overwrite )
    file_out = __open_write( file_name, "names", overwrite_all )
    
    try:
        for cluster, leca_genes in _leca_file.clusters:
            for leca_gene in leca_genes:  # type: LecaGene
                file_out.write( leca_gene.name )
    finally:
        file_out.close()


@command()
def write_fasta( file_name: Filename[__EXT_FASTA] = "stdout", overwrite: bool = False ) -> None:
    """
    Writes the FASTA file from the current KEGG pathway.
    :param overwrite:   Overwrite without prompt
    :param file_name:   File to write to. Also accepts:
                        «stdout» - write to STDOUT
                        «.xxx» - use the name of the kegg file, but replace the extension with «.xxx»
                        «.»  - same as «.fasta»  
    """
    overwrite_all = ByRef[bool]( overwrite )
    
    if _kegg_file is None or not _kegg_file.genes:
        raise ValueError( "Cannot write FASTA because KEGG has not been loaded." )
    
    if file_name == ".":
        file_name = ".fasta"
    
    if file_name.startswith( "." ):
        file_name = file_helper.replace_extension( _kegg_file.file_name, file_name )
    
    used_names = set()
    file_out = __open_write( file_name, "fasta", overwrite_all = overwrite_all )
    good = 0
    bad = 0
    
    try:
        for kegg_gene in MCMD.iterate( _kegg_file.genes, "Writing genes" ):
            if kegg_gene.aaseq:
                name = kegg_gene.gene_id
                
                if name in used_names:
                    raise ValueError( "Refusing to write the FASTA file because the name «{}» is not unique. Try using a different naming strategy.".format( name ) )
                
                file_out.write( ">{}\n".format( name ) )
                file_out.write( kegg_gene.aaseq )
                file_out.write( "\n" )
                good += 1
            else:
                bad += 1
    finally:
        file_out.close()
    
    MCMD.print( "{} gene-sequences written and empty {} gene-sequences skipped.".format( good, bad ) )


class _StdOutWriter:
    """
    Handles writing to STDOUT instead of a file.
    """
    
    
    def __init__( self, title ):
        self.title = title
        self.lines = []
    
    
    def write( self, text ):
        self.lines.append( text )
    
    
    def close( self ):
        MCMD.print( "Writing output to STDOUT." )
        
        print( Fore.GREEN + Back.YELLOW + self.title + Style.RESET_ALL )
        
        for line in self.lines:
            print( Fore.GREEN + line + Fore.RESET, end = "" )


def __open_write( file_name, title, overwrite_all: ByRef[bool] ):
    """
    Opens a file for writing, also accepts `stdout` as the file name.
    """
    if file_name.lower() == "stdout":
        MCMD.print( "Ready to write to standard output." )
        return _StdOutWriter( title )
    else:
        MCMD.print( "Ready to write to «{}»".format( file_name ) )
        
        if path.isfile( file_name ):
            if not overwrite_all.value:
                q = MCMD.question( "The previous file «{}» is in the way and will be overwritten.".format( file_name ), [True, False, "always"] )
                
                if q is False:
                    raise FileExistsError( "A previous file «{}» is in the way.".format( file_name ) )
                elif q is True:
                    pass
                elif q == "always":
                    overwrite_all.value = True
            
            MCMD.warning( "The previous file «{}» is in the way and will be overwritten.".format( file_name ) )
        
        return open( file_name, "w" )


class EResolveColour( Enum ):
    """
    How to colour the output.
    
    :data TEXT:     By text
    :data BLAST:    By BLAST
    :data COMBINED: By text and BLAST
    :data BEST:     A variant of `COMBINED` 
    """
    TEXT = 1
    BLAST = 2
    COMBINED = 3


@command()
def reload():
    """
    Reloads last loaded files.
    """
    load_leca()
    load_kegg()
    load_blast()


@command()
def resolve( silent: bool = False,
             using: Optional[str] = None,
             remove: Optional[List[str]] = None,
             combine: bool = False,
             report: MOptional[Filename[__EXT_REPORT]] = None,
             overwrite: bool = False,
             all: bool = False ):
    """
    Prints the overlap between the loaded KEGG, LECA and BLAST sets.
    
    :param overwrite:       Overwrite files without prompt
    :param using:           Set this to a gene symbol or kegg ID and only that gene will be resolved.
                            Using this option changes the default output filename to stdout.
    :param report:          Output REPORT file.
                            If set, a CLUSTERS file is written.
                            If not set, no CLUSTERS output is written.
                            Accepts `None` (default) and `stdout` as a value.
                            The default is a file is generated adjacent to your KEGG file, when `using` is not set.
                            When `using` is set, the default is `stdout`.
                            Note: The `combine` parameter affects the output.
    :param all:             Set this to `True` and a warning will be generated if the KEGG gene isn't in BLAST
                            (i.e. if you are using all clusters, not just the conserved ones)
    :param silent:          Don't run in interactive mode.
                            If set, no interactive prompts are shown.
                            If not set, interactive prompts are shown for ambiguous results (BLUE).
                            
    :param remove:          Remove this text from search.
                            Use this to ignore phrases which confuse gene names (e.g. "CYCLE" being mistaken for "CYC").
                            In interactive mode these can always be added later.
                            
    :param combine:         Combine clusters.
                            If set, one result per gene is yielded. This also greatly reduces the number of interactive prompts!
                            If not set, one result per gene and cluster is yielded.
    """
    if _kegg_file is None:
        raise ValueError( "You must load the KEGG data before calling `resolve`. Status = Not loaded." )
    
    if not _kegg_file.genes or _leca_file is None or not _leca_file.clusters:
        raise ValueError( "You must load the KEGG data before calling `resolve`. Status = Loaded, empty." )
    
    if _leca_file is None:
        raise ValueError( "You must load the LECA data before calling `resolve`. Status = Not loaded." )
    
    if not _leca_file.clusters:
        raise ValueError( "You must load the LECA data before calling `resolve`. Status = Loaded, empty." )
    
    if _blast_file is None:
        raise ValueError( "You must load the BLAST data before calling `resolve`. Status = Not loaded." )
    
    if not _blast_file.contents:
        raise ValueError( "You must load the BLAST data before calling `resolve`. Status = Loaded, empty." )
    
    # Get the remove list 
    remove = remove if remove is not None else []
    
    # Keep track of interactive settings
    ref_interactive = ByRef[bool]( not silent )
    
    # File handles
    report_file = None
    diagram_file = None
    repeated_names = { }
    
    if report is None:
        report = "default"
    
    if report == "default":
        if using:
            report = "stdout"
        else:
            report = file_helper.replace_extension( _kegg_file.file_name, ".report" if not combine else ".report_c" )
    
    wrn_mismatch = ByRef[bool]( not all )
    overwrite_all = ByRef[bool]( overwrite )
    
    try:
        #
        # Open files
        #
        
        # - CLUSTERS file
        report_file = __open_write( report, "report", overwrite_all )
        report_file.write( '<report version="{}">\n'.format( 3 ) )
        
        #
        # Iterate over genes in the KEGG pathway
        #
        kegg_gene = ""
        
        for index, kegg_gene in MCMD.enumerate( _kegg_file.genes, "Exhaustive search", text = lambda x: "{} of {}: {}".format( x, len( _kegg_file.genes ), str( kegg_gene ) ) ):
            assert isinstance( kegg_gene, KeggGene )
            
            if using and using not in kegg_gene.symbols and using != kegg_gene.gene_id:
                continue
            
            #
            # Get the confidence level(s) for this gene
            #
            query = ConfidenceQuery( gene_symbols = kegg_gene.symbols,
                                     ref_interactive = ref_interactive,
                                     remove = remove,
                                     show_leca = False,
                                     show_kegg = False,
                                     by_cluster = not combine )
            
            text_results: Dict[LecaCluster, EConfidence] = find_confidences( query, "GENE {}/{}".format( index, len( _kegg_file.genes ) ) )
            blast_results: Dict[LecaCluster, int] = find_blast_confidences( kegg_gene, wrn_mismatch )
            
            #
            # Get the best confidence level for this gene
            #
            best_text = EConfidence.NO_MATCH
            
            for confidence in text_results.values():
                if confidence.value > best_text.value:
                    best_text = confidence
            
            if len( blast_results ) == 0:
                best_blast = EBlastConfidence.NO_MATCH
            elif len( blast_results ) == 1:
                best_blast = EBlastConfidence.SINGLE
            else:
                best_blast = EBlastConfidence.MULTIPLE
            
            #
            # Write the REPORT file
            #
            if report is not None:
                all_organisms = set()
                text_organisms = __get_organisms( text_results )
                blast_organisms = __get_organisms( blast_results )
                all_organisms.update( text_organisms )
                all_organisms.update( blast_organisms )
                
                report_file.write( '    <gene name="{}" symbols="{}" classes="{}" unique="{}" num_organisms="{}" organisms="{}">\n'.format( kegg_gene.gene_id,
                                                                                                                                            ",".join( kegg_gene.symbols ),
                                                                                                                                            ",".join( str( x.index ) for x in kegg_gene.kegg_classes ),
                                                                                                                                            kegg_gene.unique_class.index if kegg_gene.unique_class is not None else "-1",
                                                                                                                                            len( all_organisms ),
                                                                                                                                            ",".join( all_organisms ) ) )
                
                # Warning
                if kegg_gene.gene_id in repeated_names:
                    report_file.write( '    <warning>!!!NON_UNIQUE_NAME!!!</warning>\n' )
                
                # TEXT
                report_file.write( '        <text confidence="{}" num_clusters="{}" num_organisms="{}" organisms="{}">\n'.format( best_text.name,
                                                                                                                                  len( text_results ),
                                                                                                                                  len( text_organisms ),
                                                                                                                                  ",".join( text_organisms ) ) )
                
                for cluster, confidence in text_results.items():
                    report_file.write( '            <cluster confidence="{}" {} />\n'.format( confidence.name, cluster.xml ) )
                
                report_file.write( '        </text>\n' )
                
                # BLAST
                report_file.write( '        <blast confidence="{}" num_clusters="{}" num_genes="{}" num_organisms="{}" organisms="{}">\n'.format( best_blast.name,
                                                                                                                                                  len( blast_results ),
                                                                                                                                                  sum( blast_results.values() ),
                                                                                                                                                  len( blast_organisms ),
                                                                                                                                                  ",".join( blast_organisms ) ) )
                
                for cluster, count in blast_results.items():
                    report_file.write( '            <cluster num_matches="{}" {} />\n'.format( count, cluster.xml ) )
                
                report_file.write( '        </blast>\n' )
                
                report_file.write( '    </gene>\n' )
    
    finally:
        if report_file is not None:
            report_file.write( '</report>\n' )
            
            global _last_report, _last_report_file
            
            if isinstance( report_file, _StdOutWriter ):
                _last_report = report_file.lines
                _last_report_file = None
            else:
                _last_report = []
                _last_report_file = report
            
            report_file.close()
        
        if diagram_file is not None:
            diagram_file.close()


def __get_organisms( confidences: Iterable[LecaCluster] ) -> Set[str]:
    organisms = set()
    
    for cluster in confidences:
        for organism in cluster.organisms:
            organisms.add( organism )
    
    return organisms


@command()
def process_all( directories: List[str], silent: bool = True, combine: bool = False, all: bool = False ):
    """
    Processes all files in the specified directory.
    **Existing files are overwritten**
    
    :param directories:   Directory to process 
    :param silent:      Passed to `resolve`. Note the default is different. 
    :param all:         Passed to `resolve`. Note the default is different.
    :param combine:     Passed to `resolve`.
    """
    file_names = []
    
    for directory in directories:
        file_names.extend( file_helper.list_dir( directory, ".xml" ) )
    
    for file_name in MCMD.iterate( file_names, "Iterating files" ):
        m = re.search( "\(([a-z]+)[0-9]+\)", file_name )
        
        if m is None:
            continue
        
        load_kegg( file_name, permit = [m.group( 1 )] )
        resolve( silent = silent, combine = combine, overwrite = True, all = all )
        translate( EResolveColour.BLAST, overwrite = True )
        translate( EResolveColour.COMBINED, overwrite = True )
        translate( EResolveColour.TEXT, overwrite = True )


@command()
def translate_all( directory: Dirname ):
    """
    Translates all files in the specified directory.
    **Existing files are overwritten**
    
    :param directory:   Directory to process
    """
    file_names = file_helper.list_dir( directory, ".report" )
    
    for file_name in MCMD.iterate( file_names, "Iterating files" ):
        m = re.search( "\(([a-z]+)[0-9]+\)", file_name )
        
        if m is None:
            continue
        
        translate( colour = EResolveColour.BLAST, read = file_name, overwrite = True )
        translate( colour = EResolveColour.COMBINED, read = file_name, overwrite = True )
        translate( colour = EResolveColour.TEXT, read = file_name, overwrite = True )


class ReportGene:
    """
    Genes read from the REPORT file.
    """
    
    
    def __init__( self, gene_name: str, gene_classes: List[str], gene_symbols: List[str], confidence_text: EConfidence, confidence_blast: EBlastConfidence ):
        self.gene_name = gene_name
        self.gene_symbols = gene_symbols
        self.gene_classes = gene_classes
        self.confidence_text = confidence_text
        self.confidence_blast = confidence_blast
    
    
    def get_colour( self, colour: EResolveColour ):
        if colour == EResolveColour.TEXT:
            return COLOURS_TEXT[self.confidence_text]
        elif colour == EResolveColour.BLAST:
            return COLOURS_BLAST[self.confidence_blast]
        elif colour == EResolveColour.COMBINED:
            return COLOURS_COMBINED[self.confidence_text, self.confidence_blast]
        else:
            raise SwitchError( "colour", colour )


class EOrder( Enum ):
    """
    Colour ordering mode.
    
    :data NORMAL:   Colours are written best-first.
                    KEGG uses the first colour for a class, so this means that classes with more than one gene get
                    the colour of the best-matched gene.
    :data REVERSED: Colours are written best-last.
                    KEGG uses the first colour for a class, so this means that classes with more than one gene get
                    the colour of the least-matched gene.
    """
    NORMAL = 1
    REVERSED = 2


@command()
def describe( read: MOptional[Filename[__EXT_REPORT]] = None, write: MOptional[Filename[__EXT_TXT]] = None, overwrite: bool = False ):
    """
    Translates the report to a human-readable file.
    :param overwrite:   Overwrite files without asking
    :param write:       Output diagram file.
                        Accepts `stdout` as a value. 
                        If this is `None`, a file is written next to the read file, or the kegg file if the read file is also `None`.

    :param read:        File to read. If `None` uses the last output by `resolve` (assuming that you wrote to stdout).
    """
    overwrite_all = ByRef[bool]( overwrite )
    table = __open_write_translation( read, write, ".description", overwrite_all )
    
    try:
        reports = __read_report( read )
        
        classes: Dict[str, List[ReportGene]] = defaultdict( list )
        
        for gene in reports:
            for kegg_class_name in gene.gene_classes:
                classes[kegg_class_name].append( gene )
        
        table.write( "{} genes and {} classes".format( len( reports ), len( classes ) ) )
        
        for class_name, gene_list in classes.items():
            table.write( "\n\n" )
            
            table.write( "[{}]".format( class_name ) + "\n" )
            
            for gene in gene_list:  # type: ReportGene
                symbol: str = array_helper.first( gene.gene_symbols )
                table.write( symbol.ljust( 20, " " )
                             + gene.confidence_text.name.ljust( 20 )
                             + gene.confidence_blast.name.ljust( 20 )
                             + "\n" )
    finally:
        table.close()


@command()
def translate( colour: EResolveColour, read: MOptional[Filename[__EXT_REPORT]] = None, write: MOptional[Filename[__EXT_UDM]] = None, order: EOrder = EOrder.NORMAL, overwrite: bool = False ):
    """
    Translates the report to KEGG user data mapping.
    
    :param overwrite:   Overwrite file(s) without asking
    :param order:       Controls colouring of classes (boxes) containing more than one gene.
    :param colour:      How to colour the output.
    :param write:       Output diagram file.
                        Accepts `stdout` as a value. 
                        If this is `None`, a file is written next to the read file, or the kegg file if the read file is also `None`.

    :param read:        File to read. If `None` uses the last output by `resolve` (assuming that you wrote to stdout).
    :param write:       File to write.
    """
    overwrite_all = ByRef[bool]( overwrite )
    diagram = __open_write_translation( read, write, ".udm({})".format( colour.name.lower() ), overwrite_all )
    
    try:
        reports = __read_report( read )
        
        if order == EOrder.NORMAL:
            reports = list( sorted( reports, key = lambda x: x.get_colour( colour )[0] ) )
        elif order == EOrder.REVERSED:
            reports = list( sorted( reports, key = lambda x: -x.get_colour( colour )[0] ) )
        else:
            raise SwitchError( "order", order )
        
        for line in reports:
            colour_ = line.get_colour( colour )
            foreground_colour = colour_[1].html
            background_colour = colour_[2].html
            diagram.write( "{}\t{},{}".format( line.gene_name, background_colour, foreground_colour ) )
            diagram.write( "\n" )
    finally:
        diagram.close()


def __open_write_translation( read, write, extension, overwrite_all ):
    if write is None:
        if read is None:
            if _last_report_file is not None:
                read_file = _last_report_file
            elif _kegg_file is not None and _kegg_file.file_name:
                read_file = _kegg_file.file_name
            else:
                read_file = None
        else:
            read_file = read
        
        if not read_file:
            raise ValueError( "Don't know where to write your output to. No KEGG file, last report file, or explicit output given." )
        
        write = file_helper.replace_extension( read_file, extension )
    
    diagram_file = __open_write( write, "diagram", overwrite_all )
    
    return diagram_file


def __read_report( read ) -> List[ReportGene]:
    root = None
    
    if read is None:
        if _last_report_file is not None:
            read = _last_report_file
        elif _last_report:
            root = ElementTree.fromstring( _last_report )
        else:
            raise ValueError( "There is no last report." )
    
    if root is None:
        tree = ElementTree.parse( read )
        root = tree.getroot()
    
    lines: List[ReportGene] = []
    
    for element in root:
        assert element.tag in ("kegg", "gene")
        
        gene_name = element.attrib["name"]
        gene_classes = element.attrib.get( "classes", "old_version" ).split( "," )
        gene_symbols = element.attrib.get( "symbols", "old_version" ).split( "," )
        
        text_confidence = None
        blast_confidence = None
        
        for sub_element in element:
            if sub_element.tag == "text":
                text_confidence = EConfidence[sub_element.attrib["confidence"]]
            elif sub_element.tag == "blast":
                blast_confidence = EBlastConfidence[sub_element.attrib["confidence"]]
            else:
                raise SwitchError( "element.tag", sub_element.tag )
        
        if text_confidence is None or blast_confidence is None:
            raise ValueError( "Missing confidence for «{}».".format( gene_name ) )
        
        lines.append( ReportGene( gene_name, gene_classes, gene_symbols, text_confidence, blast_confidence ) )
    
    return lines


def __warn_about_used_values( getter, getter_name, affects, warning: ByRef[bool] ):
    """
    Shows a warning if a KEGG name is already in use.
    :param getter:          How to get the name 
    :param getter_name:     For the error message, the name of the name
    :param affects:         For the error message, what this affects
    :return:                Set of repeated names 
    """
    used_uids = set()
    repeated_uids = set()
    
    for kegg_gene in _kegg_file.genes:
        if getter( kegg_gene ) in used_uids:
            repeated_uids.add( getter( kegg_gene ) )
        else:
            used_uids.add( getter( kegg_gene ) )
    
    if repeated_uids and not warning.value:
        warning.value = True
        MCMD.warning( "There is at least one {} (e.g. «{}») that is used by more than one gene. This means that these genes cannot be presented in {}.".format( getter_name, array_helper.first( repeated_uids ), affects ) )
    
    return repeated_uids


def find_blast_confidences( kegg_gene: KeggGene, wrn_mismatch: ByRef[bool] ) -> Dict[LecaCluster, int]:
    """
    Finds the BLAST matches.
    
    :param wrn_mismatch:    Interaction setting 
    :param kegg_gene:       Gene to find 
    :return:                Dictionary of cluster names vs number of matches  
    """
    if _blast_file is None or not _blast_file.contents:
        return { }
    
    clusters = Counter()
    
    blast_lines = _blast_file.lookup_by_kegg.get( kegg_gene.gene_id )
    
    if blast_lines is not None:
        for blast_line in blast_lines:
            leca_gene = blast_line.lookup_leca_gene()
            
            if leca_gene is None:
                if not wrn_mismatch.value:
                    wrn_mismatch.value = True
                    MCMD.warning( "One or more KEGG genes (e.g. «{}») reference a missing LECA gene (e.g. «{}») via BLAST.".format( kegg_gene, blast_line.subject_id ) )
                
                continue
            
            for cluster in leca_gene.clusters:
                clusters[cluster] += 1
    
    return clusters


ALL_CLUSTERS = LecaCluster( "all_clusters" )


def find_confidences( query: ConfidenceQuery, title: str ) -> Dict[LecaCluster, EConfidence]:
    """
    Gets our confidence level that a gene is in the LECA set.
    
    :param title:           Title used for interactive queries 
    :param query:           The query     
    :return:                The confidence level
    """
    results: List[Result] = find_all( query )
    lp_results = ByRef[List[Result]]( results )
    
    if query.by_cluster:
        clusters = set()
        
        for result in results:
            clusters.update( result.leca_gene.clusters )
        
        results_: Dict[LecaCluster, EConfidence] = { }
        
        for cluster in clusters:
            results_[cluster] = __find_confidence_of_subset( query, lp_results, lambda x: cluster in x.leca_gene.clusters, "{} - CLUSTER {}".format( title, cluster ) )
        
        return results_
    else:
        return { ALL_CLUSTERS: __find_confidence_of_subset( query, lp_results, None, "{} - ALL_CLUSTERS".format( title ) ) }


def __find_confidence_of_subset( query: ConfidenceQuery, results: ByRef[List[Result]], filter, title: str, *, remake = False ) -> EConfidence:
    if remake:
        results.value = find_all( query )
    
    if filter:
        subset = [x for x in results.value if filter( x )]
    else:
        subset = results.value
    
    best_result = None
    
    for result in subset:
        if best_result is None or result.confidence.value > best_result.confidence.value:
            best_result = result
    
    if best_result is None:
        return EConfidence.NO_MATCH
    
    best_subset = [x for x in subset if x.confidence == best_result.confidence]
    
    if query.interactive and best_result.confidence.value <= EConfidence.TEXT_CONTAINS.value:
        result = __user_query_confidence_of_subset( best_subset, query, title )
        
        if result is None:
            if query.interactive:
                return __find_confidence_of_subset( query, results, filter, title, remake = True )
            else:
                return best_result.confidence
        else:
            return result
    
    return best_result.confidence


def __user_query_confidence_of_subset( subset: List[Result], query: ConfidenceQuery, title: str ):
    """
    Queries a confidence level with the user.
    :param subset: Matches
    :param query:   Query 
    :return: 
    """
    msg = []
    
    if query.show_kegg:
        for kegg_gene in _kegg_file.genes:
            if any( gene_symbol in query.gene_symbols for gene_symbol in kegg_gene.symbols ):
                msg.append( "********** KEGG **********" )
                msg.append( string_helper.prefix_lines( kegg_gene.full_info, "KEGG: " ) )
    
    for index, result in enumerate( subset ):
        msg.append( "TARGET {}/{} = ".format( index, len( subset ) ) + __get_leca_ansi( result.leca_gene, query ) )
    
    msg_ = []
    msg_set = set()
    
    msg_.append( "***** UNCERTAIN ABOUT THE FOLLOWING MATCH IN «{}», PLEASE PROVIDE DETAILS *****".format( title ) )
    msg_.append( "SEARCH     = " + (Fore.LIGHTBLACK_EX + "|" + Fore.RESET).join( (Fore.YELLOW + gene_symbol + Fore.RESET) for gene_symbol in query.gene_symbols ) )
    
    for line_ in msg:
        for line in line_.split( "\n" ):
            if not any( x.lower() in line.lower() for x in query.gene_symbols ):
                if query.show_leca:
                    msg_.append( Style.DIM + Fore.LIGHTBLACK_EX + "(X)" + line + Style.NORMAL )
            elif line not in msg_set:
                msg_.append( line )
                msg_set.add( line )
            else:
                if query.show_leca:
                    msg_.append( Style.DIM + Fore.LIGHTBLACK_EX + "(^)" + line + Style.NORMAL )
    
    while True:
        answer = MCMD.question( message = "\n".join( msg_ ),
                                options = (_USER_YES,
                                           _USER_DOMAIN,
                                           _USER_NO,
                                           _USER_UNSURE,
                                           _USER_STOP,
                                           _USER_REMOVE,
                                           _USER_REMOVE_ONCE,
                                           _USER_KEGG_SUMMARISE if query.show_kegg else _USER_KEGG_SHOW,
                                           _USER_LECA_SUMMARISE if query.show_leca else _USER_LECA_SHOW,
                                           _USER_HELP) )
        
        if answer == _USER_YES:
            return EConfidence.USER_FOUND
        elif answer == _USER_NO:
            return EConfidence.USER_NOT_FOUND
        elif answer == _USER_DOMAIN:
            return EConfidence.USER_DOMAIN
        elif answer == _USER_UNSURE:
            return EConfidence.USER_AMBIGUOUS
        elif answer == _USER_STOP:
            query.interactive = False
            return None
        elif answer == _USER_HELP:
            MCMD.information( string_helper.highlight_quotes(
                    string_helper.strip_lines( """For this gene:
                                                  ....«yes»            = yes, the gene exists
                                                  ....«domain»         = the domain exists, but not the gene
                                                  ....«no»             = no, the gene doesn't exist
                                                  ....«unsure»         = I'm unsure, mark it as such
                                                  ....«filter»         = I'd like you to remove some specific text from the searches
                                                  
                                                  For all queries in this operation:
                                                  ....«stop_asking»    = Stop asking me these questions and just use the best automated guess*
                                                  ....«remove»         = I'd like you to remove some specific text from the searches
                                                  ....«show.kegg»      = Please provide more/less information about these genes (for KEGG, displays only IDs by default, when on shows everything)
                                                  ....«summarise.kegg» = ^^
                                                  ....«show.leca»      = Please provide more/less information about these genes (for LECA, attempts to summarise by default, when on shows everything)
                                                  ....«summarise.leca» = ^^
                                                  ....«help»           = Show this help message""" ), "«", "»", Fore.YELLOW, Fore.RESET ) )
            continue
        elif answer == _USER_LECA_SHOW or answer == _USER_LECA_SUMMARISE:
            query.show_leca = not query.show_leca
            return __user_query_confidence_of_subset( subset, query, title )
        elif answer == _USER_KEGG_SHOW or answer == _USER_KEGG_SUMMARISE:
            query.show_kegg = not query.show_kegg
            return __user_query_confidence_of_subset( subset, query, title )
        elif answer == _USER_REMOVE or answer == _USER_REMOVE_ONCE:
            r_answer = MCMD.question( message = "Enter exact text to remove",
                                      options = ["*"] )
            
            if r_answer:
                if answer == _USER_REMOVE_ONCE:
                    query = query.copy()
                
                query.remove.append( r_answer )
            
            return None
        else:
            raise SwitchError( "answer", answer )


def find_all( query: ConfidenceQuery ) -> List[Result]:
    """
    Find all matches to the specified gene in the LECA file.
    
    :param query:       Query
    """
    results: List[Result] = []
    
    for gene_symbol in query.gene_symbols:
        gene_symbol = gene_symbol.lower()
        escaped_gene_symbol = re.escape( gene_symbol )
        num_accept = gene_symbol[-1] not in "0123456789"
        escaped_gene_symbol_num = escaped_gene_symbol + "[0-9]+"
        
        #
        # Search over all the clusters
        #
        for leca_cluster in _leca_file.clusters:
            #
            # Search over all the genes in each cluster
            #
            for leca_gene in leca_cluster.genes:
                leca_text = leca_gene.removed_text( query.remove )
                
                if leca_gene.gene_symbol == gene_symbol:
                    # Exact match
                    r = Result( gene_symbol, leca_gene, EConfidence.NAME_EXACT )
                elif num_accept and re.search( escaped_gene_symbol_num, leca_gene.gene_symbol, re.IGNORECASE ):
                    r = Result( gene_symbol, leca_gene, EConfidence.NAME_NUMERIC )
                elif re.search( escaped_gene_symbol, leca_text, re.IGNORECASE ):
                    r = Result( gene_symbol, leca_gene, EConfidence.TEXT_CONTAINS )
                else:
                    r = None
                
                if r is not None:
                    results.append( r )
    
    return results


@command()
def text_search( text: str, regex: bool = False, remove: List[str] = None ):
    """
    Finds text in the loaded file
    
    :param remove:  Don't include this text
    :param text:    Text to find 
    :param regex:   Use regex? 
    """
    
    colour = Fore.GREEN
    normal = Fore.RESET
    
    if not regex:
        text = re.escape( text )
    
    text_regex = re.compile( text, re.IGNORECASE )
    
    for leca_cluster in _leca_file.clusters:
        printed = False
        
        for gene in leca_cluster.genes:
            line = gene.removed_text( remove )
            text_result = text_regex.search( line )
            
            if text_result:
                s = text_result.start( 0 )
                e = text_result.end( 0 )
                
                if not printed:
                    MCMD.print( "\n" + Fore.CYAN + "CLUSTER " + leca_cluster.name + Fore.RESET )
                    printed = True
                
                MCMD.print( line[:s] + colour + line[s:e] + normal + line[e:] )


@command()
def legend( colour: EResolveColour ):
    """
    Prints the legend.
    
    :param colour: Colour to get legend for
    """
    # from intermake import function_inspector
    # documentation = function_inspector.extract_documentation( EConfidence.__doc__, "data" )
    
    if colour == EResolveColour.BLAST:
        mode = COLOURS_BLAST
    elif colour == EResolveColour.TEXT:
        mode = COLOURS_TEXT
    elif colour == EResolveColour.COMBINED:
        mode = COLOURS_COMBINED
    elif colour == EResolveColour.NONE:
        return
    else:
        raise SwitchError( "colour", colour )
    
    for key, value in mode.items():
        if isinstance( key, tuple ):
            key_name = key[0].name + " + " + key[1].name
        else:
            key_name = key.name
        
        _, fore, back = value
        
        MCMD.print( "{}{}{}{}".format( ansi.back( back.r, back.g, back.b ),
                                       ansi.fore( fore.r, fore.g, fore.b ),
                                       string_helper.centre_align( key_name, 40 ),
                                       ansi.RESET ) )


@command()
def gene_search( text: List[str], remove: List[str], silent: bool = False, combine: bool = False ):
    """
    Finds a specific gene in the loaded file
    
    :param text:    Gene name or aliases to find 
    :param silent:  Don't run in interactive mode
    :param remove:  Remove this text from search
    :param combine: Combine clusters (yields one result per gene)
    """
    lecas = set()
    
    ref_interactive = ByRef[bool]( not silent )
    
    query = ConfidenceQuery( gene_symbols = text,
                             ref_interactive = ref_interactive,
                             remove = remove,
                             show_kegg = False,
                             show_leca = False,
                             by_cluster = not combine )
    
    for r in find_all( query ):
        MCMD.print( r )
        lecas.add( r.leca_gene )
    
    for leca in lecas:
        leca_text = __get_leca_ansi( leca, query )
        MCMD.print( leca_text )


def __get_leca_ansi( leca: LecaGene, query: ConfidenceQuery ):
    """
    Formats a LECA gene for the ANSI console.
    :param leca:    The gene 
    :param query:   The query 
    :return:        ANSI text 
    """
    leca_text = leca.removed_text( query.remove )
    leca_text = string_helper.highlight_regex( leca_text, " [a-zA-Z_]+:", "\n" + Fore.RED, Fore.RESET, group = 0 )
    
    for gene_symbol in query.gene_symbols:
        leca_text = string_helper.highlight_regex( leca_text, re.escape( gene_symbol ), Back.YELLOW + Fore.BLUE, Fore.RESET + Back.RESET, group = 0 )
    
    return leca_text


@command()
def cluster_regex( new_regex: Optional[str] = None ):
    """
    View of modifies the cluster regex in the LECA file.
    :param new_regex:   New regex to use. Leave blank to display the current regex.
    """
    if new_regex:
        global _RE_CLUSTER
        _RE_CLUSTER = re.compile( new_regex, re.IGNORECASE )
    
    MCMD.print( _RE_CLUSTER.pattern )


@command()
def garbage( add: Optional[List[str]] = None, remove: Optional[List[str]] = None, clear: bool = False ):
    """
    Adds, removes or views garbage elements.
    :param clear:   Clear all garbage elements
    :param add:     Element(s) to add 
    :param remove:  Element(s) to remove
    :return: 
    """
    if clear:
        _GARBAGE.clear()
    
    if add:
        for x in add:
            _GARBAGE.add( x )
    
    if remove:
        for x in remove:
            _GARBAGE.remove( x )
    
    MCMD.print( ", ".join( _GARBAGE ) )

import hashlib
import re
from enum import Enum
from io import TextIOWrapper
from typing import List, Dict, Optional
from xml.etree import ElementTree

from colorama import Fore, Back, Style
from os import path
from mhelper import ByRef, MOptional

from intermake import MCMD, MENV, command 
import urllib.request

from mhelper import io_helper, string_helper, SwitchError, file_helper, Filename

# KEGG types we recognise.
# - Everything but these gets eliminated to avoid unnecessary lookups and odd errors.
# - If you're working with different data you might want to add your own to this list.
# - hsa = Human gene
# - sce = Yeast gene
# - ko  = Orthology
PERMITTED_KEGG_TYPES = ("hsa", "ko", "sce")

# Regular expressions
RE_GENE_SYMBOL = re.compile( "gene_symbol:([^ ]+)", re.IGNORECASE )
RE_DESC = re.compile( "description:([^[]*)", re.IGNORECASE )
RE_CLUSTER = re.compile( "cluster([0-9]+)untagged", re.IGNORECASE )

leca_file: "LecaFile" = None
kegg_file: "KeggFile" = None

__EXT_TXT = ".txt"
__EXT_FASTA = ".fasta"

class LecaGene:
    """
    Represents a gene in the LECA file.
    """
    
    
    def __init__( self, cluster_name: str, text: str ):
        """
        Constructor
        :param text: Raw text from the LECA file, representing this gene 
        """
        self.cluster_name = cluster_name
        self.text = text.strip().lower()
        
        m = RE_GENE_SYMBOL.search( text )
        
        if m:
            self.gene_symbol = str( m.group( 1 ) ).strip( " ." ).lower()
        else:
            self.gene_symbol = ""
        
        m = RE_DESC.search( text )
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


class LecaFile:
    """
    Reads and parses the LECA file.
    """
    
    
    def __init__( self, file_name: str ):
        self.clusters: Dict[str, List[LecaGene]] = { }
        self.total = 0
        cluster_name = ""
        cluster_list = []
        
        with open( file_name, "r" ) as file:
            with MCMD.action( "Loading" ) as action:
                for line in file:
                    action.increment()
                    line = line.strip()
                    
                    if line:
                        cluster_result = RE_CLUSTER.search( line )
                        
                        if cluster_result:
                            cluster_name = cluster_result.group( 1 )
                            cluster_list = []
                            self.clusters[cluster_name] = cluster_list
                        else:
                            cluster_list.append( LecaGene( cluster_name, line ) )
                            self.total += 1


class KeggGene:
    """
    Represents a gene (or ortholog) in the KEGG file.
    
    :data gene_ids: KEGG ID(s) for this gene
    :data symbols:  KEGG symbols for this gene
    :data aaseq:    Amino acid sequence for this gene
    """
    
    
    def __init__( self, gene_ids: List[str] ):
        """
        CONSTRUCTOR
        See class comments for parameter meanings. 
        """
        self.gene_ids = gene_ids
        self.symbols = set()
        self.aaseq = ""
        self.full_info = ""
        self.uid = None
    
    
    def __str__( self ):
        """
        OVERRIDE 
        """
        return "(KEGG)" + self.uid


class KeggFile:
    """
    Reads and parses the KEGG (KGML) file.
    """
    
    
    def __init__( self, file_name: str ):
        """
        CONSTRUCTOR
        :param file_name:   File to read 
        """
        
        tree = ElementTree.parse( file_name )
        
        root = tree.getroot()
        entries = [x for x in root if x.tag == "entry"]
        self.genes: List[KeggGene] = []
        used_uids = set()
        self.total = 0
        
        cache_folder = MENV.local_data.local_folder( "caches" )
        file_helper.delete_file( path.join( cache_folder, "cached.pickle" ) )  # update old file
        cache_fn = path.join( cache_folder, "cached2.pickle" )
        
        cached = io_helper.load_binary( cache_fn, { } )
        
        for entry in MCMD.iterate( entries, "Resolving names via HTTP" ):
            gene_id_list = entry.attrib["name"]
            gene_ids = [x for x in gene_id_list.split( " " ) if _is_gene_permitted( x )]
            
            if not gene_ids:
                continue
            
            kegg_gene = KeggGene( gene_ids )
            self.genes.append( kegg_gene )
            
            for gene_id in kegg_gene.gene_ids:
                kegg_gene.symbols = set()
                
                link = "http://rest.kegg.jp/get/{}".format( gene_id )
                kegg_gene.full_info = _get_url( cached, link )
                data_array = kegg_gene.full_info.split( "\n" )
                
                for line in data_array:
                    if line.startswith( "NAME" ):
                        for y in [x.strip() for x in line[4:].split( "," ) if x]:
                            if kegg_gene.uid is None:
                                kegg_gene.uid = y
                            
                            kegg_gene.symbols.add( y )
                
                self.total += len( kegg_gene.symbols )
                
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
                
                if not kegg_gene.symbols:
                    MCMD.warning( "Gene «{}» has no symbol".format( kegg_gene ) )
                    
                if not kegg_gene.aaseq:
                    MCMD.warning( "Gene «{}» has no AA-Seq".format( kegg_gene ) )
            
            if kegg_gene.uid is None:
                kegg_gene.uid = "MISSING"
            
            orig_name = kegg_gene.uid
            index = 1
            
            while kegg_gene.uid in used_uids:
                index += 1
                kegg_gene.uid = "{}__{}__".format( orig_name, index )
            
            if index != 1:
                MCMD.warning( "Gene «{}» does not have a unique UID.".format( kegg_gene ) )
            
            used_uids.add( kegg_gene.uid )
        
        io_helper.save_binary( cache_fn, cached )


class EConfidence( Enum ):
    """
    Confidence of the match. See the `readme.md` for details.
    """
    NAME_EXACT = 1
    USER_DOMAIN = 2
    USER_AMBIGUOUS = 3
    USER_FOUND = 4
    USER_NOT_FOUND = 5
    NAME_NUMERIC = 6
    TEXT_EXACT = 9
    ERROR = 11
    NO_MATCH = 12


COLOURS = { EConfidence.NAME_EXACT    : ("#00FF00", "#000000"),     # BLACK  on GREEN
            EConfidence.NAME_NUMERIC  : ("#FFFF00", "#000000"),     # BLACK  on YELLOW
            EConfidence.USER_FOUND    : ("#00FF00", "#FFFF00"),     # YELLOW on GREEN
            EConfidence.USER_NOT_FOUND: ("#FF0000", "#FFFF00"),     # YELLOW on RED
            EConfidence.USER_AMBIGUOUS: ("#0000FF", "#FFFF00"),     # YELLOW on BLUE
            EConfidence.USER_DOMAIN   : ("#00FFFF", "#FFFF00"),     # YELLOW on CYAN
            EConfidence.TEXT_EXACT    : ("#0000FF", "#000000"),     # BLACK  on BLUE
            EConfidence.ERROR         : ("#FFFFFF", "#FF0000"),     # RED    on YELLOW
            EConfidence.NO_MATCH      : ("#FF0000", "#000000") }    # BLACK  on RED
"""Colours of the confidence levels"""


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
    
    
    def __init__( self, *, gene_symbols: List[str], ref_interactive: ByRef[bool], remove: Optional[List[str]], show_leca: bool, show_kegg: bool, by_cluster: bool ):
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


def _is_gene_permitted( lst ):
    """
    Obtains if the KEGG type of the entity is permitted.
    For instance we allow orthologies (ko:xxx) to pass, but not compounds (cpd:xxx) or things we don't understand (blah:xxx).
    """
    if " " in lst:
        lst = lst.split( " ", 1 )[0]
    
    if not ":" in lst:
        return False
    
    type_ = lst.split( ":" )[0]
    
    return type_.lower() in PERMITTED_KEGG_TYPES


def _get_url( cached: Dict[str, str], link: str ):
    """
    Gets the URL, from the cache if available.
    """
    result = cached.get( link )
    
    if result is None:
        result = urllib.request.urlopen( link ).read().decode( "utf-8" )
        cached[link] = result
    
    return result


@command()
def load_leca( file_name: str ):
    """
    Loads the LECA clusters file.
    
    :param file_name:   File to load.
    """
    global leca_file
    leca_file = LecaFile( file_name )
    MCMD.print( "{} clusters and {} genes loaded.".format( len( leca_file.clusters ), leca_file.total ) )


@command()
def load_kegg( file_name: str ):
    """
    Loads the KEGG (KGML) file.
    
    :param file_name:   File to load.
                        Obtain this by selecting `download KGML` from a KEGG pathway. The `Reference Pathway (KO)` is recommended.
    """
    global kegg_file
    kegg_file = KeggFile( file_name )
    MCMD.print( "{} genes and {} names loaded.".format( len( kegg_file.genes ), kegg_file.total ) )


@command()
def resolve( silent: bool = False,
             remove: Optional[List[str]] = None,
             combine: bool = False,
             clusters: MOptional[Filename[__EXT_TXT]] = None,
             fasta: MOptional[Filename[__EXT_FASTA]] = None ):
    """
    Prints the overlap between the loaded KEGG and LECA sets
    
    :param fasta:       Output FASTA file.
                        If set, a FASTA file is written.
                        If not set, no FASTA output is written.
                        
    :param clusters:    Output clusters file.
                        If set, a CLUSTERS file is written.
                        If not set, no CLUSTERS output is written.
                         
    :param silent:      Don't run in interactive mode.
                        If set, no interactive prompts are shown.
                        If not set, interactive prompts are shown for ambiguous results (BLUE).
    
    :param remove:      Remove this text from search.
                        Use this to ignore phrases which confuse gene names (e.g. "CYCLE" being mistaken for "CYC").
                        In interactive mode these can always be added later.
    
    :param combine:     Combine clusters.
                        If set, one result per gene is yielded. This also greatly reduces the number of interactive prompts!
                        If not set, one result per gene and cluster is yielded.
    """
    
    # Get the remove list 
    remove = remove if remove is not None else []
    
    # Keep a record of what we've found
    written_to_color = { }
    written_to_fasta = set()
    
    # Keep track of interactive settings
    ref_interactive = ByRef[bool]( not silent )
    
    cleanup_stack : List[TextIOWrapper] = []
    
    try:
        #
        # Open files
        #
        
        # - FASTA file
        if fasta:
            fasta_file = open( fasta, "w" )
            cleanup_stack.append(fasta_file)
        else:
            fasta_file = None
    
        # - CLUSTERS file
        if clusters:
            cluster_file = open( clusters, "w" )
            cleanup_stack.append(cluster_file)
        else:
            cluster_file = None
        
        #
        # Iterate over genes in pathway
        #
        for index, kegg_gene in MCMD.enumerate( kegg_file.genes, "Exhaustive search" ):
            #
            # Get the confidence level(s) for this gene
            #
            query = ConfidenceQuery( gene_symbols = kegg_gene.symbols,
                                     ref_interactive = ref_interactive,
                                     remove = remove,
                                     show_leca = False,
                                     show_kegg = False,
                                     by_cluster = not combine )
            
            confidences: Dict[str, EConfidence] = find_confidences( query, "GENE {}/{}".format( index, len( kegg_file.genes ) ) )
            
            #
            # Get the best confidence level for this gene
            #
            best_type = EConfidence.NO_MATCH
            
            for confidence in confidences.values():
                if confidence.value < best_type.value:
                    best_type = confidence
            
            #
            # Write the CLUSTER file
            #
            if clusters is not None:
                for cluster_name, confidence in confidences.items():
                    cluster_file.write( kegg_gene.uid + '\t' + confidence.name + '\tcluster' + cluster_name + '\n' )
            
            #
            # For the gene name(s), colour it like the best result
            #
            for kegg_id in kegg_gene.gene_ids:
                if kegg_id in written_to_color and written_to_color[kegg_id][0] != best_type:
                    best_type = EConfidence.ERROR
                
                background_colour = COLOURS[best_type][0]
                foreground_colour = COLOURS[best_type][1]
                written_to_color[kegg_id] = best_type, "{}\t{},{}".format( kegg_id, background_colour, foreground_colour )
                
                if fasta_file is not None:
                    fasta_file.write( ">" + kegg_gene.uid + '\t' + best_type.name + '\n' )
                    fasta_file.write( kegg_gene.aaseq + "\n" )
                
                if kegg_gene.aaseq and kegg_gene.aaseq_hexdigest in written_to_fasta:
                    MCMD.warning( "Gene «{}» (starting «{}») probably already in BLAST output. Unnecessary repeat? ".format( kegg_gene, kegg_gene.aaseq[:10] ) )
                
                written_to_fasta.add( kegg_gene.aaseq_hexdigest )
            
            MCMD.print( "PRINTING OUTPUT DIRECT TO STD.OUT." )
            print( "\n".join( x[1] for x in written_to_color.values() ) )
        
    finally:
        for file in cleanup_stack:
            file.close()


def find_confidences( query: ConfidenceQuery, title: str ) -> Dict[str, EConfidence]:
    """
    Gets our confidence level that a gene is in the LECA set.
    
    :param title:           Title used for interactive queries 
    :param query:           The query     
    :return:                The confidence level
    """
    results: List[Result] = find_all( query )
    lp_results = ByRef[List[Result]]( results )
    
    if query.by_cluster:
        cluster_names = set( x.leca_gene.cluster_name for x in results )
        results_: Dict[str, EConfidence] = { }
        
        for cluster_name in cluster_names:
            results_[cluster_name] = __find_confidence_of_subset( query, lp_results, lambda x: x.leca_gene.cluster_name == cluster_name, "{} - CLUSTER {}".format( title, cluster_name ) )
        
        return results_
    else:
        return { "all_clusters": __find_confidence_of_subset( query, lp_results, None, "{} - ALL_CLUSTERS".format( title ) ) }


def __find_confidence_of_subset( query: ConfidenceQuery, results: ByRef[List[Result]], filter, title: str, remake = False ) -> EConfidence:
    if remake:
        results.value = find_all( query )
    
    if filter:
        subset = [x for x in results.value if filter( x )]
    else:
        subset = results.value
    
    best_result = None
    
    for result in subset:
        if best_result is None or result.confidence.value < best_result.confidence.value:
            best_result = result
    
    if best_result is None:
        return EConfidence.NO_MATCH
    
    best_subset = [x for x in subset if x.confidence == best_result.confidence]
    
    if query.interactive and best_result.confidence.value >= EConfidence.TEXT_EXACT.value:
        result = __user_query_confidence_of_subset( best_subset, query, title )
        
        if result is None:
            if query.interactive:
                __find_confidence_of_subset( query, results, filter, title, True )
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
        for kegg_gene in kegg_file.genes:
            if any( gene_symbol in kegg_gene.gene_ids for gene_symbol in query.gene_symbols ):
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
        answer = MCMD.question( "\n".join( msg_ ), ("yes", "domain", "no", "unsure", "stop_asking", "remove", "filter", "less.info", "summarise.kegg" if query.show_kegg else "show.kegg", "summarise.leca" if query.show_leca else "show.leca", "full.info", "help") )
        
        if answer == "yes":
            return EConfidence.USER_FOUND
        elif answer == "no":
            return EConfidence.USER_NOT_FOUND
        elif answer == "domain":
            return EConfidence.USER_DOMAIN
        elif answer == "unsure":
            return EConfidence.USER_AMBIGUOUS
        elif answer == "stop_asking":
            query.interactive = False
            return None
        elif answer == "help":
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
        elif answer == "show.leca":
            query.show_leca = not query.show_leca
            return __user_query_confidence_of_subset( subset, query, title )
        elif answer == "show.leca":
            query.show_kegg = not query.show_kegg
            return __user_query_confidence_of_subset( subset, query, title )
        elif answer == "remove" or answer == "remove.always":
            r_answer = MCMD.question( "Enter exact text to remove", ["*"] )
            
            if r_answer:
                if answer != "remove.always":
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
        for cluster_name, leca_genes in leca_file.clusters.items():
            #
            # Search over all the genes in each cluster
            #
            for leca_gene in leca_genes:
                leca_text = leca_gene.removed_text( query.remove )
                
                if leca_gene.gene_symbol == gene_symbol:
                    # Exact match
                    r = Result( gene_symbol, leca_gene, EConfidence.NAME_EXACT )
                elif num_accept and re.search( escaped_gene_symbol_num, leca_gene.gene_symbol, re.IGNORECASE ):
                    r = Result( gene_symbol, leca_gene, EConfidence.NAME_NUMERIC )
                elif re.search( escaped_gene_symbol, leca_text, re.IGNORECASE ):
                    r = Result( gene_symbol, leca_gene, EConfidence.TEXT_EXACT )
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
    
    for cluster_name, cluster_list in leca_file.clusters.items():
        printed = False
        
        for gene in cluster_list:
            line = gene.removed_text( remove )
            text_result = text_regex.search( line )
            
            if text_result:
                s = text_result.start( 0 )
                e = text_result.end( 0 )
                
                if not printed:
                    MCMD.print( "\n" + Fore.CYAN + "CLUSTER " + cluster_name + Fore.RESET )
                    printed = True
                
                MCMD.print( line[:s] + colour + line[s:e] + normal + line[e:] )


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

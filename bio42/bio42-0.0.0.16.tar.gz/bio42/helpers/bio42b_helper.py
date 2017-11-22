"""
Helper functions for common database actions.
"""
from mhelper import string_helper



def go_id_to_uid( go_id ) -> str:
    """
    Abbreviates a GO ID to save database space.
    """
    _GO_ID_PREFIX = "GO:"
    result = string_helper.remove_prefix( go_id, _GO_ID_PREFIX )
    assert len( result ) == 7 and all( x.isdigit() for x in result ), result
    return result


def kegg_id_to_uid( kegg_id ):
    """
    Abbreviates a KEGG ID to save database space.
    """
    return kegg_id


def pfam_id_to_uid( pfam_id: str ) -> str:
    """
    Abbreviates a PFAM ID to save database space.
    """
    return string_helper.remove_prefix( pfam_id, "PF" )


def ipr_id_to_uid( ipr_id: str ) -> str:
    """
    Abbreviates a InterproScan ID to save database space.
    """
    return string_helper.remove_prefix( ipr_id, "IPR" )




"""
Utility functions
"""

from box import Box, BoxList

def make_box(data):
    """Create Box instance from dict."""
    return Box(data, camel_killer_box=True)

def make_box_list(data):
    """Create BoxList instance from dict."""
    return BoxList(data, camel_killer_box=True)

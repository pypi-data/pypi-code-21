
from procgraph import register_simple_block
from procgraph_images.copied_from_reprep import skim_top_and_bottom


def skim(a, percent=5):

    return skim_top_and_bottom(a, percent)

register_simple_block(skim, doc=skim_top_and_bottom.__doc__)

#doc='Skims the top and bottom percentile from the data.')

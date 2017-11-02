from .reflow_paragraph import reflow_paragraph
from .tools import space_fill

def reflow_footnote(text, space):
    output = []
    leading_space = text.replace(text.lstrip(), '')
    ref = text.lstrip().split(']')[0]
    rest_of_text = text.lstrip()[len(ref)::]
    
    lspace = leading_space + space_fill(len(ref), ' ') + '  '
    paragraph = reflow_paragraph(rest_of_text, space, lspace)
    
    return leading_space + ref + paragraph.lstrip()

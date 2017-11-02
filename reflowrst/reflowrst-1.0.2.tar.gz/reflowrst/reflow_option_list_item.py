from .reflow_paragraph import reflow_paragraph
from .tools import space_fill

def reflow_option_list_item(text, space):

    leading_space = text.replace(text.lstrip(), '')
    option = text.lstrip().split('  ')[0]
    rest_of_text = text.lstrip()[len(option)::]
    interspace = rest_of_text.replace(rest_of_text.lstrip(), '')
    
    lspace = leading_space + space_fill(len(option), ' ') + interspace
    
    paragraph = reflow_paragraph(rest_of_text.lstrip(), space, lspace)
    paragraph = paragraph.lstrip()
    
    return leading_space + option + interspace + paragraph

from .reflow_paragraph import reflow_paragraph
from .tools import space_fill

def reflow_option_list_item(text, space):
    
    leading_space = text.replace(text.lstrip(), '')
    option = text.lstrip().split('  ')[0]
    rest_of_text = text.lstrip()[len(option)::]
    interspace = rest_of_text.replace(rest_of_text.lstrip(), '')
    
    lspace = leading_space + space_fill(len(option), ' ') + interspace
    
    blocks = rest_of_text.split('\n')
    for b in range(len(blocks)):
        blocks[b] = reflow_paragraph(blocks[b].lstrip(), space, lspace).lstrip()
    
    
    for b in range(len(blocks)):
        if b == 0:
            blocks[b] = leading_space + option + interspace + blocks[b]
        else:
            blocks[b] = lspace + blocks[b]
    
    return '\n'.join(blocks)

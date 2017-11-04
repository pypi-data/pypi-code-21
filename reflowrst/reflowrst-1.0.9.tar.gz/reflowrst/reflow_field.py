from .tools.space_fill import space_fill
from .reflow_paragraph import reflow_paragraph

def reflow_field(text, space):
    output = []
    
    leading_space = text.replace(text.lstrip(), '')
    
    field_name = ''
    words = text.strip().split(' ')
    for x in range(len(words)):
        if words[x].endswith(':') and not words[x].endswith('\\:'):
            field_name = ' '.join(words[0:x + 1])
            break
    
    rest_of_text = text[len(leading_space + field_name)::]

    interspace = rest_of_text.replace(rest_of_text.lstrip(), '')
    rest_of_text = rest_of_text.lstrip()
    
    lspace = leading_space + space_fill(len(field_name), ' ') + interspace
    
    paragraph = reflow_paragraph(rest_of_text, space, lspace)
    paragraph = paragraph.lstrip()
    
    lines = paragraph.split('\n')
    output.append(leading_space + field_name + interspace + lines[0])
    output.extend(lines[1::])

    return '\n'.join(output)

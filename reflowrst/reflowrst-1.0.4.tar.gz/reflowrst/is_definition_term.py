def is_definition_term(lines, index):
    '''Verify if the line is a definition term'''
    if index == len(lines) - 1:
        return False
        
    leading_space = lines[index].replace(lines[index].lstrip(), '')
    if lines[index + 1].startswith(leading_space + '    '):
        return True
    

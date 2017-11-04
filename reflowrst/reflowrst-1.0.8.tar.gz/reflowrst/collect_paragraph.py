def collect_paragraph(lines, index):
    output = [lines[index]]
    leading_space = lines[index].replace(lines[index].lstrip(), '')
    index += 1
    
    while index < len(lines):
        if lines[index].startswith(leading_space) and not lines[index] == '':
            output.append(lines[index].strip())
            index += 1
        else:
            return ' '.join(output), index
    return ' '.join(output), index

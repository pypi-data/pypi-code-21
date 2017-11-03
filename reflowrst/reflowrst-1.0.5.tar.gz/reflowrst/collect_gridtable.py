def collect_gridtable(lines, index):
    output = []
    while (index < len(lines) and 
            (lines[index].lstrip().startswith('+') or 
             lines[index].lstrip().startswith('|'))
          ):
        output.append(lines[index])
        index += 1
    return '\n'.join(output), index

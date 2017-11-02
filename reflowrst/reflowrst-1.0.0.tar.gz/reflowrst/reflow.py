from .tools import get_enumerator_level
from .tools import get_enumerator_type
from .tools import make_enumerator
from .tools import space_fill

from dashtable import grid2data
from dashtable import data2rst

from .is_main_title import is_main_title
from .is_title import is_title
from .is_bullet_list_item import is_bullet_list_item
from .is_enumerated_list_item import is_enumerated_list_item
from .is_todo_list_item import is_todo_list_item
from .is_definition_term import is_definition_term
from .is_field import is_field
from .is_option_list_item import is_option_list_item
from .is_footnote import is_footnote
from .is_gridtable import is_gridtable

from .collect_main_title import collect_main_title
from .collect_title import collect_title
from .collect_bullet_list_item import collect_bullet_list_item
from .collect_enumerated_list_item import collect_enumerated_list_item
from .collect_todo_list_item import collect_todo_list_item
from .collect_field import collect_field
from .collect_option_list_item import collect_option_list_item
from .collect_footnote import collect_footnote
from .collect_gridtable import collect_gridtable
from .collect_paragraph import collect_paragraph

from .reflow_bullet_list_item import reflow_bullet_list_item
from .reflow_enumerated_list_item import reflow_enumerated_list_item
from .reflow_todo_list_item import reflow_todo_list_item
from .reflow_field import reflow_field
from .reflow_option_list_item import reflow_option_list_item
from .reflow_footnote import reflow_footnote
from .reflow_paragraph import reflow_paragraph

import itertools
import copy

def renumerate_enumerators(lines):
    last_enumerator_level = 0
    for i in range(len(lines)):
        if is_enumerated_list_item(lines, i):
            leading_space = lines[i].replace(lines[i].lstrip(), '')
            enumerator = lines[i].lstrip().split(' ')[0]
            enumerator_type = get_enumerator_type(enumerator)
            initial = len(leading_space) + len(enumerator)
            rest_of_text = lines[i][initial::]
            
            if i > 0 and is_enumerated_list_item(lines, i - 1):
                last_enumerator_level += 1
                enumerator_level = last_enumerator_level
                enumerator = make_enumerator(enumerator_type, enumerator_level)
            else:
                enumerator_level = get_enumerator_level(
                    enumerator, enumerator_type)
                last_enumerator_level = enumerator_level
            
            lines[i] = leading_space + enumerator + rest_of_text
    return lines

def reflow(text, space=0):
    '''Reflow the text to fit within "space" number of characters'''
    lines = text.split('\n')
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip()
    lines = renumerate_enumerators(lines)
        
    reflowed = []
    
    index = 0
    while index < len(lines):
        if lines[index] == '':
            reflowed.append('')
            index += 1
        elif is_main_title(lines, index):
            flat, index = collect_main_title(lines, index)
            reflowed.append(flat)
        elif is_title(lines, index):
            flat, index = collect_title(lines, index)
            reflowed.append(title)
        elif is_gridtable(lines, index):
            text, index = collect_gridtable(lines, index)
            leading_space = text.replace(text.lstrip(), '')
            table, spans, use_headers = grid2data(text)
            
            cell_widths = get_cell_widths(table, spans, space - len(leading_space))
            for row in range(len(table)):
                for column in range(len(table[row])):
                    table[row][column] = reflow(table[row][column], cell_widths[row][column]).rstrip()
            gridtable = data2rst(table, spans, use_headers, center_headers=True)
            grid_lines = gridtable.split('\n')
            for i in range(len(grid_lines)):
                grid_lines[i] = leading_space + grid_lines[i]
            reflowed.append('\n'.join(grid_lines))
            
        elif is_bullet_list_item(lines, index):
            flat, index = collect_bullet_list_item(lines, index)
            if space:
                reflowed.append(reflow_bullet_list_item(flat, space))
            else:
                reflowed.append(flat)
        elif is_enumerated_list_item(lines, index):
            max_ewidth = 0
            for x in range(index, len(lines)):
                if (
                    is_enumerated_list_item(lines, x) or
                    is_bullet_list_item(lines, x) or
                    is_todo_list_item(lines, x)
                ):
                    if is_enumerated_list_item(lines, x):
                        enumerator = lines[x].lstrip().split(' ')[0]
                        if len(enumerator) > max_ewidth:
                            max_ewidth = len(enumerator)
                else:
                    break
            flat, index = collect_enumerated_list_item(
                lines, index, max_ewidth)
            if space:
                reflowed.append(reflow_enumerated_list_item(flat, space))
            else:
                reflowed.append(flat)
        elif is_todo_list_item(lines, index):
            flat, index = collect_todo_list_item(lines, index)
            if space:
                reflowed.append(reflow_todo_list_item(flat, space))
            else:
                reflowed.append(flat)
        elif is_definition_term(lines, index):
            flat = lines[index]
            reflowed.append(flat)
            index += 1
        
        elif is_field(lines, index):
            field_names = []
            for i in reversed(range(0, len(reflowed))):
                if is_field(reflowed, i):
                    words = reflowed[i].strip().split(' ')
                    for x in range(len(words)):
                        if words[x].endswith(':') and not words[x].endswith('\\:'):
                            field_name = ' '.join(words[0:x + 1])
                            field_names.append(field_name)
                            break
                else:
                    break
            current_field_name = ''
            for i in range(index, len(lines)):
                if is_field(lines, index):
                    words = lines[i].strip().split(' ')
                    for x in range(len(words)):
                        if words[x].endswith(':') and not words[x].endswith('\\:'):
                            field_name = ' '.join(words[0:x + 1])
                            field_names.append(field_name)
                            if i == index:
                                current_field_name = field_name
                            break
                else:
                    break
            max_field_name_length = len(max(field_names, key=len))
            remainder = max_field_name_length - len(current_field_name)
            interspace = space_fill(remainder, ' ') + ' '
            
            flat, index = collect_field(lines, index, interspace)
            if space:
                reflowed.append(reflow_field(flat, space))
            else:
                reflowed.append(flat)
        
        elif is_option_list_item(lines, index):
            options = []
            for i in reversed(range(0, len(reflowed))):
                if is_option_list_item(reflowed, i):
                    options.append(reflowed[i].lstrip().split('  ')[0])
                else:
                    break
            
            current_option = ''
            for i in range(index, len(lines)):
                if is_option_list_item(lines, i):
                    if i == index:
                        options.append(lines[i].lstrip().split(' ')[0])
                        current_option = lines[i].lstrip().split(' ')[0]
            
            max_option_width = len(max(options, key=len))
            remainder = max_option_width - len(current_option)
            interspace = space_fill(remainder, ' ') + '  '
            flat, index = collect_option_list_item(lines, index, interspace)
            if space:
                reflowed.append(reflow_option_list_item(flat, space))
            else:
                reflowed.append(flat)
        
        elif is_footnote(lines, index):
            flat, index = collect_footnote(lines, index)
            if space:
                reflowed.append(reflow_footnote(flat, space))
            else:
                reflowed.append(flat)
        
        else:
            leading_space = lines[index].replace(lines[index].lstrip(), '')
            flat, index = collect_paragraph(lines, index)
            if space:
                reflowed.append(reflow_paragraph(flat, space, leading_space))
            else:
                reflowed.append(flat)
    
    return '\n'.join(reflowed)

def getSpanColumnCount(span):
    """Gets the number of columns inluded in a span"""
    columns = 1
    first_column = span[0][1]
    for i in range(len(span)):
        if span[i][1] > first_column:
            columns += 1
            first_column = span[i][1]
    return columns

def getSpanRowCount(span):
    """Gets the number of rows included in a span"""
    rows = 1
    first_row = span[0][0]
    for i in range(len(span)):
        if span[i][0] > first_row:
            rows += 1
            first_row = span[i][0]
    return rows
    
def grid_height_from_cols(table, spans, combo):
    '''Calculate the sum of the cell text heights given column widths'''
    row_heights = []
    for row in table:
        row_heights.append(1)
    
    for row in range(len(table)):
        for column in range(len(table[row])):
            text = table[row][column]
            space = combo[column]
            for span in spans:
                if [row, column] in span:
                    span_row_count = getSpanRowCount(span)
                    if not span_row_count > 1:
                        span_col_count = getSpanColumnCount(span)
                        span_row_count = getSpanRowCount(span)
                        r = span[0][0]
                        c = span[0][1]
                        if span_col_count > 1 and span_row_count == 1 and row == r:
                            text = table[r][c]
                            space = sum(combo[c: c + span_col_count + 1]) + (span_col_count - 1)
                    break
            reflowed = reflow(text, space)
            height = len(reflowed.split('\n'))
            if row_heights[row] < height:
                row_heights[row] = height
    
    for row in range(len(table)):
        for column in range(len(table[row])):
            for span in spans:
                if [row, column] in span:
                    span_row_count = getSpanRowCount(span)
                    if span_row_count > 1:
                        span_col_count = getSpanColumnCount(span)
                        r = span[0][0]
                        c = span[0][1]
                        if span_col_count > 1 and row == r:
                            text = table[r][c]
                            space = sum(combo[c: c + span_col_count + 1]) + (span_col_count - 1)
                    reflowed = reflow(text, space)
                    height = len(reflowed.split('\n'))
                    height = height - (span_col_count - 1)
                    add_row = 0
                    while height > sum(row_heights[r:r + span_row_count]):
                        row_heights[r + add_row] += 1
                        if add_row + 1 < len(row_heights):
                            add_row += 1
                        else:
                            add_row = 0
    return sum(row_heights)
    

def get_column_combo(height, col_height_width_dicts):
    '''Get the column widths as they would be if set at height'''
    combo = []
    for col in col_height_width_dicts:
        keys = list(sorted(col.keys()))
        for key in keys:
            if height >= key:
                addition = col[key]
        if type(addition).__name__ == 'int':
            combo.append(addition)
        elif type(addition).__name__ == 'tuple':
            combo.extend(addition)
    return combo

def reevaluate_max_col_widths(
    max_col_widths, min_col_widths, space):
    '''
    A column's max width must not be more than 
    allowed space - sum(all other min_col_widths)
    '''
    column_count = len(max_col_widths)
    text_space = space - (column_count + 1) - (2 * column_count)
    for i in range(len(max_col_widths)):
        min_sum = sum(min_col_widths[0:i]) + sum(min_col_widths[i + 1::])
        if max_col_widths[i] + min_sum > text_space:
            
            if text_space - min_sum >= min_col_widths[i]:
                max_col_widths[i] = text_space - min_sum
            else:
                max_col_widths[i] = min_col_widths[i]
    return max_col_widths

def get_breakpoints(text, min_width, max_width):
    '''
    Find where newlines could be added to a string
    but don't bother if the result would be longer than max width
    or shorter than min width
    '''
    breakpoints = []
    text = text.replace('\n', ' ')
    words = text.split(' ')
    growing_string = ''
    for word in words:
        growing_string += word + ' '
        if len(growing_string.rstrip()) >= min_width and len(growing_string.rstrip()) <= max_width:
            breakpoints.append(len(growing_string.rstrip()))
    return breakpoints

def make_cell_width_dict(
    table, row, column, spans, max_col_widths, min_col_widths):
    '''Create a dictionary of cell heights at specific widths'''
    cell_width_dict = {}
    text = table[row][column]
    
    for span in spans:
        if [row, column] in span:
            r = span[0][0]
            c = span[0][1]
            text = table[r][c]
    
    breakpoints = get_breakpoints(
        table[row][column], min_col_widths[column], max_col_widths[column])
    
    for bp in breakpoints:
        reflowed = reflow(text, bp)
        rlines = reflowed.split('\n')
        cell_width_dict[bp] = len(rlines)
    
    if len(breakpoints) == 0:
        cell_width_dict[min_col_widths[column]] = 1
    
    return cell_width_dict

def get_key_column_widths(
    table, spans, max_col_widths, min_col_widths):
    '''
    Discover which widths are significant to a column's reflowed height
    '''
    cell_width_dicts = []
    for row in range(len(table)):
        cell_width_dicts.append([])
        for column in range(len(table[row])):
            cell_width_dicts[-1].append(
                make_cell_width_dict(
                    table, row, column, spans, max_col_widths, min_col_widths))
    
    key_column_widths = []
    for column in max_col_widths:
        key_column_widths.append([])
    
    for row in range(len(cell_width_dicts)):
        for column in range(len(cell_width_dicts[row])):
            key_column_widths[column].extend(list(cell_width_dicts[row][column].keys()))
    
    for col in range(len(key_column_widths)):
        key_column_widths[col] = list(set(key_column_widths[col]))
    
    return cell_width_dicts, key_column_widths

def has_column_span(table, column, spans):
    '''
    Determine if a column has any rows containing a column-spanned cell
    If so, return the row containing the furthest longest column span
    '''
    rows = {}
    for row in range(len(table)):
        for span in spans:
            if [row, column] in span:
                span_col_count = getSpanColumnCount(span)
                if span_col_count > 1:
                    rows[span_col_count] = row
    if rows == {}:
        return None
    else:
        keys = list(rows.keys())
        return rows[max(keys)]
    
    return None

def make_column_height_width_dict(column, cell_width_dicts):
    '''
    For a non-column-spanned column, determine it's height at breakpoint
    widths and make a dictionary of the heights:widths
    '''
    breakpoints = []
    for row in range(len(cell_width_dicts)):
        for col in range(len(cell_width_dicts[row])):
            if col == column:
                breakpoints.extend(list(cell_width_dicts[row][col].keys()))
    breakpoints = list(set(breakpoints))
    height_widths = {}
    for bp in breakpoints:
        column_height = 0
        for row in range(len(cell_width_dicts)):
            for col in range(len(cell_width_dicts[row])):
                if column == col:
                    keys = list(sorted(cell_width_dicts[row][column].keys(), reverse=True))
                    added = False
                    for i in range(len(keys)):
                        if bp >= keys[i] and added == False:
                            column_height += cell_width_dicts[row][column][keys[i]]
                            added = True
                    if added == False:
                        column_height += cell_width_dicts[row][column][keys[-1]] + 1
        try:
            if bp < height_widths[column_height]:
                height_widths[column_height] = bp
        except KeyError:
            height_widths[column_height] = bp
    return height_widths
    
def get_last_column(table, column, furthest, spans):
    '''
    This is useful for when a grid has multiple column spans that
    overlap eachother. We need the group of columns that share
    overlapping column spans.
    '''
    for row in range(len(table)):
        for col in range(len(table[row])):
            if col >= column and col <= furthest:
                long_row = has_column_span(table, column, spans)
                if long_row and long_row > furthest:
                    furthest = get_last_column(table, col, long_row, spans)
    return furthest
    
def in_spans(row, column, spans):
    for span in spans:
        if [row, column] in span:
            return True
    return False
    
def make_spanned_column_height_width_dict(
    table, min_column_widths, column, long_row, spans, max_column_widths, 
    cell_width_dicts, text_space):
    '''
    For a group of columns united by column spans, go through all
    possible combinations of widths to arrive at the few that would give
    the best possible height for those widths.
    
    If you have a grid with lots of column spans, this function is the
    reason why the script is running slow.
    '''
    for span in spans:
        if [long_row, column] in span:
            span_col_count = getSpanColumnCount(span)
            furthest = span[0][1] + span_col_count - 1
    last_column = get_last_column(table, column, furthest, spans)
    
    included_columns = list(range(column, last_column + 1))
    
    key_column_widths = []
    for column in max_column_widths:
        key_column_widths.append([])
    
    for row in range(len(cell_width_dicts)):
        for col in range(len(cell_width_dicts[row])):
            if col in included_columns:
                if not in_spans(row, col, spans):
                    key_column_widths[col].extend(list(cell_width_dicts[row][col].keys()))
    
    col = 0
    while col < len(key_column_widths):
        if key_column_widths[col] == []:
            key_column_widths.pop(col)
        else:
            key_column_widths[col] = list(set(key_column_widths[col]))
            col += 1
    
    combos = list(itertools.product(*key_column_widths))
        
    i = 0
    while i < len(combos):
        if sum(combos[i]) >= text_space:
            combos.pop(i)
        else:
            i += 1
    
    adjusted_table = []
    adjusted_spans = []
    for row in range(len(table)):
        adjusted_table.append([])
        for col in range(len(table[row])):
            if col in included_columns:
                adjusted_table[-1].append(table[row][col])
            for span in spans:
                if [row, col] in span:
                    if not span in adjusted_spans:
                        new_span = copy.deepcopy(span)
                        adjusted_spans.append(new_span)
    
    for i in range(len(adjusted_spans)):
        for p in range(len(adjusted_spans[i])):
            adjusted_spans[i][p][1] -= 1
    
    adjusted_min_column_widths = []
    for col in range(len(min_column_widths)):
        if col in included_columns:
            adjusted_min_column_widths.append(min_column_widths[col])
    
    smallest_height = grid_height_from_cols(adjusted_table, adjusted_spans, adjusted_min_column_widths)
    height_width_dict = {}
    
    for i in range(len(combos)):
        height = grid_height_from_cols(adjusted_table, adjusted_spans, combos[i])
        try:
            if sum(combos[i]) < sum(height_width_dict[height]):
                height_width_dict[height] = combos[i]
        except KeyError:
            height_width_dict[height] = combos[i]
    
    return height_width_dict, column + span_col_count

def make_final_cell_widths(table, spans, column_widths):
    '''
    Determine the final width of each cell. This should be the same
    as the column widths for normal cells, but will be different for
    column-spanded cells
    '''
    cell_widths = []
    for row in range(len(table)):
        cell_widths.append([])
        for column in range(len(table[row])):
            cell_widths[-1].append(column_widths[column])
    
    for row in range(len(table)):
        for column in range(len(table[row])):
            width = column_widths[column]
            for span in spans:
                if [row, column] in span:
                    span_col_count = getSpanColumnCount(span)
                    if span_col_count > 1:
                        r = span[0][0]
                        c = span[0][1]
                        width = sum(column_widths[c: c + span_col_count + 1]) + (span_col_count - 1)
            cell_widths[row][column] = width
    return cell_widths

def get_combo_widths(combo, col_height_width_dicts):
    cols = []
    for c in range(len(combo)):
        if type(col_height_width_dicts[c][combo[c]]).__name__ == 'int':
            cols.append(col_height_width_dicts[c][combo[c]])
        else:
            cols.extend(col_height_width_dicts[c][combo[c]])
    return cols

def get_cell_widths(table, spans, space):
    '''Get the new cell widths for the reflowed grid table'''
    
    min_cell_widths = []
    max_cell_widths = []
    for row in range(len(table)):
        min_cell_widths.append([])
        max_cell_widths.append([])
        for column in range(len(table[row])):
            span_col_count = 1
            for span in spans:
                if [row, column] in span:
                    span_col_count = getSpanColumnCount(span)
            if span_col_count == 1:
                min_text = reflow(table[row][column], 1)
                max_text = reflow(table[row][column], 0)

                min_lines = min_text.split('\n')
                min_cell_widths[row].append(len(max(min_lines, key=len)))
                
                max_lines = max_text.split('\n')
                max_cell_widths[row].append(len(max(max_lines, key=len)))
            else:
                min_cell_widths[row].append(0)
                max_cell_widths[row].append(space)
    
    for row in range(len(table)):
        for column in range(len(table[row])):
            for span in spans:
                if [row, column] in span:
                    span_col_count = getSpanColumnCount(span)
                    r = span[0][0]
                    c = span[0][1]
                    if span_col_count > 1 and row == r and column == c:
                        text = table[r][c]
                        reflowed = reflow(text, 1)
                        min_lines = reflowed.split('\n')
                        min_text_length = len(max(min_lines, key=len))
                        add_col = 0
                        while sum(min_cell_widths[row][c:c + span_col_count]) < min_text_length:
                            min_cell_widths[row][c + add_col] += 1
                            if add_col + 1 < span_col_count:
                                add_col += 1
                            else:
                                add_col = 0
                        reflowed = reflow(text, 0)
                        max_lines = reflowed.split('\n')
                        max_text_length = len(max(max_lines, key=len))
                        add_col = 0
                        while sum(max_cell_widths[row][c:c + span_col_count]) < max_text_length:
                            max_cell_widths[row][c + add_col] += 1
                            if add_col + 1 < span_col_count:
                                add_col += 1
                            else:
                                add_col = 0
    
    max_col_widths = []
    min_col_widths = []

    for column in range(len(table[0])):
        max_col_widths.append(0)
        min_col_widths.append(0)
    for row in range(len(table)):
        for column in range(len(table[row])):
            if min_cell_widths[row][column] > min_col_widths[column]:
                min_col_widths[column] = min_cell_widths[row][column]
            if max_cell_widths[row][column] > max_col_widths[column]:
                max_col_widths[column] = max_cell_widths[row][column]

    column_count = len(table[0])
    text_space = space - (column_count + 1) - (2 * column_count)
    
    if sum(max_col_widths) <= text_space or space == 0:
        new_column_widths = max_col_widths
        
    elif sum(min_col_widths) > text_space:
        new_column_widths = min_col_widths

    else:
        max_col_widths = reevaluate_max_col_widths(
            max_col_widths, min_col_widths, space)
        cell_width_dicts, key_column_widths = get_key_column_widths(
            table, spans, max_col_widths, min_col_widths)
        
        col_height_width_dicts = []
        column = 0
        while column < column_count:
            long_row = has_column_span(table, column, spans)
            if not long_row:
                col_height_width_dicts.append(
                    make_column_height_width_dict(column, cell_width_dicts))
                column += 1
            else:
                height_width_dict, column = make_spanned_column_height_width_dict(
                    table, min_col_widths, column, long_row, spans, 
                    max_col_widths, cell_width_dicts, text_space)
                col_height_width_dicts.append(height_width_dict)
        
        col_heights = []
        for col in col_height_width_dicts:
            col_heights.append(list(col.keys()))
        
        combos = list(itertools.product(*col_heights))
        
        i = 0
        while i < len(combos):
            if sum(get_combo_widths(combos[i], col_height_width_dicts)) > text_space:
                combos.pop(i)
            else:
                i += 1
        
        smallest_height = grid_height_from_cols(table, spans, min_col_widths)
        min_widths = min_col_widths
        
        for i in range(len(combos)):
            height = grid_height_from_cols(table, spans, get_combo_widths(combos[i], col_height_width_dicts))
            if height < smallest_height:
                smallest_height = height
                min_widths = get_combo_widths(combos[i], col_height_width_dicts)
        new_column_widths = min_widths

    cell_widths = make_final_cell_widths(table, spans, new_column_widths)
    return cell_widths

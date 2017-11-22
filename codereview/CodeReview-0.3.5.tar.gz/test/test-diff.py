####################################################################################################

from CodeReview.Diff.RawTextDocument import RawTextDocument
from CodeReview.Diff.RawTextDocumentDiff import TwoWayFileDiffFactory, TwoWayLineChunkEqual
from CodeReview.TextDistance import levenshtein_distance

####################################################################################################

text1 = """
def pairwise(iterable):

    prev = iterable[0]
    for x in iterable[1:]:
        yield prev, x
        prev = x

def html_highlight_backtrace(backtrace_text):

    lines = [x for x in backtrace_text.split('\n') if x]

    backtrace_highlighted = '<h3>' + lines[0] + '</h3>'

    for line in lines[1:-1]:
        line = line.replace('<', '(')
        line = line.replace('>', ')')
        if 'File' in line:
            line = '<font color="blue"><h6>' + line + '</h6>'
        else:
            line = '<font color="black"><code>' + line + '</code>'
        backtrace_highlighted += line

    backtrace_highlighted += '<font color="blue"><h4>' + lines[-1] + '</h4>'

    return backtrace_highlighted

def iter_with_last_flag(iterable):

    last_index = len(iterable) -1
    for i, x in enumerate(iterable):
        yield x, i == last_index
"""

text2 = """
def iter_with_last_flag(iterable):

    last_index = len(iterable) -1
    for i, x in enumerate(iterable):
        yield x, i == last_index

def html_highlight_backtrace(backtrace_text):

    lines = [x for x in backtrace_text.split('\n') if x]

    backtrace_highlighted = '<h3>' + lines[0] + '</h3>'

    for line in lines[1:-1]:
        line = line.replace('<', '(')
        line = line.replace('>', ')')
        if 'File' in line:
            line = '<font color="blue"><h6>' + line + '</h6>'
        else:
            line = '<font color="black"><code>' + line + '</code>'
        backtrace_highlighted += line

    backtrace_highlighted += '<font color="blue"><h4>' + lines[-1] + '</h4>'

    return backtrace_highlighted

def pairwise(iterable):

    prev = iterable[0]
    for x in iterable[1:]:
        print(x)
        yield prev, x
        prev = x
"""

####################################################################################################

texts = (text1, text2)

raw_text_documents = [RawTextDocument(text) for text in texts]
file_diff = TwoWayFileDiffFactory().process(* raw_text_documents,
                                            number_of_lines_of_context=3)

# file_diff.pretty_print()
# print('\n'*5)
# file_diff.print_unidiff()
# print('\n'*5)

chunks1 = []
chunks2 = []

# Grab long chunk over files
# chunk > group > file

for group in file_diff:
    group_text1 = ''
    group_text2 = ''
    for chunk in group:
        if not isinstance(chunk, TwoWayLineChunkEqual):
            chunks1.append(chunk.chunk1)
            chunks2.append(chunk.chunk2)
        text1 = str(chunk.chunk1)
        text2 = str(chunk.chunk2)
        group_text1 += text1
        group_text2 += text2
        print(chunk)
        print('-'*100)
        print(text1.rstrip())
        print('-'*100)
        print(text2.rstrip())
        print('-'*100)
    # chunks1.append(group_text1)
    # chunks2.append(group_text2)

# Compute distance matrix
distances = []
for i, chunk1 in enumerate(chunks1):
    for j, chunk2 in enumerate(chunks2):
        distance = levenshtein_distance(str(chunk1), str(chunk2))
        distances.append((i, j, distance))
# Find best candidate for each chunk
distances.sort(key=lambda x: x[2])

print('\n'*5)
for i, j, distance in distances:
    print('='*100)
    text1 = str(chunks1[i])
    text2 = str(chunks2[j])
    print(distance)
    print('-'*50)
    print(text1.rstrip())
    print('-'*50)
    print(text2.rstrip())

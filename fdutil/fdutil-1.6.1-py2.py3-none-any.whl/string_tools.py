# encoding: utf-8
import re


def limit_word_length(word,
                      maximum_width):

    word_parts = []

    while len(word) > maximum_width:
        word_parts.append(word[0:maximum_width - 1] + u'-')
        word = word[(maximum_width - 1):]

    word_parts.append(word)

    return word_parts


def limit_word_lengths(words,
                       max_width):

    limited_words = []
    [limited_words.extend(limit_word_length(word=word,
                                            maximum_width=max_width)) for word in words]

    return limited_words


def make_multi_line_list(line,
                         maximum_width=50):

    """
    Takes a string makes it many lines with a maximum
    maximum_width while with the split points at word
    boundaries (doesn't split words in the middle unless
    the word is over the maximum width).

    :param line:
    :param maximum_width:
    :return:
    """

    multi_line = []
    lines = line.split(u'\n')

    if len(lines) > 1:
        # Need to call multiple times, respecting \n
        for line in lines:
            multi_line.extend(make_multi_line_list(line=line,
                                                   maximum_width=maximum_width))

    else:
        words = limit_word_lengths(words=line.split(u' '),
                                   max_width=maximum_width)
        line = []

        while words:
            word = words.pop(0)
            if not line:
                line.append(word)
                continue

            if len(word) + sum([len(w) for w in line]) + len(line) > maximum_width:
                multi_line.append(u' '.join(line))
                line = [word]
                continue

            line.append(word)

        multi_line.append(u' '.join(line))

    return multi_line


def make_multi_line(line,
                    maximum_width=50):
    return u'\n'.join(make_multi_line_list(line,
                                           maximum_width=maximum_width))


def make_multi_line_conversion(maximum_width=50):
    return {u'converter':     make_multi_line_list,
            u'maximum_width': maximum_width}


def multiple_replace(string,
                     replacements):
    u"""
    From https://stackoverflow.com/a/15448887/2916546

    :param string: Original string
    :param replacements: replacements dictionary
    :return: Modified string

    e.g. multiple_replace("Do you like coffee? No, I prefer tea.",
                          {'coffee':'tea',
                           'tea':'coffee',
                           'like':'prefer'})
    returns 'Do you prefer tea? No, I prefer coffee.'
    """

    pattern = re.compile(u"|".join([re.escape(k)
                                    for k in replacements.keys()]),
                         re.M)
    return pattern.sub(lambda x: replacements[x.group(0)], string)


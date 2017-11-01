

def dedent(text):
    """
    Sames as textwrap's dedent, except that handles the multi-line strings formated like this:
      dedent(
        '''
          line 1
          line 2
        '''
      )
    """
    from textwrap import dedent as _dedent

    # Ignores dedent if the text is a single line.
    if '\n' not in text:
        return text

    result = _dedent(text)

    # Removes (first) leading EOL if there's any.
    if result.startswith('\n'):
        result = result[1:]

    return result

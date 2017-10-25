
import re
def split(s):
    """
    Splits a triple-quoted string by whitespace.

    Also allows comments - anything from '#' to EOL is removed.

    This is used to make it easier to maintain long lists of modules in a simple string, yet also
    have some minimal documentation comments.
    """
    s = s.strip()
    s = re.sub(r'#[^\n]+\n', '', s)
    s = re.sub('[\r\n\t]', '', s)
    a = s.split()

    if __debug__:
        from collections import Counter
        c = Counter(a)
        dups = [key for (key,count) in c.items() if count > 1]
        if dups:
            print('ERROR: Duplicate entries')
            for dup in dups:
                print(' ' + dup)
            import sys
            sys.exit(1)

    return s.split()

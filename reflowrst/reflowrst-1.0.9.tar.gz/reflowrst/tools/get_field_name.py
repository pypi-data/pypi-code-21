def get_field_name(words):
    for x in range(len(words)):
        if words[x].endswith(':') and not words[x].endswith('\\:'):
            field_name = ' '.join(words[0:x + 1])
            words = words[x + 1::]
            return field_name, words
    return 'collect_field.py: ERROR:', []
